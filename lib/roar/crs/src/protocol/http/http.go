// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy

package http

import (
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// HTTP mengeksekusi request. Secara dinamis melakukan routing antara
// Standard Engine (retryablehttp) atau Raw Engine (rawhttp).
func HTTP(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()
	
	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 10 * time.Second
	}

	if req.RawMode {
		return ExecuteRaw(req, timeout)
	}

	return ExecuteStandard(req, timeout)
}
