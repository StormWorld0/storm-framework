package socket

import (
	"fmt"
	"net"
	"net/url"
	"strconv"
	"strings"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)


func BuildTarget(req packet.RequestPacket) (host, port, error) {
	rawHost := strings.TrimSpace(req.Host)
	if rawHost == "" {
		return nil, nil, fmt.Errorf("target host cannot be empty")
	}

	// Tangani Unix Domain Socket secara eksplisit
	if strings.HasPrefix(rawHost, "unix://") || strings.HasPrefix(rawHost, "/") {
		return strings.TrimPrefix(rawHost, "unix://"), nil
	}

	// Berikan dummy scheme jika tidak ada, agar url.Parse tidak gagal
	parseTarget := rawHost
	if !strings.Contains(parseTarget, "://") {
		parseTarget = "tcp://" + parseTarget
	}

	u, err := url.Parse(parseTarget)
	if err != nil {
		return nil, nil, fmt.Errorf("invalid target format: %w", err)
	}

	hostOnly := u.Hostname()
	if hostOnly == "" {
		return nil, nil, fmt.Errorf("failed to extract host from target")
	}

	finalPort := -1

	// Priority 1: Port dari parameter override
	if req.Port != nil {
		finalPort = *req.Port
	} else if u.Port() != "" {
		// Priority 2: Port dari string URI
		if p, parseErr := strconv.Atoi(u.Port()); parseErr == nil {
			finalPort = p
		}
	}

	// Validasi Range Port HANYA jika port memang didefinisikan
	if finalPort != -1 {
		if finalPort < 0 || finalPort > 65535 {
			return nil, nil, fmt.Errorf("port out of valid range (0-65535): %d", finalPort)
		}
		return hostOnly, finalPort, nil
	}
	return hostOnly, nil, nil
}
