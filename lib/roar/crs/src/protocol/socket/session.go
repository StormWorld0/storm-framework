package socket

import (
	"fmt"
	"net"
	"time"
	"strings"
	"golang.org/x/sys/unix"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

type ExecutionContext struct {
	Req         packet.RequestPacket
	Host        *string
	Mode        string
	Timeout     time.Duration
	StartTime   time.Time
	Conn        net.Conn
	RawFD       int
	CFD         int
	IsReused    bool
	KeepSession bool
}

type ClientSessionKey struct {
	SessionID string
	FD        int
}

func NewExecutionContext(req packet.RequestPacket) *ExecutionContext {
	timeout := 0 * time.Second
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
		CFD:       -1,
	}
}

func (ctx *ExecutionContext) LoadSessionState() error {
	if ctx.Req.SessionID == "" {
		return nil
	}

	if ctx.Req.CltFD >= 0 {
	    key := ClientSessionKey{
		    SessionID: ctx.Req.SessionID,
		    FD:        ctx.Req.CltFD,
	    }
	    if _, ok := utils.ClientFD.Load(key); ok {
	    	ctx.CFD = ctx.Req.CltFD
	    }
    }


	if hostVal, ok := utils.SessionHosts.Load(ctx.Req.SessionID); ok {
		switch h := hostVal.(type) {
		case *string:
			ctx.Host = h
		case string:
			ctx.Host = &h
		}
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
		ctx.IsReused = true
	default:
		return fmt.Errorf("corrupted session data")
	}
	return nil
}

// Save the ClientFD taken from the accept lintener
func (ctx *ExecutionContext) SaveSessionCFD(val int) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		key := ClientSessionKey{
			SessionID: ctx.Req.SessionID,
			FD:        val,
		}
		utils.ClientFD.Store(key, true)
		ctx.KeepSession = true
	}
}

// Save Host taken from Connect
func (ctx *ExecutionContext) SaveSessionHost(host *string) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		utils.SessionHosts.Store(ctx.Req.SessionID, host)
	}
}

// Saving RawFD & net.Conn
func (ctx *ExecutionContext) SaveSession(val interface{}) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		utils.ActiveSessions.Store(ctx.Req.SessionID, val)
		ctx.KeepSession = true
	}
}

// Close Session The socket's Close mode
func (ctx *ExecutionContext) CloseSession() packet.ResponsePacket {
	if ctx.Req.SessionID != "" && ctx.Req.CloseSess {
		utils.SessionHosts.Delete(ctx.Req.SessionID) // Delete host
		utils.SessionLocks.Delete(ctx.Req.SessionID) // Delete SessionLock

		// Delete Client's Descriptor File
	    sessID := ctx.Req.SessionID
		utils.ClientFD.Range(func(k, _ any) bool {
			if key, ok := k.(ClientSessionKey); ok && key.SessionID == sessID {
				if _, loaded := utils.ClientFD.LoadAndDelete(key); loaded && key.FD >= 0 {
					unix.Close(key.FD)
				}
			}
			return true
		})
		if val, ok := utils.ActiveSessions.LoadAndDelete(ctx.Req.SessionID); ok {
			switch v := val.(type) {
			case net.Conn:    //
				v.Close()     // Close if data type net.Conn
			case int:         //
				unix.Close(v) // Close if raw FD data type
			}
			return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
		}
		return packet.ResponsePacket{Status: "WARN", Message: "No active session found to close"}
	}
	return packet.ResponsePacket{Status: "WARN", Message: "Incomplete data to close the connection"}
}

// Close ClientFD Accept Listener's Close mode
func (ctx *ExecutionContext) CloseCFD() packet.ResponsePacket {
	ctx.KeepSession = true
	if ctx.Req.SessionID == "" || ctx.Req.CltFD < 0 {
		return packet.ResponsePacket{Status: "WARN", Message: "Incomplete data to close the ClientFD"}
	}
	key := ClientSessionKey{
		SessionID: ctx.Req.SessionID,
		FD:        ctx.Req.CltFD,
	}
	if _, ok := utils.ClientFD.LoadAndDelete(key); ok {
		if err := unix.Close(ctx.Req.CltFD); err != nil {
			return packet.ResponsePacket{Status: "S-ERROR", Message: "Failed to close ClientFD: " + err.Error()}
		}
		return packet.ResponsePacket{Status: "SUCCESS", Message: "ClientFD closed"}
	}
	return packet.ResponsePacket{Status: "WARN", Message: "No active ClientFD found to close"}
}


// Emergency run by defer
func (ctx *ExecutionContext) Cleanup() {
	if !ctx.KeepSession {
		if ctx.Conn != nil {
			ctx.Conn.Close()         // Close net.Conn
		}
		if ctx.RawFD != -1 {
			unix.Close(ctx.RawFD)    // Closed RawFD
		}
		if ctx.Req.SessionID != "" {
			sessID := ctx.Req.SessionID
			utils.ClientFD.Range(func(k, _ any) bool {
				if key, ok := k.(ClientSessionKey); ok && key.SessionID == sessID {
					if _, loaded := utils.ClientFD.LoadAndDelete(key); loaded && key.FD >= 0 {
						unix.Close(key.FD) // Closed ClienFD
					}
				}
				return true
			})
			utils.ActiveSessions.Delete(ctx.Req.SessionID) // Delete Active Session
			utils.SessionHosts.Delete(ctx.Req.SessionID)   // Delete Host
			utils.SessionLocks.Delete(ctx.Req.SessionID)   // Delete SessionsLock
		}
	}
}
