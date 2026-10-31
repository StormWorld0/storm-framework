package socket

import (
	"os"
	"net"
	"fmt"
	"time"
	"sync"
	"context"
	"strconv"
	"strings"
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

func resolveCanonicalName(ctx context.Context, host string, flags int) string {
	if flags&aiCanonName == 0 {
		return ""
	}
	cname, err := net.DefaultResolver.LookupCNAME(ctx, host)
	if err != nil {
		return ""
	}
	return cname
}

func resolveAddrCombination(sockType, protocol int) ([]addrResult, error) {
	switch {
	case sockType == 0 && protocol == 0:
		return []addrResult{
			{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP},
			{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP},
		}, nil

	case sockType == unix.SOCK_STREAM && protocol == 0:
		return []addrResult{
			{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP},
		}, nil

	case sockType == unix.SOCK_DGRAM && protocol == 0:
		return []addrResult{
			{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP},
		}, nil

	case sockType == 0 && protocol == unix.IPPROTO_TCP:
		return []addrResult{
			{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP},
		}, nil

	case sockType == 0 && protocol == unix.IPPROTO_UDP:
		return []addrResult{
			{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP},
		}, nil

	case sockType == unix.SOCK_STREAM && protocol == unix.IPPROTO_TCP:
		return []addrResult{
			{SockType: unix.SOCK_STREAM, Protocol: unix.IPPROTO_TCP},
		}, nil

	case sockType == unix.SOCK_DGRAM && protocol == unix.IPPROTO_UDP:
		return []addrResult{
			{SockType: unix.SOCK_DGRAM, Protocol: unix.IPPROTO_UDP},
		}, nil

	default:
		return nil, fmt.Errorf("incompatible type & proto: socktype=%d protocol=%d", sockType, protocol)
	}
}

func GetAddrInfo(ctx *ExecutionContext) (str, str, str, int, error) {
	addr, port, err := BuildTarget(ctx.Req.Host, ctx.Req.Port)
	if err != nil {
		return nil, nil, nil, nil, fmt.Errorf("Failed build target: %s", err)
	}

	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")

	family := ParseAF(ctx.Req.AF)
	sockType := ParseSockType(ctx.Req.SType)
	protocol := ParseProtocol(ctx.Req.SProto)
	flags := ParseFlags(ctx.Req.Flags)

	var targetPort int

	// Port Resolution (Service) with AI_NUMERICSERV & Dynamic Transport Protocol
	if portFinal != "" {
		if p, err := strconv.Atoi(portFinal); err == nil {
			targetPort = p
		} else {
			// AI_NUMERICSERV evaluation: Abort if input is not a number
			if (flags & aiNumericServ) != 0 {
				return nil, nil, nil, nil, fmt.Errorf("getaddrinfo: Servname not supported for ai_flags")
			}

			// Define proto lookup based on hint sockType / protocol
			lookupProto := "tcp"
			if sockType == unix.SOCK_DGRAM || protocol == unix.IPPROTO_UDP {
				lookupProto = "udp"
			}

			if p, err := net.LookupPort(lookupProto, portFinal); err == nil {
				targetPort = p
			} else {
				return nil, nil, nil, nil, fmt.Errorf("Servname not supported for ai_socktype")
			}
		}
	}

	// Host Resolution with Network Query Optimization (Preventing Unnecessary DNS Noise)
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
				return nil, nil, nil, nil, fmt.Errorf("getaddrinfo: Name or service not known (AI_NUMERICHOST enforced)")
			}

			// Determine the scope of the network resolver based on the AF hint
			// Avoid DNS AAAA queries if the caller only needs IPv4 (AF_INET)
			lookupNetwork := "ip"
			switch family {
			case unix.AF_INET:
				lookupNetwork = "ip4"
			case unix.AF_INET6:
				lookupNetwork = "ip6"
			}

			resolvedIPs, err := net.DefaultResolver.LookupIP(context.Background(), lookupNetwork, hostFinal)
			if err != nil {
				return nil, nil, nil, nil, fmt.Errorf("getaddrinfo failed: %s", err)
			}
			ips = resolvedIPs

			// AI_CANONNAME Evaluation
			if hostFinal != "" && flags&aiCanonName != 0 {
				canonName = resolveCanonicalName(context.Background(), hostFinal, int(flags))
            }
		}
	}

	// SockType & Protocol Inference Matrix
	// POSIX getaddrinfo fills in concreted socktype & protocol if hints is 0
	combinations, err := resolveAddrCombination(int(sockType), int(protocol))
    if err != nil {
	    return nil, nil, nil, nil, fmt.Errorf("getaddrinfo: %s", err)
    }

	// Construct Multi-tuple Results
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
        return nil, nil, nil, nil, fmt.Errorf("getaddrinfo: No address associated with hostname.")
	}

    return hostFinal, portFinal, results, len(results), nil
}
