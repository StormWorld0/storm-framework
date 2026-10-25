package utils

import (
	"sync"
)

// SessionManager thread-safe
var ActiveSessions = sync.Map{} // map[string]string (net.Conn or FD)
var SessionHosts = sync.Map{}   // map[string]string (Host)
var ClientFD = sync.Map{}       // map[string]string (File Decriptor Client)

// Store Mutex (Lock) per SessionID
var SessionLocks sync.Map
func GetSessionLock(sessionID string) *sync.Mutex {
	mu, _ := SessionLocks.LoadOrStore(sessionID, &sync.Mutex{})
	return mu.(*sync.Mutex)
}
