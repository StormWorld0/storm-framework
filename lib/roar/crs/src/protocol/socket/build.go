package socket

import (
	"net"
	"fmt"
	"time"
	"net/url"
	"strconv"
	"strings"
	"golang.org/x/sys/unix"
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


// Build UDS Path File-Decriptor
func BuildUdsPath(fd int, name string) (string, error) {
	// Menghindari format string verb bug
	udsPath := name
	realPath := strings.Replace(udsPath, "@", "\x00", 1)

	addr, err := net.ResolveUnixAddr("unix", realPath)
	if err != nil {
		return "", fmt.Errorf("failed to resolve UDS address: %w", err)
	}

	// Inisialisasi Listen secara sinkron di fungsi utama.
	// Klien dijamin tidak akan mengalami 'connection refused' saat path di-return.
	l, err := net.ListenUnix("unix", addr)
	if err != nil {
		return "", fmt.Errorf("failed to listen on UDS: %w", err)
	}

	// Lempar proses penerimaan dan syscall ke background
	go func() {
		defer l.Close()
		
		l.SetDeadline(time.Now().Add(3 * time.Second))
		unxConn, err := l.AcceptUnix()
		if err != nil {
			// Pertimbangkan logging sentral di sini alih-alih channel,
			// karena FD transfer gagal tidak bisa selalu membatalkan eksekusi utama.
			return 
		}
		defer unxConn.Close()

		rawConn, err := unxConn.SyscallConn()
		if err != nil {
			return 
		}

		_ = rawConn.Control(func(sysFd uintptr) {
			// SECURITY ARCHITECT NOTE: 
			// Implementasikan syscall unix.GetsockoptUcred(int(sysFd), unix.SOL_SOCKET, unix.SO_PEERCRED) 
			// di sini untuk memvalidasi UID/GID yang terkoneksi sebelum mengirim file descriptor berhak istimewa.
			
			rights := unix.UnixRights(fd)
			unix.Sendmsg(int(sysFd), []byte("F"), rights, nil, 0)
		})
	}()

	return udsPath, nil
}
