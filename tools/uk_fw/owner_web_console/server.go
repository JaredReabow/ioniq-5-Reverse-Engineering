package main

import (
	"context"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	sessionCookieName = "owner_web_session"
	csrfCookieName    = "owner_web_csrf"
	loginBodyMaximum  = 512
)

type browserSession struct {
	id             string
	expires        time.Time
	lastSeen       time.Time
	ticket         string
	ticketExpires  time.Time
	terminalActive bool
	cancelTerminal context.CancelFunc
}

type loginAttemptRecord struct {
	start int
	times []time.Time
}

type ownerWebServer struct {
	config       Config
	password     DecodedPassword
	tlsInputs    tlsInputs
	publicHost   string
	now          func() time.Time
	mu           sync.Mutex
	sessions     map[string]*browserSession
	attempts     map[string]*loginAttemptRecord
	activePTY    int
	shutdownOnce sync.Once
	done         chan struct{}
}

type statusResponse struct {
	Version       string `json:"version"`
	Authenticated bool   `json:"authenticated"`
	CSRF          string `json:"csrf,omitempty"`
	Ticket        string `json:"ticket,omitempty"`
	ExpiresAt     string `json:"expires_at,omitempty"`
	ActivePTY     int    `json:"active_pty"`
	MaxPTY        int    `json:"max_pty"`
}

type websocketAuthorization struct {
	sessionID string
}

// newOwnerWebServer creates the specified HTTP handler without opening a
// network listener. Tests use this entry point with loopback TLS.
func newOwnerWebServer(config Config, password DecodedPassword, material tlsInputs) (*ownerWebServer, error) {
	if _, err := validateConfig(config); err != nil {
		return nil, err
	}
	server := &ownerWebServer{
		config:     config,
		password:   password,
		tlsInputs:  material,
		publicHost: defaultListen,
		now:        time.Now,
		sessions:   make(map[string]*browserSession),
		attempts:   make(map[string]*loginAttemptRecord),
		done:       make(chan struct{}),
	}
	go server.expirationLoop()
	return server, nil
}

func (server *ownerWebServer) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	server.securityHeaders(writer, request)
	if !server.validHost(request) {
		http.Error(writer, "invalid host", http.StatusMisdirectedRequest)
		return
	}
	switch request.URL.Path {
	case "/":
		if request.Method != http.MethodGet {
			methodNotAllowed(writer, http.MethodGet)
			return
		}
		server.serveAsset(writer, "WEB_UI.html", "text/html; charset=utf-8")
	case "/assets/app.js":
		if request.Method != http.MethodGet {
			methodNotAllowed(writer, http.MethodGet)
			return
		}
		server.serveAsset(writer, "assets/app.js", "text/javascript; charset=utf-8")
	case "/api/status":
		server.handleStatus(writer, request)
	case "/api/login":
		server.handleLogin(writer, request)
	case "/api/logout":
		server.handleLogout(writer, request)
	case "/terminal":
		server.handleTerminal(writer, request)
	default:
		http.NotFound(writer, request)
	}
}

