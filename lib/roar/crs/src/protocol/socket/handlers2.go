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
	aiPassive     = 0x01 // AI_PASSIVE: bind to 0.0.0.0 / ::
	aiNumericHost = 0x04 // AI_NUMERICHOST: prevent DNS lookup if domain
)

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	// BuildTarget bisa mereturn (host, nil, nil)
	addr, port, err := BuildTarget(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Failed build target: " + err.Error(),
		}
	}

	// Aman: fallback ke string kosong ("") jika nil
	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")

	// 4 argumen ini langsung diekstrak.
	// Jika kosong, Parse* otomatis me-return 0. Kita percaya penuh pada parser.
	family := ParseAF(ctx.Req.AF)
	sockType := ParseSockType(ctx.Req.SType)
	protocol := ParseProtocol(ctx.Req.SProto)
	flags := ParseOptName(ctx.Req.Flags)

	var results []map[string]interface{}
	var targetPort int

	// 1. Resolusi Port (Service)
	// Hanya diproses jika portFinal ada isinya. Jika tidak, targetPort tetap 0.
	if portFinal != "" {
		// Coba ubah string angka (cth: "8080") langsung ke integer
		if p, err := strconv.Atoi(portFinal); err == nil {
			targetPort = p
		} else {
			// Fallback: Jika input berupa nama service (cth: "http" atau "ssh")
			// Kita gunakan "tcp" sebagai standar lookup ke /etc/services
			if p, err := net.LookupPort("tcp", portFinal); err == nil {
				targetPort = p
			} else {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "Servname not supported",
				}
			}
		}
	}

	// 2. Resolusi Host (Node)
	var ips []net.IP

	if hostFinal == "" {
		// Evaluasi flag AI_PASSIVE (0x1) jika node kosong
		if (flags & aiPassive) != 0 {
			ips = append(ips, net.ParseIP("0.0.0.0"), net.ParseIP("::"))
		} else {
			ips = append(ips, net.ParseIP("127.0.0.1"), net.ParseIP("::1"))
		}
	} else {
		parsedIP := net.ParseIP(hostFinal)
		if parsedIP != nil {
			// Input adalah Raw IP Address (IPv4/IPv6)
			ips = append(ips, parsedIP)
		} else {
			// Evaluasi flag AI_NUMERICHOST (0x4)
			// Jika flag ini di-set tapi input berupa domain, fungsi harus abort
			// untuk mencegah DNS leakage pada agen Red Team
			if (flags & aiNumericHost) != 0 {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo: Name or service not known (AI_NUMERICHOST enforced)",
				}
			}

			// Jalankan DNS Lookup
			resolvedIPs, err := net.DefaultResolver.LookupIP(context.Background(), "ip", hostFinal)
			if err != nil {
				return packet.ResponsePacket{
					Status:  "ERROR",
					Message: "getaddrinfo failed: " + err.Error(),
				}
			}
			ips = resolvedIPs
		}
	}

	// 3. Construct Results (Mem-filter berdasarkan AF_INET / AF_INET6 jika diminta)
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

		results = append(results, map[string]interface{}{
			"family":   int(resFamily),
			"socktype": int(sockType),
			"protocol": int(protocol),
			"flags":    int(flags),
			"ip":       ip.String(),
			"port":     targetPort,
		})
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
