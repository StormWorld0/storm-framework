package socket

import (
	"fmt"
	"net"
	"strconv"
	"strings"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// BuildTarget merakit alamat host dan port menjadi format koneksi yang valid.
func BuildTarget(req packet.RequestPacket) (string, error) {
	rawHost := strings.TrimSpace(req.Host)
	if rawHost == "" {
		return "", fmt.Errorf("invalid empty host")
	}

	if strings.Contains(rawHost, "://") {
		parts := strings.SplitN(rawHost, "://", 2)
		rawHost = parts[1]
	}

	hostOnly, portStr, err := net.SplitHostPort(rawHost)
	if err != nil {
		hostOnly = rawHost
		portStr = ""
	}

	if idx := strings.Index(hostOnly, "/"); idx != -1 {
		hostOnly = hostOnly[:idx]
	}

	if strings.HasPrefix(hostOnly, "[") && strings.HasSuffix(hostOnly, "]") {
		hostOnly = hostOnly[1 : len(hostOnly)-1]
	}

	finalPort := -1
	if req.Port >= 0 {
		finalPort = req.Port
	} else if portStr != "" {
		if p, parseErr := strconv.Atoi(portStr); parseErr == nil && p >= 0 {
			finalPort = p
		}
	}

	// Validasi: Error HANYA jika port berada di luar jangkauan valid socket (0 - 65535)
	if finalPort < 0 || finalPort > 65535 {
		return "", fmt.Errorf("invalid or missing port: %d", finalPort)
	}
	
	return net.JoinHostPort(hostOnly, strconv.Itoa(finalPort)), nil
}
