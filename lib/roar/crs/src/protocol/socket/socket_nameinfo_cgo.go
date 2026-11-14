package socket

/*
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdlib.h>
#include <netinet/in.h>

int call_getnameinfo(const char *ip_str, int port, uint32_t flowinfo, uint32_t scope_id, int flags, char *host_buf, int host_len, char *serv_buf, int serv_len) {
    struct sockaddr_storage sa;
    memset(&sa, 0, sizeof(sa));
    socklen_t salen = 0;

    // Coba parsing sebagai IPv4 terlebih dahulu
    struct sockaddr_in *sin = (struct sockaddr_in *)&sa;
    if (inet_pton(AF_INET, ip_str, &(sin->sin_addr)) == 1) {
        sin->sin_family = AF_INET;
        sin->sin_port = htons((uint16_t)port);
        salen = sizeof(struct sockaddr_in);
    } else {
        // Jika bukan IPv4, coba parsing sebagai IPv6
        struct sockaddr_in6 *sin6 = (struct sockaddr_in6 *)&sa;
        if (inet_pton(AF_INET6, ip_str, &(sin6->sin6_addr)) == 1) {
            sin6->sin6_family = AF_INET6;
            sin6->sin6_port = htons((uint16_t)port);
            sin6->sin6_flowinfo = flowinfo;
            sin6->sin6_scope_id = scope_id;
            salen = sizeof(struct sockaddr_in6);
        } else {
            return -1; // Format IP tidak valid
        }
    }

    return getnameinfo((struct sockaddr *)&sa, salen, host_buf, host_len, serv_buf, serv_len, flags);
}
*/
import "C"
import (
	"fmt"
	"strconv"
	"unsafe"
)

func getNameInfo(ctx *ExecutionContext) (string, string, error) {
	addr, port, err := BuildTarget(ctx.Req.Host, ctx.Req.Port)
	if err != nil {
		return "", "", fmt.Errorf("Failed build target: %w", err)
	}

	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")

	portInt, err := strconv.Atoi(portFinal)
	if err != nil {
		portInt = 0
	}

	// Ekstrak parameter IPv6 dan flags standar POSIX
	flowinfo := C.uint32_t(ctx.Req.FlowInfo)
	scopeid := C.uint32_t(ctx.Req.ScopeID)
	flags := C.int(ParseFlags(ctx.Req.Flags))

	cHostIP := C.CString(hostFinal)
	defer C.free(unsafe.Pointer(cHostIP))

	// Buffer standar POSIX untuk host dan service
	var hostBuf [C.NI_MAXHOST]C.char
	var servBuf [C.NI_MAXSERV]C.char

	// Panggil helper C yang mengeksekusi getnameinfo native
	ret := C.call_getnameinfo(
		cHostIP,
		C.int(portInt),
		flowinfo,
		scopeid,
		flags,
		&hostBuf[0],
		C.int(len(hostBuf)),
		&servBuf[0],
		C.int(len(servBuf)),
	)

	if ret != 0 {
		if int(ret) == -1 {
			return "", "", fmt.Errorf("Invalid IP address format.")
		}
		gaiErrStr := C.GoString(C.gai_strerror(ret))
		return "", fmt.Sprintf("%d", portInt), fmt.Errorf("getnameinfo failed: %s", gaiErrStr)
	}

	hostStr := C.GoString(&hostBuf[0])
	servStr := C.GoString(&servBuf[0])

	return hostStr, servStr, nil
}
