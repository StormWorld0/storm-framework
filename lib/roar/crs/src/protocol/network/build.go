package network

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

	finalPort := 0
	if req.Port != 0 {
		finalPort = req.Port
	} else if portStr != "" {
		if p, parseErr := strconv.Atoi(portStr); parseErr == nil && p > 0 {
			finalPort = p
		}
	}

	if finalPort == 0 {
		return "", fmt.Errorf("empty port error")
	}

	return net.JoinHostPort(hostOnly, strconv.Itoa(finalPort)), nil
}
