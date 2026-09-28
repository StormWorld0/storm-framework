package socket

import (
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"net"
	"os"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
	"golang.org/x/sys/unix"
)

// Helper internal untuk resolving host/IP ke unix.Sockaddr (menghindari duplikasi)
func resolveSockAddr(req packet.RequestPacket) (unix.Sockaddr, error) {
	addr, err := BuildTarget(req)
	if err != nil {
		return nil, fmt.Errorf("Build target failed: %w", err)
	}

	host, portStr, err := net.SplitHostPort(addr)
	if err != nil {
		host = addr
		portStr = "0"
	}

	port, _ := strconv.Atoi(portStr)
	ips, err := net.LookupIP(host)
	if err != nil || len(ips) == 0 {
		return nil, fmt.Errorf("DNS Resolution failed: %s", host)
	}

	afInt := ParseAF(req.AF)
	if afInt == unix.AF_INET6 {
		var addr16 [16]byte
		copy(addr16[:], ips[0].To16())
		return &unix.SockaddrInet6{Port: port, Addr: addr16}, nil
	}

	var addr4 [4]byte
	copy(addr4[:], ips[0].To4())
	return &unix.SockaddrInet4{Port: port, Addr: addr4}, nil
}

// performTLSHandshake membungkus logika upgrade TLS
func performTLSHandshake(ctx context.Context, conn net.Conn, addr string, req packet.RequestPacket) (net.Conn, error) {
	tlsConfig, err := buildCustomTLSConfig(req)
	if err != nil {
		return nil, fmt.Errorf("TLS Config Error: %w", err)
	}

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

func handleSocket(ctx *ExecutionContext) packet.ResponsePacket {
	afInt := ParseAF(ctx.Req.AF)
	sInt := ParseSockType(ctx.Req.SType)
	protoInt := ParseProtocol(ctx.Req.SProto)

	fd, err := unix.Socket(afInt, sInt, protoInt)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create socket: " + err.Error()}
	}

	udsPath := fmt.Sprintf("@storm_fd_%s", ctx.Req.MsgID)

	go func(fdInt int, path string) {
		realPath := strings.Replace(path, "@", "\x00", 1)
		addr, _ := net.ResolveUnixAddr("unix", realPath)

		l, err := net.ListenUnix("unix", addr)
		if err != nil {
			return
		}
		defer l.Close()

		l.SetDeadline(time.Now().Add(3 * time.Second))
		unxConn, err := l.AcceptUnix()
		if err != nil {
			return
		}
		defer unxConn.Close()

		rawConn, _ := unxConn.SyscallConn()
		rawConn.Control(func(sysFd uintptr) {
			rights := unix.UnixRights(fdInt)
			unix.Sendmsg(int(sysFd), []byte("F"), rights, nil, 0)
		})
	}(fd, udsPath)

	ctx.SaveSession(fd)

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"uds_path": udsPath,
		},
	}
}

func handleSetsockopt(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "SessionID is required for setsockopt"}
	}

	var targetFD int = -1

	if ctx.RawFD != -1 {
		targetFD = ctx.RawFD
	} else if ctx.Conn != nil {
		if sc, ok := ctx.Conn.(interface{ SyscallConn() (syscall.RawConn, error) }); ok {
			raw, err := sc.SyscallConn()
			if err != nil {
				return packet.ResponsePacket{Status: "ERROR", Message: "Failed to get SyscallConn: " + err.Error()}
			}

			err = raw.Control(func(fd uintptr) {
				targetFD = int(fd)
			})
			if err != nil {
				return packet.ResponsePacket{Status: "ERROR", Message: "FD Control failed: " + err.Error()}
			}
		}
	}

	if targetFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "Could not obtain raw FD for setsockopt. Invalid socket state."}
	}

	level := ParseOptLevel(ctx.Req.OptLevel)
	optName := ParseOptName(ctx.Req.OptName)
	optVal := int(ctx.Req.OptVal)

	if err := unix.SetsockoptInt(targetFD, level, optName, optVal); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Setsockopt failed: " + err.Error()}
	}

	ctx.SaveSession(nil) // Menjaga flag KeepSession jika KeepAlive=true

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"target_fd": targetFD,
			"level":     level,
			"opt_name":  optName,
			"opt_val":   optVal,
		},
	}
}

