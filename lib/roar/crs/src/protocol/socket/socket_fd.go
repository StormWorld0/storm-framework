package socket

import (
    "fmt"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleFileno(ctx *ExecutionContext) packet.ResponsePacket {
    if ctx.RawFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No raw socket (FD) found. Call 'socket' first."}
    }
    
    name := fmt.Sprintf("@socket_fd_%s", ctx.Req.MsgID)
	udsPath, err := BuildUdsPath(ctx.RawFD, name)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Fileno failed: " + err.Error()}
    }
    
    ctx.SaveSession(ctx.RawFD)
    return packet.ResponsePacket{
        Status: "SUCCESS",
        Data: map[string]interface{}{
            "uds_path": udsPath,
        },
    }
}

func handleFilenoClt(ctx *ExecutionContext) packet.ResponsePacket {
    if ctx.CFD == -1 {
		return packet.ResponsePacket{Status: "ERROR", Message: "No client socket (FD) found. Call 'accept' first."}
    }
    
    name := fmt.Sprintf("@client_fd_%s", ctx.Req.MsgID)
	udsPath, err := BuildUdsPath(ctx.CFD, name)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "FilenoClt failed: " + err.Error()}
    }
    
    ctx.SaveSession(ctx.RawFD)
    return packet.ResponsePacket{
        Status: "SUCCESS",
        Data: map[string]interface{}{
            "client_uds": udsPath,
        },
    }
} 
