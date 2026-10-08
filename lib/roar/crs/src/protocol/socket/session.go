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
	Host        string
	Mode        string
	Timeout     time.Duration
	StartTime   time.Time
	Conn        net.Conn
	RawFD       int
	CFD         int
	IsReused    bool
	KeepSession bool
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

	if v, ok := utils.ClientFD.Load(ctx.Req.SessionID); ok {
		ctx.CFD = v.(int) // Load client FD jika ada
	}

	if hostVal, ok := utils.SessionHosts.Load(ctx.Req.SessionID); ok {
		ctx.Host = hostVal.(string) // Aman karena map ini isinya pasti string
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

// Menyimpan ClienFD yang di ambil dari accept lintener
func (ctx *ExecutionContext) SaveSessionCFD(val int) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		utils.SessionHosts.Store(ctx.Req.SessionID, val)
		ctx.CFD = val // Update state di context
	}
}

// Menyimpan Host yang di ambil dari Connect
func (ctx *ExecutionContext) SaveSessionHost(host string) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		utils.SessionHosts.Store(ctx.Req.SessionID, host)
		ctx.Host = host // Update state di context
	}
}

// Menyimpan RawFD & net.Conn
func (ctx *ExecutionContext) SaveSession(val interface{}) {
	if ctx.Req.SessionID != "" && ctx.Req.KeepAlive {
		utils.ActiveSessions.Store(ctx.Req.SessionID, val)
		ctx.KeepSession = true
	}
}

// Close Session Mode Close milik socket
func (ctx *ExecutionContext) CloseSession() packet.ResponsePacket {
	if ctx.Req.SessionID != "" && ctx.Req.CloseSess {
		utils.ClientFD.Delete(ctx.Req.SessionID)     // Delete Client's Descriptor File
		utils.SessionHosts.Delete(ctx.Req.SessionID) // Delete host
		
		if val, ok := utils.ActiveSessions.LoadAndDelete(ctx.Req.SessionID); ok {
			switch v := val.(type) {
			case net.Conn:
				v.Close() // Tutup jika tipe data net.Conn
			case int:
				unix.Close(v) // Tutup jika tipe data raw FD
			}
			return packet.ResponsePacket{Status: "SUCCESS", Message: "Session closed"}
		}
		return packet.ResponsePacket{Status: "WARN", Message: "No active session found to close"}
	}
	return packet.ResponsePacket{Status: "WARN", Message: "Incomplete data to close the connection"}
}

// Close ClienFD Mode Close milik Accept Listener
func (ctx *ExecutionContext) CloseCFD() packet.ResponsePacket {
	if ctx.Req.SessionID != "" {
		if val, ok := utils.ClientFD.LoadAndDelete(ctx.Req.SessionID); ok {
			unix.Close(val)
			return packet.ResponsePacket{Status: "SUCCESS", Message: "ClienFD closed"}
		}
		return packet.ResponsePacket{Status: "WARN", Message: "No active ClientFD found to close"}
	}
	return packet.ResponsePacket{Status: "WARN", Message: "Incomplete data to close the ClientFD"}
}

// Darurat di jalankan oleh defer
func (ctx *ExecutionContext) Cleanup() {
	if !ctx.KeepSession {
		if ctx.Conn != nil {
			ctx.Conn.Close()         // Tutup net.Conn
		} else if ctx.RawFD != -1 {
			unix.Close(ctx.RawFD)    // Tutup RawFD
		}
		if ctx.CFD != -1 {
			unix.Close(ctx.CFD)      // Tutup ClienFD
		}
		if ctx.Req.SessionID != "" {
			utils.ActiveSessions.Delete(ctx.Req.SessionID) // Hapus Session Aktif
			utils.SessionHosts.Delete(ctx.Req.SessionID)   // Hapus Host
			utils.ClientFD.Delete(ctx.Req.SessionID)       // Hapus ClienFD
		}
	}
}
