package socket

import (
	"os"
	"fmt"
	"strings"
	"crypto/x509"
	utls "github.com/refraction-networking/utls"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func buildCustomTLSConfig(req packet.RequestPacket) (*utls.Config, error) {
	utlsConfig := &utls.Config{
		InsecureSkipVerify: !req.Verify,
		MinVersion:         utls.VersionTLS10,
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
		cert, err := utls.X509KeyPair(certBytes, keyBytes)
		if err != nil {
			return nil, fmt.Errorf("load x509 key pair: %w", err)
		}
		utlsConfig.Certificates = []utls.Certificate{cert}
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
		utlsConfig.RootCAs = caCertPool
	}

	return utlsConfig, nil
}
