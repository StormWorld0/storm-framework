package socket

import (
	"net"
	"fmt"
	"strconv"
	"golang.org/x/sys/unix"
)

// Helper internal untuk resolving host/IP ke unix.Sockaddr (menghindari duplikasi)
func resolveSockAddr(host, port, af) (unix.Sockaddr, error) {
	addr, p1, err := BuildTarget(host, port)
	if err != nil {
		return nil, fmt.Errorf("Build target failed: %w", err)
	}

	hostStr := DerefString(addr, "")
	portStr := DerefString(p1, "")
	
	if portStr == "" {
		portStr = "0"
	}

	Ports, _ := strconv.Atoi(portStr)
	ips, err := net.LookupIP(hostStr)
	if err != nil || len(ips) == 0 {
		return nil, fmt.Errorf("DNS Resolution failed: %s", hostStr)
	}

	afInt := ParseAF(af)
	if afInt == unix.AF_INET6 {
		var addr16 [16]byte
		copy(addr16[:], ips[0].To16())
		return &unix.SockaddrInet6{Port: Ports, Addr: addr16}, nil
	}

	var addr4 [4]byte
	copy(addr4[:], ips[0].To4())
	return &unix.SockaddrInet4{Port: Ports, Addr: addr4}, nil
}
