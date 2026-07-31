// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package network

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"net"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

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

// Interface untuk mengekstrak TLS State dari koneksi apapun (Standard tls.Conn maupun Fastdialer wrapper)
type tlsConnStateGetter interface {
	ConnectionState() tls.ConnectionState
}

func buildCustomTLSConfig(req packet.RequestPacket) (*tls.Config, error) {
	tlsConfig := &tls.Config{
		InsecureSkipVerify: !req.Verify,
		MinVersion:         tls.VersionTLS12,
	}

	getPEMBytes := func(input string) ([]byte, error) {
		if input == "" {
			return nil, nil
		}
		// 1. Jika string diawali/mengandung header PEM, langsung pakai sebagai Raw Bytes
		if strings.Contains(input, "-----BEGIN") {
			return []byte(input), nil
		}
		// 2. Jika bukan PEM string, coba baca sebagai File Path
		if _, err := os.Stat(input); err == nil {
			bytes, err := os.ReadFile(input)
			if err != nil {
				return nil, fmt.Errorf("read file %s failed: %w", input, err)
			}
			return bytes, nil
		}
		// 3. Fallback jika bukan path yang valid & bukan PEM yang valid
		return []byte(input), nil
	}

	// Client Certificate & Key (mTLS) jika diisi
	if req.TLSCert != "" && req.TLSKey != "" {
		certBytes, err := getPEMBytes(req.TLSCert)
		if err != nil {
			return nil, fmt.Errorf("process tls-cert failed: %w", err)
		}

		keyBytes, err := getPEMBytes(req.TLSKey)
		if err != nil {
			return nil, fmt.Errorf("process tls-key failed: %w", err)
		}

		cert, err := tls.X509KeyPair(certBytes, keyBytes)
		if err != nil {
			return nil, fmt.Errorf("load x509 key pair: %w", err)
		}

		tlsConfig.Certificates = []tls.Certificate{cert}
	}

	// Custom Root CA jika diisi
	if req.TLSCA != "" {
		caBytes, err := getPEMBytes(req.TLSCA)
		if err != nil {
			return nil, fmt.Errorf("process tls-ca failed: %w", err)
		}

		caCertPool := x509.NewCertPool()
		if !caCertPool.AppendCertsFromPEM(caBytes) {
			return nil, fmt.Errorf("failed to parse custom CA PEM")
		}
		tlsConfig.RootCAs = caCertPool
	}

	return tlsConfig, nil
}


func BuildTarget(req packet.RequestPacket) (string, error) {
	rawHost := strings.TrimSpace(req.Host)
	if rawHost == "" {
		return "", fmt.Errorf("Invalid empty host")
	}

	// Handling Scheme (http/https)
	if strings.Contains(rawHost, "://") {
		parts := strings.SplitN(rawHost, "://", 2)
		rawHost = parts[1] // Ambil string setelah "://"
	}

	// Separate Host dan Port dari string
	hostOnly, portStr, err := net.SplitHostPort(rawHost)
	if err != nil {
		// Jika tidak ada port di string rawHost
		hostOnly = rawHost
		portStr = ""
	}

	// Potong Trailing Path (misal: "domain.com/v1/api" -> "domain.com")
	if idx := strings.Index(hostOnly, "/"); idx != -1 {
		hostOnly = hostOnly[:idx]
	}

	// Penentuan Final Port
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
	// Return dengan format "host:port" yang valid
	return net.JoinHostPort(hostOnly, strconv.Itoa(finalPort)), nil
}

