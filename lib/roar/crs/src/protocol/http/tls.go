package http

import (
	"crypto/x509"
	"encoding/base64"
	"fmt"
	"os"
	"strings"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// parsePEMBytes mengisolasi logika parsing PEM string, Base64, atau File Path.
func parsePEMBytes(input string) ([]byte, error) {
	input = strings.TrimSpace(input)
	if input == "" {
		return nil, nil
	}

	// Cek jika input adalah raw PEM string
	if strings.Contains(input, "-----BEGIN") {
		return []byte(input), nil
	}

	// Cek jika input adalah Base64 Encoded PEM (Common pada payload JSON/Protobuf)
	if decoded, err := base64.StdEncoding.DecodeString(input); err == nil {
		if strings.Contains(string(decoded), "-----BEGIN") {
			return decoded, nil
		}
	}

	// Cek jika input berupa File Path (Langsung ReadFile tanpa os.Stat untuk mencegah TOCTOU)
	// CATATAN KEAMANAN: Hanya gunakan blok ini jika input dijamin berasal dari trusted source (misal: config internal)
	if bytes, err := os.ReadFile(input); err == nil {
		return bytes, nil
	}

	// Fallback jika berupa byte stream tanpa header PEM baku
	return []byte(input), nil
}

func buildCaTLS(req packet.RequestPacket) (*x509.CertPool, error) {
	if req.TLSCA == "" {
		return nil, nil
	}

	caBytes, err := parsePEMBytes(req.TLSCA)
	if err != nil {
		return nil, fmt.Errorf("process tls-ca failed: %w", err)
	}

	if len(caBytes) == 0 {
		return nil, nil
	}

	pool, err := x509.SystemCertPool()
	if err != nil || pool == nil {
    	pool = x509.NewCertPool()
	}

	if ok := pool.AppendCertsFromPEM(caBytes); !ok {
		return nil, fmt.Errorf("failed to parse custom CA PEM: no valid certificate blocks found")
	}

	return pool, nil
}
