package socket

import (
	"os"
    "net"
    "fmt"
	"time"
    "context"
	utls "github.com/refraction-networking/utls"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
)

// performTLSHandshake wraps the TLS upgrade logic
func performTLSHandshake(ctx context.Context, conn net.Conn, addr string, req packet.RequestPacket) (net.Conn, error) {
	utlsConfig, err := buildCustomTLSConfig(req)
	if err != nil {
		return nil, err
	}

	if utlsConfig.ServerName == "" {
		hostOnly, _, _ := net.SplitHostPort(addr)
		utlsConfig.ServerName = hostOnly
	}

	if deadline, ok := ctx.Deadline(); ok {
		if err := conn.SetDeadline(deadline); err != nil {
			return nil, err
		}
		defer conn.SetDeadline(time.Time{}) // Reset deadline
	}

	clientHello := utls.HelloRandomizedNoALPN
	utlsConn := utls.UClient(conn, utlsConfig, clientHello)
	
	if err := utlsConn.Handshake(); err != nil {
		return nil, err
	}

	return utlsConn, nil
}


func handleUpgradeTLS(ctx *ExecutionContext) packet.ResponsePacket {
	if ctls.IsUTLSConn(ctx.Conn) {
		ctx.SaveSession(ctx.Conn)
		return packet.ResponsePacket{Status: "WARN", Message: "Connection is already TLS"}
	}

	if ctx.RawFD == -1 {
    	return packet.ResponsePacket{Status: "S-WARN", Message: "No raw socket (FD) found for upgrade tls."}
	}

	file := os.NewFile(uintptr(ctx.RawFD), fmt.Sprintf("socket_tls_%d", ctx.RawFD))
	rawConn, err := net.FileConn(file)
    file.Close()
    if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "Failed to wrap net.Conn: " + err.Error()}
	}

	tCtx, cancel := context.WithTimeout(context.Background(), ctx.Timeout)
	defer cancel()

	addr, port, err := BuildTarget(ctx.Host, ctx.Req.Port)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "Failed build host & port: " + err.Error()}
	}

	addrStr := DerefString(addr, "")
	portStr := DerefString(port, "")
	host := net.JoinHostPort(addrStr, portStr) 
	
	tlsConn, err := performTLSHandshake(tCtx, rawConn, host, ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "TLS Upgrade failed: " + err.Error()}
	}

	ctx.Conn = tlsConn
	ctx.SaveSession(ctx.Conn)
	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}
