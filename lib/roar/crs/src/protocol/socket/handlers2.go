package socket

import (
	"context"
	"net"
	"strconv"
	"time"

	"golang.org/x/sys/unix"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

const (
	aiPassive     = 0x01 // AI_PASSIVE
	aiCanonName   = 0x02 // AI_CANONNAME
	aiNumericHost = 0x04 // AI_NUMERICHOST
	aiNumericServ = 0x08 // AI_NUMERICSERV
)

type addrResult struct {
	SockType int
	Protocol int
}

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	addr, port, err := BuildTarget(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Failed build target: " + err.Error(),
		}
	}

	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")

	family := ParseAF(ctx.Req.AF)
	sockType := ParseSockType(ctx.Req.SType)
	protocol := ParseProtocol(ctx.Req.SProto)
	flags := ParseOptName(ctx.Req.Flags)

	var targetPort int

	// 1. Resolusi Port (Service) dengan AI_NUMERICSERV & Dynamic Transport Protocol
	if portFinal != "" {
		if p, err := strconv.Atoi(portFinal); err == nil {
			targetPort = p
		} else {
			// Evaluasi AI_NUMERICSERV: Abort jika input bukan angka
			if (flags & aiNumericServ) != 0 {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo: Servname not supported for ai_flags",
				}
			}

			// Tentukan proto lookup berdasarkan hint sockType / protocol
			lookupProto := "tcp"
			if sockType == unix.SOCK_DGRAM || protocol == unix.IPPROTO_UDP {
				lookupProto = "udp"
			}

			if p, err := net.LookupPort(lookupProto, portFinal); err == nil {
				targetPort = p
			} else {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "Servname not supported for ai_socktype",
				}
			}
		}
	}

	// 2. Resolusi Host dengan Optimasi Network Query (Mencegah Unnecessary DNS Noise)
	var ips []net.IP
	var canonName string

	if hostFinal == "" {
		if (flags & aiPassive) != 0 {
			ips = append(ips, net.ParseIP("0.0.0.0"), net.ParseIP("::"))
		} else {
			ips = append(ips, net.ParseIP("127.0.0.1"), net.ParseIP("::1"))
		}
	} else {
		parsedIP := net.ParseIP(hostFinal)
		if parsedIP != nil {
			ips = append(ips, parsedIP)
		} else {
			if (flags & aiNumericHost) != 0 {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo: Name or service not known (AI_NUMERICHOST enforced)",
				}
			}

			// Tentukan scope network resolver berdasarkan AF hint
			// Menghindari DNS AAAA query jika caller hanya butuh IPv4 (AF_INET)
			lookupNetwork := "ip"
			switch family {
			case unix.AF_INET:
				lookupNetwork = "ip4"
			case unix.AF_INET6:
				lookupNetwork = "ip6"
			}

			resolvedIPs, err := net.DefaultResolver.LookupIP(context.Background(), lookupNetwork, hostFinal)
			if err != nil {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo failed: " + err.Error(),
				}
			}
			ips = resolvedIPs

			// Evaluasi AI_CANONNAME
			if (flags & aiCanonName) != 0 {
				if cname, err := net.DefaultResolver.LookupCNAME(context.Background(), hostFinal); err == nil {
					canonName = cname
				}
			}
		}
	}

	// 3. Matriks Inferensi SockType & Protocol
	// POSIX getaddrinfo mengisi concreted socktype & protocol jika hints bernilai 0
	var combinations []addrResult

	switch {
	case sockType == 0 && protocol == 0:
		combinations = append(combinations,
			addrResult{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP},
			addrResult{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP},
		)
	case sockType == unix.SOCK_STREAM && protocol == 0:
		combinations = append(combinations, addrResult{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP})
	case sockType == unix.SOCK_DGRAM && protocol == 0:
		combinations = append(combinations, addrResult{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP})
	case sockType == 0 && protocol == unix.IPPROTO_TCP:
		combinations = append(combinations, addrResult{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP})
	case sockType == 0 && protocol == unix.IPPROTO_UDP:
		combinations = append(combinations, addrResult{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP})
	default:
		combinations = append(combinations, addrResult{SockType: int(sockType), Protocol: int(protocol)})
	}

	// 4. Construct Multi-tuple Results
	var results []map[string]interface{}

	for _, ip := range ips {
		isIPv4 := ip.To4() != nil

		if family == unix.AF_INET && !isIPv4 {
			continue
		}
		if family == unix.AF_INET6 && isIPv4 {
			continue
		}

		resFamily := unix.AF_INET
		if !isIPv4 {
			resFamily = unix.AF_INET6
		}

		for _, combo := range combinations {
			resItem := map[string]interface{}{
				"family":   int(resFamily),
				"socktype": combo.SockType,
				"protocol": combo.Protocol,
				"flags":    int(flags),
				"ip":       ip.String(),
				"port":     targetPort,
			}
			if canonName != "" {
				resItem["canonname"] = canonName
			}
			results = append(results, resItem)
		}
	}

	if len(results) == 0 && hostFinal != "" {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "getaddrinfo: No address associated with hostname",
		}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":    hostFinal,
			"service": portFinal,
			"results": results,
			"count":   len(results),
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}
