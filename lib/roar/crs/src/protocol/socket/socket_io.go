package socket

import (
    "io"
    "net"
    "strconv"
    "encoding/hex"
    "encoding/base64"
    "golang.org/x/sys/unix"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func handleSendAll(ctx *ExecutionContext) packet.ResponsePacket {
	fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
	}
	
	if fd >= 0 {
		flag := ParseFlags(ctx.Req.Flags)
		if err := ExecuteFDWriteAll(fd, ctx.Req.Data, ctx.Timeout, flag); err != nil {
		    ctx.SaveSession(ctx.RawFD)
		    // Error timeout (EAGAIN / EWOULDBLOCK)
		    if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		    	return packet.ResponsePacket{
			    	Status:  "TIMEOUT",
				    Message: "SendAll failed: " + err.Error(),
				    Data:    ctx.GenerateMetadataFD(fd, 0),
		    	} 
	    	}
	    	return packet.ResponsePacket{Status: "ERROR", Message: "SendAll failed: " + err.Error()}
    	}
	    ctx.SaveSession(ctx.RawFD)
	    return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadataFD(fd, 0)}
	}
	
	if err := ExecuteWrite(ctx.Conn, ctx.Req.Data, ctx.Timeout); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "SendAll failed: " + err.Error()}
	}
	ctx.SaveSession(ctx.Conn)
    return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}


func handleSendFile(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.CFD == -1 {
		return packet.ResponsePacket{Status: "WARN", Message: "No client socket (FD) found for sendfile."}
	}

	if err := ExecuteFDWriteFile(ctx.CFD, ctx.Req.File, ctx.Timeout); err != nil {
		ctx.SaveSessionCFD(ctx.CFD)
		// Error timeout (EAGAIN / EWOULDBLOCK)
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		    return packet.ResponsePacket{
			    Status:  "TIMEOUT",
				Message: "Sendfile failed: " + err.Error(),
				Data:    ctx.GenerateMetadataFD(ctx.CFD, 0),
		    } 
	    }
		return packet.ResponsePacket{Status: "ERROR", Message: "Sendfile failed: " + err.Error()}
	}

	ctx.SaveSessionCFD(ctx.CFD)
	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadataFD(ctx.CFD, 0)}
}


func handleSend(ctx *ExecutionContext) packet.ResponsePacket {
	fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
	}
	
	if fd >= 0 {
		flag := ParseFlags(ctx.Req.Flags)
		if err := ExecuteFDWrite(fd, ctx.Req.Data, ctx.Timeout, flag); err != nil {
			ctx.SaveSession(ctx.RawFD)
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
	fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
	}
	
    if fd >= 0 {
		flag := ParseFlags(ctx.Req.Flags)
		buffer, n, _, bufPtr, err := ExecuteRecvFrom(fd, ctx.Req.Buffer, ctx.Timeout, flag)
	    defer ReleaseBuffer(bufPtr)

		if err != nil {
			ctx.SaveSession(ctx.RawFD)
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

		if n == 0 {
		    return packet.ResponsePacket{Status: "ERROR", Message: "EOF Recv: " + err.Error()}
	    }
		
		ctx.SaveSession(ctx.RawFD)
	    meta := ctx.GenerateMetadataFD(fd, n)
	    meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	    meta["hex_bytes"] = hex.EncodeToString(buffer[:n])
    	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
	}
	
	buffer, n, bufPtr, err := ExecuteRead(ctx.Conn, ctx.Req.Buffer, ctx.Timeout)
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
	
	if err == io.EOF {
		return packet.ResponsePacket{Status: "ERROR", Message: "EOF Recv: " + err.Error()}
	}

	ctx.SaveSession(ctx.Conn)
	meta := ctx.GenerateMetadata(n)
	meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	meta["hex_bytes"] = hex.EncodeToString(buffer[:n])
	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}


func handleSendTo(ctx *ExecutionContext) packet.ResponsePacket {
	fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
	}
	
	if fd < 0 {
		return packet.ResponsePacket{Status: "WARN", Message: "No raw socket (FD) found for sendto."}
	}

	sockAddr, err := resolveSockAddr(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "ResolveSockAddr: " + err.Error()}
	}

	flag := ParseFlags(ctx.Req.Flags)
	
	if err := ExecuteSendTo(fd, ctx.Req.Data, sockAddr, ctx.Timeout, flag); err != nil {
		ctx.SaveSession(ctx.RawFD)
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
	fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
	}
	
	if fd < 0 {
		return packet.ResponsePacket{Status: "WARN", Message: "No raw socket (FD) found for recvfrom."}
	}

	flag := ParseFlags(ctx.Req.Flags)
	
	buffer, n, sa, bufPtr, err := ExecuteRecvFrom(fd, ctx.Req.Buffer, ctx.Timeout, flag)
	defer ReleaseBuffer(bufPtr)
	
	if err != nil {
		ctx.SaveSession(ctx.RawFD)
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		    return packet.ResponsePacket{
			    Status:  "TIMEOUT",
			    Message: "Recvfrom Failed: " + err.Error(),
			    Data:    ctx.GenerateMetadataFD(fd, 0),
		    }
		}
		return packet.ResponsePacket{Status: "ERROR", Message: "Recvfrom failed: " + err.Error()}
	}

	// Extract IP and Port from Sender (Remote Address)
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

	ctx.SaveSession(ctx.RawFD)
	meta := ctx.GenerateMetadataFD(fd, n)
	meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	meta["hex_bytes"] = hex.EncodeToString(buffer[:n])
	meta["remote_ip"] = sender
	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}


