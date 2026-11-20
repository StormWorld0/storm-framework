package socket

import (
    "fmt"
	"syscall"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleFileno(ctx *ExecutionContext) packet.ResponsePacket {
    var intFD int = -1
	if ctx.RawFD != -1 {         // FD Socket
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
		return packet.ResponsePacket{Status: "S-WARN", Message: "No raw socket (FD) found. Call 'socket' first."}
    }
    
    name := fmt.Sprintf("@socket_fd_%s", ctx.Req.MsgID)
	udsPath, err := BuildUdsPath(intFD, name)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "Fileno failed: " + err.Error()}
    }

	if ctx.RawFD != -1 {
        ctx.SaveSession(ctx.RawFD)
	} else if ctx.Conn != nil {
		ctx.SaveSession(ctx.Conn)
	}
    return packet.ResponsePacket{Status: "SUCCESS", Data: map[string]interface{}{"socket_uds": udsPath}}
}

func handleFilenoClt(ctx *ExecutionContext) packet.ResponsePacket {
    if ctx.CFD == -1 {
		return packet.ResponsePacket{Status: "S-WARN", Message: "No client socket (FD) found. Call 'accept' first."}
    }
    
    name := fmt.Sprintf("@client_fd_%s", ctx.Req.MsgID)
	udsPath, err := BuildUdsPath(ctx.CFD, name)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "FilenoClt failed: " + err.Error()}
    }
    
    ctx.SaveSessionCFD(ctx.CFD)
    return packet.ResponsePacket{Status: "SUCCESS", Data: map[string]interface{}{"client_uds": udsPath}}
} 
