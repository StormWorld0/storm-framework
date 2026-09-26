package socket

import (
	"strings"
	"golang.org/x/sys/unix"
)

// ParseAF menerjemahkan string Address Family menjadi konstanta unix (int)
func ParseAF(af string) int {
	switch strings.ToUpper(af) {
	case "AF_INET", "2":
		return unix.AF_INET
	case "AF_INET6", "10":
		return unix.AF_INET6
	case "AF_UNIX", "1":
		return unix.AF_UNIX
	case "AF_UNSPEC", "0":
		return unix.AF_UNSPEC
	default:
		// Default fallback yang wajar untuk arsitektur jaringan saat ini
		return unix.AF_INET 
	}
}

// ParseSockType menerjemahkan string Socket Type menjadi konstanta unix (int)
func ParseSockType(stype string) int {
	switch strings.ToUpper(stype) {
	case "SOCK_STREAM", "1":
		return unix.SOCK_STREAM
	case "SOCK_DGRAM", "2":
		return unix.SOCK_DGRAM
	case "SOCK_RAW", "3":
		return unix.SOCK_RAW
	case "SOCK_SEQPACKET", "5":
		return unix.SOCK_SEQPACKET
	default:
		return unix.SOCK_STREAM // Default fallback
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

