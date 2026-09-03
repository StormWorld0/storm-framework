package whois

import (
	"context"
	"fmt"
	"io"
	"net"
	"net/http"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

const (
	rdapBootstrapURL = "https://rdap.org/ip/%s"
)

// Gunakan singleton client untuk memanfaatkan TCP Connection Pooling
var httpClient *http.Client

func init() {
	httpClient = &http.Client{
		// Batasi redirect untuk mencegah loop dan SSRF ke local network
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 5 {
				return fmt.Errorf("stopped after 5 redirects")
			}
			return nil
		},
	}
}

// WhoisIP mengeksekusi HTTP GET ke server RDAP
func WhoisIP(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take() // Rate limiter

	// Validasi Input (Sanitasi IP)
	if parsedIP := net.ParseIP(req.Ip); parsedIP == nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Invalid IP address format"}
	}

	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	url := fmt.Sprintf(rdapBootstrapURL, req.Ip)

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	reqs, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create request: " + err.Error()}
	}

	reqs.Header.Set("Accept", "application/rdap+json")

	// Gunakan Shared Client
	resp, err := httpClient.Do(reqs)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "HTTP Requests failed: " + err.Error()}
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: fmt.Sprintf("Receiving a non-200 status code: %d %s", resp.StatusCode, resp.Status),
		}
	}

	// Tangani Error I/O
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to read response body: " + err.Error()}
	}

	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			headers[k] = v
		}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"status_code": resp.StatusCode,
			"headers":     headers,
			"body":        string(respBody),
			"protocol":    resp.Proto,
			"engine":      "WhoisIP",
		},
	}
}
