// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package main

import (
	"bytes"
	"io"
	"net/http"
	"time"
)

func executeHTTP(req RequestPacket) ResponsePacket {
	// Setup Timeout
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	client := &http.Client{
		Timeout: timeout,
	}

	// Siapkan Body dan Request
	var bodyReader io.Reader
	if req.Body != "" {
		bodyReader = bytes.NewBufferString(req.Body)
	}

	httpReq, err := http.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		return ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	// Masukkan Headers jika ada
	for key, val := range req.Headers {
		httpReq.Header.Set(key, val)
	}

	// Tembak ke Target!
	resp, err := client.Do(httpReq)
	if err != nil {
		return ResponsePacket{Status: "ERROR", Message: err.Error()}
	}
	defer resp.Body.Close()

	// Baca Balasan Target
	respBody, _ := io.ReadAll(resp.Body)

	// Kembalikan ke Python dengan format yang rapi
	return ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"status_code": resp.StatusCode,
			"body":        string(respBody),
		},
	}
}
