package waf

import (
	"strings"
	"time"
)

// matchSignatures membandingkan HTTP response target dengan basis data signature.
func (d *Detector) matchSignatures(resp *http.Response, body []byte) (Result, bool) {
	bodyStr := string(body)

	for _, sig := range d.signatures {
		// A. Pengecekan HTTP Status Code (Paling ringan, cek pertama)
		statusMatch := false
		if len(sig.StatusCodes) == 0 {
			statusMatch = true
		} else {
			for _, code := range sig.StatusCodes {
				if resp.StatusCode == code {
					statusMatch = true
					break
				}
			}
		}

		if !statusMatch {
			continue // Skip ke signature berikutnya jika status code tidak masuk akal
		}

		// B. Pengecekan Header (Sedang)
		for headerKey, headerVal := range sig.Headers {
			if val := resp.Header.Get(headerKey); val != "" {
				if headerVal == "" || strings.Contains(strings.ToLower(val), strings.ToLower(headerVal)) {
					return Result{HasWAF: true, WAFName: sig.Name, Vendor: sig.Vendor}, true
				}
			}
		}

		// C. Pengecekan Cookies (Sedang)
		for _, cookie := range resp.Cookies() {
			for _, prefix := range sig.Cookies {
				if strings.HasPrefix(cookie.Name, prefix) {
					return Result{HasWAF: true, WAFName: sig.Name, Vendor: sig.Vendor}, true
				}
			}
		}

		// D. Pengecekan Body (Paling berat, lakukan terakhir)
		for _, keyword := range sig.BodyContains {
			if strings.Contains(bodyStr, keyword) {
				return Result{HasWAF: true, WAFName: sig.Name, Vendor: sig.Vendor}, true
			}
		}
	}

	return Result{}, false
}

