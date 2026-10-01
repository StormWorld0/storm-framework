package socket

import (
	"net"
	"strconv"

	"golang.org/x/sys/unix"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	// Parsing Parameter Node (Host) & Service (Port)
	addr, _ := BuildTarget(ctx.Req)
	host, portStr, err := net.SplitHostPort(addr)
	if err != nil {
		host = addr
		if ctx.Req.Port > 0 {
			portStr = strconv.Itoa(ctx.Req.Port)
		} else {
			portStr = "" // Service bersifat opsional di POSIX getaddrinfo
		}
	}

	// Setup Pointer Node dan Service (getaddrinfo menerima NULL jika string kosong)
	var nodePtr *string
	if host != "" {
		nodePtr = &host
	}

	var servicePtr *string
	if portStr != "" {
		servicePtr = &portStr
	}

	// Construct POSIX Hints Structure
	hints := unix.Addrinfo{
		Family:   int32(ParseAF(ctx.Req.AF)),          // family (AF_INET, AF_INET6, AF_UNSPEC)
		Socktype: int32(ParseSockType(ctx.Req.SType)),  // type (SOCK_STREAM, SOCK_DGRAM)
		Protocol: int32(ParseProtocol(ctx.Req.SProto)),// proto (IPPROTO_TCP, IPPROTO_UDP)
		Flags:    int32(ParseOptName(ctx.Req.Flags)),  // flags (AI_PASSIVE, AI_CANONNAME, dll)
	}

	// Eksekusi POSIX Getaddrinfo langsung ke Kernel/C-Library
	res, err := unix.Getaddrinfo(nodePtr, servicePtr, &hints)
	if err != nil {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "getaddrinfo failed: " + err.Error(),
		}
	}

	// Parse Linked List / Slice Result dari C/Unix
	var results []map[string]interface{}

	// unix.Getaddrinfo di Go x/sys/unix mengembalikan []unix.Addrinfo atau linked list tergantung platform
	// Berikut adalah iterasi parsing atribut dari hasil resolver OS:
	for _, ai := range res {
		var ipStr string
		var portNum int

		// Konversi Sockaddr kembali ke IP & Port String
		if ai.Addr != nil {
			switch sa := ai.Addr.(type) {
			case *unix.SockaddrInet4:
				ipStr = net.IP(sa.Addr[:]).String()
				portNum = sa.Port
			case *unix.SockaddrInet6:
				ipStr = net.IP(sa.Addr[:]).String()
				portNum = sa.Port
			}
		}

		results = append(results, map[string]interface{}{
			"family":   ai.Family,
			"socktype": ai.Socktype,
			"protocol": ai.Protocol,
			"flags":    ai.Flags,
			"ip":       ipStr,
			"port":     portNum,
		})
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":      host,
			"service":   portStr,
			"results":   results,
			"count":     len(results),
			"rtt_ms":    time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}
