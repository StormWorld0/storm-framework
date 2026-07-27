package utils

import (
	"crypto/tls"
	"net"
	"sync"
	"time"
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

func (s *SessionState) Read(b []byte) (n int, err error)   { return s.Conn.Read(b) }
func (s *SessionState) Write(b []byte) (n int, err error)  { return s.Conn.Write(b) }
func (s *SessionState) Close() error                       { return s.Conn.Close() }
func (s *SessionState) LocalAddr() net.Addr                { return s.Conn.LocalAddr() }
func (s *SessionState) RemoteAddr() net.Addr               { return s.Conn.RemoteAddr() }
func (s *SessionState) SetDeadline(t time.Time) error      { return s.Conn.SetDeadline(t) }
func (s *SessionState) SetReadDeadline(t time.Time) error { return s.Conn.SetReadDeadline(t) }
func (s *SessionState) SetWriteDeadline(t time.Time) error{ return s.Conn.SetWriteDeadline(t) }

// Interface Helper untuk TLS Connection State
type tlsStateProvider interface {
	ConnectionState() tls.ConnectionState
}

// Memungkinkan type assertion ConnectionState() tembus ke socket TLS di dalamnya
func (s *SessionState) ConnectionState() tls.ConnectionState {
	if getter, ok := s.Conn.(tlsStateProvider); ok {
		return getter.ConnectionState()
	}
	return tls.ConnectionState{}
}
