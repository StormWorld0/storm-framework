// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package dns

import (
	"context"
	"crypto/tls"
	"net/http"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
)

var httpClient *http.Client
const skipVerify = true // Sesuaikan variabel ini jika belum terdefinisi

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
		// Timeout global default jika context tidak menentukan
		Timeout: 5 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 2 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}
}

// Discovery menangani request HTTP terstandarisasi
func Discovery(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take() // rate-limiter

	targetURL := req.URL
	if targetURL == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "Domain/URL not found in RequestPacket"}
	}

	// Dynamic Timeout yang Thread-Safe menggunakan Context (Bukan mengedit httpClient global)
	timeout := 3 * time.Second
	if req.Timeout > 0 {
		timeout = time.Duration(req.Timeout * float64(time.Second))
	}
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	// Gunakan NewRequestWithContext agar timeout terisolasi khusus per-worker
	httpReq, err := http.NewRequestWithContext(ctx, "HEAD", targetURL, nil)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create HTTP request: " + err.Error()}
	}
	
	// Default UA
	httpReq.Header.Set("User-Agent", "storm-framework/3.0 (CRS Engine)")
	if req.UA != "" { // Diperbaiki dari if req.UA
		httpReq.Header.Set("User-Agent", req.UA)
	}
	
	resp, err := httpClient.Do(httpReq)
	if err != nil {
		return packet.ResponsePacket{Status: "FAILED", Message: err.Error()}
	}
	defer resp.Body.Close()

	if resp.StatusCode == 429 {
		utils.UpdateGlobalRate(req.Frl)
	}

	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			headers[k] = v 
		}
	}

	generateMetadata := func() map[string]interface{} {
	    meta := map[string]interface{}{
			"status_code": resp.StatusCode,
			"headers":     headers,
			"protocol":    resp.Proto,
			"engine":      "Discovery",
		}
	    if req.InfoTLS && resp.TLS != nil {
		    // Dapatkan detail handshake SSL/TLS
		    state := resp.TLS
		    meta["info_tls"] = ctls.ExtractTLSInfoFromState(state)
	    }
		return meta
	}

	// Evaluasi HTTP codes
	if resp.StatusCode < 400 || resp.StatusCode == 401 || resp.StatusCode == 403 {
		return packet.ResponsePacket{
			Status: "SUCCESS",
			Data: generateMetadata(),
		}
	}

	return packet.ResponsePacket{
		Status:  "FAILED",
		Message: "Endpoint not accessible or ignored status code",
	}
}