func handleSendMsg(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "WARN", Message: "No raw socket (FD) found for sendmsg."}
	}

	fd := ctx.RawFD
	buffer := ctx.Req.Buffer
	ancData := ctx.Req.Anc
	typeInt := ParseSockType(ctx.Req.SType)
	timeout := ctx.Timeout

	sockAddr, err := resolveSockAddr(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "ResolveSockAddr: " + err.Error()}
	}
	
	if err := ExecuteSendMsg(fd, buffer, ancData, sockAddr, flag, timeout); err != nil {
		ctx.SaveSession(fd)
		// Error timeout (EAGAIN / EWOULDBLOCK)
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
			return packet.ResponsePacket{
			    Status:  "TIMEOUT",
				Message: "Sendmsg failed: " + err.Error(),
				Data:    ctx.GenerateMetadataFD(fd, 0),
			} 
		}
		return packet.ResponsePacket{Status: "ERROR", Message: "Sendmsg failed: " + err.Error()}
	}
	ctx.SaveSession(fd)
	return packet.ResponsePacket{
		Status: "SUCCESS", 
		Data: ctx.GenerateMetadataFD(fd, 0),
	}
}


func handleRecvMsg(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "WARN", Message: "No raw socket (FD) found for sendmsg."}
	}

	fd := ctx.RawFD
	buffer := ctx.Req.Buffer
	ancData := ctx.Req.Anc
	timeout := ctx.Timeout
	typeInt := ParseSockType(ctx.Req.SType)
	flag := ParseFlags(ctx.Req.Flags)

	if typeInt == unix.SOCK_STREAM {
	    buffer, bufPtr, n, ob, rf, _, err := ExecuteRecvMsgStream(fd, buffer, ancData, flag, timeout)
		defer ReleaseBuffer(bufPtr)
		
		if err != nil {
			ctx.SaveSession(fd)
		    // Error timeout (EAGAIN / EWOULDBLOCK)
		    if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		        return packet.ResponsePacket{
			        Status:  "TIMEOUT",
				    Message: "Recvmsg failed: " + err.Error(),
				    Data:    ctx.GenerateMetadataFD(fd, 0),
			    } 
		    }
		    return packet.ResponsePacket{Status: "ERROR", Message: "Recvmsg failed: " + err.Error()}
		}
		
		ctx.SaveSession(fd)
	    meta := ctx.GenerateMetadataFD(fd, n)
		meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	    meta["hex_bytes"] = hex.EncodeToString(buffer[:n])
		meta["ancdata"] = ob
		meta["flags"] = rf
	    return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
	}

	buffer, bufPtr, n, ob, rf, sa, err := ExecuteRecvMsgDgram(fd, buffer, ancData, flag, timeout)
	defer ReleaseBuffer(bufPtr)
	
	if err != nil {
		ctx.SaveSession(fd)
		// Error timeout (EAGAIN / EWOULDBLOCK)
		if err == unix.EAGAIN || err == unix.EWOULDBLOCK {
		    return packet.ResponsePacket{
			    Status:  "TIMEOUT",
				Message: "Recvmsg failed: " + err.Error(),
				Data:    ctx.GenerateMetadataFD(fd, 0),
			} 
		}
		return packet.ResponsePacket{Status: "ERROR", Message: "Recvmsg failed: " + err.Error()}
	}

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
	
	ctx.SaveSession(fd)
	meta := ctx.GenerateMetadataFD(fd, n)
	meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	meta["hex_bytes"] = hex.EncodeToString(buffer[:n])
	meta["ancdata"] = ob
	meta["flags"] = rf
	meta["remote_ip"] = sender
	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}

