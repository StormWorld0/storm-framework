package tls

import (
	"net"
	"time"
	"strconv"
	"crypto/tls"
)

type tlsConnStateGetter interface {
	ConnectionState() tls.ConnectionState
}

// Validation TLS
func isTLSConn(c net.Conn) bool {
	if c == nil {
		return false
	}
	_, ok := c.(tlsConnStateGetter)
	return ok
}

// Ekstract TLS Version
func tlsVersionString(v uint16) string {
    switch v {
	    case tls.VersionTLS10:
		    return "TLS 1.0"
	    case tls.VersionTLS11:
		    return "TLS 1.1"
	    case tls.VersionTLS12:
		    return "TLS 1.2"
	    case tls.VersionTLS13:
		    return "TLS 1.3"
	    default:
		    return strconv.Itoa(int(v))
	}
}

// Extract TLS Information yang menerima (tls.ConnectionState)
func ExtractTLSInfoFromState(state *tls.ConnectionState) map[string]interface{} {
	tlsData := map[string]interface{}{
		"tls_version":    tlsVersionString(state.Version),
		"cipher_suite":   tls.CipherSuiteName(state.CipherSuite),
		"protocol":       state.NegotiatedProtocol,
		"hostname":       state.ServerName,
		"handshake":      state.HandshakeComplete,
		"session_resume": state.DidResume,
	}
	if len(state.PeerCertificates) > 0 {
		cert := state.PeerCertificates[0]
		tlsData["subject"] = cert.Subject.CommonName
		tlsData["issuer"] = cert.Issuer.CommonName
		tlsData["dns_name"] = cert.DNSNames
		tlsData["expires"] = cert.NotAfter.Format(time.RFC3339)
	}
	if len(state.VerifiedChains) > 0 {
		tlsData["cert_chain"] = len(state.VerifiedChains)
	}
	return tlsData
}

// Extract TLS Information yang menerima (net.Conn)
func ExtractTLSInfo(conn net.Conn) map[string]interface{} {
	if stateGetter, ok := conn.(tlsConnStateGetter); ok {
		state := stateGetter.ConnectionState()
		if state.HandshakeComplete || state.Version != 0 {
			return ExtractTLSInfoFromState(state)
		}
	}
	return nil
}
