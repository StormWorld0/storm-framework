// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy (Refactored: True Nuclei Socket Module)
package socket

import (
	"context"
	"io"
	"net"
	"strings"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// Socket mengeksekusi koneksi TCP/UDP/TLS menggunakan Global Fastdialer
func Network(req packet.RequestPacket) packet.ResponsePacket {
	packet.Take()
	
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	addr := req.Host
	if req.Port != "" {
		addr = net.JoinHostPort(req.Host, req.Port)
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
	conn.SetDeadline(time.Now().Add(timeout))

	// Penanganan Payload (Text vs Hex Binary)
	if req.Body != "" {
		var payload []byte
		
		// Jika modul menandai payload sebagai Hex (misal eksploitasi buffer overflow / binary protocol)
		if strings.ToLower(req.Encoding) == "hex" {
			cleanHex := strings.ReplaceAll(req.Body, " ", "")
			payload, err = hex.DecodeString(cleanHex)
			if err != nil {
				return regis.ResponsePacket{Status: "ERROR", Message: "Invalid HEX payload: " + err.Error()}
			}
		} else {
			payload = []byte(req.Body)
		}

		_, err = conn.Write(payload)
		if err != nil {
			return regis.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
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
	if err != nil && err != io.EOF && !strings.Contains(err.Error(), "timeout") {
		if n == 0 {
			return packet.ResponsePacket{Status: "ERROR", Message: "Read failed: " + err.Error()}
		}
	}

	// Ekstraksi Data Spesifik
	remoteIP := "unknown"
	if addr := conn.RemoteAddr(); addr != nil {
		remoteIP = addr.String()
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"raw_bytes":    string(buffer[:n]),
			"read_bytes":    n,
			"protocol":     protocol,
			"ip":           remoteIP, // IP hasil dari in-memory resolution fastdialer
		},
	}
}

