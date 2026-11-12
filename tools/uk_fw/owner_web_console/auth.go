package main

import (
	"crypto/pbkdf2"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"errors"
)

const passwordMaximumBytes = 256

// verifyPassword derives the configured verifier and compares it in constant
// time. Blank passwords are rejected before invoking PBKDF2.
func verifyPassword(password []byte, policy DecodedPassword) bool {
	if len(password) == 0 || len(password) > passwordMaximumBytes {
		return false
	}
	derived, err := pbkdf2.Key(
		sha256.New,
		string(password),
		policy.Salt,
		policy.Iterations,
		len(policy.Hash),
	)
	if err != nil || len(derived) != len(policy.Hash) {
		return false
	}
	return subtle.ConstantTimeCompare(derived, policy.Hash) == 1
}

// randomToken returns an unguessable URL-safe value with at least 192 bits of
// entropy.
func randomToken(bytes int) (string, error) {
	if bytes < 24 || bytes > 64 {
		return "", errors.New("token entropy must be between 24 and 64 bytes")
	}
	value := make([]byte, bytes)
	if _, err := rand.Read(value); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(value), nil
}
