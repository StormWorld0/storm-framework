package protocol

import (
	h "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/http"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/internal/packet"
)

type Handler func(packet.RequestPacket) packet.ResponsePacket

// Handlers Registry (Map)
var Handlers = map[string]Handler{
	"HTTP_SEND": h.HTTP,
	// "DNS_LOOKUP": DNS,
	// "TCP_CONNECT": TCP,
}
