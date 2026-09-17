package socket

import (
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"net"
	"time"
	"reflect"
	"strconv"
	"strings"
	"golang.org/x/sys/unix"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
)

// Network adalah entry point eksekusi koneksi menggunakan POSIX-like primitive operations.
func Socket(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()
	startTime := time.Now()

	if req.SessionID != "" {
		mu := utils.GetSessionLock(req.SessionID)
		mu.Lock()       // Goroutine lain dengan SessionID sama akan antre (pause) di sini
		defer mu.Unlock() // Otomatis dibuka saat fungsi Network selesai/return
	}

	timeout := 5 * time.Second
	if req.Timeout > 0 {
		timeout = time.Duration(req.Timeout * float64(time.Second))
	}

	// Normalisasi Primitif
	mode := strings.ToLower(req.Mode)
	if mode == "" {
		mode = "socket" // Fallback primitive
	}

	if mode == "close" {
		if req.SessionID != "" && req.CloseSess {
			// Atomic LoadAndDelete menjamin keamanan antar Goroutine
			if val, ok := utils.ActiveSessions.LoadAndDelete(req.SessionID); ok {
				targetConn := val.(net.Conn)
				targetConn.Close() // Membunuh socket yang BENAR, mencegah memory/socket leak
				return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
			}
			return packet.ResponsePacket{Status: "SUCCESS", Message: "No active session found to close"}
		}
		return packet.ResponsePacket{Status: "WARNING", Message: "Incomplete data to close the connection"}
	}

	// Ambil Sesi Aktif (Jika Ada)
	var conn net.Conn
	var rawFD int = -1
	var isReused bool
	
	if req.SessionID != "" {
		if val, ok := utils.ActiveSessions.Load(req.SessionID); ok {
			// Evaluasi tipe data yang tersimpan di dalam sync.Map
			switch v := val.(type) {
			case net.Conn:
				conn = v
				isReused = true // Sudah berupa koneksi aktif
			case int:
				rawFD = v
				// isReused tidak di-set true karena belum bisa dipakai send/recv
			default:
				return packet.ResponsePacket{Status: "ERROR", Message: "Corrupted session data"}
			}
		}
	}

	keepSession := false
	defer func() {
		// Socket HANYA ditutup jika:
		// 1. keepSession bernilai false (terjadi error/bukan keep-alive)
		// 2. socket tidak nil
		if !keepSession && conn != nil {
			conn.Close()
			// Jika terjadi error di tengah jalan, pastikan Session dihapus dari map
			if req.SessionID != "" {
				utils.ActiveSessions.Delete(req.SessionID)
			}
		}
	}()

	// Helper Closure untuk Assembly Metadata (Mencegah duplikasi kode)
	generateMetadata := func(readBytes int) map[string]interface{} {
		meta := map[string]interface{}{
			"is_reused":    isReused,
			"rtt_ms":       time.Since(startTime).Milliseconds(),
			"Cheked":       reflect.TypeOf(conn).String(),
			"isAlreadyTLS": strconv.FormatBool(ctls.IsTLSConn(conn)),
			"read_bytes":   readBytes,
		}
		if addr := conn.RemoteAddr(); addr != nil {
			meta["remote_ip"] = addr.String()
		}
		if lAddr := conn.LocalAddr(); lAddr != nil {
			meta["local_ip"] = lAddr.String()
		}
		if req.InfoTLS {
			meta["info_tls"] = ctls.ExtractTLSInfo(conn)
		}
		return meta
	}

	// Primitive State Machine (Routing Eksekusi)
	switch mode {
	case "socket":
		afInt := ParseAF(req.AF)               // req.AF adalah string, misal "AF_INET"
		sInt := ParseSockType(req.SType)       // req.SType adalah string, misal "SOCK_STREAM"
		protoInt := ParseProtocol(req.Protocol) // req.Protocol adalah string, misal "IPPROTO_TCP"
		
		fd, err := unix.Socket(afInt, sInt, protoInt)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create socket: " + err.Error()}
		}
		
		// Koneksi sudah terbuka di fase Auto-Dial. 
		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, fd)
			keepSession = true
		}
		return packet.ResponsePacket{
			Status: "SUCCESS", 
			Data: map[string]interface{}{
				"fileno": fd,
			},
		}

	case "connect":
		if req.SessionID == "" {
			return packet.ResponsePacket{Status: "ERROR", Message: "SessionID is required for connect"}
		}

		if rawFD == -1 {
			 return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found for this session. Call 'socket' primitive first."} 
		}

		// 2. Resolve DNS & Siapkan Address (syscall.Connect butuh raw IP, bukan string)
		addr, err := BuildTarget(req) // format: "host:port"
		if err != nil {
            return packet.ResponsePacket{Status: "ERROR", Message: "Build target failed: " + err.Error()}
        }
		
		host, portStr, err := net.SplitHostPort(addr)
		if err != nil {
			host = addr
			portStr = "0"
		}
		
		port, _ := strconv.Atoi(portStr)
		ips, err := net.LookupIP(host)
		if err != nil || len(ips) == 0 {
			return packet.ResponsePacket{Status: "ERROR", Message: "DNS Resolution failed: " + host}
		}

		afInt := ParseAF(req.AF)
		
		var sockAddr unix.Sockaddr
		if afInt == unix.AF_INET6 {
			var addr16 [16]byte
			copy(addr16[:], ips[0].To16())
			sockAddr = &unix.SockaddrInet6{Port: port, Addr: addr16}
		} else {
			// Default ke IPv4 (AF_INET)
			var addr4 [4]byte
			copy(addr4[:], ips[0].To4())
			sockAddr = &unix.SockaddrInet4{Port: port, Addr: addr4}
		}

		// Eksekusi Connect dengan Goroutine & Timeout Manual yang aman
		errChan := make(chan error, 1)
		go func() {
			errChan <- unix.Connect(rawFD, sockAddr)
		}()

		select {
		case err := <-errChan:
			if err != nil {
				return packet.ResponsePacket{Status: "ERROR", Message: "OS Connect failed: " + err.Error()}
			}
		case <-time.After(timeout):
			// Timeout tercapai!
			unix.Close(rawFD)
			return packet.ResponsePacket{Status: "ERROR", Message: "Connect timeout expired. Socket aborted."}
		}

		// ================================
		// Mengembalikan FD ke net.Conn
		// ================================
		
		// Golang butuh socket dalam keadaan non-blocking agar tidak hang!
		if err := unix.SetNonblock(rawFD, true); err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Failed to set non-blocking: " + err.Error()}
		}

		// Bungkus FD menjadi os.File
		file := os.NewFile(uintptr(rawFD), fmt.Sprintf("custom_socket_%d", rawFD))
		
		// Konversi os.File menjadi net.Conn
		rawConn, err := net.FileConn(file)
		if err != nil {
			file.Close() // Mencegah memory/FD leak jika gagal
			return packet.ResponsePacket{Status: "ERROR", Message: "Failed to wrap net.Conn: " + err.Error()}
		}
		
		// File asli ditutup karena net.FileConn otomatis membuat dup() (duplikat FD)
		file.Close()
		conn = rawConn

		// 4. Timpa isi Session dengan net.Conn yang baru
		// Mulai dari detik ini, request send/recv/upgrade_tls akan mendeteksi `net.Conn` normal!
		utils.ActiveSessions.Store(req.SessionID, conn)
		keepSession = true 

		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}

	case "create":
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
			
		utils.ActiveSessions.Store(req.SessionID, conn)
		keepSession = true
			
		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}
		
	case "upgrade_tls":
		// Mode khusus untuk kerentanan STARTTLS atau Protocol Smuggling
		if ctls.IsTLSConn(conn) {
			keepSession = true
			return packet.ResponsePacket{Status: "ERROR", Message: "Connection is already TLS"}
		}
		
		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()
		
		addr, _ := BuildTarget(req) // Target di-rebuild hanya untuk hostname SNI
		tlsConn, err := performTLSHandshake(ctx, conn, addr, req)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "TLS Upgrade failed: " + err.Error()}
		}
		
		conn = tlsConn 
		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, conn) // Timpa pointer lama dengan TLS socket yang baru
			keepSession = true
		}
		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}

	case "send":
		if err := ExecuteWrite(conn, req.Data, timeout); err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		}

		if req.SessionID != "" && req.KeepAlive {
			utils.ActiveSessions.Store(req.SessionID, conn)
			keepSession = true
		}
		return packet.ResponsePacket{Status: "SUCCESS", Data: generateMetadata(0)}

	case "recv":
		buffer, n, bufPtr, err := ExecuteRead(conn, req.ReadSize, timeout)
		defer ReleaseBuffer(bufPtr)

		if err != nil && err != io.EOF {
			if n == 0 {
				if req.SessionID != "" && req.KeepAlive {
			        utils.ActiveSessions.Store(req.SessionID, conn)
			        keepSession = true
		        }
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
