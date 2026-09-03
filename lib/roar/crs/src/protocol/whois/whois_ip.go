package whois

import (
	"context"
	"net/http"
	"time"
	"fmt"
	"io"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

const (
	// rdap.org bertindak sebagai global router/bootstrap
	rdapBootstrapURL = "https://rdap.org/ip/%s"
)

// WhoisIP mengeksekusi HTTP GET ke server RDAP
func WhoisIP(req packet.RequestPacket) packet.ResponsePacket {
    utils.Take() // Rate limiter
	
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}
	
	url := fmt.Sprintf(rdapBootstrapURL, req.Ip)

	// Context dengan timeout mencegah resource exhaustion (goroutine leak)
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create request: " + err.Error()}
	}
	
	// Set header HTTP sesuai standar REST
	req.Header.Set("Accept", "application/rdap+json")

	// HTTP Client bawaan otomatis menangani HTTP 302 Redirects dari IANA/rdap.org ke RIR
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "HTTP Requests failed: " + err.Error()}
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return packet.ResponsePacket{
			Status: "ERROR", 
			Message: "Receiving a non-200 status code: " + resp.StatusCode + resp.Status,
		}
	}

	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			headers[k] = v 
		}
	}

	respBody, _ := io.ReadAll(resp.Body)

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{} {
			"status_code":     resp.StatusCode,
			"headers":         headers,
			"body":            string(respBody),
			"protocol":        resp.Proto,
			"engine":          "WhoisIP",
		}
	}
}
