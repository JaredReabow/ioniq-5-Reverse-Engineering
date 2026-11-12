package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"syscall"
)

const (
	configMaximumBytes  = 16 * 1024
	pbkdf2MinimumRounds = 100_000
	pbkdf2MaximumRounds = 1_500_000
	passwordHashBytes   = 32
	passwordSaltBytes   = 16
)

// Config is the private runtime policy for the browser recovery terminal.
// It contains a verifier, never the recovery password itself.
type Config struct {
	Format   int            `json:"format"`
	Password PasswordPolicy `json:"password"`
	Session  SessionPolicy  `json:"session"`
}

// PasswordPolicy describes a PBKDF2-HMAC-SHA256 verifier.
type PasswordPolicy struct {
	Algorithm  string `json:"algorithm"`
	Iterations int    `json:"iterations"`
	Salt       string `json:"salt"`
	Hash       string `json:"hash"`
}

// SessionPolicy bounds browser logins and root terminals.
type SessionPolicy struct {
	SessionTTLSeconds    int `json:"session_ttl_seconds"`
	IdleTimeoutSeconds   int `json:"idle_timeout_seconds"`
	MaxSessions          int `json:"max_sessions"`
	MaxTerminals         int `json:"max_terminals"`
	MaxLoginAttempts     int `json:"max_login_attempts"`
	LoginWindowSeconds   int `json:"login_window_seconds"`
	TicketTTLSeconds     int `json:"ticket_ttl_seconds"`
	WebSocketReadSeconds int `json:"websocket_read_seconds"`
}

// DecodedPassword is the validated binary form of the configured verifier.
type DecodedPassword struct {
	Iterations int
	Salt       []byte
	Hash       []byte
}

// loadPrivateFile opens one bounded regular file without following a final
// symlink and, when running as root, requires root ownership.
func loadPrivateFile(path string, maximum int64) ([]byte, error) {
	file, err := os.OpenFile(path, os.O_RDONLY|syscall.O_NOFOLLOW|syscall.O_NONBLOCK, 0)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	info, err := file.Stat()
	if err != nil {
		return nil, err
	}
	if !info.Mode().IsRegular() {
		return nil, errors.New("input is not a regular file")
	}
	if info.Size() <= 0 || info.Size() > maximum {
		return nil, fmt.Errorf("input size must be between 1 and %d bytes", maximum)
	}
	if info.Mode().Perm()&0o077 != 0 {
		return nil, errors.New("private input permissions must exclude group and other")
	}
	if os.Geteuid() == 0 {
		stat, ok := info.Sys().(*syscall.Stat_t)
		if !ok || stat.Uid != 0 || stat.Gid != 0 {
			return nil, errors.New("root service inputs must be owned by root:root")
		}
	}
	data, err := io.ReadAll(io.LimitReader(file, maximum+1))
	if err != nil {
		return nil, err
	}
	if int64(len(data)) > maximum {
		return nil, errors.New("input exceeds its size limit")
	}
	return data, nil
}

// loadConfig validates and decodes the private credential policy.
func loadConfig(path string) (Config, DecodedPassword, error) {
	data, err := loadPrivateFile(path, configMaximumBytes)
	if err != nil {
		return Config{}, DecodedPassword{}, fmt.Errorf("load credentials: %w", err)
	}
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	var config Config
	if err := decoder.Decode(&config); err != nil {
		return Config{}, DecodedPassword{}, fmt.Errorf("decode credentials: %w", err)
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return Config{}, DecodedPassword{}, errors.New("credentials contain trailing data")
	}
	password, err := validateConfig(config)
	if err != nil {
		return Config{}, DecodedPassword{}, err
	}
	return config, password, nil
}

func validateConfig(config Config) (DecodedPassword, error) {
	if config.Format != 1 {
		return DecodedPassword{}, errors.New("credential format must be 1")
	}
	if config.Password.Algorithm != "pbkdf2-sha256" {
		return DecodedPassword{}, errors.New("password algorithm must be pbkdf2-sha256")
	}
	if config.Password.Iterations < pbkdf2MinimumRounds ||
		config.Password.Iterations > pbkdf2MaximumRounds {
		return DecodedPassword{}, fmt.Errorf(
			"password iterations must be between %d and %d",
			pbkdf2MinimumRounds, pbkdf2MaximumRounds,
		)
	}
	salt, err := base64.StdEncoding.Strict().DecodeString(config.Password.Salt)
	if err != nil || len(salt) != passwordSaltBytes {
		return DecodedPassword{}, fmt.Errorf("password salt must encode exactly %d bytes", passwordSaltBytes)
	}
	hash, err := base64.StdEncoding.Strict().DecodeString(config.Password.Hash)
	if err != nil || len(hash) != passwordHashBytes {
		return DecodedPassword{}, fmt.Errorf("password hash must encode exactly %d bytes", passwordHashBytes)
	}

	session := config.Session
	if session.SessionTTLSeconds < 60 || session.SessionTTLSeconds > 3600 {
		return DecodedPassword{}, errors.New("session_ttl_seconds must be between 60 and 3600")
	}
	if session.IdleTimeoutSeconds < 30 || session.IdleTimeoutSeconds > session.SessionTTLSeconds {
		return DecodedPassword{}, errors.New("idle timeout must be between 30 and the session TTL")
	}
	if session.MaxSessions < 1 || session.MaxSessions > 16 {
		return DecodedPassword{}, errors.New("max_sessions must be between 1 and 16")
	}
	if session.MaxTerminals < 1 || session.MaxTerminals > 4 {
		return DecodedPassword{}, errors.New("max_terminals must be between 1 and 4")
	}
	if session.MaxLoginAttempts < 3 || session.MaxLoginAttempts > 20 {
		return DecodedPassword{}, errors.New("max_login_attempts must be between 3 and 20")
	}
	if session.LoginWindowSeconds < 30 || session.LoginWindowSeconds > 3600 {
		return DecodedPassword{}, errors.New("login_window_seconds must be between 30 and 3600")
	}
	if session.TicketTTLSeconds < 5 || session.TicketTTLSeconds > 60 {
		return DecodedPassword{}, errors.New("ticket_ttl_seconds must be between 5 and 60")
	}
	if session.WebSocketReadSeconds < 30 || session.WebSocketReadSeconds > 300 {
		return DecodedPassword{}, errors.New("websocket_read_seconds must be between 30 and 300")
	}
	return DecodedPassword{Iterations: config.Password.Iterations, Salt: salt, Hash: hash}, nil
}

// resolveFlagPath keeps service paths predictable while still accepting an
// explicit path in a test environment.
func resolveFlagPath(value string) (string, error) {
	if value == "" {
		return "", errors.New("path must not be empty")
	}
	if filepath.Clean(value) != value || filepath.IsAbs(value) != true {
		return "", fmt.Errorf("path must be clean and absolute: %s", value)
	}
	return value, nil
}
