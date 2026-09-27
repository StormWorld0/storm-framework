package socket

import (
	"strings"
	"golang.org/x/sys/unix"
)

// ParseAF menerjemahkan string Address Family menjadi konstanta unix (int)
func ParseAF(af int) int {
	switch strings.ToUpper(af) {
	case "AF_INET", 2:
		return unix.AF_INET
	case "AF_INET6", 10:
		return unix.AF_INET6
	case "AF_UNIX", 1:
		return unix.AF_UNIX
	case "AF_UNSPEC", 0:
		return unix.AF_UNSPEC
	default:
		// Default fallback yang wajar untuk arsitektur jaringan saat ini
		return unix.AF_INET 
	}
}

// ParseSockType menerjemahkan string Socket Type menjadi konstanta unix (int)
func ParseSockType(stype string) int {
	switch strings.ToUpper(stype) {
	case "SOCK_STREAM", 1:
		return unix.SOCK_STREAM
	case "SOCK_DGRAM", 2:
		return unix.SOCK_DGRAM
	case "SOCK_RAW", 3:
		return unix.SOCK_RAW
	case "SOCK_SEQPACKET", 5:
		return unix.SOCK_SEQPACKET
	default:
		return unix.SOCK_STREAM // Default fallback SOCK_STREAM
	}
}

// ParseProtocol menerjemahkan string Protocol menjadi konstanta unix (int)
func ParseProtocol(proto string) int {
	switch strings.ToUpper(proto) {
	case "IPPROTO_IP", "0":
		return 0
	case "IPPROTO_ICMP", "1":
		return unix.IPPROTO_ICMP
	case "IPPROTO_TCP", "6":
		return unix.IPPROTO_TCP
	case "IPPROTO_UDP", "17":
		return unix.IPPROTO_UDP
	case "IPPROTO_RAW", "255":
		return unix.IPPROTO_RAW
	default:
		return 0 // Fallback ke IP (OS akan memilih default berdasarkan SockType)
	}
}

func ParseOptLevel(level string) int {
	switch strings.ToUpper(name) {
	case "SOL_SOCKET":
		return unix.SOL_SOCKET
	case "IPPROTO_TCP", "6":
		return unix.IPPROTO_TCP
	case "IPPROTO_IP", "0":
		return unix.IPPROTO_IP
	case "IPPROTO_IPV6":
		return unix.IPPROTO_IPV6
	default:
		return unix.SOL_SOCKET
	}
}

func ParseOptName(name string) int {
	switch strings.ToUpper(name) {
	// SOL
	case "SO_REUSEADDR":
		return unix.SO_REUSEADDR
	case "SO_REUSEPORT":
		return unix.SO_REUSEPORT
	case "SO_KEEPALIVE":
		return unix.SO_KEEPALIVE
	case "SO_BROADCAST":
		return unix.SO_BROADCAST
	case "SO_RCVBUF":
		return unix.SO_RCVBUF
	case "SO_SNDBUF":
		return unix.SO_SNDBUF
	case "SO_RCVTIMEO":
		return unix.SO_RCVTIMEO
	case "SO_SNDTIMEO":
		return unix.SO_SNDTIMEO
	case "SO_LINGER":
		return unix.SO_LINGER
	case "SO_BINDTODEVICE":
		return unix.SO_BINDTODEVICE
	case "SO_ERROR":
		return unix.SO_ERROR
	case "SO_TYPE":
		return unix.SO_TYPE
	case "SO_DONTROUTE":
		return unix.SO_DONTROUTE

	// TCP
	case "TCP_NODELAY":
		return unix.TCP_NODELAY
	case "TCP_MAXSEG":
		return unix.TCP_MAXSEG
	case "TCP_KEEPIDLE":
		return unix.TCP_KEEPIDLE
	case "TCP_KEEPINTVL":
		return unix.TCP_KEEPINTVL
	case "TCP_KEEPCNT":
		return unix.TCP_KEEPCNT
	case "TCP_QUICKACK":
		return unix.TCP_QUICKACK
	case "TCP_FASTOPEN":
		return unix.TCP_FASTOPEN
	case "TCP_CONGESTION":
		return unix.TCP_CONGESTION

	// IPV4
	case "IP_TTL":
		return unix.IP_TTL
	case "IP_TOS":
		return unix.IP_TOS
	case "IP_HDRINCL":
		return unix.IP_HDRINCL
	case "IP_ADD_MEMBERSHIP":
		return unix.IP_ADD_MEMBERSHIP
	case "IP_DROP_MEMBERSHIP":
		return unix.IP_DROP_MEMBERSHIP

	// IPV6
	case "IPV6_V6ONLY":
		return unix.IPV6_V6ONLY
	case "IPV6_UNICAST_HOPS":
		return unix.IPV6_UNICAST_HOPS
	default:
		return unix.SO_REUSEADDR
	}
}
