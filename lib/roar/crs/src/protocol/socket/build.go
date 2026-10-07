package socket

import (
	"fmt"
	"net/url"
	"strconv"
	"strings"
)

func BuildTarget(host string, port *int) (*string, *int, error) {
	rawHost := strings.TrimSpace(host)
	if rawHost == "" {
		return nil, nil, fmt.Errorf("target host cannot be empty")
	}

	// Tangani Unix Domain Socket secara eksplisit
	if strings.HasPrefix(rawHost, "unix://") || strings.HasPrefix(rawHost, "/") {
		cleanPath := strings.TrimPrefix(rawHost, "unix://")
		return &cleanPath, nil, nil
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

	var finalPort *int
	if port != nil {
		// Priority 1: Ambil dari req.Port
		finalPort = port
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
func DerefString[T any](ptr *T, defaultValue string) string {
	if ptr == nil {
		return defaultValue
	}

	// Type switch untuk performa maksimal
	switch v := any(*ptr).(type) {
	case string:
		return v
	case int:
		return strconv.Itoa(v)
	case int64:
		return strconv.FormatInt(v, 10)
	default:
		return defaultValue
	}
}
