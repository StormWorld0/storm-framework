package socket

import (
    "net"
    "fmt"
    "time"
    "context"
    "golang.org/x/sys/unix"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)


func handleSocket(ctx *ExecutionContext) packet.ResponsePacket {
	afInt := ParseAF(ctx.Req.AF)
	sInt := ParseSockType(ctx.Req.SType)
	protoInt := ParseProtocol(ctx.Req.SProto)

	fd, err := unix.Socket(afInt, sInt, protoInt)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed to create socket: " + err.Error()}
	}

	name := fmt.Sprintf("@storm_fd_%s", ctx.Req.MsgID)
	udsPath, err := BuildUdsPath(fd, name)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}
	
	ctx.SaveSession(fd)

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"uds_path": udsPath,
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
	if ctx.Req.BackLog > 0 {
		backlog = int(ctx.Req.BackLog)
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

	if ctx.Timeout > 0 {
	    tv := unix.NsecToTimeval(ctx.Timeout.Nanoseconds())
	    unix.SetsockoptTimeval(ctx.RawFD, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(ctx.RawFD, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &zeroTv)
		}()
	}

	nFD, _, err := unix.Accept(ctx.RawFD)
	if err != nil {
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
			return packet.ResponsePacket{Status: "TIMEOUT", Message: "Accept timeout expired. No incoming connections."}
		}
		return packet.ResponsePacket{Status: "ERROR", Message: "Accept failed: " + err.Error()}
	}

	ctx.SaveSessionCFD(nFD)

	name := fmt.Sprintf("@client_fd_%s", ctx.Req.MsgID)
	udsPath, err := BuildUdsPath(nFD, name)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	ctx.SaveSession(ctx.RawFD)
	
	return packet.ResponsePacket{
		Status: "SUCCESS", 
		Data: map[string]interface{}{
			"client_uds": udsPath,
		},
	}
}


func handleConnect(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "SessionID is required for connect"}
	}
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found for this session. Call 'socket' primitive first."}
	}

	ctx.SaveSessionHost(ctx.Req.Host)

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

	ctx.SaveSession(ctx.RawFD)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadataFD(ctx.RawFD, 0)}
}


func handleCreate(ctx *ExecutionContext) packet.ResponsePacket {
	addr, port, err := BuildTarget(ctx.Req.Host, ctx.Req.Port)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Build target failed: " + err.Error()}
	}

	addrStr := DerefString(addr, "")
	portStr := DerefString(port, "")

	host := net.JoinHostPort(addrStr, portStr)

	fd := utils.GetDialer()
	if fd == nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Global dialer not initialized"}
	}

	tCtx, cancel := context.WithTimeout(context.Background(), ctx.Timeout)
	defer cancel()

	rawConn, err := fd.Dial(tCtx, "tcp", host)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "TCP Dial failed: " + err.Error()}
	}

	ctx.Conn = rawConn
	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}
