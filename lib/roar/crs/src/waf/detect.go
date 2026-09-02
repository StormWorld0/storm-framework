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

func WAFDetection(host string) (bool, error) {
	// Validation input
	if ip := net.ParseIP(host); ip != nil {
		matched, _, err := client.CheckWAF(ip)
		return matched, err
	}
	// Fallback
	matched, _, _, err := client.CheckDomainWithFallback(host)
	return matched, err
}
