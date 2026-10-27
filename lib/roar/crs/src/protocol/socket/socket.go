package socket

import (
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

type CommandHandler func(ctx *ExecutionContext) packet.ResponsePacket

var handlers = map[string]CommandHandler{
	"socket":      handleSocket,
	"bind":        handleBind,
	"listen":      handleListen,
	"accept":      handleAccept,
	"connect":     handleConnect,
	"create":      handleCreate,
	"fileno":      handleFileno,
	"fileno-clt":  handleFilenoClt,
	"upgrade-tls": handleUpgradeTLS,
	"sendall":     handleSendAll,
	"send":        handleSend,
	"recv":        handleRecv,
	"sendto":      handleSendTo,
	"recvfrom":    handleRecvFrom,
	"setsockopt":  handleSetsockopt,
	"getsockopt":  handleGetSockOpt,
	"getaddrinfo": handleGetAddrInfo,
	"getnameinfo": handleGetNameInfo,
	"getpeername": handleGetPeerName,
	"getsockname": handleGetSockName,
}

// A socket is an entry point for executing a connection using POSIX-like primitive operations.
func Socket(req packet.RequestPacket) packet.ResponsePacket {
	ctx := NewExecutionContext(req)
	defer ctx.Cleanup()

	// Per-Session Locking to Prevent Race Conditions
	if ctx.Req.SessionID != "" {
		mu := utils.GetSessionLock(ctx.Req.SessionID)
		mu.Lock()
		defer mu.Unlock()
	}

	// Session Cleanup Execution
	if ctx.Mode == "close" {
		return ctx.CloseSession()
	}

	// clienFD Cleanup Execution
	if ctx.Mode == "close-cfd" {
		return ctx.CloseCFD()
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
