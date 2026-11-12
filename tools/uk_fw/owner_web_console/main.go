package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"errors"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const (
	programVersion      = "1.0.2"
	versionMarker       = "IONIQ5_OWNER_WEB_VERSION=1.0.2"
	defaultListen       = "10.42.0.1:8443"
	testLoopbackListen  = "127.0.0.1"
	certificateMaxBytes = 64 * 1024
	privateKeyMaxBytes  = 32 * 1024
)

type tlsInputs struct {
	certificate tls.Certificate
}

func main() {
	if err := run(os.Args[1:]); err != nil {
		log.Printf("owner web console: %v", err)
		os.Exit(1)
	}
}

func run(arguments []string) error {
	flags := flag.NewFlagSet("owner-web-console", flag.ContinueOnError)
	flags.SetOutput(os.Stderr)
	listen := flags.String("listen", defaultListen, "private Ethernet listen address")
	credentialsPath := flags.String("credentials", "", "absolute PBKDF2 credential JSON path")
	certificatePath := flags.String("tls-cert", "", "absolute private certificate path")
	keyPath := flags.String("tls-key", "", "absolute private key path")
	version := flags.Bool("version", false, "print the access-console version")
	if err := flags.Parse(arguments); err != nil {
		return err
	}
	if *version {
		fmt.Println(versionMarker)
		return nil
	}
	if flags.NArg() != 0 {
		return errors.New("unexpected positional arguments")
	}
	if err := validateListen(*listen); err != nil {
		return err
	}
	for name, value := range map[string]string{
		"credentials":     *credentialsPath,
		"TLS certificate": *certificatePath,
		"TLS private key": *keyPath,
	} {
		if _, err := resolveFlagPath(value); err != nil {
			return fmt.Errorf("%s: %w", name, err)
		}
	}

	config, password, err := loadConfig(*credentialsPath)
	if err != nil {
		return err
	}
	tlsMaterial, err := loadTLSCertificate(*certificatePath, *keyPath)
	if err != nil {
		return err
	}
	console, err := newOwnerWebServer(config, password, tlsMaterial)
	if err != nil {
		return err
	}
	console.publicHost = *listen
	defer console.shutdown()

	listener, err := net.Listen("tcp4", *listen)
	if err != nil {
		return fmt.Errorf("listen: %w", err)
	}
	tlsListener := tls.NewListener(listener, &tls.Config{
		Certificates: []tls.Certificate{tlsMaterial.certificate},
		MinVersion:   tls.VersionTLS12,
	})
	httpServer := &http.Server{
		Handler:           console,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      15 * time.Second,
		IdleTimeout:       45 * time.Second,
		MaxHeaderBytes:    16 * 1024,
	}
	serverErr := make(chan error, 1)
	go func() {
		err := httpServer.Serve(tlsListener)
		if !errors.Is(err, http.ErrServerClosed) {
			serverErr <- err
			return
		}
		serverErr <- nil
	}()

	fmt.Printf("%s HTTPS https://%s max-terminal=root-pty\n", versionMarker, *listen)
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM, syscall.SIGHUP)
	defer signal.Stop(signals)
	select {
	case err := <-serverErr:
		return err
	case <-signals:
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		return httpServer.Shutdown(ctx)
	}
}

func validateListen(value string) error {
	host, port, err := net.SplitHostPort(value)
	if err != nil {
		return fmt.Errorf("invalid listen address: %w", err)
	}
	if port == "" || port == "0" {
		return errors.New("listen port must be fixed and nonzero")
	}
	if host == "10.42.0.1" {
		if port != "8443" {
			return errors.New("production listener must be 10.42.0.1:8443")
		}
		return nil
	}
	address := net.ParseIP(host)
	if address == nil || !address.IsLoopback() {
		return errors.New("listener host must be 10.42.0.1 or explicit loopback")
	}
	return nil
}

func loadTLSCertificate(certificatePath, keyPath string) (tlsInputs, error) {
	certificatePEM, err := loadPrivateFile(certificatePath, certificateMaxBytes)
	if err != nil {
		return tlsInputs{}, fmt.Errorf("load TLS certificate: %w", err)
	}
	keyPEM, err := loadPrivateFile(keyPath, privateKeyMaxBytes)
	if err != nil {
		return tlsInputs{}, fmt.Errorf("load TLS private key: %w", err)
	}
	certificate, err := tls.X509KeyPair(certificatePEM, keyPEM)
	if err != nil {
		return tlsInputs{}, fmt.Errorf("parse TLS certificate and key: %w", err)
	}
	if len(certificate.Certificate) == 0 {
		return tlsInputs{}, errors.New("TLS certificate chain is empty")
	}
	leaf, err := x509.ParseCertificate(certificate.Certificate[0])
	if err != nil {
		return tlsInputs{}, fmt.Errorf("parse TLS leaf: %w", err)
	}
	if !leafHasIP(leaf, net.ParseIP("10.42.0.1")) {
		return tlsInputs{}, errors.New("TLS certificate must include IP SAN 10.42.0.1")
	}
	if err := leaf.CheckSignature(
		leaf.SignatureAlgorithm,
		leaf.RawTBSCertificate,
		leaf.Signature,
	); err != nil {
		return tlsInputs{}, errors.New("TLS certificate must be a self-signed pinned certificate")
	}
	certificate.Leaf = leaf
	return tlsInputs{certificate: certificate}, nil
}

func leafHasIP(certificate *x509.Certificate, wanted net.IP) bool {
	for _, candidate := range certificate.IPAddresses {
		if candidate.Equal(wanted) {
			return true
		}
	}
	return false
}