func (server *ownerWebServer) securityHeaders(writer http.ResponseWriter, request *http.Request) {
	host := server.publicHost
	if host == "" {
		host = defaultListen
	}
	writer.Header().Set("Cache-Control", "no-store, max-age=0")
	writer.Header().Set("Content-Security-Policy",
		"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "+
			"connect-src 'self' wss://"+host+"; img-src 'self' data:; "+
			"frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
	writer.Header().Set("Cross-Origin-Opener-Policy", "same-origin")
	writer.Header().Set("Cross-Origin-Resource-Policy", "same-origin")
	writer.Header().Set("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
	writer.Header().Set("Referrer-Policy", "no-referrer")
	writer.Header().Set("Strict-Transport-Security", "max-age=86400")
	writer.Header().Set("X-Content-Type-Options", "nosniff")
	writer.Header().Set("X-Frame-Options", "DENY")
}

func (server *ownerWebServer) validHost(request *http.Request) bool {
	return subtle.ConstantTimeCompare(
		[]byte(request.Host),
		[]byte(server.publicHost),
	) == 1
}

func (server *ownerWebServer) validOrigin(request *http.Request) bool {
	expected := "https://" + server.publicHost
	return subtle.ConstantTimeCompare(
		[]byte(request.Header.Get("Origin")),
		[]byte(expected),
	) == 1
}

func (server *ownerWebServer) validWriteCSRF(request *http.Request) bool {
	if !server.validOrigin(request) {
		return false
	}
	cookie, err := request.Cookie(csrfCookieName)
	if err != nil || cookie.Value == "" {
		return false
	}
	provided := request.Header.Get("X-Owner-CSRF")
	return provided != "" && subtle.ConstantTimeCompare(
		[]byte(cookie.Value),
		[]byte(provided),
	) == 1
}

func (server *ownerWebServer) serveAsset(writer http.ResponseWriter, name, contentType string) {
	data, err := embeddedAssets.ReadFile(name)
	if err != nil {
		http.Error(writer, "asset unavailable", http.StatusInternalServerError)
		return
	}
	writer.Header().Set("Content-Type", contentType)
	writer.WriteHeader(http.StatusOK)
	_, _ = writer.Write(data)
}

func (server *ownerWebServer) handleStatus(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodGet {
		methodNotAllowed(writer, http.MethodGet)
		return
	}
	csrf, err := server.ensureCSRF(writer, request)
	if err != nil {
		http.Error(writer, "session unavailable", http.StatusServiceUnavailable)
		return
	}
	response := statusResponse{
		Version: programVersion,
		CSRF:    csrf,
		MaxPTY:  server.config.Session.MaxTerminals,
	}
	if session, ok := server.authenticatedSession(request); ok {
		ticket, err := randomToken(24)
		if err != nil {
			http.Error(writer, "session unavailable", http.StatusServiceUnavailable)
			return
		}
		now := server.now()
		server.mu.Lock()
		session.ticket = ticket
		session.ticketExpires = now.Add(
			time.Duration(server.config.Session.TicketTTLSeconds) * time.Second,
		)
		session.lastSeen = now
		response.Authenticated = true
		response.Ticket = ticket
		response.ExpiresAt = session.expires.UTC().Format(time.RFC3339)
		response.ActivePTY = server.activePTY
		server.mu.Unlock()
	}
	writeJSON(writer, http.StatusOK, response)
}

func (server *ownerWebServer) ensureCSRF(writer http.ResponseWriter, request *http.Request) (string, error) {
	if cookie, err := request.Cookie(csrfCookieName); err == nil && len(cookie.Value) >= 32 {
		return cookie.Value, nil
	}
	token, err := randomToken(24)
	if err != nil {
		return "", err
	}
	http.SetCookie(writer, server.cookie(csrfCookieName, token, time.Hour))
	return token, nil
}

func (server *ownerWebServer) cookie(name, value string, ttl time.Duration) *http.Cookie {
	return &http.Cookie{
		Name:     name,
		Value:    value,
		Path:     "/",
		MaxAge:   int(ttl / time.Second),
		Expires:  server.now().Add(ttl),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
	}
}

func (server *ownerWebServer) expiredCookie(name string) *http.Cookie {
	return &http.Cookie{
		Name:     name,
		Value:    "",
		Path:     "/",
		MaxAge:   -1,
		Expires:  time.Unix(1, 0),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
	}
}

func (server *ownerWebServer) authenticatedSession(request *http.Request) (*browserSession, bool) {
	cookie, err := request.Cookie(sessionCookieName)
	if err != nil || cookie.Value == "" {
		return nil, false
	}
	now := server.now()
	server.mu.Lock()
	defer server.mu.Unlock()
	session := server.sessions[cookie.Value]
	if session == nil || !now.Before(session.expires) {
		if session != nil {
			server.endSessionLocked(session)
		}
		return nil, false
	}
	idle := time.Duration(server.config.Session.IdleTimeoutSeconds) * time.Second
	if now.Sub(session.lastSeen) >= idle {
		server.endSessionLocked(session)
		return nil, false
	}
	session.lastSeen = now
	return session, true
}

func (server *ownerWebServer) handleLogin(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		methodNotAllowed(writer, http.MethodPost)
		return
	}
	if !server.validWriteCSRF(request) {
		http.Error(writer, "request rejected", http.StatusForbidden)
		return
	}
	mediaType, _, err := mime.ParseMediaType(request.Header.Get("Content-Type"))
	if err != nil || mediaType != "application/json" {
		http.Error(writer, "application/json required", http.StatusUnsupportedMediaType)
		return
	}
	body := http.MaxBytesReader(writer, request.Body, loginBodyMaximum)
	decoder := json.NewDecoder(body)
	decoder.DisallowUnknownFields()
	var payload struct {
		Password string `json:"password"`
	}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(writer, "invalid login request", http.StatusBadRequest)
		return
	}
	if err := decoder.Decode(&struct{}{}); err != io.EOF {
		http.Error(writer, "invalid login request", http.StatusBadRequest)
		return
	}
	if !server.allowLoginAttempt(request.RemoteAddr) {
		writer.Header().Set("Retry-After", strconv.Itoa(server.config.Session.LoginWindowSeconds))
		http.Error(writer, "too many attempts", http.StatusTooManyRequests)
		return
	}
	if !verifyPassword([]byte(payload.Password), server.password) {
		http.Error(writer, "authentication failed", http.StatusUnauthorized)
		return
	}
	token, err := randomToken(32)
	if err != nil {
		http.Error(writer, "session unavailable", http.StatusServiceUnavailable)
		return
	}
	now := server.now()
	server.mu.Lock()
	for id, session := range server.sessions {
		if !now.Before(session.expires) ||
			now.Sub(session.lastSeen) >= time.Duration(server.config.Session.IdleTimeoutSeconds)*time.Second {
			server.endSessionLocked(session, id)
		}
	}
	if len(server.sessions) >= server.config.Session.MaxSessions {
		server.mu.Unlock()
		http.Error(writer, "session limit reached", http.StatusTooManyRequests)
		return
	}
	server.sessions[token] = &browserSession{
		id:       token,
		expires:  now.Add(time.Duration(server.config.Session.SessionTTLSeconds) * time.Second),
		lastSeen: now,
	}
	server.mu.Unlock()
	http.SetCookie(writer, server.cookie(
		sessionCookieName,
		token,
		time.Duration(server.config.Session.SessionTTLSeconds)*time.Second,
	))
	writer.WriteHeader(http.StatusNoContent)
}

