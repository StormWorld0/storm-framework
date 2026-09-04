package whois

import (
	"io"
	"fmt"
	"time"
	"context"
	"strings"
	"net/http"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

const (
	rdapDomBootstrapURL = "https://rdap.org/domain/%s"
)

func IsDomain(s string) bool {
	s = strings.TrimSuffix(strings.TrimSpace(s), ".")
	return s != "" &&
		!strings.Contains(s, "://") &&
		!strings.ContainsAny(s, "/?#") &&
		strings.Contains(s, ".")
}

// WhoisDom mengeksekusi HTTP GET ke server RDAP
func WhoisDom(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take() // Rate limiter

	// Validasi Input (Sanitasi Domain)
	if parsedDom := IsDomain(req.Domain); parsedDom == true {
		return packet.ResponsePacket{Status: "ERROR", Message: "Invalid Domain format"}
	}

	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	url := fmt.Sprintf(rdapDomBootstrapURL, req.Domain)

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
			"engine":      "WhoisDOM",
		},
	}
}