func handleBind(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "SessionID is required for bind"}
	}
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found. Call 'socket' primitive first."}
	}

	sockAddr, err := resolveSockAddr(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	if err := unix.Bind(ctx.RawFD, sockAddr); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Bind failed: " + err.Error()}
	}

	localAddr, err := unix.Getsockname(ctx.RawFD)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to see local addr & port: " + err.Error()}
	}

	ctx.SaveSession(ctx.RawFD)

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"local_ip": localAddr,
		},
	}
}

func handleListen(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found for listen."}
	}

	backlog := 128
	if ctx.Req.ReadSize > 0 {
		backlog = int(ctx.Req.ReadSize)
	}

	if err := unix.Listen(ctx.RawFD, backlog); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Listen failed: " + err.Error()}
	}

	ctx.SaveSession(ctx.RawFD)

	return packet.ResponsePacket{Status: "SUCCESS", Data: map[string]interface{}{"backlog": backlog}}
}

func handleAccept(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw listener socket (FD) found."}
	}

	tv := unix.NsecToTimeval(ctx.Timeout.Nanoseconds())
	unix.SetsockoptTimeval(ctx.RawFD, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &tv)

	nFD, _, err := unix.Accept(ctx.RawFD)
	if err != nil {
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
			return packet.ResponsePacket{Status: "TIMEOUT", Message: "Accept timeout expired. No incoming connections."}
		}
		return packet.ResponsePacket{Status: "ERROR", Message: "Accept failed: " + err.Error()}
	}

	if err := unix.SetNonblock(nFD, true); err != nil {
		unix.Close(nFD)
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to set non-blocking on accepted socket: " + err.Error()}
	}

	file := os.NewFile(uintptr(nFD), fmt.Sprintf("socket_accepted_%d", nFD))
	rawConn, err := net.FileConn(file)
	file.Close()
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to wrap accepted net.Conn: " + err.Error()}
	}

	ctx.Conn = rawConn
	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}

func handleConnect(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "SessionID is required for connect"}
	}
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found for this session. Call 'socket' primitive first."}
	}

	sockAddr, err := resolveSockAddr(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	errChan := make(chan error, 1)
	go func() {
		errChan <- unix.Connect(ctx.RawFD, sockAddr)
	}()

	select {
	case err := <-errChan:
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "OS Connect failed: " + err.Error()}
		}
	case <-time.After(ctx.Timeout):
		unix.Close(ctx.RawFD)
		return packet.ResponsePacket{Status: "ERROR", Message: "Connect timeout expired. Socket aborted."}
	}

	// Perbaikan Bug: Memakai ctx.RawFD (sebelumnya nFD yang undefined)
	if err := unix.SetNonblock(ctx.RawFD, true); err != nil {
		unix.Close(ctx.RawFD)
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to set non-blocking: " + err.Error()}
	}

	file := os.NewFile(uintptr(ctx.RawFD), fmt.Sprintf("socket_connect_%d", ctx.RawFD))
	rawConn, err := net.FileConn(file)
	file.Close()
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to wrap net.Conn: " + err.Error()}
	}

	ctx.Conn = rawConn
	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}

func handleCreate(ctx *ExecutionContext) packet.ResponsePacket {
	addr, err := BuildTarget(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Build target failed: " + err.Error()}
	}

	fd := utils.GetDialer()
	if fd == nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Global dialer not initialized"}
	}

	tCtx, cancel := context.WithTimeout(context.Background(), ctx.Timeout)
	defer cancel()

	rawConn, err := fd.Dial(tCtx, "tcp", addr)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "TCP Dial failed: " + err.Error()}
	}

	ctx.Conn = rawConn
	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}

