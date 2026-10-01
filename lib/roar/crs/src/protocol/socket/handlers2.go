package socket

/*
// Header file C yang wajib dilampirkan untuk mengakses POSIX dan manajemen memori C.
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdlib.h>
#include <string.h>
*/
import "C"

import (
	"strconv"
	"time"
	"unsafe"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	// 1. Parsing Parameter dari Request
	addr, port, err := BuildTarget(ctx.Req)
	if err != nil {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Failed build host&port: " + err.Error(),
		}
	}

	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")

	// 2. Persiapan C-String (Pointer memori C)
	// getaddrinfo menerima NULL jika parameter tidak diisi.
	var cHost, cService *C.char
	if hostFinal != "" {
		cHost = C.CString(hostFinal)
		defer C.free(unsafe.Pointer(cHost)) // Wajib: Hapus dari RAM setelah fungsi selesai
	}
	if portFinal != "" {
		cService = C.CString(portFinal)
		defer C.free(unsafe.Pointer(cService)) // Wajib: Hapus dari RAM setelah fungsi selesai
	}

	// 3. Setup Struct Hints (POSIX) di memori C
	var hints C.struct_addrinfo
	// Wajib: Zero-value initialization untuk mencegah undefined behavior di C
	C.memset(unsafe.Pointer(&hints), 0, C.sizeof_struct_addrinfo) 
	
	hints.ai_family = C.int(ParseAF(ctx.Req.AF))
	hints.ai_socktype = C.int(ParseSockType(ctx.Req.SType))
	hints.ai_protocol = C.int(ParseProtocol(ctx.Req.SProto))
	hints.ai_flags = C.int(ParseOptName(ctx.Req.Flags))

	// 4. Eksekusi POSIX getaddrinfo (Akses 6 Argumen Penuh)
	var res *C.struct_addrinfo
	errCode := C.getaddrinfo(cHost, cService, &hints, &res)
	if errCode != 0 {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "getaddrinfo failed: " + C.GoString(C.gai_strerror(errCode)),
		}
	}

	// WAJIB: Membebaskan linked-list dari RAM setelah parsing selesai agar tidak Memory Leak
	defer C.freeaddrinfo(res)

	// 5. Parsing Linked-List Result dari C ke Slice Map Go
	var results []map[string]interface{}

	for ptr := res; ptr != nil; ptr = ptr.ai_next {
		var ipStr string
		var portNum int

		// Buffer statis untuk menyimpan string IP dan Port hasil terjemahan C
		var hostBuf [C.NI_MAXHOST]C.char
		var servBuf [C.NI_MAXSERV]C.char

		// Gunakan getnameinfo (POSIX) untuk mengekstrak raw IP bytes menjadi String
		// Casting C.socklen_t dan C.int ini yang memastikan CGO lolos kompilasi tanpa error
		getnameErr := C.getnameinfo(
			ptr.ai_addr,
			ptr.ai_addrlen,
			&hostBuf[0],
			C.socklen_t(C.NI_MAXHOST), 
			&servBuf[0],
			C.socklen_t(C.NI_MAXSERV),
			C.int(C.NI_NUMERICHOST|C.NI_NUMERICSERV),
		)

		// Jika berhasil di-parse, konversi C-String menjadi Go-String
		if getnameErr == 0 {
			ipStr = C.GoString(&hostBuf[0])
			portStr := C.GoString(&servBuf[0])
			portNum, _ = strconv.Atoi(portStr)
		}

		results = append(results, map[string]interface{}{
			"family":   int(ptr.ai_family),
			"socktype": int(ptr.ai_socktype),
			"protocol": int(ptr.ai_protocol),
			"flags":    int(ptr.ai_flags),
			"ip":       ipStr,
			"port":     portNum,
		})
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
