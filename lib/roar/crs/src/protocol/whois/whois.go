// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package whois

import (
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// Entry point DNS yang menentukan eksekusi
func WHOIS(req packet.RequestPacket) packet.ResponsePacket {
	switch req.Mode {
	case "WhoisIP":
		return WhoisIP(req)
	default:
		// Fallback guard
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Invalid routing condition",
		}
	}
}
