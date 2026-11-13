package protocol

import (
	h "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/http"
	d "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/dns"
	w "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/whois"
	s "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/socket"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

type Handler func(packet.RequestPacket) packet.ResponsePacket

// Handlers Registry (Map)
var Handlers = map[string]Handler{
	"HTTP":         h.HTTP,
	"DNS":          d.DNS,
	"WHOIS":        w.WHOIS,
	"SOCKET":       s.Socket,
}
