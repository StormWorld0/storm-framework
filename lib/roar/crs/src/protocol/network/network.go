// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package network

import (
	"context"
	"io"
	"net"
	"fmt"
	"strings"
	"time"
	"strconv"
	"encoding/hex"
	"crypto/tls"
	"sync"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

var bufferPool = sync.Pool{
	New: func() interface{} {
		// Default allocation size
		b := make([]byte, 4096)
		return &b
	},
}

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

func BuildTarget(req packet.RequestPacket) (string, error) {
	rawHost := strings.TrimSpace(req.Host)
	if rawHost == "" {
		return "", fmt.Errorf("Invalid empty host")
	}

	// 1. Handling Scheme (http/https)
	if strings.Contains(rawHost, "://") {
		parts := strings.SplitN(rawHost, "://", 2)
		rawHost = parts[1] // Ambil string setelah "://"
	}

	// 2. Separate Host dan Port dari string
	hostOnly, portStr, err := net.SplitHostPort(rawHost)
	if err != nil {
		// Jika tidak ada port di string rawHost
		hostOnly = rawHost
		portStr = ""
	}

	// 3. Potong Trailing Path (misal: "domain.com/v1/api" -> "domain.com")
	if idx := strings.Index(hostOnly, "/"); idx != -1 {
		hostOnly = hostOnly[:idx]
	}

	// 4. Penentuan Final Port
	finalPort := 0
	if req.Port != 0 {
		// Prioritas 1: Port dari struct req.Port
		finalPort = req.Port
	} else if portStr != "" {
		// Prioritas 2: Port dari string "host:port"
		if p, parseErr := strconv.Atoi(portStr); parseErr == nil && p > 0 {
			finalPort = p
		}
	}
	if finalPort == 0 {
		return "", fmt.Errorf("Empty port error")
	}
	// 5. Return dengan format "host:port" yang valid
	return net.JoinHostPort(hostOnly, strconv.Itoa(finalPort)), nil
}

// Socket mengeksekusi koneksi TCP/SSL/TLS
func Network(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()

	var (
		conn net.Conn
		err error
		isReused bool
	) 
	
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	if req.SessionID != "" && req.CloseSess {
        if val, ok := utils.ActiveSessions.LoadAndDelete(req.SessionID); ok {
            val.(net.Conn).Close()
            return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
        }
    }

	if req.SessionID != "" {
        if val, ok := utils.ActiveSessions.Load(req.SessionID); ok {
            conn = val.(net.Conn)
            isReused = true
        }
    }

	protocol := strings.ToLower(req.Protocol)
    if protocol == "" {
        protocol = "tcp"
    }

	if conn == nil {
        addr, err := BuildTarget(req)
        if err != nil {
            return packet.ResponsePacket{Status: "ERROR", Message: "Build target: " + err.Error()}
        }

        fd := utils.GetDialer()
        if fd == nil {
            return packet.ResponsePacket{Status: "ERROR", Message: "Global dialer not initialized"}
        }

        ctx, cancel := context.WithTimeout(context.Background(), timeout)
        defer cancel()

        if protocol == "tls" || protocol == "ssl" {
            conn, err = fd.DialTLS(ctx, "tcp", addr)
        } else {
            conn, err = fd.Dial(ctx, "tcp", addr)
        }

        if err != nil {
            return packet.ResponsePacket{Status: "ERROR", Message: "Connection failed: " + err.Error()}
        }
    }
	
	shouldKeepAlive := req.KeepAlive && req.SessionID != ""
	keepSession := false

	defer func() {
		// Tutup koneksi HANYA jika TIDAK disimpan ke session aktif
		if !keepSession {
			if req.SessionID != "" {
				utils.ActiveSessions.Delete(req.SessionID)
			}
			conn.Close()
		}
	}()

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
			// Jika koneksi re-used ternyata sudah stale/broken di server side, hapus session
            if req.SessionID != "" {
                utils.ActiveSessions.Delete(req.SessionID)
                conn.Close()
            }
			return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		}
	}

	readSize := req.ReadSize
	if readSize <= 0 {
		readSize = 4096 // Default fallback
	}

	// Mengambil buffer dari Pool jika ukuran standar, atau buat baru jika custom
	var bufPtr *[]byte
	var buffer []byte

	if readSize == 4096 {
		bufPtr = bufferPool.Get().(*[]byte)
		buffer = *bufPtr
		defer bufferPool.Put(bufPtr) // Kembalikan ke pool saat selesai
	} else {
		buffer = make([]byte, readSize)
	}
	
	// Pembacaan Buffer
	// Membaca stream sampai EOF atau buffer penuh agar tidak ada data tertinggal
	n, err := io.ReadFull(conn, buffer)
	if err != nil && err != io.EOF && err != io.ErrUnexpectedEOF {
		return packet.ResponsePacket{Status: "ERROR", Message: "Read failed: " + err.Error()}
	}

	// Jika sampai tahap ini sukses & KeepAlive diaktifkan, simpan koneksi
	if shouldKeepAlive {
		utils.ActiveSessions.Store(req.SessionID, conn)
		keepSession = true // Toggle flag agar defer tidak me-close socket
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
			    "dns_names":        cert.DNSNames,
			    "expires_at":       cert.NotAfter.Format(time.RFC3339),
			    "tls_version":      tlsVersionString(state.Version),
			    "cipher_suite":     tls.CipherSuiteName(state.CipherSuite),
				"protocol":         state.NegotiatedProtocol,
				"hostname":         state.ServerName,
				"handshake":        state.HandshakeComplete,
				"session_resume":   state.DidResume,
				"cert_chain":       state.VerifiedChains,
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
			"is_reused":    isReused, // Flag indikator arsitektur hybrid
			"rtt_ms":       rtt,
			"info_tls":     tlsData,
		},
	}
}

