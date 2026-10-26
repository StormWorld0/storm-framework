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


func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	addr, port, err := BuildTarget(ctx.Req.Host, ctx.Req.Port)
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
	flags := ParseFlags(ctx.Req.Flags)

	var targetPort int

	// Port Resolution (Service) with AI_NUMERICSERV & Dynamic Transport Protocol
	if portFinal != "" {
		if p, err := strconv.Atoi(portFinal); err == nil {
			targetPort = p
		} else {
			// AI_NUMERICSERV evaluation: Abort if input is not a number
			if (flags & aiNumericServ) != 0 {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo: Servname not supported for ai_flags",
				}
			}

			// Define proto lookup based on hint sockType / protocol
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
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo: Name or service not known (AI_NUMERICHOST enforced)",
				}
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
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo failed: " + err.Error(),
				}
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
	    return packet.ResponsePacket{Status:  "ERROR", Message: "getaddrinfo: " + err.Error()}
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


const (
	ni_Numerichost = 0x01 // Don't resolve hostname, return IP as is
	ni_Numericserv = 0x02 // Do not resolve service, return numeric port
	ni_Namereqd    = 0x04 // Error if hostname cannot be resolved
	ni_Dgram       = 0x08 // Use UDP protocol for lookup service (default TCP)
	ni_Nofqdn      = 0x10 // Return only hostname without domain (before first dot)
)

func loadService(path string) (map[int]map[string]string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	result := make(map[int]map[string]string)
	lines := strings.Split(string(data), "\n")

	for _, line := range lines {
		// Hapus komentar dan spasi berlebih.
		if idx := strings.Index(line, "#"); idx != -1 {
			line = line[:idx]
		}
		fields := strings.Fields(line)
		if len(fields) < 2 {
			continue
		}

		serviceName := fields[0]
		portProto := fields[1] // contoh: "80/tcp"

		parts := strings.Split(portProto, "/")
		if len(parts) != 2 {
			continue
		}

		portNum, err := strconv.Atoi(parts[0])
		if err != nil {
			continue
		}

		protocol := parts[1]
		if protocol != "tcp" && protocol != "udp" {
			continue
		}

		if result[portNum] == nil {
			result[portNum] = make(map[string]string)
		}

		if _, exists := result[portNum][protocol]; !exists {
			result[portNum][protocol] = serviceName
		}
	}
	return result, nil
}


func handleGetNameInfo(ctx *ExecutionContext) packet.ResponsePacket {
	addr, port, err := BuildTarget(ctx.Req.Host, ctx.Req.Port)
	if err != nil {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Failed build target: " + err.Error(),
		}
	}

	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")
	flags := ParseFlags(ctx.Req.Flags)
	
	ip := net.ParseIP(hostFinal)
	if ip == nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Invalid IP address."}
	}

	var host string
	var serv string

	// -- Host / Reverse DNS --
	if flags&ni_Numerichost != 0 {
		host = ip.String()
	} else {
		names, err := net.DefaultResolver.LookupAddr(context.Background(), ip.String())
		if err != nil || len(names) == 0 {
			if flags&ni_Namereqd != 0 {
				return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
			}
			// Fallback to IP string if name not found
			host = ip.String()
		} else {
		
		    host = strings.TrimSuffix(names[0], ".")
		    // Extract hostname
		    if flags&ni_Nofqdn != 0 {
			    if idx := strings.Index(host, "."); idx != -1 {
				    host = host[:idx]
			    }
		    }
		}
	}

	// -- Service / Port --
	if flags&ni_Numericserv != 0 {
		serv = portFinal
	} else {
		protocol := "tcp"
		if flags&ni_Dgram != 0 {
			protocol = "udp"
		}

		var serviceMapOnce sync.Once
		var serviceMap map[int]map[string]string
		var serviceErr error
		
		serviceMapOnce.Do(func() {
			serviceMap, serviceErr = loadService("/etc/services")
		})
		if serviceErr != nil {
			serv = portFinal // Fallback to port number
		} 
		
		portNum, _ := strconv.Atoi(portFinal)
		if proto, ok := serviceMap[portNum]; ok {
			if name, ok := proto[protocol]; ok {
				serv = name
			}
		}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":    host,
			"service": serv,
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}

