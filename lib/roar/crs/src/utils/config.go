package utils

import(
  "sync"
  "net"
)

// SessionManager thread-safe
var ActiveSessions = sync.Map{} // map[string]net.Conn

// Struct untuk menyimpan koneksi + state metadata TLS-nya
type SessionState struct {
	Conn       net.Conn
	TLSCert    string
	TLSKey     string
	TLSCA      string
	Verify     bool
	IsTLS      bool
	Host       string
}
