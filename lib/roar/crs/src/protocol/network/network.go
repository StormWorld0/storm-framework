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
	netutils "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol" 
)

// Socket mengeksekusi koneksi TCP/UDP/TLS menggunakan Global Fastdialer
func Network(req packet.RequestPacket) packet.ResponsePacket {
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	// Ambil Global Dialer dari lapisan Core (Zero Overhead!)
	fd := netutils.GetDialer()
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
		conn, err = fd.DialTLS(ctx, "tcp", req.Target)
	} else {
		conn, err = fd.Dial(ctx, protocol, req.Target)
	}

	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Connection failed: " + err.Error()}
	}
	defer conn.Close()

	// I/O Deadlines (Sabuk pengaman anti-Tarpit)
	conn.SetDeadline(time.Now().Add(timeout))

	// Injeksi Payload
	if req.Body != "" {
		_, err = conn.Write([]byte(req.Body))
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		}
	}

	// Pembacaan Buffer (Mencegah Memory Exhaustion dari stream infinit)
	buffer := make([]byte, 4096)
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
			"bytes_resp":   string(buffer[:n]),
			"bytes_int":    n,
			"protocol":     protocol,
			"ip":           remoteIP, // IP hasil dari in-memory resolution fastdialer
		},
	}
}

