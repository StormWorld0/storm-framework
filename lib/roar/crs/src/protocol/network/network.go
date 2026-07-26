// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package network

import (
	"context"
	"io"
	"os"
	"net"
	"fmt"
	"strings"
	"time"
	"strconv"
	"encoding/hex"
	"encoding/base64"
	"crypto/tls"
	"crypto/x509"
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

func buildCustomTLSConfig(req packet.RequestPacket) (*tls.Config, error) {
	verify := true
	if req.Verify {
		verify = false
	}
	
	tlsConfig := &tls.Config{
		InsecureSkipVerify: verify,
	}

	// 1. Client Certificate & Key (mTLS) jika diisi
	if req.TLSCert != "" && req.TLSKey != "" {
		var certBytes, keyBytes []byte
		var err error

		// Cek apakah string berupa path file atau raw PEM
		if _, err = os.Stat(req.TLSCert); err == nil {
			certBytes, err = os.ReadFile(req.TLSCert)
			if err != nil {
				return nil, fmt.Errorf("read cert file: %w", err)
			}
			keyBytes, err = os.ReadFile(req.TLSKey)
			if err != nil {
				return nil, fmt.Errorf("read key file: %w", err)
			}
		} else {
			certBytes = []byte(req.TLSCert)
			keyBytes = []byte(req.TLSKey)
		}

		cert, err := tls.X509KeyPair(certBytes, keyBytes)
		if err != nil {
			return nil, fmt.Errorf("load x509 key pair: %w", err)
		}

		tlsConfig.Certificates = []tls.Certificate{cert}
	}

	// 2. Custom Root CA jika diisi
	if req.TLSCA != "" {
		var caBytes []byte
		var err error

		if _, err = os.Stat(req.TLSCA); err == nil {
			caBytes, err = os.ReadFile(req.TLSCA)
			if err != nil {
				return nil, fmt.Errorf("read CA file: %w", err)
			}
		} else {
			caBytes = []byte(req.TLSCA)
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
        protocol = "tcp" // Default TCP
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
		
		hasCertKey := req.TLSCert != "" && req.TLSKey != ""

        if protocol == "tls" || protocol == "ssl" {
			// Melakukan handshake TCP && Handshake TLS 
			// menggunakan internal library fastdialer.
            conn, err = fd.DialTLS(ctx, "tcp", addr)
			if err != nil {
				return packet.ResponsePacket{Status: "ERROR", Message: "Connection DialTLS failed: " + err.Error()}
			}
        } else if protocol == "tcp" {

			// Protocol TCP = True
            rawConn, err := fd.Dial(ctx, "tcp", addr)
			if err != nil {
				return packet.ResponsePacket{Status: "ERROR", Message: "TCP Dial failed: " + err.Error()}
			}
			conn = rawConn
			
			// Cert/Key = True
			if hasCertKey {

			    // Melakukan parsing custom TLS
			    tlsConfig, err := buildCustomTLSConfig(req)
			    if err != nil {
				    rawConn.Close()
				    return packet.ResponsePacket{Status: "ERROR", Message: "TLS Config Error: " + err.Error()}
			    }
				
		    	// Melakukan handshake custom TLS
		    	tlsConn := tls.Client(rawConn, tlsConfig)
		    	if err := tlsConn.HandshakeContext(ctx); err != nil {
			    	rawConn.Close()
			    	return packet.ResponsePacket{Status: "ERROR", Message: "Custom TLS Handshake failed: " + err.Error()}
		    	}
				// Update session dengan koneksi TLS yang baru
                utils.ActiveSessions.Store(req.SessionID, tlsConn)
				conn = tlsConn
			}
        } 
    }
	
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

	
	// Penanganan Payload (Text vs Hex Binary)
	if mode == "duplex" || mode == "send_only" {
	    if req.Data != "" {
			// Malakukan decode
	        data_dec, err := base64.StdEncoding.DecodeString(req.Data)
	        if err != nil {
		        return packet.ResponsePacket{Status: "ERROR", Message: "Base64 decode failed: " + err.Error()}
	        }

			// Lakukan 
	    	_, err = conn.Write(data_dec)
	    	if err != nil {
		    	// Jika koneksi re-used ternyata sudah stale/broken di server side, hapus session
                if req.SessionID != "" {
                    utils.ActiveSessions.Delete(req.SessionID)
                    conn.Close()
                }
		    	return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
		    }
	    }
		if mode == "send_only" {
            // Pastikan state KeepAlive / SessionID tersimpan atau ditutup dengan benar
            // sebelum kabur dari fungsi.
            if req.SessionID != "" {
                if req.KeepAlive {
                    utils.ActiveSessions.Store(req.SessionID, conn)
                    keepSession = true
                } else {
                    utils.ActiveSessions.Delete(req.SessionID)
                    // keepSession tetap false, defer akan close conn
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

	// Readsize di gunakan untuk read byte
	readSize := req.ReadSize
	if readSize <= 0 {
		readSize = 0 // Default fallback
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
	
	conn.SetDeadline(time.Now().Add(timeout))
	defer conn.SetDeadline(time.Time{})
	
	// Pembacaan Buffer
	// Membaca stream sampai EOF atau buffer penuh agar tidak ada data tertinggal
	n, err := conn.Read(buffer)
	// --- Penanganan hasil baca ---
    if err != nil && err != io.EOF {
        // Error selain EOF -> hapus session, defer akan tutup
        if req.SessionID != "" {
            utils.ActiveSessions.Delete(req.SessionID)
        }
        if n == 0 {
            return packet.ResponsePacket{
                Status:  "ERROR",
                Message: "Read failed: " + err.Error(),
            }
        }
        // Jika n>0, kita tetap lanjutkan untuk mengembalikan data yang terbaca
    } else if err == io.EOF {
        // EOF: tidak ada data tersisa, hapus session dan tutup
        if req.SessionID != "" {
            utils.ActiveSessions.Delete(req.SessionID)
            // keepSession tetap false, defer akan tutup
        }
        // Jika tidak ada data terbaca, return respons kosong
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
        // Jika ada data meskipun EOF, proses di bawah (tetapi setelah return, defer tutup)
    }

	// --- Simpan session jika diminta dan tidak terjadi error ---
    if req.SessionID != "" && req.KeepAlive && err == nil {
        // Hanya simpan jika tidak ada error sama sekali (termasuk EOF)
        utils.ActiveSessions.Store(req.SessionID, conn)
        keepSession = true
    } else {
        // Jika ada error (termasuk EOF) atau KeepAlive=false, hapus session
        if req.SessionID != "" {
            utils.ActiveSessions.Delete(req.SessionID)
        }
        // keepSession tetap false
    }
	
	var tlsData map[string]interface{}
    if tlsConn, ok := conn.(*tls.Conn); ok {
	    // Dapatkan detail handshake SSL/TLS
    	state := tlsConn.ConnectionState()
		tlsData = map[string]interface{}{
            "tls_version":    tlsVersionString(state.Version),
            "cipher_suite":   tls.CipherSuiteName(state.CipherSuite),
            "protocol":       state.NegotiatedProtocol,
            "hostname":       state.ServerName,
            "handshake":      state.HandshakeComplete,
            "session_resume": state.DidResume,
        }
    	if len(state.PeerCertificates) > 0 {
		    cert := state.PeerCertificates[0] // Leaf Certificate
		    tlsData["subject"] = cert.Subject.CommonName
            tlsData["issuer"] = cert.Issuer.CommonName
            tlsData["dns_names"] = cert.DNSNames
            tlsData["expires_at"] = cert.NotAfter.Format(time.RFC3339)
	    }
		if len(state.VerifiedChains) > 0 {
            tlsData["cert_chain_count"] = len(state.VerifiedChains)
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

