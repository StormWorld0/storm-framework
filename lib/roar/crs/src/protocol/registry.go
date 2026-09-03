package protocol

import (
	h "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/http"
	d "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/dns"
	w "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/whois"
	n "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/network"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

type Handler func(packet.RequestPacket) packet.ResponsePacket

// Handlers Registry (Map)
var Handlers = map[string]Handler{
	"HTTP_SEND":         h.HTTP,
	"DNS_SEND":          d.DNS,
	"WHOIS_SEND":        w.WHOIS,
	"NETWORK_SEND":      n.Network,
}
