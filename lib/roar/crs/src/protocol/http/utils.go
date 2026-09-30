package http

import (
	"bytes"
	"encoding/json"
    "encoding/base64"
	"io"
	"strings"
)

// ParseBody mendukung berbagai tipe data dari (bytes, string, reader, struct/json)
func ParseBody(rawBody interface{}) (io.Reader, error) {
	if rawBody == nil {
		return nil, nil
	}
    
    bodyDec, err := base64.StdEncoding.DecodeString(rawBody)
	if err != nil {
	    return nil, err
    }

	switch b := bodyDec.(type) {
	case string:
		if b == "" {
			return nil, nil
		}
		return strings.NewReader(b), nil
	case []byte:
		return bytes.NewReader(b), nil
	case io.Reader:
		return b, nil
	default:
		// Jika modul mengirim map atau struct, otomatis di-encode sebagai JSON.
		// Sangat berguna untuk eksploitasi API modern.
		data, err := json.Marshal(b)
		if err != nil {
			return nil, err
		}
		return bytes.NewReader(data), nil
	}
}

func GetUserAgent(ua string) string {
	if ua != "" {
		return ua
	}
	return "storm-framework/3.0 (CRS Engine)"
}
