package http

import (
    "encoding/base64"
	"net/url"
	"time"

	"github.com/projectdiscovery/rawhttp"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

func ExecuteRaw(req packet.RequestPacket, timeout time.Duration) packet.ResponsePacket {
	options := rawhttp.DefaultOptions
	options.Timeout = timeout

	client := rawhttp.NewClient(options)

	parsedURL, err := url.Parse(req.URL)
	if err != nil {
		return BuildErrorResponse("rawhttp", "Invalid URL: "+err.Error())
	}

	uriPath := parsedURL.RequestURI()
	if uriPath == "" {
		uriPath = "/"
	}

    dataDec, err := base64.StdEncoding.DecodeString(req.Body)
	if err != nil {
		return BuildErrorResponse("rawhttp", "base64 decode failed: "+err.Error())
    }

	// Otomatis konversi body (string/bytes/json) menjadi io.Reader
	bodyReader, err := ParseBody(dataDec)
	if err != nil {
		return BuildErrorResponse("rawhttp", "Body parse error: "+err.Error())
	}

	// Normalisasi Headers: Injeksi manual ke map[string][]string sesuai standar ProjectDiscovery
	headers := make(map[string][]string)
	headers["Host"] = []string{parsedURL.Host}
	headers["User-Agent"] = []string{GetUserAgent(req.UA)}
	
	for k, v := range req.Headers {
		headers[k] = []string{v}
	}

	// DoRaw sekarang bekerja dengan aman tanpa memaksa modul merakit raw string
	resp, err := client.DoRaw(req.Method, req.URL, uriPath, headers, bodyReader)
	if err != nil {
		return BuildErrorResponse("rawhttp", "Execution failed: "+err.Error())
	}
	defer resp.Body.Close()

	if resp.StatusCode == 429 {
		utils.UpdateGlobalRate(req.Frl)
	}

	return BuildSuccessResponse(resp, req.InfoTLS, "rawhttp")
}
