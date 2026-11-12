package main

import (
	"bytes"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/pbkdf2"
	"crypto/rand"
	"crypto/sha256"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"io"
	"math/big"
	"net"
	"net/http"
	"net/http/cookiejar"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/gorilla/websocket"
)

const (
	testPassword = "fixture-recovery-password"
	testColumns  = uint16(120)
	testRows     = uint16(33)
)

type testConsole struct {
	server *ownerWebServer
	http   *httptest.Server
	client *http.Client
	host   string
}

func fixtureConfigAndPassword(t *testing.T) (Config, DecodedPassword) {
	t.Helper()
	salt := []byte("0123456789abcdef")
	hash, err := pbkdf2.Key(
		sha256.New,
		testPassword,
		salt,
		100_000,
		32,
	)
	if err != nil {
		t.Fatal(err)
	}
	config := Config{
		Format: 1,
		Password: PasswordPolicy{
			Algorithm:  "pbkdf2-sha256",
			Iterations: 100_000,
			Salt:       base64.StdEncoding.EncodeToString(salt),
			Hash:       base64.StdEncoding.EncodeToString(hash),
		},
		Session: SessionPolicy{
			SessionTTLSeconds:    300,
			IdleTimeoutSeconds:   120,
			MaxSessions:          4,
			MaxTerminals:         4,
			MaxLoginAttempts:     5,
			LoginWindowSeconds:   60,
			TicketTTLSeconds:     30,
			WebSocketReadSeconds: 60,
		},
	}
	return config, DecodedPassword{Iterations: 100_000, Salt: salt, Hash: hash}
}

