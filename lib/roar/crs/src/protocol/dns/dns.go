// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package dns

import (
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// Entry point DNS yang menentukan eksekusi
func DNS(req packet.RequestPacket) packet.ResponsePacket {
	switch req.Mode {
	case DNSLookup:
		return Lookup(req)
	case DNSDiscovery:
		return Discovery(req)
	default:
		// Fallback guard
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Invalid routing condition",
		}
	}
}
