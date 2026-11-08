package socket

import (
	"os"
	"fmt"
	"net"
	"sync"
	"time"
	"unsafe"
	"errors"
	"syscall"
	"encoding/base64"
	"golang.org/x/sys/unix"
)

var bufferPool = sync.Pool{
	New: func() interface{} {
		b := make([]byte, 4096)
		return &b
	},
}

// ReleaseBuffer returns the buffer to the memory pool.
func ReleaseBuffer(bufPtr *[]byte) {
	if bufPtr != nil {
		bufferPool.Put(bufPtr)
	}
}

// --- READ/WRITE net.conn ---

func ExecuteWrite(conn net.Conn, data string, timeout time.Duration) error {
	if data == "" {
		return nil
	}
	dataDec, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}

	if timeout > 0 {
	    conn.SetWriteDeadline(time.Now().Add(timeout))
	    defer conn.SetWriteDeadline(time.Time{})
	}
	
	_, err = conn.Write(dataDec)
	return err
}

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

	if timeout > 0 {
	    conn.SetReadDeadline(time.Now().Add(timeout))
	    defer conn.SetReadDeadline(time.Time{})
    }
	
	n, err := conn.Read(buffer)
	return buffer, n, bufPtr, err
}


// --- READ/WRITE RawFD ---

func ExecuteFDWrite(fd int, data string, timeout time.Duration, flags int) error {
	if data == "" {
		return nil
	}

	dataDec, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}

	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &zeroTv)
		}()
	}
	
	err = unix.Send(fd, dataDec, flags)
	return err
}

func ExecuteFDWriteAll(fd int, data string, timeout time.Duration, flags int) error {
	if data == "" {
		return nil
	}

	buf, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}

	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &zeroTv)
		}()
	}

	total := 0
	for total < len(buf) {
		var p0 unsafe.Pointer
		if len(buf[total:]) > 0 {
			p0 = unsafe.Pointer(&buf[total:][0])
		}
	    r1, _, e1 := unix.Syscall6(unix.SYS_SENDTO, uintptr(fd), uintptr(p0), 
								   uintptr(len(buf[total:])), uintptr(flags), 0, 0)
		if e1 != 0 {
			if e1 == unix.EINTR {
				continue
			}
			return e1
		}
		n := int(r1)
		total += n
	}
	return nil
}

func ExecuteFDWriteFile(outfd int, file string, timeout time.Duration) error {
	if file == "" {
		return nil
	}

	f, err := os.Open(file)
	if err != nil {
		return err
	}
	defer f.Close()

	md, err := f.Stat()
	if err != nil {
		return err
	}
	fSize := md.Size() // int64

	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(outfd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(outfd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &zeroTv)
		}()
	}

	var offset int64 = 0
	for offset < fSize {
		remaining := fSize - offset
		count := int(remaining)
		
		if count > 256*1024 { count = 256*1024 } // Max Chunk 256kb
		
	    n1, e1 := unix.Sendfile(outfd, int(f.Fd()), &offset, count)
		if e1 != nil {
			if e1 == unix.EINTR {
				continue
			}
			return e1
		}
		if n1 <= 0 {
			break
		}
	}
	return nil
}


func ExecuteSendTo(fd int, data string, sa unix.Sockaddr, timeout time.Duration, flag int) error {
	if data == "" {
		return nil
	}
	
	dataDec, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return fmt.Errorf("base64 decode failed: %w", err)
	}
	
	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &zeroTv)
		}()
	}

	return unix.Sendto(fd, dataDec, flag, sa)
}

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
	
	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &zeroTv)
		}()
	}

	n, sa, err := unix.Recvfrom(fd, buffer, flag)
	return buffer, n, sa, bufPtr, err
}


func ExecuteSendMsg(fd int, p int, oob int, sa unix.Sockaddr, flag int, timeout time.Duration) error {
	buff := make([]byte, p)
	anc := make([]byte, oob)
	
	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_SNDTIMEO, &zeroTv)
		}()
	}

	return unix.Sendmsg(fd, buff, anc, sa, flag)
}

func ExecuteRecvMsgStream(fd int, readSize int, oob int, flag int, timeout time.Duration) ([]byte, *[]byte, int, int, int, unix.Sockaddr, error) {
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
	anc := make([]byte, oob)

	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &zeroTv)
		}()
	}

	var n  int
	var ob int
	var rf int
	var sa unix.Sockaddr
	var e1 error
	
	for {
		n, ob, rf, sa, e1 := unix.Recvmsg(fd, buffer, anc, flag)
		if e1 != nil {
			if errors.Is(e1, syscall.EINTR) {
				continue
			}
			return buffer, bufPtr, n, ob, rf, sa, e1
		}
		break
	}
	return buffer, bufPtr, n, ob, rf, sa, e1
}

func ExecuteRecvMsgDgram(fd int, readSize int, oob int, flag int, timeout time.Duration) ([]byte, *[]byte, int, int, int, unix.Sockaddr, error) {
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
	anc := make([]byte, oob)

	if timeout > 0 {
		tv := unix.NsecToTimeval(timeout.Nanoseconds())
		unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &tv)

		defer func() {
			zeroTv := unix.Timeval{Sec: 0, Usec: 0}
		    unix.SetsockoptTimeval(fd, unix.SOL_SOCKET, unix.SO_RCVTIMEO, &zeroTv)
		}()
	}
	
	n, ob, rf, sa, e1 := unix.Recvmsg(fd, buffer, anc, flag)
	if e1 != nil {
		return buffer, bufPtr, n, ob, rf, sa, e1
	}
	return buffer, bufPtr, n, ob, rf, sa, e1 
}
