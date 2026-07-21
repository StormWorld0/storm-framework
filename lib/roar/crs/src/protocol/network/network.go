// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy (Refactored: True Nuclei Socket Module)
package network

import (
	"context"
	"io"
	"net"
	"strings"
	"time"
	"strconv"
	"encoding/hex"
	"crypto/tls"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// Socket mengeksekusi koneksi TCP/UDP/TLS menggunakan Global Fastdialer
func Network(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()
	
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	addr := req.Host
	if req.Port != 0 {
        addr = net.JoinHostPort(req.Host, strconv.Itoa(req.Port))
    }
	
	// Ambil Global Dialer dari lapisan Core (Zero Overhead!)
	fd := utils.GetDialer()
	if fd == nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Global dialer not initialized"}
	}

	protocol := strings.ToLower(req.Protocol)
	if protocol == "" {
		protocol = "tcp"
	}

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	var conn net.Conn
	var err error

	// Eksekusi koneksi (Fastdialer otomatis menggunakan DNS Cache dari memori)
	if protocol == "tls" || protocol == "ssl" {
		conn, err = fd.DialTLS(ctx, "tcp", addr)
	} else {
		conn, err = fd.Dial(ctx, protocol, addr)
	}

	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Connection failed: " + err.Error()}
	}
	defer conn.Close()

	// I/O Deadlines (Sabuk pengaman anti-Tarpit)
	startTime := time.Now()
	conn.SetDeadline(time.Now().Add(timeout))

	// Penanganan Payload (Text vs Hex Binary)
	if req.Body != "" {
		var payload []byte
		
		// Jika modul menandai payload sebagai Hex (misal eksploitasi buffer overflow / binary protocol)
		if strings.ToLower(req.Encoding) == "hex" {
			cleanHex := strings.ReplaceAll(req.Body, " ", "")
			payload, err = hex.DecodeString(cleanHex)
			if err != nil {
				return packet.ResponsePacket{Status: "ERROR", Message: "Invalid HEX payload: " + err.Error()}
			}
		} else {
			payload = []byte(req.Body)
		}

		_, err = conn.Write(payload)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		}
	}

	readSize := req.ReadSize
	if readSize <= 0 {
		readSize = 4096 // Default fallback
	}
	
	// Pembacaan Buffer
	buffer := make([]byte, readSize)
	n, err := conn.Read(buffer)

	// Validasi error I/O raw socket
	if err != nil && err != io.EOF {
		if n == 0 {
			return packet.ResponsePacket{Status: "ERROR", Message: "Read failed: " + err.Error()}
		}
	}

	var tlsData map[string]interface{}

    if tlsConn, ok := conn.(*tls.Conn); ok {
	    // Dapatkan detail handshake SSL/TLS
    	state := tlsConn.ConnectionState()
    	if len(state.PeerCertificates) > 0 {
		    cert := state.PeerCertificates[0] // Leaf Certificate
		    tlsData = map[string]interface{}{
			    "subject":          cert.Subject.CommonName,
			    "issuer":           cert.Issuer.CommonName,
			    "dns_names":        cert.DNSNames, // Subject Alternative Names (SANs) - Bagus buat Subdomain Enum!
			    "expires_at":       cert.NotAfter.Format(time.RFC3339),
			    "tls_version":      state.Version,
			    "cipher_suite":     state.CipherSuite,
		    }
	    }
    }
	

	// Ekstraksi Data Spesifik
	remoteIP := "unknown"
	if addr := conn.RemoteAddr(); addr != nil {
		remoteIP = addr.String()
	}
	localAddr := "unknown"
    if lAddr := conn.LocalAddr(); lAddr != nil {
	    localAddr = lAddr.String()
    }
	rtt := time.Since(startTime).Milliseconds()

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"raw_bytes":    string(buffer[:n]),
			"hex_bytes":    hex.EncodeToString(buffer[:n]),
			"read_bytes":   n,
			"protocol":     protocol,
			"ip":           remoteIP,
			"local_ip":     localAddr,
			"rtt_ms":       rtt,
			"tls_info":     tlsData,
		},
	}
}

