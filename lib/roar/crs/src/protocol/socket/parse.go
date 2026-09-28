package socket

import (
	"strconv"
	"strings"

	"golang.org/x/sys/unix"
)

// Helper parser utama: Menerima int, float64 (dari JSON), atau string
func parseConstant(input any, lookupMap map[string]int, defaultVal int) int {
	if input == nil {
		return defaultVal
	}

	switch v := input.(type) {
	case int:
		return v // Passthrough kalau pengguna kirim int
	case float64:
		return int(v) // Handling angka dari JSON Unmarshal
	case string:
		clean := strings.ToUpper(strings.TrimSpace(v))
		if clean == "" {
			return defaultVal
		}

		// 1. Cek dari mapping string ("AF_INET")
		if val, exists := lookupMap[clean]; exists {
			return val
		}

		// 2. Cek jika string berupa angka ("2")
		if num, err := strconv.Atoi(clean); err == nil {
			return num
		}
	}

	return defaultVal
}

// --- MAPPING TABLES ---

var afMap = map[string]int{
	"AF_INET":   unix.AF_INET,
	"AF_INET6":  unix.AF_INET6,
	"AF_UNIX":   unix.AF_UNIX,
	"AF_UNSPEC": unix.AF_UNSPEC,
}

var sockTypeMap = map[string]int{
	"SOCK_STREAM":    unix.SOCK_STREAM,
	"SOCK_DGRAM":     unix.SOCK_DGRAM,
	"SOCK_RAW":       unix.SOCK_RAW,
	"SOCK_SEQPACKET": unix.SOCK_SEQPACKET,
}

var protoMap = map[string]int{
	"IPPROTO_IP":   unix.IPPROTO_IP,
	"IPPROTO_ICMP": unix.IPPROTO_ICMP,
	"IPPROTO_TCP":  unix.IPPROTO_TCP,
	"IPPROTO_UDP":  unix.IPPROTO_UDP,
	"IPPROTO_RAW":  unix.IPPROTO_RAW,
	"IPPROTO_IPV6": unix.IPPROTO_IPV6,
}

var optLevelMap = map[string]int{
	"SOL_SOCKET":   unix.SOL_SOCKET,
	"IPPROTO_TCP":  unix.IPPROTO_TCP,
	"IPPROTO_IP":   unix.IPPROTO_IP,
	"IPPROTO_IPV6": unix.IPPROTO_IPV6,
}

