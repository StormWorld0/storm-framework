package protocol

import (
	h "github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol/http"
)

// Handlers Registry (Map)
var Handlers = map[string]Handler{
	"HTTP_SEND": h.HTTP,
	// "DNS_LOOKUP": DNS,
	// "TCP_CONNECT": TCP,
}
