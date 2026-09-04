package whois

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

const (
	rdapDomBootstrapURL = "https://rdap.org/domain/%s"
)

// Struktur minimal untuk mengekstrak hypermedia link dari RDAP
type rdapPartialResponse struct {
	Links []struct {
		Rel  string `json:"rel"`
		Href string `json:"href"`
	} `json:"links"`
}

func IsDomain(s string) bool {
	s = strings.TrimSuffix(strings.TrimSpace(s), ".")
	return s != "" &&
		!strings.Contains(s, "://") &&
		!strings.ContainsAny(s, "/?#") &&
		strings.Contains(s, ".")
}

func WhoisDom(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take() // Rate limiter

	// Idiomatic Go: gunakan !IsDomain
	if !IsDomain(req.Domain) {
		return packet.ResponsePacket{Status: "ERROR", Message: "Invalid Domain format"}
	}

	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	url := fmt.Sprintf(rdapDomBootstrapURL, req.Domain)
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	// Eksekusi request pertama ke Bootstrap/Registry
	respBody, headers, statusCode, protocol, err := fetchRDAP(ctx, url)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	// Parsing JSON untuk mencari link delegasi ke Registrar ("related")
	var partial rdapPartialResponse
	if err := json.Unmarshal(respBody, &partial); err == nil {
		for _, link := range partial.Links {
			if link.Rel == "related" {
				// Ditemukan endpoint Registrar, lakukan request kedua untuk data lengkap (Thick Data)
				relatedBody, relatedHeaders, relatedStatus, relatedProto, relatedErr := fetchRDAP(ctx, link.Href)
				if relatedErr == nil && relatedStatus == http.StatusOK {
					// Timpa hasil awal dengan hasil dari Registrar yang lebih lengkap
					respBody = relatedBody
					headers = relatedHeaders
					statusCode = relatedStatus
					protocol = relatedProto
				}
				break 
			}
		}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"status_code": statusCode,
			"headers":     headers,
			"body":        string(respBody),
			"protocol":    protocol,
			"engine":      "WhoisDOM",
		},
	}
}

// fetchRDAP memisahkan logika HTTP request agar bisa di-reuse untuk request related link
func fetchRDAP(ctx context.Context, targetURL string) ([]byte, map[string]interface{}, int, string, error) {
	reqs, err := http.NewRequestWithContext(ctx, http.MethodGet, targetURL, nil)
	if err != nil {
		return nil, nil, 0, "", fmt.Errorf("failed to create request: %v", err)
	}
	
	reqs.Header.Set("Accept", "application/rdap+json")
	
	resp, err := httpClient.Do(reqs)
	if err != nil {
		return nil, nil, 0, "", fmt.Errorf("HTTP Requests failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, nil, resp.StatusCode, resp.Proto, fmt.Errorf("receiving a non-200 status code: %d %s", resp.StatusCode, resp.Status)
	}

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, nil, resp.StatusCode, resp.Proto, fmt.Errorf("failed to read response body: %v", err)
	}

	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			headers[k] = v
		}
	}
	return respBody, headers, resp.StatusCode, resp.Proto, nil
}