func handleUpgradeTLS(ctx *ExecutionContext) packet.ResponsePacket {
	if ctls.IsTLSConn(ctx.Conn) {
		ctx.SaveSession(ctx.Conn)
		return packet.ResponsePacket{Status: "ERROR", Message: "Connection is already TLS"}
	}

	tCtx, cancel := context.WithTimeout(context.Background(), ctx.Timeout)
	defer cancel()

	addr, _ := BuildTarget(ctx.Req)
	tlsConn, err := performTLSHandshake(tCtx, ctx.Conn, addr, ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "TLS Upgrade failed: " + err.Error()}
	}

	ctx.Conn = tlsConn
	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}

func handleSend(ctx *ExecutionContext) packet.ResponsePacket {
	if err := ExecuteWrite(ctx.Conn, ctx.Req.Data, ctx.Timeout); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Write failed: " + err.Error()}
	}

	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}

func handleRecv(ctx *ExecutionContext) packet.ResponsePacket {
	buffer, n, bufPtr, err := ExecuteRead(ctx.Conn, ctx.Req.ReadSize, ctx.Timeout)
	defer ReleaseBuffer(bufPtr)

	if err != nil && err != io.EOF {
		if n == 0 {
			ctx.SaveSession(ctx.Conn)
			return packet.ResponsePacket{
				Status:  "TIMEOUT",
				Message: "Read failed: " + err.Error(),
				Data:    ctx.GenerateMetadata(0),
			}
		}
	}

	ctx.SaveSession(ctx.Conn)

	meta := ctx.GenerateMetadata(n)
	meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	meta["hex_bytes"] = hex.EncodeToString(buffer[:n])

	if err == io.EOF {
		return packet.ResponsePacket{Status: "WARN", Message: "EOF Read: " + err.Error()}
	}

	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}

func handleSendTo(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found. Call 'socket' primitive first."}
	}

	// Resolve target IP dan Port
	sockAddr, err := resolveSockAddr(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	flag := ParseFlags(ctx.Req.Flags)
	
	// Eksekusi menggunakan helper
	if err := ExecuteSendTo(ctx.RawFD, ctx.Req.Data, sockAddr, ctx.Timeout, flag); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Sendto failed: " + err.Error()}
	}

	ctx.SaveSession(ctx.RawFD)

	return packet.ResponsePacket{
		Status: "SUCCESS", 
		Data: map[string]interface{}{
			"is_reused":    ctx.IsReused,
			"rtt_ms":       time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}


func handleRecvFrom(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found for recvfrom."}
	}

	flag := ParseFlags(ctx.Req.Flags)

	buffer, n, sa, bufPtr, err := ExecuteRecvFrom(ctx.RawFD, int(ctx.Req.ReadSize), ctx.Timeout, flag)
	defer ReleaseBuffer(bufPtr)
	
	if err != nil && err != unix.EAGAIN && err != unix.EWOULDBLOCK {
		return packet.ResponsePacket{Status: "ERROR", Message: "Recvfrom failed: " + err.Error()}
	}
	
	if n == 0 || err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		ctx.SaveSession(ctx.RawFD)
		return packet.ResponsePacket{
			Status:  "TIMEOUT",
			Message: "Recvfrom Failed: " + err.Error(),
		}
	}

	ctx.SaveSession(ctx.RawFD)

	// Ekstrak IP dan Port dari Sender (Remote Address)
	var senderIP string
	var senderPort int
	switch v := sa.(type) {
	case *unix.SockaddrInet4:
		senderIP = net.IP(v.Addr[:]).String()
		senderPort = v.Port
	case *unix.SockaddrInet6:
		senderIP = net.IP(v.Addr[:]).String()
		senderPort = v.Port
	}

	sender := net.JoinHostPort(senderIP, strconv.Itoa(senderPort))

	if err == io.EOF {
		return packet.ResponsePacket{Status: "WARN", Message: "EOF Read: " + err.Error()}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS", 
		Data: map[string]interface{}{
			"is_reused":    ctx.IsReused,
			"rtt_ms":       time.Since(ctx.StartTime).Milliseconds(),
			"remote_ip":    sender,
			"raw_bytes":    base64.StdEncoding.EncodeToString(buffer[:n]),
			"hex_bytes":    hex.EncodeToString(buffer[:n]),
			"read_bytes":   n,
		},
	}
}
