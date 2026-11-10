package socket

import (
    "io"
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

	if n == 0 {
		return packet.ResponsePacket{Status: "ERROR", Message: "EOF Recvfrom: " + err.Error()}
	}

	ctx.SaveSession(ctx.RawFD)
	meta := ctx.GenerateMetadataFD(fd, n)
	meta["raw_bytes"] = base64.StdEncoding.EncodeToString(buffer[:n])
	meta["hex_bytes"] = hex.EncodeToString(buffer[:n])
	meta["remote_ip"] = formatSockaddr(sa)
	return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}
