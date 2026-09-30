package http

import (
	"bytes"
	"encoding/json"
    "encoding/base64"
	"io"
	"strings"
)

// ParseBody mendukung berbagai tipe data dari (bytes, string, reader, struct/json)
func ParseBody(encoding string, rawBody interface{}) (io.Reader, error) {
	if rawBody == nil {
		return nil, nil
	}

	strBody, _ := rawBody.(string)
	if strBody == nil {
		return nil, nil
	}
	
	bodyDec, err := base64.StdEncoding.DecodeString(strBody)
	if err != nil {
	    return nil, err
    }
	
	var bodyFinal interface{}
	if encoding == "string" {
		bodyFinal = string(bodyDec)
	} else if encoding == "bytes" {
		bodyFinal = bodyDec
	} else {
		bodyFinal = rawBody
	}

	switch b := bodyFinal(type) {
	case string:
		if b == "" {
			return nil, nil
		}
		return strings.NewReader(b), nil
	case []byte:
		if len(b) == 0 {
			return nil, nil
		}
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
