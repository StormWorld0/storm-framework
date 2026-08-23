package network

import (
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/hex"
	"io"
	"net"
	"reflect"
	"strconv"
	"strings"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// Network adalah entry point eksekusi koneksi
func Network(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()

	var (
		conn     net.Conn
		err      error
		isReused bool
		timeout  time.Duration
	)

	if req.Timeout <= 0 {
		timeout = 5 * time.Second
	} else {
		timeout = time.Duration(req.Timeout * float64(time.Second))
	}

	// 1. Manajemen Sesi (Close)
	if req.SessionID != "" && req.CloseSess {
		if val, ok := utils.ActiveSessions.LoadAndDelete(req.SessionID); ok {
			val.(net.Conn).Close()
			return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
		}
	}

	// 2. Manajemen Sesi (Reuse)
	if req.SessionID != "" {
		if val, ok := utils.ActiveSessions.Load(req.SessionID); ok {
			conn = val.(net.Conn)
			isReused = true
		}
	}

	mode := strings.ToLower(req.Mode)
	if mode == "" {
		mode = "duplex"
	}
	protocol := strings.ToLower(req.Protocol)
	if protocol == "" {
		protocol = "tcp"
	}

	addr, err := BuildTarget(req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Build target: " + err.Error()}
	}

	// 3. Fase Dialing
	if conn == nil {
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
	}

	// 4. Fase TLS Upgrade
	hasCertKey := req.TLSCert != "" && req.TLSKey != ""
	shouldUseTLS := protocol == "tls" || protocol == "ssl" || hasCertKey

	if req.Mode == "upgrade_tls" && shouldUseTLS && !isTLSConn(conn) {
		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()

		tlsConfig, err := buildCustomTLSConfig(req)
		if err != nil {
			if !isReused {
				conn.Close()
			}
			return packet.ResponsePacket{Status: "ERROR", Message: "TLS Config Error: " + err.Error()}
		}

		if tlsConfig.ServerName == "" {
			hostOnly, _, _ := net.SplitHostPort(addr)
			tlsConfig.ServerName = hostOnly
		}

		tlsConn := tls.Client(conn, tlsConfig)
		if err := tlsConn.HandshakeContext(ctx); err != nil {
			if !isReused {
				conn.Close()
			}
			return packet.ResponsePacket{Status: "ERROR", Message: "TLS Handshake failed: " + err.Error()}
		}

		if req.SessionID != "" {
			utils.ActiveSessions.Store(req.SessionID, tlsConn)
		}
		conn = tlsConn
	}

	keepSession := false
	defer func() {
		if !keepSession {
			if req.SessionID != "" {
				utils.ActiveSessions.Delete(req.SessionID)
			}
			conn.Close()
		}
	}()

	startTime := time.Now()

	// 5. Fase Write
	if mode == "duplex" || mode == "send_only" {
		if err := ExecuteWrite(conn, req.Data); err != nil {
			if req.SessionID != "" {
				utils.ActiveSessions.Delete(req.SessionID)
				conn.Close()
			}
			return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		}

		if mode == "send_only" {
			if req.SessionID != "" {
				if req.KeepAlive {
					utils.ActiveSessions.Store(req.SessionID, conn)
					keepSession = true
				} else {
					utils.ActiveSessions.Delete(req.SessionID)
				}
			}
			return packet.ResponsePacket{
				Status: "SUCCESS",
				Data: map[string]interface{}{
					"is_reused":    isReused,
					"rtt_ms":       time.Since(startTime).Milliseconds(),
					"Cheked":       reflect.TypeOf(conn).String(),
					"isAlreadyTLS": strconv.FormatBool(isTLSConn(conn)),
				},
			}
		}
	}

	// 6. Fase Read
	var (
		buffer []byte
		n      int
		bufPtr *[]byte
	)

	if mode == "recv_only" || mode == "duplex" {
		buffer, n, bufPtr, err = ExecuteRead(conn, req.ReadSize, timeout)
		defer ReleaseBuffer(bufPtr)

		if err != nil && err != io.EOF {
			if n == 0 {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "Read failed: " + err.Error(),
					Data: map[string]interface{}{
						"buffer":       n,
						"is_reused":    isReused,
						"Cheked":       reflect.TypeOf(conn).String(),
						"isAlreadyTLS": strconv.FormatBool(isTLSConn(conn)),
					},
				}
			}
		} else if err == io.EOF {
			if n == 0 {
				return packet.ResponsePacket{
					Status:  "SUCCESS",
					Message: "EOF - no more data",
					Data: map[string]interface{}{
						"read_bytes": 0,
						"is_reused":  isReused,
						"rtt_ms":     time.Since(startTime).Milliseconds(),
					},
				}
			}
		}
	}

	// 7. Penentuan Sesi & Assembly Respon Akhir
	if req.SessionID != "" && req.KeepAlive {
		utils.ActiveSessions.Store(req.SessionID, conn)
		keepSession = true
	} else if req.SessionID != "" {
		utils.ActiveSessions.Delete(req.SessionID)
	}

	var tlsData map[string]interface{}
	if req.InfoTLS {
		tlsData = ExtractTLSInfo(conn)
	}

	remoteIP, localAddr := "unknown", "unknown"
	if addr := conn.RemoteAddr(); addr != nil {
		remoteIP = addr.String()
	}
	if lAddr := conn.LocalAddr(); lAddr != nil {
		localAddr = lAddr.String()
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"raw_bytes":    base64.StdEncoding.EncodeToString(buffer[:n]),
			"hex_bytes":    hex.EncodeToString(buffer[:n]),
			"read_bytes":   n,
			"protocol":     protocol,
			"remote_ip":    remoteIP,
			"local_ip":     localAddr,
			"is_reused":    isReused,
			"rtt_ms":       time.Since(startTime).Milliseconds(),
			"info_tls":     tlsData,
			"Cheked":       reflect.TypeOf(conn).String(),
			"isAlreadyTLS": strconv.FormatBool(isTLSConn(conn)),
		},
	}
}
