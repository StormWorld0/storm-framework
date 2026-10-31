package socket

import (
	"time"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	h1, p2, r1, r2, e1 := getAddrInfo(ctx)
	if e1 != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: e1.Error()}
	}
	
	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":    h1,
			"service": p2,
			"results": r1,
			"count":   r2,
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}


func handleGetNameInfo(ctx *ExecutionContext) packet.ResponsePacket {
	host, serv, err := getNameInfo(ctx)
	if err != nil {
		return packet.ResponsePacket{Status: "SUCCESS", Message: err.Error()}
	}
	
	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":    host,
			"service": serv,
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}

