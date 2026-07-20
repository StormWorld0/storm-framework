// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package http

import (
	"bytes"
	"io"
	"net/http"
	"time"

	regis "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// Fungsi HTTP sesuai signature Handler
func HTTP(req regis.RequestPacket) regis.ResponsePacket {
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	client := &http.Client{Timeout: timeout}
	
	var bodyReader io.Reader
	if req.Body != "" {
		bodyReader = bytes.NewBufferString(req.Body)
	}

	httpReq, err := http.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		return regis.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	resp, err := client.Do(httpReq)
	if err != nil {
		return regis.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)

	return regis.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"status_code": resp.StatusCode,
			"body":        string(respBody),
		},
	}
}
