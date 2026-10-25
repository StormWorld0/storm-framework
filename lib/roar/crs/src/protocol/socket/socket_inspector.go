package socket

import (
    "golang.org/x/sys/unix"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleGetPeerName(ctx *ExecutionContext) packet.ResponsePacket {
    fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
    }

    if fd >= 0 {
        remoteAddr, err := unix.Getpeername(fd)
        ctx.SaveSession(ctx.RawFD)
        if err != nil {
		    return packet.ResponsePacket{Status: "ERROR", Message: "Getpeername failed: " + err.Error()}
	    }
        meta := ctx.GenerateMetadataFD(fd, 0)
        if addr := formatSockaddr(remoteAddr); addr != "" {
            meta["remote_ip"] = addr
        }
        return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
    }
    
    meta := ctx.GenerateMetadata(0)
    if rAddr := ctx.Conn.RemoteAddr(); rAddr != nil {
        meta["remote_ip"] = rAddr
    }
    ctx.SaveSession(ctx.Conn)
    return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}

func handleGetSockName(ctx *ExecutionContext) packet.ResponsePacket {
    fd := ctx.RawFD
	if ctx.Req.CltFD >= 0 {
		fd = ctx.Req.CltFD
    }

    if fd >= 0 {
        ctx.SaveSession(ctx.RawFD)
        localAddr, err := unix.Getsockname(fd)
        if err != nil {
            return packet.ResponsePacket{Status: "ERROR", Message: "Getsockname failed: " + err.Error()}
        }
        meta := ctx.GenerateMetadataFD(fd, 0)
		if addr := formatSockaddr(localAddr); addr != "" {
			meta["local_ip"] = addr
		}
        return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
    }

    meta := ctx.GenerateMetadata(0)
    if lAddr := ctx.Conn.LocalAddr(); lAddr != nil {
		meta["local_ip"] = lAddr.String()
	}
    ctx.SaveSession(ctx.Conn)
    return packet.ResponsePacket{Status: "SUCCESS", Data: meta}
}