func newTestConsole(t *testing.T) *testConsole {
	t.Helper()
	home := t.TempDir() + "/home"
	if err := os.Mkdir(home, 0o700); err != nil {
		t.Fatal(err)
	}
	t.Setenv("HOME", home)
	config, password := fixtureConfigAndPassword(t)
	server, err := newOwnerWebServer(config, password, tlsInputs{})
	if err != nil {
		t.Fatal(err)
	}
	httpServer := httptest.NewTLSServer(server)
	host := strings.TrimPrefix(httpServer.URL, "https://")
	server.publicHost = host
	jar, err := cookiejar.New(nil)
	if err != nil {
		t.Fatal(err)
	}
	transport := httpServer.Client().Transport.(*http.Transport).Clone()
	client := &http.Client{
		Transport: transport,
		Jar:       jar,
		CheckRedirect: func(_ *http.Request, _ []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	t.Cleanup(httpServer.Close)
	t.Cleanup(server.shutdown)
	return &testConsole{server: server, http: httpServer, client: client, host: host}
}

func readStatus(t *testing.T, console *testConsole) statusResponse {
	t.Helper()
	request, err := http.NewRequest(http.MethodGet, console.http.URL+"/api/status", nil)
	if err != nil {
		t.Fatal(err)
	}
	response, err := console.client.Do(request)
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		t.Fatalf("status returned %d", response.StatusCode)
	}
	var status statusResponse
	if err := json.NewDecoder(response.Body).Decode(&status); err != nil {
		t.Fatal(err)
	}
	return status
}

func csrfCookie(t *testing.T, console *testConsole) string {
	t.Helper()
	request, err := http.NewRequest(http.MethodGet, console.http.URL+"/api/status", nil)
	if err != nil {
		t.Fatal(err)
	}
	response, err := console.client.Do(request)
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	for _, cookie := range console.client.Jar.Cookies(request.URL) {
		if cookie.Name == csrfCookieName {
			return cookie.Value
		}
	}
	t.Fatal("CSRF cookie missing")
	return ""
}

func login(t *testing.T, console *testConsole, password, origin string) *http.Response {
	t.Helper()
	body, err := json.Marshal(map[string]string{"password": password})
	if err != nil {
		t.Fatal(err)
	}
	request, err := http.NewRequest(
		http.MethodPost,
		console.http.URL+"/api/login",
		bytes.NewReader(body),
	)
	if err != nil {
		t.Fatal(err)
	}
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Origin", origin)
	request.Header.Set("X-Owner-CSRF", csrfCookie(t, console))
	response, err := console.client.Do(request)
	if err != nil {
		t.Fatal(err)
	}
	return response
}

func successfulLogin(t *testing.T, console *testConsole) {
	t.Helper()
	response := login(t, console, testPassword, "https://"+console.host)
	defer response.Body.Close()
	if response.StatusCode != http.StatusNoContent {
		body, _ := io.ReadAll(response.Body)
		t.Fatalf("login returned %d: %s", response.StatusCode, body)
	}
}

func sessionCookie(t *testing.T, console *testConsole) string {
	t.Helper()
	request, err := http.NewRequest(http.MethodGet, console.http.URL, nil)
	if err != nil {
		t.Fatal(err)
	}
	for _, cookie := range console.client.Jar.Cookies(request.URL) {
		if cookie.Name == sessionCookieName {
			return cookie.Value
		}
	}
	return ""
}

func dialTerminal(t *testing.T, console *testConsole, ticket, origin string) (*websocket.Conn, *http.Response, error) {
	t.Helper()
	dialer := websocket.Dialer{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		Subprotocols:    []string{"owner-terminal.v1", "owner-ticket." + ticket},
	}
	headers := http.Header{}
	if cookie := sessionCookie(t, console); cookie != "" {
		headers.Set("Cookie", sessionCookieName+"="+cookie)
	}
	if origin != "" {
		headers.Set("Origin", origin)
	}
	url := "wss://" + console.host + "/terminal"
	return dialer.Dial(url, headers)
}

func TestPasswordVerification(t *testing.T) {
	_, password := fixtureConfigAndPassword(t)
	if !verifyPassword([]byte(testPassword), password) {
		t.Fatal("correct password was rejected")
	}
	for _, candidate := range []string{"", "wrong", testPassword + "x"} {
		if verifyPassword([]byte(candidate), password) {
			t.Fatalf("invalid password accepted: %q", candidate)
		}
	}
}

func TestLoginValidationAndOriginEnforcement(t *testing.T) {
	console := newTestConsole(t)
	status := readStatus(t, console)
	if status.Authenticated || status.CSRF == "" || status.Ticket != "" {
		t.Fatalf("unexpected unauthenticated status: %+v", status)
	}
	for _, password := range []string{"", "wrong"} {
		response := login(t, console, password, "https://"+console.host)
		response.Body.Close()
		if response.StatusCode != http.StatusUnauthorized {
			t.Fatalf("password %q returned %d", password, response.StatusCode)
		}
	}
	response := login(t, console, testPassword, "https://evil.example")
	response.Body.Close()
	if response.StatusCode != http.StatusForbidden {
		t.Fatalf("cross-origin login returned %d", response.StatusCode)
	}
	successfulLogin(t, console)
	status = readStatus(t, console)
	if !status.Authenticated || status.Ticket == "" {
		t.Fatalf("authenticated status missing ticket: %+v", status)
	}
}

func TestWebSocketRejectsMissingAuthenticationAndOrigin(t *testing.T) {
	console := newTestConsole(t)
	_, _, err := dialTerminal(t, console, strings.Repeat("A", 32), "")
	if err == nil {
		t.Fatal("unauthenticated websocket was accepted")
	}
	successfulLogin(t, console)
	ticket := readStatus(t, console).Ticket
	if _, _, err := dialTerminal(t, console, ticket, "https://evil.example"); err == nil {
		t.Fatal("cross-origin websocket was accepted")
	}
}

func TestInteractivePTYEchoResizeCtrlCAndTicketReuse(t *testing.T) {
	console := newTestConsole(t)
	successfulLogin(t, console)
	ticket := readStatus(t, console).Ticket
	connection, response, err := dialTerminal(t, console, ticket, "https://"+console.host)
	if err != nil {
		if response != nil {
			body, _ := io.ReadAll(response.Body)
			t.Fatalf("websocket dial: %v (%s)", err, body)
		}
		t.Fatal(err)
	}
	defer connection.Close()
	if connection.Subprotocol() != "owner-terminal.v1" {
		t.Fatalf("unexpected websocket protocol: %q", connection.Subprotocol())
	}
	if err := connection.WriteMessage(
		websocket.TextMessage,
		[]byte(`{"type":"resize","cols":120,"rows":33}`),
	); err != nil {
		t.Fatal(err)
	}
	if err := connection.WriteMessage(
		websocket.BinaryMessage,
		[]byte("stty size; printf '\\nOWNER_ECHO_OK\\n'\r"),
	); err != nil {
		t.Fatal(err)
	}
	if !readUntil(t, connection, "OWNER_ECHO_OK") {
		t.Fatal("PTY command output was not returned")
	}
	if !readUntilContainsAny(t, connection, []string{"33 120", "33 120\r\n", "33 120\n"}) {
		t.Fatal("PTY resize was not applied")
	}
	if err := connection.WriteMessage(websocket.BinaryMessage, []byte("sleep 30\r")); err != nil {
		t.Fatal(err)
	}
	time.Sleep(100 * time.Millisecond)
	if err := connection.WriteMessage(websocket.BinaryMessage, []byte{3}); err != nil {
		t.Fatal(err)
	}
	if err := connection.WriteMessage(
		websocket.BinaryMessage,
		[]byte("printf 'OWNER_CTRL_C_OK\\n'\r"),
	); err != nil {
		t.Fatal(err)
	}
	if !readUntil(t, connection, "OWNER_CTRL_C_OK") {
		t.Fatal("Ctrl-C did not interrupt the PTY command")
	}
	if _, _, err := dialTerminal(t, console, ticket, "https://"+console.host); err == nil {
		t.Fatal("websocket ticket was reusable")
	}
}

func TestSessionExpiryInvalidatesTicketAndClosesTerminal(t *testing.T) {
	console := newTestConsole(t)
	current := time.Now()
	console.server.now = func() time.Time { return current }
	successfulLogin(t, console)
	ticket := readStatus(t, console).Ticket
	connection, _, err := dialTerminal(t, console, ticket, "https://"+console.host)
	if err != nil {
		t.Fatal(err)
	}
	defer connection.Close()

	current = current.Add(301 * time.Second)
	request := httptest.NewRequest(http.MethodGet, "/", nil)
	request.AddCookie(&http.Cookie{Name: sessionCookieName, Value: sessionCookie(t, console)})
	if session, ok := console.server.authenticatedSession(request); ok || session != nil {
		t.Fatal("expired session remained authenticated")
	}
	_ = connection.SetReadDeadline(time.Now().Add(2 * time.Second))
	if _, _, err := connection.ReadMessage(); err == nil {
		t.Fatal("expired terminal websocket remained open")
	}
	console.server.mu.Lock()
	sessionCount := len(console.server.sessions)
	active := console.server.activePTY
	console.server.mu.Unlock()
	if sessionCount != 0 || active != 0 {
		t.Fatalf("expired session did not clean up: sessions=%d active=%d", sessionCount, active)
	}
}

func readUntil(t *testing.T, connection *websocket.Conn, marker string) bool {
	t.Helper()
	deadline := time.Now().Add(5 * time.Second)
	_ = connection.SetReadDeadline(deadline)
	var output strings.Builder
	for time.Now().Before(deadline) {
		messageType, data, err := connection.ReadMessage()
		if err != nil {
			return false
		}
		if messageType == websocket.BinaryMessage {
			output.Write(data)
			if strings.Contains(output.String(), marker) {
				return true
			}
		} else {
			t.Logf("terminal control: %s", data)
		}
	}
	t.Logf("terminal output: %q", output.String())
	return false
}

func readUntilContainsAny(t *testing.T, connection *websocket.Conn, markers []string) bool {
	t.Helper()
	deadline := time.Now().Add(2 * time.Second)
	_ = connection.SetReadDeadline(deadline)
	var output strings.Builder
	for time.Now().Before(deadline) {
		messageType, data, err := connection.ReadMessage()
		if err != nil {
			return false
		}
		if messageType == websocket.BinaryMessage {
			output.Write(data)
			for _, marker := range markers {
				if strings.Contains(output.String(), marker) {
					return true
				}
			}
		} else {
			t.Logf("terminal control: %s", data)
		}
	}
	t.Logf("terminal output: %q", output.String())
	return false
}

func TestListenerAndPrivateFilePolicy(t *testing.T) {
	for _, valid := range []string{"10.42.0.1:8443", "127.0.0.1:9443"} {
		if err := validateListen(valid); err != nil {
			t.Fatalf("valid listener rejected: %s: %v", valid, err)
		}
	}
	for _, invalid := range []string{"0.0.0.0:8443", "10.42.0.1:22", "192.168.1.1:8443", "127.0.0.1:0"} {
		if err := validateListen(invalid); err == nil {
			t.Fatalf("invalid listener accepted: %s", invalid)
		}
	}
	path := t.TempDir() + "/private"
	if err := os.WriteFile(path, []byte("secret"), 0o600); err != nil {
		t.Fatal(err)
	}
	data, err := loadPrivateFile(path, 16)
	if err != nil || string(data) != "secret" {
		t.Fatalf("private file rejected: %s %v", data, err)
	}
	if err := os.Chmod(path, 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := loadPrivateFile(path, 16); err == nil {
		t.Fatal("group-readable private file was accepted")
	}
}

func TestSelfSignedNonCATLSCertificateIsAccepted(t *testing.T) {
	key, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		t.Fatal(err)
	}
	template := x509.Certificate{
		SerialNumber: big.NewInt(1),
		Subject:      pkix.Name{CommonName: "owner web"},
		NotBefore:    time.Now().Add(-time.Minute),
		NotAfter:     time.Now().Add(time.Hour),
		IPAddresses:  []net.IP{net.ParseIP("10.42.0.1")},
		KeyUsage:     x509.KeyUsageDigitalSignature,
	}
	der, err := x509.CreateCertificate(rand.Reader, &template, &template, &key.PublicKey, key)
	if err != nil {
		t.Fatal(err)
	}
	keyDER, err := x509.MarshalPKCS8PrivateKey(key)
	if err != nil {
		t.Fatal(err)
	}
	directory := t.TempDir()
	certificatePath := directory + "/cert.pem"
	keyPath := directory + "/key.pem"
	if err := os.WriteFile(
		certificatePath,
		pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der}),
		0o600,
	); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(
		keyPath,
		pem.EncodeToMemory(&pem.Block{Type: "PRIVATE KEY", Bytes: keyDER}),
		0o600,
	); err != nil {
		t.Fatal(err)
	}
	material, err := loadTLSCertificate(certificatePath, keyPath)
	if err != nil {
		t.Fatal(err)
	}
	if material.certificate.Leaf == nil {
		t.Fatal("parsed TLS leaf was not retained")
	}
}
