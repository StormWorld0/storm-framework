package socket

/*
#cgo LDFLAGS:
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdlib.h>
#include <netinet/in.h>

int parse_sockaddr(struct sockaddr *sa, char *ip_str, int ip_len, int *port, uint32_t *flowinfo, uint32_t *scope_id) {
    if (sa->sa_family == AF_INET) {
        struct sockaddr_in *sin = (struct sockaddr_in *)sa;
        inet_ntop(AF_INET, &(sin->sin_addr), ip_str, ip_len);
        *port = ntohs(sin->sin_port);
        *flowinfo = 0;
        *scope_id = 0;
        return AF_INET;
    } else if (sa->sa_family == AF_INET6) {
        struct sockaddr_in6 *sin6 = (struct sockaddr_in6 *)sa;
        inet_ntop(AF_INET6, &(sin6->sin6_addr), ip_str, ip_len);
        *port = ntohs(sin6->sin6_port);
        *flowinfo = sin6->sin6_flowinfo;
        *scope_id = sin6->sin6_scope_id;
        return AF_INET6;
    }
    return 0;
}
*/
import "C"
import (
	"fmt"
	"strconv"
	"unsafe"

	"golang.org/x/sys/unix"
)

func getAddrInfo(ctx *ExecutionContext) (string, int, []map[string]interface{}, int, error) {
	hostFinal := ""
	if ctx.Req.Host != nil {
		hostFinal = *ctx.Req.Host
	}

	portPtr := 0
	if ctx.Req.Port != nil {
		portPtr = *ctx.Req.Port
	}

	family := ParseAF(ctx.Req.AF)
	sockType := ParseSockType(ctx.Req.SType)
	protocol := ParseProtocol(ctx.Req.SProto)
	flags := ParseFlags(ctx.Req.Flags)

	// Tangani host (*string) untuk C-string
	var cNode *C.char
	if hostFinal != "" {
		cNode = C.CString(hostFinal)
		defer C.free(unsafe.Pointer(cNode))
	}

	// Konversi *int port menjadi string service untuk C-string
	var cService *C.char
	if ctx.Req.Port != nil {
		portStrVal := strconv.Itoa(*ctx.Req.Port)
		cService = C.CString(portStrVal)
		defer C.free(unsafe.Pointer(cService))
	}

	// Siapkan struct hints C
	var hints C.struct_addrinfo
	C.memset(unsafe.Pointer(&hints), 0, C.size_t(unsafe.Sizeof(hints)))
	hints.ai_family = C.int(family)
	hints.ai_socktype = C.int(sockType)
	hints.ai_protocol = C.int(protocol)
	hints.ai_flags = C.int(flags)

	var res *C.struct_addrinfo

	// Panggil libc getaddrinfo asli
	ret := C.getaddrinfo(cNode, cService, &hints, &res)
	if ret != 0 {
		gaiErrStr := C.GoString(C.gai_strerror(ret))
		return "", 0, nil, 0, fmt.Errorf("getaddrinfo failed: %s", gaiErrStr)
	}
	defer C.freeaddrinfo(res)

	var results []map[string]interface{}
	var canonName string

	for curr := res; curr != nil; curr = curr.ai_next {
		if curr.ai_canonname != nil && canonName == "" {
			canonName = C.GoString(curr.ai_canonname)
		}

		var ipBuf [128]C.char
		var cPort C.int
		var cFlowInfo C.uint32_t
		var cScopeId C.uint32_t

		fam := C.parse_sockaddr(curr.ai_addr, &ipBuf[0], C.int(len(ipBuf)), &cPort, &cFlowInfo, &cScopeId)
		if fam == 0 {
			continue
		}

		ipStr := C.GoString(&ipBuf[0])

		var portVal interface{} = nil
		if ctx.Req.Port != nil {
			portVal = int(cPort)
		}

		resItem := map[string]interface{}{
			"family":   int(curr.ai_family),
			"socktype": int(curr.ai_socktype),
			"protocol": int(curr.ai_protocol),
			"flags":    int(flags),
			"ip":       ipStr,
			"port":     portVal,
		}
		if int(curr.ai_family) == unix.AF_INET6 {
			resItem["flowinfo"] = uint32(cFlowInfo)
			resItem["scope_id"] = uint32(cScopeId)
		}
		if canonName != "" {
			resItem["canonname"] = canonName
		}
		results = append(results, resItem)
	}

	if len(results) == 0 {
		return "", 0, nil, 0, fmt.Errorf("getaddrinfo: No address associated with hostname.")
	}

	return hostFinal, portPtr, results, len(results), nil
}
