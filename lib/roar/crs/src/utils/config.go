package utils

import (
	"sync"
)

// SessionManager thread-safe
var ActiveSessions = sync.Map{} // map[string]string (net.Conn or FD)
var SessionHosts = sync.Map{}   // map[string]string (Host)
var ClientFD = sync.Map{}       // map[string]string (File Decriptor Client)

// Store Mutex (Lock) per SessionID
var sessionLocks sync.Map
func GetSessionLock(sessionID string) *sync.Mutex {
	mu, _ := sessionLocks.LoadOrStore(sessionID, &sync.Mutex{})
	return mu.(*sync.Mutex)
}
