package socket

import (
    "syscall"
    "golang.org/x/sys/unix"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func handleSetsockopt(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "SessionID is required for setsockopt"}
	}

	var intFD int = -1

	if ctx.Req.CltFD != -1 {     // FD Client Listener
		intFD = ctx.Req.CltFD
	} else if ctx.RawFD != -1 {  // FD Socket
		intFD = ctx.RawFD
	} else if ctx.Conn != nil {  // FD net.Conn / tls.UConn
		if sc, ok := ctx.Conn.(interface{ SyscallConn() (syscall.RawConn, error) }); ok {
			raw, err := sc.SyscallConn()
			if err != nil {
				return packet.ResponsePacket{Status: "S-ERROR", Message: "Failed to get SyscallConn: " + err.Error()}
			}
			err = raw.Control(func(fd uintptr) {
				intFD = int(fd)
			})
			if err != nil {
				return packet.ResponsePacket{Status: "S-ERROR", Message: "FD Control failed: " + err.Error()}
			}
		}
	}

	if intFD == -1 {
        return packet.ResponsePacket{Status:  "S-ERROR", Message: "Setsockopt no valid socket descriptor available"}
    }

	level := ParseOptLevel(ctx.Req.OptLevel)
	optName := ParseOptName(ctx.Req.OptName)
	optVal := int(ctx.Req.OptVal)

	if err := unix.SetsockoptInt(intFD, level, optName, optVal); err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "Setsockopt failed: " + err.Error()}
	}

	if ctx.Req.CltFD != -1 {
		ctx.SaveSessionCFD(ctx.Req.CltFD)
	} else if ctx.RawFD != -1 {
		ctx.SaveSession(ctx.RawFD)
	} else if ctx.Conn != nil {
	    ctx.SaveSession(ctx.Conn)
	}
	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadataFD(intFD, 0)}
}

func handleGetSockOpt(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "SessionID is required for getsockopt"}
	}

	var intFD int = -1

	if ctx.Req.CltFD != -1 {       // FD Client Listener
		intFD = ctx.Req.CltFD
	} else if ctx.RawFD != -1 {    // FD Socket
		intFD = ctx.RawFD
	} else if ctx.Conn != nil {    // FD net.Conn / tls.UConn
		if sc, ok := ctx.Conn.(interface{ SyscallConn() (syscall.RawConn, error) }); ok {
			raw, err := sc.SyscallConn()
			if err != nil {
				return packet.ResponsePacket{Status: "S-ERROR", Message: "Failed to get SyscallConn: " + err.Error()}
			}
			err = raw.Control(func(fd uintptr) {
				intFD = int(fd)
			})
			if err != nil {
				return packet.ResponsePacket{Status: "S-ERROR", Message: "FD Control failed: " + err.Error()}
			}
		}
	}

	if intFD == -1 {
        return packet.ResponsePacket{Status:  "S-ERROR", Message: "Getsockopt no valid socket descriptor available"}
    }

	level := ParseOptLevel(ctx.Req.OptLevel)
	optName := ParseOptName(ctx.Req.OptName)

	val, err := unix.GetsockoptInt(intFD, level, optName)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "Getsockopt failed: " + err.Error()}
	}
	
	if ctx.Req.CltFD != -1 {
		ctx.SaveSessionCFD(ctx.Req.CltFD)
	} else if ctx.RawFD != -1 {
		ctx.SaveSession(ctx.RawFD)
	} else if ctx.Conn != nil {
		ctx.SaveSession(ctx.Conn)
	}
	return packet.ResponsePacket{Status: "SUCCESS", Data: map[string]interface{}{"val_opt": val}}
}

