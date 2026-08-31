package utils

import (
	"sync"
)

// SessionManager thread-safe
var ActiveSessions = sync.Map{} // map[string]net.Conn

// Store Mutex (Lock) per SessionID
var sessionLocks sync.Map
func GetSessionLock(sessionID string) *sync.Mutex {
	mu, _ := sessionLocks.LoadOrStore(sessionID, &sync.Mutex{})
	return mu.(*sync.Mutex)
}
