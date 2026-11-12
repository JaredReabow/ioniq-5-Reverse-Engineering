package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"syscall"
	"time"

	"github.com/creack/pty"
	"github.com/gorilla/websocket"
)

const (
	websocketBinaryMaximum = 4096
	websocketTextMaximum   = 512
	websocketWriteWait     = 10 * time.Second
)

type resizeControl struct {
	Type string `json:"type"`
	Cols uint16 `json:"cols"`
	Rows uint16 `json:"rows"`
}

type terminalProcess struct {
	master  *os.File
	command *exec.Cmd
	done    chan error
	once    sync.Once
}

// startRootTerminal starts /bin/sh in a pseudo-terminal owned by the service.
// No getpwnam, shell-config, SSH, or PAM lookup is involved.
func startRootTerminal(columns, rows uint16) (*terminalProcess, error) {
	home, err := runtimeHome()
	if err != nil {
		return nil, err
	}
	command := exec.Command("/bin/sh")
	command.Env = []string{
		"HOME=" + home,
		"TERM=xterm-256color",
		"PATH=/opt/ioniq-owner/bin:/usr/sbin:/usr/bin:/sbin:/bin",
		"LANG=C",
	}
	command.Dir = home
	master, err := pty.StartWithSize(command, &pty.Winsize{Cols: columns, Rows: rows})
	if err != nil {
		return nil, fmt.Errorf("start root PTY: %w", err)
	}
	process := &terminalProcess{
		master:  master,
		command: command,
		done:    make(chan error, 1),
	}
	go func() {
		process.done <- command.Wait()
		close(process.done)
	}()
	return process, nil
}

func (process *terminalProcess) resize(columns, rows uint16) error {
	return pty.Setsize(process.master, &pty.Winsize{Cols: columns, Rows: rows})
}

func (process *terminalProcess) close() {
	process.once.Do(func() {
		select {
		case <-process.done:
			_ = process.master.Close()
			return
		default:
		}
		if process.command.Process != nil {
			pid := process.command.Process.Pid
			_ = syscall.Kill(-pid, syscall.SIGHUP)
			_ = syscall.Kill(-pid, syscall.SIGTERM)
		}
		_ = process.master.Close()
		select {
		case <-process.done:
		case <-time.After(500 * time.Millisecond):
			if process.command.Process != nil {
				_ = syscall.Kill(-process.command.Process.Pid, syscall.SIGKILL)
			}
			select {
			case <-process.done:
			case <-time.After(time.Second):
			}
		}
	})
}

func (server *ownerWebServer) handleTerminal(writer http.ResponseWriter, request *http.Request) {
	authorization, err := server.authorizeWebSocket(request)
	if err != nil {
		http.Error(writer, "terminal authentication failed", http.StatusUnauthorized)
		return
	}
	ctx, release, err := server.claimTerminal(authorization.sessionID)
	if err != nil {
		http.Error(writer, err.Error(), http.StatusConflict)
		return
	}
	defer release()

	upgrader := websocket.Upgrader{
		Subprotocols: []string{"owner-terminal.v1"},
		CheckOrigin: func(candidate *http.Request) bool {
			return server.validOrigin(candidate) && server.validHost(candidate)
		},
	}
	connection, err := upgrader.Upgrade(writer, request, nil)
	if err != nil {
		return
	}
	defer connection.Close()

	process, err := startRootTerminal(100, 30)
	if err != nil {
		log.Printf("start root terminal: %v", err)
		_ = connection.WriteMessage(
			websocket.TextMessage,
			[]byte(`{"type":"error","message":"terminal start failed"}`),
		)
		return
	}
	defer process.close()
	terminalContext, cancel := context.WithCancel(ctx)
	defer cancel()

	var writeMu sync.Mutex
	writeFrame := func(messageType int, data []byte) error {
		writeMu.Lock()
		defer writeMu.Unlock()
		_ = connection.SetWriteDeadline(time.Now().Add(websocketWriteWait))
		return connection.WriteMessage(messageType, data)
	}
	connection.SetPongHandler(func(string) error {
		return connection.SetReadDeadline(time.Now().Add(
			time.Duration(server.config.Session.WebSocketReadSeconds) * time.Second,
		))
	})
	_ = connection.SetReadDeadline(time.Now().Add(
		time.Duration(server.config.Session.WebSocketReadSeconds) * time.Second,
	))
	connection.SetReadLimit(websocketBinaryMaximum)

	result := make(chan error, 3)
	go func() {
		buffer := make([]byte, 4096)
		for {
			count, err := process.master.Read(buffer)
			if count > 0 {
				if err := writeFrame(websocket.BinaryMessage, buffer[:count]); err != nil {
					result <- err
					return
				}
			}
			if err != nil {
				if errors.Is(err, io.EOF) {
					result <- nil
				} else {
					result <- err
				}
				return
			}
		}
	}()
	go func() {
		for {
			messageType, data, err := connection.ReadMessage()
			if err != nil {
				result <- err
				return
			}
			switch messageType {
			case websocket.BinaryMessage:
				if len(data) > websocketBinaryMaximum {
					result <- errors.New("terminal input frame exceeds limit")
					return
				}
				if len(data) > 0 {
					if _, err := process.master.Write(data); err != nil {
						result <- err
						return
					}
				}
			case websocket.TextMessage:
				if len(data) > websocketTextMaximum {
					result <- errors.New("terminal control frame exceeds limit")
					return
				}
				var control resizeControl
				if err := json.Unmarshal(data, &control); err != nil ||
					control.Type != "resize" || control.Cols < 20 || control.Cols > 300 ||
					control.Rows < 5 || control.Rows > 120 {
					result <- errors.New("invalid terminal control frame")
					return
				}
				if err := process.resize(control.Cols, control.Rows); err != nil {
					result <- err
					return
				}
			default:
				result <- errors.New("unsupported terminal frame type")
				return
			}
		}
	}()
	go func() {
		ticker := time.NewTicker(20 * time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-terminalContext.Done():
				return
			case <-ticker.C:
				writeMu.Lock()
				_ = connection.SetWriteDeadline(time.Now().Add(websocketWriteWait))
				err := connection.WriteMessage(websocket.PingMessage, []byte("owner"))
				writeMu.Unlock()
				if err != nil {
					result <- err
					return
				}
			}
		}
	}()

	select {
	case <-terminalContext.Done():
	case <-result:
	}
	cancel()
	process.close()
	writeMu.Lock()
	_ = connection.SetWriteDeadline(time.Now().Add(time.Second))
	_ = connection.WriteControl(
		websocket.CloseMessage,
		websocket.FormatCloseMessage(websocket.CloseNormalClosure, "terminal closed"),
		time.Now().Add(time.Second),
	)
	writeMu.Unlock()
	_ = connection.Close()
}
