package waf

import (
	"net"
	"github.com/projectdiscovery/cdncheck"
)

var client *cdncheck.Client

func init() {
	// Inisialisasi cdncheck client
	client = cdncheck.New()
}

func WAFDetection(host string) (bool) {
	// Validation input
	if ip := net.ParseIP(host); ip != nil {
		matched, _, _ := client.CheckWAF(ip)
		return matched
	}
	// Fallback
	matched, _, _, _ := client.CheckDomainWithFallback(host)
	return matched
}
