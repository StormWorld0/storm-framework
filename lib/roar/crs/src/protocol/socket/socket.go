package socket

import (
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

type CommandHandler func(ctx *ExecutionContext) packet.ResponsePacket

var handlers = map[string]CommandHandler{
	"socket":      handleSocket,
	"setsockopt":  handleSetsockopt,
	"bind":        handleBind,
	"listen":      handleListen,
	"accept":      handleAccept,
	"connect":     handleConnect,
	"create":      handleCreate,
	"upgrade_tls": handleUpgradeTLS,
	"send":        handleSend,
	"recv":        handleRecv,
}

// Socket adalah entry point eksekusi koneksi menggunakan POSIX-like primitive operations.
func Socket(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()

	ctx := NewExecutionContext(req)
	defer ctx.Cleanup()

	// Locking Per-Session untuk Mencegah Race Condition
	if ctx.Req.SessionID != "" {
		mu := utils.GetSessionLock(ctx.Req.SessionID)
		mu.Lock()
		defer mu.Unlock()
	}

	// Eksekusi Pembersihan Sesi
	if ctx.Mode == "close" {
		return ctx.CloseSession()
	}

	// Load Active Session Data
	if err := ctx.LoadSessionState(); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
	}

	// Dispatcher Router
	handler, exists := handlers[ctx.Mode]
	if !exists {
		return packet.ResponsePacket{Status: "ERROR", Message: "Unknown socket primitive: " + ctx.Mode}
	}

	return handler(ctx)
}
