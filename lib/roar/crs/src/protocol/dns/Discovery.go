// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package dns

import (
	"crypto/tls"
	"net/http"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

var httpClient *http.Client

func init() {
	// Reusable transport object to avoid socket exhaustion (TIME_WAIT limit)
	customTransport := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: skipVerify,
			MinVersion:         tls.VersionTLS10,
		},
		DisableKeepAlives:   true,
		MaxIdleConns:        1000,
		MaxIdleConnsPerHost: 100,
	}

	httpClient = &http.Client{
		Transport: customTransport,
		// Default timeout fallback, overridden by packet below if provided
		Timeout: 3 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 2 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}
}

// HTTP menangani request HTTP terstandarisasi
func Discovery(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take() // rate-limiter

	targetURL := req.URL
	if targetURL == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "Domain/URL not found in RequestPacket"}
	}

	// Dynamic Timeout
	if req.Timeout > 0 {
		httpClient.Timeout = time.Duration(req.Timeout * float64(time.Second))
	}

	httpReq, err := http.NewRequest("HEAD", targetURL, nil)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create HTTP request: " + err.Error()}
	}
	
	// Default UA
	httpReq.Header.Set("User-Agent", "storm-framework/3.0 (CRS Engine)")
    if req.UA {
		httpReq.Header.Set("User-Agent", req.UA)
	}
	
	resp, err := httpClient.Do(httpReq)
	if err != nil {
		return packet.ResponsePacket{Status: "FAILED", Message: err.Error()}
	}
	defer resp.Body.Close()

	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			headers[k] = v 
		}
	}

	var tlsData map[string]interface{}

    if req.InfoTLS && resp.TLS != nil {
	    // Dapatkan detail handshake SSL/TLS
    	state := resp.TLS
    	if len(state.PeerCertificates) > 0 {
		    cert := state.PeerCertificates[0] // Leaf Certificate
		    tlsData = map[string]interface{}{
			    "subject":          cert.Subject.CommonName,
			    "issuer":           cert.Issuer.CommonName,
			    "dns_names":        cert.DNSNames,
			    "expires_at":       cert.NotAfter.Format(time.RFC3339),
			    "tls_version":      tlsVersionString(state.Version),
			    "cipher_suite":     tls.CipherSuiteName(state.CipherSuite),
				"protocol":         state.NegotiatedProtocol,
				"hostname":         state.ServerName,
				"handshake":        state.HandshakeComplete,
				"session_resume":   state.DidResume,
				"cert_chain":       state.VerifiedChains,
			}
	    }
    }

	// Evaluasi HTTP codes
	if resp.StatusCode < 400 || resp.StatusCode == 401 || resp.StatusCode == 403 {
		return packet.ResponsePacket{
			Status: "SUCCESS",
			Data: map[string]interface{}{
				"status_code":   resp.StatusCode,
				"headers":       headers,
				"protocol":      resp.Proto,
			    "info_tls":      tlsData,
				"engine":        "Discovery",
			},
		}
	}

	return packet.ResponsePacket{
		Status:  "FAILED",
		Message: "Endpoint not accessible or ignored status code",
	}
}

