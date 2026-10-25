package utils

import (
	"context"
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


// -- SEMAPHORE TYPE CONFIGURATION --
type DynamicSemaphore struct {
	mu       sync.Mutex
	capacity int
	ch       chan struct{}
}

func NewDynamicSemaphore(initialCap int) *DynamicSemaphore {
	if initialCap <= 0 {
		initialCap = 1
	}
	return &DynamicSemaphore{
		capacity: initialCap,
		ch:       make(chan struct{}, initialCap),
	}
}

// Acquire takes the token and adjusts the capacity if there is a change in IPC
func (ds *DynamicSemaphore) Acquire(ctx context.Context, newCap int) error {
	ds.mu.Lock()
	if newCap > 0 && newCap != ds.capacity {
		ds.resizeLocked(newCap)
	}
	ds.mu.Unlock()

	select {
	case ds.ch <- struct{}{}:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func (ds *DynamicSemaphore) Release() {
	<-ds.ch
}

// resizeLocked changes the channel capacity safely at runtime
func (ds *DynamicSemaphore) resizeLocked(newCap int) {
	if newCap <= 0 || newCap == ds.capacity {
		return
	}

	oldCh := ds.ch
	newCh := make(chan struct{}, newCap)

	// Count the tokens currently in use on the old channel
	// Without closing the channel to avoid panic, we drain non-blocking
	activeTokens := 0
drainLoop:
	for {
		select {
		case <-oldCh:
			activeTokens++
		default:
			break drainLoop
		}
	}

	// Move active tokens to a new channel (limited by new capacity)
	for i := 0; i < activeTokens; i++ {
		if i < newCap {
			newCh <- struct{}{}
		}
		// If the old tokens exceed the new reduced capacity,
		// excess tokens will be automatically trimmed (ignored)
	}

	ds.ch = newCh
	ds.capacity = newCap
}

