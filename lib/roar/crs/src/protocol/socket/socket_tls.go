package socket

import (
    "net"
    "fmt"
    "context"
    "crypto/tls"
    "github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
)

// performTLSHandshake membungkus logika upgrade TLS
func performTLSHandshake(ctx context.Context, conn net.Conn, addr string, req packet.RequestPacket) (net.Conn, error) {
	tlsConfig, err := buildCustomTLSConfig(req)
	if err != nil {
		return nil, fmt.Errorf("TLS Config Error: %w", err)
	}

	if tlsConfig.ServerName == "" {
		hostOnly, _, _ := net.SplitHostPort(addr)
		tlsConfig.ServerName = hostOnly
	}

	tlsConn := tls.Client(conn, tlsConfig)
	if err := tlsConn.HandshakeContext(ctx); err != nil {
		return nil, fmt.Errorf("handshake failed: %w", err)
	}

	return tlsConn, nil
}


func handleUpgradeTLS(ctx *ExecutionContext) packet.ResponsePacket {
	if ctls.IsTLSConn(ctx.Conn) {
		ctx.SaveSession(ctx.Conn)
		return packet.ResponsePacket{Status: "ERROR", Message: "Connection is already TLS"}
	}

	tCtx, cancel := context.WithTimeout(context.Background(), ctx.Timeout)
	defer cancel()

	addr, port, err := BuildTarget(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Failed build host & port: " + err.Error()}
	}

	addrStr := DerefString(addr, "")
	portStr := DerefString(port, "")
	host := net.JoinHostPort(addrStr, portStr) 
	
	tlsConn, err := performTLSHandshake(tCtx, ctx.Conn, host, ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "TLS Upgrade failed: " + err.Error()}
	}

	ctx.Conn = tlsConn
	ctx.SaveSession(ctx.Conn)

	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}