var optNameMap = map[string]int{
	// SOL_SOCKET (Level 1)
	"SO_DEBUG":                 unix.SO_DEBUG,
	"SO_REUSEADDR":             unix.SO_REUSEADDR,
	"SO_TYPE":                  unix.SO_TYPE,
	"SO_ERROR":                 unix.SO_ERROR,
	"SO_DONTROUTE":             unix.SO_DONTROUTE,
	"SO_BROADCAST":             unix.SO_BROADCAST,
	"SO_SNDBUF":                unix.SO_SNDBUF,
	"SO_RCVBUF":                unix.SO_RCVBUF,
	"SO_KEEPALIVE":             unix.SO_KEEPALIVE,
	"SO_OOBINLINE":             unix.SO_OOBINLINE,
	"SO_NO_CHECK":              unix.SO_NO_CHECK,
	"SO_PRIORITY":              unix.SO_PRIORITY,
	"SO_LINGER":                unix.SO_LINGER,
	"SO_BSDCOMPAT":             unix.SO_BSDCOMPAT,
	"SO_REUSEPORT":             unix.SO_REUSEPORT,
	"SO_PASSCRED":              unix.SO_PASSCRED,
	"SO_PEERCRED":              unix.SO_PEERCRED,
	"SO_RCVLOWAT":              unix.SO_RCVLOWAT,
	"SO_SNDLOWAT":              unix.SO_SNDLOWAT,
	"SO_RCVTIMEO":              unix.SO_RCVTIMEO,
	"SO_SNDTIMEO":              unix.SO_SNDTIMEO,
	"SO_BINDTODEVICE":          unix.SO_BINDTODEVICE,
	"SO_ATTACH_FILTER":         unix.SO_ATTACH_FILTER,
	"SO_DETACH_FILTER":         unix.SO_DETACH_FILTER,
	"SO_TIMESTAMP":             unix.SO_TIMESTAMP,
	"SO_ACCEPTCONN":            unix.SO_ACCEPTCONN,

	// IPPROTO_TCP (Level 6)
	"TCP_NODELAY":              unix.TCP_NODELAY,
	"TCP_MAXSEG":               unix.TCP_MAXSEG,
	"TCP_CORK":                 unix.TCP_CORK,
	"TCP_KEEPIDLE":             unix.TCP_KEEPIDLE,
	"TCP_KEEPINTVL":            unix.TCP_KEEPINTVL,
	"TCP_KEEPCNT":              unix.TCP_KEEPCNT,
	"TCP_SYNCNT":               unix.TCP_SYNCNT,
	"TCP_LINGER2":              unix.TCP_LINGER2,
	"TCP_DEFER_ACCEPT":         unix.TCP_DEFER_ACCEPT,
	"TCP_WINDOW_CLAMP":         unix.TCP_WINDOW_CLAMP,
	"TCP_INFO":                 unix.TCP_INFO,
	"TCP_QUICKACK":             unix.TCP_QUICKACK,
	"TCP_CONGESTION":           unix.TCP_CONGESTION,
	"TCP_MD5SIG":               unix.TCP_MD5SIG,
	"TCP_THIN_LINEAR_TIMEOUTS": unix.TCP_THIN_LINEAR_TIMEOUTS,
	"TCP_THIN_DUPACK":          unix.TCP_THIN_DUPACK,
	"TCP_USER_TIMEOUT":         unix.TCP_USER_TIMEOUT,
	"TCP_REPAIR":               unix.TCP_REPAIR,
	"TCP_FASTOPEN":             unix.TCP_FASTOPEN,
	"TCP_TIMESTAMP":            unix.TCP_TIMESTAMP,
	"TCP_NOTSENT_LOWAT":        unix.TCP_NOTSENT_LOWAT,

	// IPPROTO_IP (Level 0)
	"IP_TOS":                   unix.IP_TOS,
	"IP_TTL":                   unix.IP_TTL,
	"IP_HDRINCL":               unix.IP_HDRINCL,
	"IP_ADD_MEMBERSHIP":        unix.IP_ADD_MEMBERSHIP,
	"IP_DROP_MEMBERSHIP":       unix.IP_DROP_MEMBERSHIP,

	// IPPROTO_IPV6 (Level 41)
	"IPV6_UNICAST_HOPS":        unix.IPV6_UNICAST_HOPS,
	"IPV6_V6ONLY":              unix.IPV6_V6ONLY,
}


var flagsMap = map[string]int{
	"MSG_DONTWAIT"    unix.MSG_DONTWAIT,
	"MSG_OOB"         unix.MSG_OOB,
	"MSG_MORE"        unix.MSG_MORE,
	"MSG_NOSIGNAL"    unix.MSG_NOSIGNAL,
	"MSG_CONFIRM"     unix.MSG_CONFIRM,
	"MSG_PEEK"        unix.MSG_PEEK,
	"MSG_WAITALL"     unix.MSG_WAITALL,
	"MSG_TRUNC"       unix.MSG_TRUNC,
}

// --- PUBLIC PARSER FUNCTIONS ---

func ParseAF(af any) int {
	return parseConstant(af, afMap, unix.AF_INET)
}

func ParseSockType(stype any) int {
	return parseConstant(stype, sockTypeMap, unix.SOCK_STREAM)
}

func ParseProtocol(proto any) int {
	return parseConstant(proto, protoMap, 0)
}

func ParseOptLevel(level any) int {
	return parseConstant(level, optLevelMap, unix.SOL_SOCKET)
}

func ParseOptName(name any) int {
	return parseConstant(name, optNameMap, unix.SO_REUSEADDR)
}

func ParseFlags(flags any) int {
	return parseConstant(flags, flagsMap, 0)
}
