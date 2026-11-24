package socket

import (
	"net"
	"fmt"
	"strconv"
	"golang.org/x/sys/unix"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// Helper for resolving host/IP to unix.Sockaddr
func resolveSockAddr(req packet.RequestPacket) (unix.Sockaddr, error) {
	addr, port, err := BuildTarget(req.Host, req.Port)
	if err != nil {
		return nil, fmt.Errorf("Build target failed: %w", err)
	}

	hostStr := DerefString(addr, "")
	portStr := DerefString(port, "0")
	
	ports, _ := strconv.Atoi(portStr)
	ips, err := net.LookupIP(hostStr)
	if err != nil || len(ips) == 0 {
		return nil, fmt.Errorf("DNS Resolution failed: %s", hostStr)
	}

	afInt := ParseAF(req.AF)
	for _, ip := range ips {
		if afInt == unix.AF_INET6 {
			if ip6 := ip.To16(); ip6 != nil {
				var addr16 [16]byte
				copy(addr16[:], ip6)
				return &unix.SockaddrInet6{Port: ports, Addr: addr16}, nil
			}
		} else {
			if ip4 := ip.To4(); ip4 != nil {
				var addr4 [4]byte
				copy(addr4[:], ip4)
				return &unix.SockaddrInet4{Port: ports, Addr: addr4}, nil
			}
		}
	}
	return nil, fmt.Errorf("no matching IP address found for target family")
}
