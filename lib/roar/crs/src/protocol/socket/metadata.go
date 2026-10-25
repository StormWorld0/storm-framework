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

	// Ambil RTT Asli dari Kernel TCP Stack Linux (TCP_INFO)
	if tcpInfo, err := unix.GetsockoptTCPInfo(fd, unix.IPPROTO_TCP, unix.TCP_INFO); err == nil {
		// tcpInfo.Rtt menyimpan nilai Microsecond (µs) dari TCP ACK
		meta["kernel_rtt_ms"] = tcpInfo.Rtt / 1000
	}
	
	return meta
}