// Socket mengeksekusi koneksi TCP/SSL/TLS
func Network(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()

	var (
		conn net.Conn
		err error
		isReused bool
		timeout time.Duration
	) 
	
	if req.Timeout <= 0 {
		timeout = 5 * time.Second
	} else {
		timeout = time.Duration(req.Timeout * float64(time.Second))
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

	mode := strings.ToLower(req.Mode)
	if mode == "" {
		mode = "duplex" // Default mode Normal
	}

	protocol := strings.ToLower(req.Protocol)
    if protocol == "" {
        protocol = "tcp"
    }

	addr, err := BuildTarget(req)
	if err != nil {
		return packet.ResponsePacket{
			Status: "ERROR", 
			Message: "Build target: " + err.Error(),
		}
	}
	
	if conn == nil {
		fd := utils.GetDialer()
		if fd == nil {
			return packet.ResponsePacket{
				Status: "ERROR", 
				Message: "Global dialer not initialized",
			}
		}

		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()

		rawConn, err := fd.Dial(ctx, "tcp", addr)
		if err != nil {
			return packet.ResponsePacket{
				Status: "ERROR", 
				Message: "TCP Dial failed: " + err.Error(),
			}
		}
		conn = rawConn
	}

	hasCertKey := req.TLSCert != "" && req.TLSKey != ""
	shouldUseTLS := protocol == "tls" || protocol == "ssl" || hasCertKey
	_, isAlreadyTLS := conn.(tlsConnStateGetter)

	return packet.ResponsePacket{
        Status: "INFO",
        Message: reflect.TypeOf(conn).String(),
    }

	if shouldUseTLS && !isAlreadyTLS {
		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()

		tlsConfig, err := buildCustomTLSConfig(req)
		if err != nil {
			if !isReused {
				conn.Close()
			}
			return packet.ResponsePacket{
				Status: "ERROR", 
				Message: "TLS Config Error: " + err.Error(),
			}
		}

		if tlsConfig.ServerName == "" {
			hostOnly, _, err := net.SplitHostPort(addr)
			if err != nil {
				return packet.ResponsePacket{
					Status: "ERROR",
					Message: "Invalid host for TLS ServerName: " + err.Error(),
				}
			}
			tlsConfig.ServerName = hostOnly
		}

		// Upgrade Socket ke TLS Client
		tlsConn := tls.Client(conn, tlsConfig)
		if err := tlsConn.HandshakeContext(ctx); err != nil {
			if !isReused {
				conn.Close()
			}
			return packet.ResponsePacket{
				Status: "ERROR", 
				Message: "TLS Handshake failed: " + err.Error(),
			}
		}
		
		// Update ActiveSessions dengan instance TLS yang baru
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
	

	// I/O Deadlines
	startTime := time.Now()

	
	// Penanganan Payload (Text vs Hex Binary)
	if mode == "duplex" || mode == "send_only" {
	    if req.Data != "" {
	        data_dec, err := base64.StdEncoding.DecodeString(req.Data)
	        if err != nil {
		        return packet.ResponsePacket{Status: "ERROR", Message: "Base64 decode failed: " + err.Error()}
	        }
	    	_, err = conn.Write(data_dec)
	    	if err != nil {
                if req.SessionID != "" {
                    utils.ActiveSessions.Delete(req.SessionID)
                    conn.Close()
                }
		    	return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		    }
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
            
            rtt := time.Since(startTime).Milliseconds()
            return packet.ResponsePacket{
                Status: "SUCCESS",
                Data: map[string]interface{}{
                    "is_reused": isReused,
                    "rtt_ms":    rtt,
                    "mode":      mode,
                },
            }
        }
	}

	// ==========================================
	// FASE READ (recv_only dan duplex masuk ke sini)
	// Mode recv_only akan langsung melompat ke baris ini 
	// tanpa menyentuh komputasi base64 dan Write.
	// ==========================================
	var (
        buffer []byte
		bufPtr *[]byte
        n int
    )

	if req.Mode == "recv_only" || req.Mode == "duplex" {
	    // Readsize di gunakan untuk read byte
    	readSize := req.ReadSize
    	if readSize <= 0 {
    		readSize = 0
	    }

    	if readSize == 4096 {
		    bufPtr = bufferPool.Get().(*[]byte)
		    buffer = *bufPtr
		    defer bufferPool.Put(bufPtr)
	    } else {
		    buffer = make([]byte, readSize)
	    }
	
	    conn.SetDeadline(time.Now().Add(timeout))
	    defer conn.SetDeadline(time.Time{})
	
    	// Pembacaan Buffer
	    n, err = conn.Read(buffer)
	  
    	// --- Penanganan hasil baca ---
        if err != nil && err != io.EOF {
            if req.SessionID != "" {
                utils.ActiveSessions.Delete(req.SessionID)
            }
            if n == 0 {
                return packet.ResponsePacket{
                    Status:  "ERROR",
                    Message: "Read failed: " + err.Error(),
			    	Data: map[string]interface{}{
			    		"buffer": n,
			    	},
                }
            }
        } else if err == io.EOF {
            if req.SessionID != "" {
                utils.ActiveSessions.Delete(req.SessionID)
            }
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

	    // --- Simpan session jika diminta dan tidak terjadi error ---
        if req.SessionID != "" && req.KeepAlive && err == nil {
	    	utils.ActiveSessions.Store(req.SessionID, conn)
	    	keepSession = true
        } else {
            if req.SessionID != "" {
                utils.ActiveSessions.Delete(req.SessionID)
            }
        }
	}
	
	var tlsData map[string]interface{}
	if req.InfoTLS {
	    if stateGetter, ok := conn.(tlsConnStateGetter); ok {
	    	state := stateGetter.ConnectionState()
		    if state.HandshakeComplete || state.Version != 0 {
		    	tlsData = map[string]interface{}{
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
		    		tlsData["cert_chain_count"] = len(state.VerifiedChains)
     	    	}
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
			"raw_bytes":    base64.StdEncoding.EncodeToString(buffer[:n]),
			"hex_bytes":    hex.EncodeToString(buffer[:n]),
			"read_bytes":   n,
			"protocol":     protocol,
			"ip":           remoteIP,
			"local_ip":     localAddr,
			"is_reused":    isReused,
			"rtt_ms":       rtt,
			"info_tls":     tlsData,
		},
	}
}

