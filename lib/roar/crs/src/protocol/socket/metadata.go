package socket

import (
	"reflect"
	"strconv"
	"time"
	"net"

	"golang.org/x/sys/unix"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
)

func (ctx *ExecutionContext) GenerateMetadata(readBytes int) map[string]interface{} {
	meta := map[string]interface{}{
		"is_reused":    ctx.IsReused,
		"rtt_ms":       time.Since(ctx.StartTime).Milliseconds(),
		"Cheked":       reflect.TypeOf(ctx.Conn).String(),
		"isAlreadyTLS": strconv.FormatBool(ctls.IsTLSConn(ctx.Conn)),
		"read_bytes":   readBytes,
	}

	if ctx.Conn != nil {
		if addr := ctx.Conn.RemoteAddr(); addr != nil {
			meta["remote_ip"] = addr.String()
		}
		if lAddr := ctx.Conn.LocalAddr(); lAddr != nil {
			meta["local_ip"] = lAddr.String()
		}
	}

	if ctx.Req.InfoTLS {
		meta["info_tls"] = ctls.ExtractTLSInfo(ctx.Conn)
	}

	return meta
}

func (ctx *ExecutionContext) GenerateMetadataFD(fd int, readBytes int) map[string]interface{} {
	meta := map[string]interface{}{
		"is_reused":    ctx.IsReused,
		"rtt_ms":       time.Since(ctx.StartTime).Milliseconds(),
		"Cheked":       "RawSocket",
		"read_bytes":   readBytes,
	}

	// Ambil IP & Port Remote via syscall getpeername(2)
	if remoteAddr, err := unix.Getpeername(fd); err == nil {
		if formatted := formatSockaddr(remoteAddr); formatted != "" {
			meta["remote_ip"] = formatted
		}
	}

	// Ambil IP & Port Local via syscall getsockname(2)
	if localAddr, err := unix.Getsockname(fd); err == nil {
		if formatted := formatSockaddr(localAddr); formatted != "" {
			meta["local_ip"] = formatted
		}
	}

	// Ambil RTT Asli dari Kernel TCP Stack Linux (TCP_INFO)
	if tcpInfo, err := unix.GetsockoptTCPInfo(fd, unix.IPPROTO_TCP, unix.TCP_INFO); err == nil {
		// tcpInfo.Rtt menyimpan nilai Microsecond (µs) dari TCP ACK
		meta["kernel_rtt_ms"] = tcpInfo.Rtt / 1000
	}
	return meta
}

// helper untuk mengonversi unix.Sockaddr ke string IP:Port
func formatSockaddr(sa unix.Sockaddr) string {
	switch v := sa.(type) {
	case *unix.SockaddrInet4:
		ip := net.IP(v.Addr[:])
		return net.JoinHostPort(ip.String(), strconv.Itoa(v.Port))
	case *unix.SockaddrInet6:
		ip := net.IP(v.Addr[:])
		return net.JoinHostPort(ip.String(), strconv.Itoa(v.Port))
	case *unix.SockaddrUnix:
		return v.Name
	}
	return ""
}
