package http

import (
	"io"
	"net/http"
	"strings"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
)

const MaxResponseBodySize = 2 << 20 // 2MB Hard Limit mencegah Memory Exhaustion/DoS

func BuildErrorResponse(engine, message string) packet.ResponsePacket {
	return packet.ResponsePacket{
		Status:  "ERROR",
		Message: "[" + engine + "] " + message,
	}
}

// BuildSuccessResponse menangani normalisasi output untuk kedua engine
func BuildSuccessResponse(resp *http.Response, infoTLS bool, engine string) packet.ResponsePacket {
	bodyBytes, _ := io.ReadAll(io.LimitReader(resp.Body, MaxResponseBodySize))

	headers := make(map[string]interface{})
	for k, v := range resp.Header {
		if len(v) == 1 {
			headers[k] = v[0]
		} else {
			// Mengatasi slice duplikasi dari raw engine
			headers[k] = strings.Join(v, ", ")
		}
	}

	meta := map[string]interface{}{
		"status_code": resp.StatusCode,
		"body":        string(bodyBytes),
		"headers":     headers,
		"engine":      engine,
	}

	if resp.Proto != "" {
		meta["protocol"] = resp.Proto
	}

	if infoTLS && resp.TLS != nil {
		meta["info_tls"] = ctls.ExtractTLSInfoFromState(resp.TLS)
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data:   meta,
	}
}
