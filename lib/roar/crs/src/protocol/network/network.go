package network

import (
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"net"
	"reflect"
	"strconv"
	"strings"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// Network adalah entry point eksekusi koneksi menggunakan POSIX-like primitive operations.
func Network(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()
	startTime := time.Now()

	timeout := 5 * time.Second
	if req.Timeout > 0 {
		timeout = time.Duration(req.Timeout * float64(time.Second))
	}

	// 1. Eksekusi Perintah Close Session secara eksplisit
	if req.SessionID != "" && req.CloseSess {
		if val, ok := utils.ActiveSessions.LoadAndDelete(req.SessionID); ok {
			val.(net.Conn).Close()
			return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
		}
		// Jika tujuannya hanya menutup sesi (primitif 'close')
		if req.Mode == "close" {
			return packet.ResponsePacket{Status: "SUCCESS", Message: "No active session found to close"}
		}
	}

	// 2. Ambil Sesi Aktif (Jika Ada)
	var conn net.Conn
	var isReused bool
	if req.SessionID != "" {
		if val, ok := utils.ActiveSessions.Load(req.SessionID); ok {
			conn = val.(net.Conn)
			isReused = true
		}
	}

	// Normalisasi Primitif
	mode := strings.ToLower(req.Mode)
	if mode == "" {
		mode = "open" // Fallback primitive
	}

	// 3. Auto-Dial: Pastikan Koneksi Tersedia
	// (Mengizinkan arsitektur 'single-shot' di mana user bisa panggil recv/send tanpa open)
	if conn == nil {
		addr, err := BuildTarget(req)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Build target failed: " + err.Error()}
		}

		fd := utils.GetDialer()
		if fd == nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Global dialer not initialized"}
		}

		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()

		rawConn, err := fd.Dial(ctx, "tcp", addr)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "TCP Dial failed: " + err.Error()}
		}
		conn = rawConn

		// Evaluasi TLS State sejak awal (Jika protocol == tls)
		protocol := strings.ToLower(req.Protocol)
		hasCertKey := req.TLSCert != "" && req.TLSKey != ""
		if protocol == "tls" || protocol == "ssl" || hasCertKey {
			tlsConn, err := performTLSHandshake(ctx, conn, addr, req)
			if err != nil {
				conn.Close()
				return packet.ResponsePacket{Status: "ERROR", Message: "Initial TLS Handshake failed: " + err.Error()}
			}
			conn = tlsConn
		}
	}

	// Manajemen Memori & Socket Leak Prevention
	keepSession := false
	defer func() {
		if !keepSession && conn != nil {
			if req.SessionID != "" {
				utils.ActiveSessions.Delete(req.SessionID)
			}
			conn.Close()
		}
	}()

	// Helper Closure untuk Assembly Metadata (Mencegah duplikasi kode)
	generateMetadata := func(readBytes int) map[string]interface{} {
		meta := map[string]interface{}{
			"is_reused":    isReused,
			"rtt_ms":       time.Since(startTime).Milliseconds(),
			"Cheked":       reflect.TypeOf(conn).String(),
			"isAlreadyTLS": strconv.FormatBool(isTLSConn(conn)),
			"read_bytes":   readBytes,
		}
		if addr := conn.RemoteAddr(); addr != nil {
			meta["remote_ip"] = addr.String()
		}
		if lAddr := conn.LocalAddr(); lAddr != nil {
			meta["local_ip"] = lAddr.String()
		}
		if req.InfoTLS {
			meta["info_tls"] = ExtractTLSInfo(conn)
		}
		return meta
	}

	// 4. Primitive State Machine (Routing Eksekusi)
	switch mode {
	case "open":
		// Koneksi sudah terbuka di fase Auto-Dial. 
		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, conn)
			keepSession = true
		}
		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}

	case "upgrade_tls":
		// Mode khusus untuk kerentanan STARTTLS atau Protocol Smuggling
		if isTLSConn(conn) {
			return packet.ResponsePacket{Status: "ERROR", Message: "Connection is already TLS"}
		}
		
		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()
		
		addr, _ := BuildTarget(req) // Target di-rebuild hanya untuk hostname SNI
		tlsConn, err := performTLSHandshake(ctx, conn, addr, req)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "TLS Upgrade failed: " + err.Error()}
		}
		conn = tlsConn // Replace pointer dengan socket TLS baru
		
		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, conn)
			keepSession = true
		}
		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}

	case "send", "send_only":
		if err := ExecuteWrite(conn, req.Data, req.Timeout); err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		}

		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, conn)
			keepSession = true
		}
		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}

	case "recv", "recv_only":
		buffer, n, bufPtr, err := ExecuteRead(conn, req.ReadSize, req.Timeout)
		defer ReleaseBuffer(bufPtr)

		if err != nil && err != io.EOF {
			if n == 0 {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "Read failed: " + err.Error(),
					Data:    generateMetadata(0),
				}
			}
		}

		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, conn)
			keepSession = true
		}

		meta := generateMetadata(n)
		meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
		meta["hex_bytes"] = hex.EncodeToString(buffer[:n])

		if err == io.EOF {
			return packet.ResponsePacket{Status: "INFO", Message: "EOF Read: " + err.Error()}
		}

		return packet.ResponsePacket{Status: "SUCCESS", Data: meta}

	default:
		return packet.ResponsePacket{Status: "ERROR", Message: "Unknown socket primitive: " + mode}
	}
}

// performTLSHandshake adalah internal helper untuk membungkus logika upgrade TLS
// Digunakan oleh primitive 'open' dan 'upgrade_tls'.
func performTLSHandshake(ctx context.Context, conn net.Conn, addr string, req packet.RequestPacket) (net.Conn, error) {
	tlsConfig, err := buildCustomTLSConfig(req)
	if err != nil {
		return nil, fmt.Errorf("TLS Config Error: %w", err)
	}

	// Set SNI secara otomatis jika kosong
	if tlsConfig.ServerName == "" {
		hostOnly, _, _ := net.SplitHostPort(addr)
		tlsConfig.ServerName = hostOnly
	}

	tlsConn := tls.Client(conn, tlsConfig)
	if err := tlsConn.HandshakeContext(ctx); err != nil {
		return nil, fmt.Errorf("handshake failed: %w", err)
	}

	return tlsConn, nil
}
