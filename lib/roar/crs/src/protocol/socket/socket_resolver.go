package socket

import (
	"time"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	r1, c1, e1 := getAddrInfo(ctx)
	if e1 != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: e1.Error()}
	}
	
	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"results": r1,
			"count":   c1,
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}


func handleGetNameInfo(ctx *ExecutionContext) packet.ResponsePacket {
	host, serv, err := getNameInfo(ctx)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: err.Error()}
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

