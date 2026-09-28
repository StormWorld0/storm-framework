package socket

import (
	"encoding/base64"
	"fmt"
	"net"
	"sync"
	"time"

	"golang.org/x/sys/unix"
)

var bufferPool = sync.Pool{
	New: func() interface{} {
		b := make([]byte, 4096)
		return &b
	},
}

// ReleaseBuffer mengembalikan buffer ke memory pool
func ReleaseBuffer(bufPtr *[]byte) {
	if bufPtr != nil {
		bufferPool.Put(bufPtr)
	}
}

// ExecuteWrite menangani dekode base64 dan pengiriman payload TCP/TLS.
func ExecuteWrite(conn net.Conn, data string, timeout time.Duration) error {
	if data == "" {
		return nil
	}
	dataDec, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}
	
	conn.SetWriteDeadline(time.Now().Add(timeout))
	defer conn.SetWriteDeadline(time.Time{})
	
	_, err = conn.Write(dataDec)
	return err
}

// ExecuteRead menangani alokasi buffer efisien dan timeout untuk operasi baca.
func ExecuteRead(conn net.Conn, readSize int, timeout time.Duration) ([]byte, int, *[]byte, error) {
	if readSize <= 0 {
		readSize = 4096
	}

	var buffer []byte
	var bufPtr *[]byte

	if readSize == 4096 {
		bufPtr = bufferPool.Get().(*[]byte)
		buffer = *bufPtr
	} else {
		buffer = make([]byte, readSize)
	}
	
	conn.SetReadDeadline(time.Now().Add(timeout))
	defer conn.SetReadDeadline(time.Time{})

	n, err := conn.Read(buffer)
	return buffer, n, bufPtr, err
}

func ExecuteSendTo(fd int, data string, sa unix.Sockaddr, timeout time.Duration, flag int) error {
	if data == "" {
		return nil
	}
	
	dataDec, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}
	
	// Terapkan SO_SNDTIMEO untuk mencegah goroutine hang jika kernel send buffer penuh
	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &tv)
	}

	// Flag default 0. Eksekusi pengiriman datagram
	return unix.Sendto(fd, dataDec, flag, sa)
}

// ExecuteReadFrom mengeksekusi blocking recvfrom dengan timeout dan buffer pooling
func ExecuteRecvFrom(fd int, readSize int, timeout time.Duration, flag int) ([]byte, int, unix.Sockaddr, *[]byte, error) {
	if readSize <= 0 {
		readSize = 4096
	}

	var buffer []byte
	var bufPtr *[]byte

	if readSize == 4096 {
		bufPtr = bufferPool.Get().(*[]byte)
		buffer = *bufPtr
	} else {
		buffer = make([]byte, readSize)
	}

	// Terapkan Timeout hanya jika > 0 untuk menghindari reset RCVTIMEO yang tidak perlu
	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &tv)
	}

	// Eksekusi syscall membaca dari Raw Socket / UDP
	n, sa, err := unix.Recvfrom(fd, buffer, flag)
	return buffer, n, sa, bufPtr, err
}
