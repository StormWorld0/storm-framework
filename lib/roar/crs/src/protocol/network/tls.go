package network

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

type tlsConnStateGetter interface {
	ConnectionState() tls.ConnectionState
}

func isTLSConn(c net.Conn) bool {
	if c == nil {
		return false
	}
	_, ok := c.(tlsConnStateGetter)
	return ok
}

func tlsVersionString(v uint16) string {
	switch v {
	case tls.VersionTLS10:
		return "TLS 1.0"
	case tls.VersionTLS11:
		return "TLS 1.1"
	case tls.VersionTLS12:
		return "TLS 1.2"
	case tls.VersionTLS13:
		return "TLS 1.3"
	default:
		return strconv.Itoa(int(v))
	}
}

func buildCustomTLSConfig(req packet.RequestPacket) (*tls.Config, error) {
	tlsConfig := &tls.Config{
		InsecureSkipVerify: !req.Verify,
		MinVersion:         tls.VersionTLS10,
	}

	getPEMBytes := func(input string) ([]byte, error) {
		if input == "" {
			return nil, nil
		}
		if strings.Contains(input, "-----BEGIN") {
			return []byte(input), nil
		}
		if _, err := os.Stat(input); err == nil {
			bytes, err := os.ReadFile(input)
			if err != nil {
				return nil, fmt.Errorf("read file %s failed: %w", input, err)
			}
			return bytes, nil
		}
		return []byte(input), nil
	}

	if req.TLSCert != "" && req.TLSKey != "" {
		certBytes, err := getPEMBytes(req.TLSCert)
		if err != nil {
			return nil, fmt.Errorf("process tls-cert failed: %w", err)
		}
		keyBytes, err := getPEMBytes(req.TLSKey)
		if err != nil {
			return nil, fmt.Errorf("process tls-key failed: %w", err)
		}
		cert, err := tls.X509KeyPair(certBytes, keyBytes)
		if err != nil {
			return nil, fmt.Errorf("load x509 key pair: %w", err)
		}
		tlsConfig.Certificates = []tls.Certificate{cert}
	}

	if req.TLSCA != "" {
		caBytes, err := getPEMBytes(req.TLSCA)
		if err != nil {
			return nil, fmt.Errorf("process tls-ca failed: %w", err)
		}
		caCertPool := x509.NewCertPool()
		if !caCertPool.AppendCertsFromPEM(caBytes) {
			return nil, fmt.Errorf("failed to parse custom CA PEM")
		}
		tlsConfig.RootCAs = caCertPool
	}

	return tlsConfig, nil
}

// ExtractTLSInfo menarik state kriptografi dari koneksi.
func ExtractTLSInfo(conn net.Conn) map[string]interface{} {
	if stateGetter, ok := conn.(tlsConnStateGetter); ok {
		state := stateGetter.ConnectionState()
		if state.HandshakeComplete || state.Version != 0 {
			tlsData := map[string]interface{}{
				"tls_version":    tlsVersionString(state.Version),
				"cipher_suite":   tls.CipherSuiteName(state.CipherSuite),
				"protocol":       state.NegotiatedProtocol,
				"hostname":       state.ServerName,
				"handshake":      state.HandshakeComplete,
				"session_resume": state.DidResume,
			}
			if len(state.PeerCertificates) > 0 {
				cert := state.PeerCertificates[0]
				tlsData["subject"] = cert.Subject.CommonName
				tlsData["issuer"] = cert.Issuer.CommonName
				tlsData["dns_name"] = cert.DNSNames
				tlsData["expires"] = cert.NotAfter.Format(time.RFC3339)
			}
			if len(state.VerifiedChains) > 0 {
				tlsData["cert_chain_count"] = len(state.VerifiedChains)
			}
			return tlsData
		}
	}
	return nil
}