func (server *ownerWebServer) allowLoginAttempt(remote string) bool {
	host, _, err := net.SplitHostPort(remote)
	if err != nil || host == "" {
		host = remote
	}
	now := server.now()
	window := time.Duration(server.config.Session.LoginWindowSeconds) * time.Second
	server.mu.Lock()
	defer server.mu.Unlock()
	if len(server.attempts) >= 128 {
		for key, record := range server.attempts {
			if now.Sub(record.times[len(record.times)-1]) >= window {
				delete(server.attempts, key)
			}
		}
		if len(server.attempts) >= 128 {
			return false
		}
	}
	record := server.attempts[host]
	if record == nil {
		record = &loginAttemptRecord{start: 0}
		server.attempts[host] = record
	}
	firstValid := 0
	for firstValid < len(record.times) && now.Sub(record.times[firstValid]) >= window {
		firstValid++
	}
	record.times = record.times[firstValid:]
	if len(record.times) >= server.config.Session.MaxLoginAttempts {
		return false
	}
	record.times = append(record.times, now)
	return true
}

func (server *ownerWebServer) handleLogout(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		methodNotAllowed(writer, http.MethodPost)
		return
	}
	if !server.validWriteCSRF(request) {
		http.Error(writer, "request rejected", http.StatusForbidden)
		return
	}
	if cookie, err := request.Cookie(sessionCookieName); err == nil {
		server.mu.Lock()
		if session := server.sessions[cookie.Value]; session != nil {
			server.endSessionLocked(session, cookie.Value)
		}
		server.mu.Unlock()
	}
	http.SetCookie(writer, server.expiredCookie(sessionCookieName))
	writer.WriteHeader(http.StatusNoContent)
}

