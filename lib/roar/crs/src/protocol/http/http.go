// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy (Refactored: Dual-Engine Nuclei Standard)
package http

import (
	"bytes"
	"crypto/tls"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/projectdiscovery/rawhttp"
	"github.com/projectdiscovery/retryablehttp-go"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// HTTP mengeksekusi request. Secara dinamis beralih antara Standard Engine dan Raw Engine
// tergantung pada flag req.RawMode yang ditentukan oleh module.
func HTTP(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()
	
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 10 * time.Second
	}

	// ---------------------------------------------------------
	// ENGINE 1: RAW HTTP (Mode Tidak Waras / Malformed / Bypass)
	// ---------------------------------------------------------
	if req.RawMode { // Asumsi Anda menambahkan field 'RawMode bool' di struct regis.RequestPacket
		options := rawhttp.DefaultOptions
		options.Timeout = timeout

		rawClient := rawhttp.NewClient(options)

		parsedURL, err := url.Parse(req.URL)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Invalid URL for RawHTTP: " + err.Error()}
		}

		uriPath := parsedURL.RequestURI()
		if uriPath == "" {
			uriPath = "/"
		}
		
		// Module bisa menyuplai FULL raw HTTP string di req.Body
		// Contoh: "GET / HTTP/1.1\r\nHost: target\r\nX-Injected:  spasi_aneh\r\n\r\n"
		resp, err := rawClient.DoRaw(req.Method, req.URL, uriPath, map[string][]string{}, io.NopCloser(strings.NewReader(req.Body)))
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "RawHTTP failed: " + err.Error()}
		}

		// Konversi raw headers
		headers := make(map[string]interface{})
		for k, v := range resp.Header {
			headers[k] = strings.Join(v, ", ") // Raw engine sering mempertahankan array string
		}

		bodyBytes, _ := io.ReadAll(resp.Body)

		return packet.ResponsePacket{
			Status: "SUCCESS",
			Data: map[string]interface{}{
				"status_code": resp.StatusCode,
				"body":        string(bodyBytes),
				"headers":     headers,
				"engine":      "rawhttp", // Penanda untuk module debugging
			},
		}
	}

	// ---------------------------------------------------------
	// ENGINE 2: RETRYABLE HTTP (Mode Waras / Standard Scanning)
	// ---------------------------------------------------------
	
	// Menggunakan retryablehttp milik ProjectDiscovery (Lebih stabil dari http.Client bawaan)
	retryOptions := retryablehttp.DefaultOptionsSingle
	retryOptions.Timeout = timeout
	retryOptions.RetryMax = 2 // Otomatis retry jika koneksi terputus di tengah jalan

	retryClient := retryablehttp.NewClient(retryOptions)
	
	// Konfigurasi Transport untuk TLS Bypass
	retryClient.HTTPClient.Transport = &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS10,
		},
		MaxIdleConns:          100,
		MaxIdleConnsPerHost:   10,
	}

	// Cek redirect bool
	if !req.Redirect {
        retryClient.HTTPClient.CheckRedirect = func(r *http.Request, via []*http.Request) error {
		    return http.ErrUseLastResponse
	    }
	}

	var bodyReader io.Reader
	if req.Body != "" {
		bodyReader = bytes.NewBufferString(req.Body)
	}

	httpReq, err := retryablehttp.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Request creation failed: " + err.Error()}
	}

	// Set User-Agent Default
	httpReq.Header.Set("User-Agent", "StormWorld/storm-framework 3.0 (Security Framework)")

	resp, err := retryClient.Do(httpReq)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Execution failed: " + err.Error()}
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

	respBody, _ := io.ReadAll(io.LimitReader(resp.Body, 2*1024*1024))

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"status_code": resp.StatusCode,
			"body":        string(respBody),
			"headers":     headers,
			"protocol":    resp.Proto,
			"engine":      "retryablehttp",
		},
	}
}
