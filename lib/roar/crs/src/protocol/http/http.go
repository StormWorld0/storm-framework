// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy (Refactored to Industry Security Standard)
package http

import (
	"bytes"
	"crypto/tls"
	"io"
	"net"
	"net/http"
	"strings"
	"time"

	regis "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// HTTP mengeksekusi request dengan custom transport yang di-tuning untuk security scanning
func HTTP(req regis.RequestPacket) regis.ResponsePacket {
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 10 * time.Second
	}

	// 1. Tuning Transport Layer (Krusial untuk koneksi masif & target kotor)
	transport := &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		DialContext: (&net.Dialer{
			Timeout:   timeout,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		MaxIdleConns:          100,              // Connection pooling
		MaxIdleConnsPerHost:   10,               // Mencegah bottleneck pada 1 host
		IdleConnTimeout:       90 * time.Second,
		TLSHandshakeTimeout:   10 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	    DisableKeepAlives:     true, // Menghindari statefull WAF Bloking
		
		// TLS Bypass: Wajib untuk scanner (mengabaikan self-signed, expired cert, atau IP targeting)
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MinVersion:         tls.VersionTLS10, // Downgrade support untuk target legacy
		},
	}

	// Modifikasi Client Behavior
	client := &http.Client{
		Transport: transport,
		Timeout:   timeout,
		// Redirect Control: Jangan ikuti redirect secara membabi buta.
		// Security module seringkali perlu membaca isi dari respons 301/302.
		CheckRedirect: func(r *http.Request, via []*http.Request) error {
			// Menghentikan client dari auto-follow
			return http.ErrUseLastResponse 
		},
	}

	var bodyReader io.Reader
	if req.Body != "" {
		bodyReader = bytes.NewBufferString(req.Body)
	}

	httpReq, err := http.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		return regis.ResponsePacket{Status: "ERROR", Message: "Request creation failed: " + err.Error()}
	}

	// Injeksi Header Kustom (Opsional tapi wajib ada jalurnya)
	// Jika req.Headers tersedia di struct packet, mapping di sini:
	// for k, v := range req.Headers { httpReq.Header.Set(k, v) }
	
	// Pastikan User-Agent diset jika tidak ada, default Go sering diblokir WAF
	if httpReq.Header.Get("User-Agent") == "" {
		httpReq.Header.Set("User-Agent", "StormWorld/storm-framework 3.0 (Security Framework)")
	}

	// Eksekusi
	resp, err := client.Do(httpReq)
	if err != nil {
		return regis.ResponsePacket{Status: "ERROR", Message: "Execution failed: " + err.Error()}
	}
	defer resp.Body.Close()

	// Limitasi pembacaan Body (Proteksi dari serangan Tarpit/Infinite Stream)
	// Membatasi pembacaan maksimal ke 2MB untuk mencegah memory exhaustion
	limitedReader := io.LimitReader(resp.Body, 2*1024*1024)
	respBody, _ := io.ReadAll(limitedReader)

	// Header Fidelity: Jangan ratakan header menjadi v[0]
	// Banyak kerentanan (seperti HTTP Response Splitting) atau proteksi memunculkan header ganda (misal: Set-Cookie)
	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			headers[k] = v // Simpan sebagai array/slice string
		}
	}

	return regis.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"status_code": resp.StatusCode,
			"body":        string(respBody),
			"headers":     headers,
			"protocol":    resp.Proto, // Berguna untuk deteksi HTTP/1.1 vs HTTP/2
		},
	}
}
