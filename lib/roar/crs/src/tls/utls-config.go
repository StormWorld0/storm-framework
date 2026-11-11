package tls

import (
	"net"
	"time"
	"strconv"
	tls "github.com/refraction-networking/utls"
)

type utlsConnStateGetter interface {
	ConnectionState() tls.ConnectionState
}

// TLS Validation
func IsUTLSConn(c net.Conn) bool {
	if c == nil {
		return false
	}
	_, ok := c.(utlsConnStateGetter)
	return ok
}

// Extract TLS Version
func tlsVersion(v uint16) string {
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

// Extract TLS Information that receives (tls.ConnectionState)
func ExtractUTLSInfoFromState(state *tls.ConnectionState) map[string]interface{} {
	tlsData := map[string]interface{}{
		"tls_version":    tlsVersion(state.Version),
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

// Extract TLS Information that receives (net.Conn)
func ExtractUTLSInfo(conn net.Conn) map[string]interface{} {
	if stateGetter, ok := conn.(utlsConnStateGetter); ok {
		state := stateGetter.ConnectionState()
		if state.HandshakeComplete || state.Version != 0 {
			return ExtractUTLSInfoFromState(&state)
		}
	}
	return nil
}
