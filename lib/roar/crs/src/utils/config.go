package utils

import (
	"sync"
)

// SessionManager thread-safe
var ActiveSessions = sync.Map{} // map[string]net.Conn
// Store Mutex (Lock) per SessionID
var sessionLocks sync.Map
