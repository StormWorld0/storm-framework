package network

import (
	"strings"
	"syscall"
)

// ParseAF menerjemahkan string Address Family menjadi konstanta syscall (int)
func ParseAF(af string) int {
	switch strings.ToUpper(af) {
	case "AF_INET":
		return syscall.AF_INET
	case "AF_INET6":
		return syscall.AF_INET6
	case "AF_UNIX":
		return syscall.AF_UNIX
	case "AF_UNSPEC":
		return syscall.AF_UNSPEC
	default:
		// Default fallback yang wajar untuk arsitektur jaringan saat ini
		return syscall.AF_INET 
	}
}

// ParseSockType menerjemahkan string Socket Type menjadi konstanta syscall (int)
func ParseSockType(stype string) int {
	switch strings.ToUpper(stype) {
	case "SOCK_STREAM":
		return syscall.SOCK_STREAM
	case "SOCK_DGRAM":
		return syscall.SOCK_DGRAM
	case "SOCK_RAW":
		return syscall.SOCK_RAW
	case "SOCK_SEQPACKET":
		return syscall.SOCK_SEQPACKET
	default:
		return syscall.SOCK_STREAM // Default fallback
	}
}

// ParseProtocol menerjemahkan string Protocol menjadi konstanta syscall (int)
func ParseProtocol(proto string) int {
	switch strings.ToUpper(proto) {
	case "IPPROTO_IP", "0":
		return 0
	case "IPPROTO_ICMP", "1":
		return syscall.IPPROTO_ICMP
	case "IPPROTO_TCP", "6":
		return syscall.IPPROTO_TCP
	case "IPPROTO_UDP", "17":
		return syscall.IPPROTO_UDP
	case "IPPROTO_RAW", "255":
		return syscall.IPPROTO_RAW
	default:
		return 0 // Fallback ke IP (OS akan memilih default berdasarkan SockType)
	}
}

