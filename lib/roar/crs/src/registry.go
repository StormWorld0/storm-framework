package main
// Handler adalah signature untuk semua fungsi protokol
type Handler func(RequestPacket) ResponsePacket

// Handlers Registry (Map)
var Handlers = map[string]Handler{
	"HTTP_SEND": HTTP,
	// "DNS_LOOKUP": DNS,
	// "TCP_CONNECT": TCP,
}
