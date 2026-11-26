package http

import (
	"os"
	"fmt"
	"strings"
	"net/url"
	"crypto/x509"
	"crypto/tls"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func buildCustomTLSConfig(req packet.RequestPacket) (*tls.Config, error) {
	tlsConfig := &tls.Config{
		InsecureSkipVerify: !req.Verify,
		MinVersion:         tls.VersionTLS10,
		Renegotiation:      tls.RenegotiateOnceAsClient,
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

	u, err := url.Parse(req.URL)
	if err != nil {
		return nil, err
	}

	hostOnly := u.Hostname()
	if hostOnly == "" {
		return nil, fmt.Errorf("failed to extract host from url")
	}

	if tlsConfig.ServerName == "" {
		tlsConfig.ServerName = hostOnly
	}

	return tlsConfig, nil
}
