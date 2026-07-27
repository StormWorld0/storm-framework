package utils

import (
	"sync"
)

// SessionManager thread-safe
var ActiveSessions = sync.Map{} // map[string]net.Conn

var SessionTLSMap = sync.Map{} // map[string]TLSMetadata

// Struct untuk menyimpan koneksi + state metadata TLS-nya
type TLSMetadata struct {
	TLSCert    string
	TLSKey     string
	TLSCA      string
	Verify     bool
	Host       string
	Protocol   string
}
