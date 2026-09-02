package waf

import (
	"context"
	"io"
	"net/http"
)

// Detector adalah engine utama pencari WAF.
type Detector struct {
	client     *http.Client
	signatures []Signature
	payloads   []string
}

// NewDetector menginisialisasi engine dengan custom HTTP client.
// HTTP client harus di-tuning (timeout, max idle conns) oleh Storm Framework.
func NewDetector(client *http.Client, sigs []Signature) *Detector {
	return &Detector{
		client:     client,
		signatures: sigs,
		// Payloads lintas vektor untuk memicu ruleset yang berbeda
		payloads: []string{
			"/?id=1+AND+1=1+UNION+ALL+SELECT+1,NULL,'<script>alert(1)</script>'",
			"/../../../../etc/passwd",
			"/?exec=/bin/bash+-c+'ls'",
		},
	}
}

// Result menyimpan hasil deteksi.
type Result struct {
	HasWAF  bool
	WAFName string
	Vendor  string
	Trigger string
}

// Analyze adalah fungsi utama untuk mendeteksi WAF pada sebuah target.
func (d *Detector) Analyze(ctx context.Context, targetURL string) (Result, error) {
	// 1. Passive Fingerprinting (Baseline)
	baselineReq, err := http.NewRequestWithContext(ctx, "GET", targetURL, nil)
	if err != nil {
		return Result{}, err
	}
	// (Opsional) Analisis respons baseline jika target sudah memblokir dari awal

	// 2. Active Probing (Memancing WAF)
	for _, payload := range d.payloads {
		probeURL := targetURL + payload
		req, err := http.NewRequestWithContext(ctx, "GET", probeURL, nil)
		if err != nil {
			continue
		}

		resp, err := d.client.Do(req)
		if err != nil {
			// WAF seringkali merespons dengan TCP RST (Connection Reset)
			// Ini bisa menjadi heuristik WAF tingkat lanjut.
			continue
		}
		
		// Baca body dengan limit (mencegah memory exhaustion dari infinite stream)
		bodyBytes, _ := io.ReadAll(io.LimitReader(resp.Body, 64*1024)) // Limit 64KB
		resp.Body.Close()

		// 3. Signature Matching
		if result, found := d.matchSignatures(resp, bodyBytes); found {
			result.Trigger = payload
			return result, nil
		}
	}

	return Result{HasWAF: false}, nil
}