func (server *ownerWebServer) authorizeWebSocket(request *http.Request) (websocketAuthorization, error) {
	if request.Method != http.MethodGet {
		return websocketAuthorization{}, errors.New("method")
	}
	if !server.validHost(request) || !server.validOrigin(request) {
		return websocketAuthorization{}, errors.New("origin")
	}
	cookie, err := request.Cookie(sessionCookieName)
	if err != nil || cookie.Value == "" {
		return websocketAuthorization{}, errors.New("session")
	}
	ticket := ""
	validProtocol := false
	for _, protocol := range strings.Split(request.Header.Get("Sec-WebSocket-Protocol"), ",") {
		protocol = strings.TrimSpace(protocol)
		if protocol == "owner-terminal.v1" {
			validProtocol = true
		}
		if strings.HasPrefix(protocol, "owner-ticket.") {
			if ticket != "" {
				return websocketAuthorization{}, errors.New("ticket")
			}
			ticket = strings.TrimPrefix(protocol, "owner-ticket.")
		}
	}
	if !validProtocol || len(ticket) < 32 {
		return websocketAuthorization{}, errors.New("protocol")
	}
	now := server.now()
	server.mu.Lock()
	defer server.mu.Unlock()
	session := server.sessions[cookie.Value]
	if session == nil || !now.Before(session.expires) ||
		now.Sub(session.lastSeen) >= time.Duration(server.config.Session.IdleTimeoutSeconds)*time.Second ||
		session.ticket == "" || !now.Before(session.ticketExpires) ||
		subtle.ConstantTimeCompare([]byte(session.ticket), []byte(ticket)) != 1 {
		if session != nil {
			server.endSessionLocked(session, session.id)
		}
		return websocketAuthorization{}, errors.New("session")
	}
	session.ticket = ""
	session.ticketExpires = time.Time{}
	session.lastSeen = now
	return websocketAuthorization{sessionID: session.id}, nil
}

func (server *ownerWebServer) claimTerminal(sessionID string) (context.Context, context.CancelFunc, error) {
	server.mu.Lock()
	defer server.mu.Unlock()
	session := server.sessions[sessionID]
	if session == nil || !server.now().Before(session.expires) || session.terminalActive {
		return nil, nil, errors.New("terminal session unavailable")
	}
	if server.activePTY >= server.config.Session.MaxTerminals {
		return nil, nil, errors.New("terminal limit reached")
	}
	ctx, cancel := context.WithCancel(context.Background())
	session.terminalActive = true
	session.cancelTerminal = cancel
	server.activePTY++
	return ctx, func() {
		cancel()
		server.mu.Lock()
		session.terminalActive = false
		session.cancelTerminal = nil
		server.activePTY--
		server.mu.Unlock()
	}, nil
}

func (server *ownerWebServer) endSessionLocked(session *browserSession, ids ...string) {
	id := session.id
	if len(ids) > 0 {
		id = ids[0]
	}
	if session.cancelTerminal != nil {
		session.cancelTerminal()
	}
	delete(server.sessions, id)
}

func (server *ownerWebServer) expirationLoop() {
	ticker := time.NewTicker(15 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-server.done:
			return
		case now := <-ticker.C:
			idle := time.Duration(server.config.Session.IdleTimeoutSeconds) * time.Second
			server.mu.Lock()
			for id, session := range server.sessions {
				if !now.Before(session.expires) || now.Sub(session.lastSeen) >= idle {
					server.endSessionLocked(session, id)
				}
			}
			for host, record := range server.attempts {
				if len(record.times) == 0 ||
					now.Sub(record.times[len(record.times)-1]) >=
						time.Duration(server.config.Session.LoginWindowSeconds)*time.Second {
					delete(server.attempts, host)
				}
			}
			server.mu.Unlock()
		}
	}
}

func (server *ownerWebServer) shutdown() {
	server.shutdownOnce.Do(func() {
		close(server.done)
		server.mu.Lock()
		for _, session := range server.sessions {
			server.endSessionLocked(session, session.id)
		}
		server.mu.Unlock()
	})
}

func methodNotAllowed(writer http.ResponseWriter, allowed string) {
	writer.Header().Set("Allow", allowed)
	http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}

// runtimeHome ensures a private HOME exists for the root shell without looking
// up an account in /etc/passwd.
func runtimeHome() (string, error) {
	home := os.Getenv("HOME")
	if home == "" {
		home = "/run/ioniq-owner-web"
	}
	if !strings.HasPrefix(home, "/") {
		return "", errors.New("HOME must be absolute")
	}
	if err := os.MkdirAll(home, 0o700); err != nil {
		return "", fmt.Errorf("create terminal HOME: %w", err)
	}
	info, err := os.Stat(home)
	if err != nil {
		return "", fmt.Errorf("inspect terminal HOME: %w", err)
	}
	if !info.IsDir() || info.Mode().Perm() != 0o700 {
		return "", fmt.Errorf(
			"terminal HOME must be a private directory with mode 0700, got %04o",
			info.Mode().Perm(),
		)
	}
	return home, nil
}
