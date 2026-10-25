package socket

import (
    "syscall"
    "golang.org/x/sys/unix"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func handleSetsockopt(ctx *ExecutionContext) packet.ResponsePacket {
	if ctx.Req.SessionID == "" {
		return packet.ResponsePacket{Status: "ERROR", Message: "SessionID is required for setsockopt"}
	}

	var targetFD int = -1

	if ctx.RawFD != -1 {         // FD Socket
		targetFD = ctx.RawFD
	} else if ctx.CltFD != -1 {  // FD Client Listener
		targetFD = ctx.CltFD
	} else if ctx.Conn != nil {  // FD net.Conn / tls.Conn
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

	level := ParseOptLevel(ctx.Req.OptLevel)
	optName := ParseOptName(ctx.Req.OptName)
	optVal := int(ctx.Req.OptVal)

	if err := unix.SetsockoptInt(targetFD, level, optName, optVal); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Setsockopt failed: " + err.Error()}
	}

	if ctx.Conn != nil {
	    ctx.SaveSession(ctx.Conn)
	} else if ctx.RawFD != -1 {
		ctx.SaveSession(ctx.RawFD)
	} else if ctx.CltFD != -1 {
		ctx.SaveSessionCFD(ctx.CltFD)
	}

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
