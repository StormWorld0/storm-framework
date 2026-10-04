package socket

import (
    "io"
    "net"
    "time"
    "strconv"
    "encoding/hex"
    "encoding/base64"
    "golang.org/x/sys/unix"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func handleSend(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD != -1 {
		flag := ParseFlags(ctx.Req.Flags)
		fd := ctx.RawFD
		if err := ExecuteFDWrite(fd, ctx.Req.Data, ctx.Timeout, flag); err != nil {
			ctx.SaveSession(fd)
		    // Error timeout (EAGAIN / EWOULDBLOCK)
		    if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
			    return packet.ResponsePacket{
				    Status:  "TIMEOUT",
				    Message: "Send failed: " + err.Error(),
				    Data:    ctx.GenerateMetadataFD(fd, 0),
			    } 
		    }
			return packet.ResponsePacket{Status: "ERROR", Message: "Send failed: " + err.Error()}
		}
		ctx.SaveSession(ctx.RawFD)
		return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadataFD(fd, 0)}
    }
	
	if err := ExecuteWrite(ctx.Conn, ctx.Req.Data, ctx.Timeout); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Send failed: " + err.Error()}
	}
	ctx.SaveSession(ctx.Conn)
    return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}	
}


func handleRecv(ctx *ExecutionContext) packet.ResponsePacket {
    if ctx.RawFD != -1 {
		flag := ParseFlags(ctx.Req.Flags)
		fd := ctx.RawFD
		buffer, n, _, bufPtr, err := ExecuteRecvFrom(fd, ctx.Req.ReadSize, ctx.Timeout, flag)
	    defer ReleaseBuffer(bufPtr)

		if err != nil {
			ctx.SaveSession(fd)
		    // Error timeout (EAGAIN / EWOULDBLOCK)
		    if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
			    return packet.ResponsePacket{
				    Status:  "TIMEOUT",
				    Message: "Recv failed: " + err.Error(),
				    Data:    ctx.GenerateMetadataFD(fd, 0),
			    } 
		    }
			return packet.ResponsePacket{Status: "ERROR", Message: "Recv failed: " + err.Error()}
		}
		ctx.SaveSession(fd)
	    meta := ctx.GenerateMetadataFD(fd, n)
	    meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	    meta["hex_bytes"] = hex.EncodeToString(buffer[:n])

		if n == 0 {
		    return packet.ResponsePacket{Status: "ERROR", Message: "EOF Recv: " + err.Error()}
	    }
    	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
	}
	
	buffer, n, bufPtr, err := ExecuteRead(ctx.Conn, ctx.Req.ReadSize, ctx.Timeout)
	defer ReleaseBuffer(bufPtr)
	
	if err != nil && err != io.EOF {
		if n == 0 {
			ctx.SaveSession(ctx.Conn)
			return packet.ResponsePacket{
				Status:  "TIMEOUT",
				Message: "Recv failed: " + err.Error(),
				Data:    ctx.GenerateMetadata(0),
			}
		}
	}
	ctx.SaveSession(ctx.Conn)
	meta := ctx.GenerateMetadata(n)
	meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	meta["hex_bytes"] = hex.EncodeToString(buffer[:n])

	if err == io.EOF {
		return packet.ResponsePacket{Status: "ERROR", Message: "EOF Recv: " + err.Error()}
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
		return packet.ResponsePacket{Status: "ERROR", Message: "ResolveSockAddr: " + err.Error()}
	}

	flag := ParseFlags(ctx.Req.Flags)
	fd := ctx.RawFD
	
	// Eksekusi menggunakan helper
	if err := ExecuteSendTo(fd, ctx.Req.Data, sockAddr, ctx.Timeout, flag); err != nil {
		ctx.SaveSession(fd)
		// Error timeout (EAGAIN / EWOULDBLOCK)
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
			return packet.ResponsePacket{
				Status:  "TIMEOUT",
				Message: "Sendto failed: " + err.Error(),
				Data:    ctx.GenerateMetadataFD(fd, 0),
			} 
		}
		return packet.ResponsePacket{Status: "ERROR", Message: "Sendto failed: " + err.Error()}
	}
	ctx.SaveSession(ctx.RawFD)
	return packet.ResponsePacket{
		Status: "SUCCESS", 
		Data: ctx.GenerateMetadataFD(fd, 0),
	}
}


func handleRecvFrom(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found for recvfrom."}
	}

	flag := ParseFlags(ctx.Req.Flags)
    fd := ctx.RawFD
	
	buffer, n, sa, bufPtr, err := ExecuteRecvFrom(fd, int(ctx.Req.ReadSize), ctx.Timeout, flag)
	defer ReleaseBuffer(bufPtr)
	
	if err != nil && err != unix.EAGAIN && err != unix.EWOULDBLOCK {
		return packet.ResponsePacket{Status: "ERROR", Message: "Recvfrom failed: " + err.Error()}
	}
	
	if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		ctx.SaveSession(fd)
		return packet.ResponsePacket{
			Status:  "TIMEOUT",
			Message: "Recvfrom Failed: " + err.Error(),
			Data:    ctx.GenerateMetadataFD(fd, 0),
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

	if n == 0 {
		return packet.ResponsePacket{Status: "ERROR", Message: "EOF Recvfrom: " + err.Error()}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS", 
		Data: map[string]interface{}{
			"raw_bytes":    base64.StdEncoding.EncodeToString(buffer[:n]),
			"hex_bytes":    hex.EncodeToString(buffer[:n]),
		    "remote_ip":    sender,
		    "is_reused":    ctx.IsReused,
		    "rtt_ms":       time.Since(ctx.StartTime).Milliseconds(),
		    "Cheked":       "RawSocket",
		    "read_bytes":   readBytes,
		},
	}
}
