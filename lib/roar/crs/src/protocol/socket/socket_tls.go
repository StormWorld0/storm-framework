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

	clientHello := utls.HelloChrome_Auto
	utlsConn := utls.UClient(conn, utlsConfig, clientHello)

	var spec utls.TLSExtension
	if spec, err := utls.UTLSIdToSpec(clientHello); err != nil {
        return nil, err
    }

	var cleanedExtensions []utls.TLSExtension
    for _, ext := range spec.Extensions {
        // Check ALPN extension
        if _, ok := ext.(*utls.ALPNExtension); ok {
            // Skip/remove ALPN extension
            continue
        }
        cleanedExtensions = append(cleanedExtensions, ext)
    }
    spec.Extensions = cleanedExtensions

	if err := utlsConn.ApplyPreset(&spec); err != nil {
        return nil, err
    }
	
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

	if ctx.RawFD != -1 {
    	file := os.NewFile(uintptr(ctx.RawFD), fmt.Sprintf("socket_tls_%d", ctx.RawFD))
	    rawConn, err := net.FileConn(file)
    	file.Close()
    	if err != nil {
		    return packet.ResponsePacket{Status: "S-ERROR", Message: "Failed to wrap net.Conn: " + err.Error()}
	    }
	    ctx.Conn = rawConn
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
	
	tlsConn, err := performTLSHandshake(tCtx, ctx.Conn, host, ctx.Req)
	if err != nil {
		return packet.ResponsePacket{Status: "S-ERROR", Message: "TLS Upgrade failed: " + err.Error()}
	}

	ctx.Conn = tlsConn
	ctx.SaveSession(ctx.Conn)
	return packet.ResponsePacket{Status: "SUCCESS", Data: ctx.GenerateMetadata(0)}
}
