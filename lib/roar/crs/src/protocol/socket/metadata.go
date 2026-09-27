package socket

import (
	"reflect"
	"strconv"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
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
