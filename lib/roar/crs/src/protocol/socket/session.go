package socket

import (
	"fmt"
	"net"
	"strings"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
	"golang.org/x/sys/unix"
)

type ExecutionContext struct {
	Req         packet.RequestPacket
	Mode        string
	Timeout     time.Duration
	StartTime   time.Time
	Conn        net.Conn
	RawFD       int
	IsReused    bool
	KeepSession bool
}

func NewSessionContext(req packet.RequestPacket) *ExecutionContext {
	timeout := 5 * time.Second
	if req.Timeout > 0 {
		timeout = time.Duration(req.Timeout * float64(time.Second))
	}

	mode := strings.ToLower(req.Mode)
	if mode == "" {
		mode = "socket"
	}

	return &ExecutionContext{
		Req:       req,
		Mode:      mode,
		Timeout:   timeout,
		StartTime: time.Now(),
		RawFD:     -1,
	}
}

func (ctx *ExecutionContext) LoadSessionState() error {
	if ctx.Req.SessionID == "" {
		return nil
	}
	val, ok := utils.ActiveSessions.Load(ctx.Req.SessionID)
	if !ok {
		return nil
	}

	switch v := val.(type) {
	case net.Conn:
		ctx.Conn = v
		ctx.IsReused = true
	case int:
		ctx.RawFD = v
	default:
		return fmt.Errorf("corrupted session data")
	}
	return nil
}

func (ctx *ExecutionContext) SaveSession(val interface{}) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		utils.ActiveSessions.Store(ctx.Req.SessionID, val)
		ctx.KeepSession = true
	}
}

func (ctx *ExecutionContext) CloseSession() packet.ResponsePacket {
	if ctx.Req.SessionID != "" && ctx.Req.CloseSess {
		if _, ok := utils.ActiveSessions.LoadAndDelete(ctx.Req.SessionID); ok {
			if ctx.Conn != nil {
				ctx.Conn.Close()
			}
			if ctx.RawFD != -1 {
				unix.Close(ctx.RawFD)
			}
			return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
		}
		return packet.ResponsePacket{Status: "WARN", Message: "No active session found to close"}
	}
	return packet.ResponsePacket{Status: "WARN", Message: "Incomplete data to close the connection"}
}

func (ctx *ExecutionContext) Cleanup() {
	if !ctx.KeepSession {
		if ctx.Conn != nil {
			ctx.Conn.Close()
		} else if ctx.RawFD != -1 {
			unix.Close(ctx.RawFD)
		}
		if ctx.Req.SessionID != "" {
			utils.ActiveSessions.Delete(ctx.Req.SessionID)
		}
	}
}
