package protocol

import (
	h "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/http"
	d "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/dns"
	n "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/network"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

type Handler func(packet.RequestPacket) packet.ResponsePacket

// Handlers Registry (Map)
var Handlers = map[string]Handler{
	"HTTP_SEND": h.HTTP,
	"DNS_SEND": d.DNS,
	"NETWORK_SEND": n.NETWORK,
}
