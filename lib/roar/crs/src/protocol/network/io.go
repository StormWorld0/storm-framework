package network

import (
	"encoding/base64"
	"fmt"
	"net"
	"sync"
	"time"
)

var bufferPool = sync.Pool{
	New: func() interface{} {
		b := make([]byte, 4096)
		return &b
	},
}

// ExecuteWrite menangani dekode base64 dan pengiriman payload TCP/TLS.
func ExecuteWrite(conn net.Conn, data string) error {
	if data == "" {
		return nil
	}
	dataDec, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}
	_, err = conn.Write(dataDec)
	return err
}

// ExecuteRead menangani alokasi buffer efisien dan timeout untuk operasi baca.
func ExecuteRead(conn net.Conn, readSize int, timeout time.Duration) ([]byte, int, *[]byte, error) {
	if readSize <= 0 {
		readSize = 0
	}

	var buffer []byte
	var bufPtr *[]byte

	if readSize == 4096 {
		bufPtr = bufferPool.Get().(*[]byte)
		buffer = *bufPtr
	} else {
		buffer = make([]byte, readSize)
	}

	conn.SetDeadline(time.Now().Add(timeout))
	defer conn.SetDeadline(time.Time{})

	n, err := conn.Read(buffer)
	return buffer, n, bufPtr, err
}

// ReleaseBuffer mengembalikan buffer ke memory pool
func ReleaseBuffer(bufPtr *[]byte) {
	if bufPtr != nil {
		bufferPool.Put(bufPtr)
	}
}

