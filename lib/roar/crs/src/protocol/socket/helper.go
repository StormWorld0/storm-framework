package socket

import (
	"net"
	"fmt"
	"unsafe"
	"strconv"
	"strings"
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



func udsToFD(udsPath string) int {
	if !strings.HasPrefix(udsPath, "@") {
		return -1
	}

	// Abstract namespace in Linux begins with a null byte ('\x00')
	addr := &unix.SockaddrUnix{Name: "\x00" + udsPath[1:]}

	fd, err := unix.Socket(unix.AF_UNIX, unix.SOCK_STREAM, 0)
	if err != nil {
		return -1
	}
	defer unix.Close(fd)
	
	unix.Connect(fd, addr)

	fdSize := int(unsafe.Sizeof(int(0)))
	oob := make([]byte, unix.CmsgSpace(fdSize))
	payload := make([]byte, 1)

	var oobn int
	for {
		_, oobn, _, _, err = unix.Recvmsg(fd, payload, oob, unix.MSG_CMSG_CLOEXEC)
		if err == unix.EINTR {
			continue
		}
		break
	}
	if err != nil || oobn == 0 {
		return -1
	}

	msgs, err := unix.ParseSocketControlMessage(oob[:oobn])
	if err != nil {
		return -1
	}

	for _, msg := range msgs {
		if msg.Header.Level != unix.SOL_SOCKET || msg.Header.Type != unix.SCM_RIGHTS {
			continue
		}
		fds, err := unix.ParseSCMRights(&msg)
		if err != nil || len(fds) == 0 {
			return -1
		}
		for _, extra := range fds[1:] {
			_ = unix.Close(extra)
		}
		iFD := fds[0]
		flags, err := unix.FcntlInt(iFD, unix.F_GETFD, 0)
		if err == nil {
			_, _ = unix.FcntlInt(iFD, unix.F_SETFD, flags|unix.FD_CLOEXEC)
		}
		fl, err := unix.FcntlInt(iFD, unix.F_GETFL, 0)
		if err != nil {
			_ = unix.Close(iFD)
			return -1
		}
		if fl&unix.O_NONBLOCK != 0 {
			if _, err := unix.FcntlInt(iFD, unix.F_SETFL, fl&^unix.O_NONBLOCK); err != nil {
				_ = unix.Close(iFD)
				return -1
			}
		}
		return iFD
	}
	return -1
}
