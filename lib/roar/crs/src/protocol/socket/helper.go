package socket

import (
	"net"
	"fmt"
	"strconv"
	"golang.org/x/sys/unix"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// Helper internal untuk resolving host/IP ke unix.Sockaddr (menghindari duplikasi)
func resolveSockAddr(req packet.RequestPacket) (unix.Sockaddr, error) {
	addr, port, err := BuildTarget(req)
	if err != nil {
		return nil, fmt.Errorf("Build target failed: %w", err)
	}

	host := DerefString(addr, "")
	portStr := DerefString(port, "")
	
	if portStr == "" {
		portStr = "0"
	}

	Ports, _ := strconv.Atoi(portStr)
	ips, err := net.LookupIP(host)
	if err != nil || len(ips) == 0 {
		return nil, fmt.Errorf("DNS Resolution failed: %s", host)
	}

	afInt := ParseAF(req.AF)
	if afInt == unix.AF_INET6 {
		var addr16 [16]byte
		copy(addr16[:], ips[0].To16())
		return &unix.SockaddrInet6{Port: Ports, Addr: addr16}, nil
	}

	var addr4 [4]byte
	copy(addr4[:], ips[0].To4())
	return &unix.SockaddrInet4{Port: Ports, Addr: addr4}, nil
}
