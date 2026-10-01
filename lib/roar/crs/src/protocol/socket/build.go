package socket

import (
	"fmt"
	"net/url"
	"strconv"
	"strings"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func BuildTarget(req packet.RequestPacket) (*string, *int, error) {
	rawHost := strings.TrimSpace(req.Host)
	if rawHost == "" {
		return nil, nil, fmt.Errorf("target host cannot be empty")
	}

	// Tangani Unix Domain Socket secara eksplisit
	if strings.HasPrefix(rawHost, "unix://") || strings.HasPrefix(rawHost, "/") {
		cleanPath := strings.TrimPrefix(rawHost, "unix://")
		return &cleanPath, nil, nil
	}

	if idx := strings.Index(rawHost, "://"); idx != -1 {
		rawHost = rawHost[idx+3:] // +3 untuk melewati "://"
	}

	// Pembersihan Trailing Path untuk TCP/UDP (misal example.com:80/api -> example.com:80)
	if idx := strings.Index(rawHost, "/"); idx != -1 {
		rawHost = rawHost[:idx]
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

	if strings.HasPrefix(hostOnly, "[") && strings.HasSuffix(hostOnly, "]") {
		hostOnly = hostOnly[1 : len(hostOnly)-1]
	}

	var finalPort *int
	if req.Port != nil {
		// Priority 1: Ambil dari req.Port
		finalPort = req.Port
	} else if u.Port() != "" {
		// Priority 2: Port dari string URI
		if p, parseErr := strconv.Atoi(u.Port()); parseErr == nil {
			finalPort = &p
		}
	}

	// Validasi Range Port HANYA jika port memang didefinisikan
	if finalPort != nil {
		if *finalPort < 0 || *finalPort > 65535 {
			return nil, nil, fmt.Errorf("port out of valid range (0-65535): %d", *finalPort)
		}
		return &hostOnly, finalPort, nil
	}
	return &hostOnly, nil, nil
}

// Deref returns the value of the pointer, or defaultValue if pointer is nil.
func Deref[T any](ptr *T, defaultValue T) T {
	if ptr == nil {
		return defaultValue
	}
	return *ptr
}
