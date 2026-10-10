// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package utils

import (
	"context"
	"sync"
	"time"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/projectdiscovery/ratelimit"
)

// EngineRateLimiter menangani rate limit untuk satu primitif spesifik.
type EngineRateLimiter struct {
	mu         sync.RWMutex
	limiter    *ratelimit.Limiter
	ctx        context.Context
	cancelFunc context.CancelFunc
}

// RateLimiterManager mengelola kumpulan limiter untuk berbagai primitif secara concurrent-safe.
type RateLimiterManager struct {
	mu       sync.RWMutex
	rootCtx  context.Context
	limiters map[string]*EngineRateLimiter
}

var (
	globalManager *RateLimiterManager
	managerOnce   sync.Once
)

// InitRateLimiterManager menginisialisasi manager utama yang terikat dengan rootCtx daemon.
// Dipanggil sekali saat daemon startup.
func InitRateLimiterManager(ctx context.Context) {
	managerOnce.Do(func() {
		globalManager = &RateLimiterManager{
			rootCtx:  ctx,
			limiters: make(map[string]*EngineRateLimiter),
		}
	})
}

// SetPrimitiveRate mengatur atau memperbarui rate limit untuk primitif tertentu secara on-the-fly
// TANPA memengaruhi primitif lain yang sedang berjalan.
func SetPrimitiveRate(primitiveKey string, maxUnits int) {
	if globalManager == nil {
		return
	}

	globalManager.mu.Lock()
	limiter, exists := globalManager.limiters[primitiveKey]
	if !exists {
		limiter = &EngineRateLimiter{
			ctx: globalManager.rootCtx,
		}
		globalManager.limiters[primitiveKey] = limiter
	}
	globalManager.mu.Unlock()

	limiter.setRate(maxUnits)
}

func (e *EngineRateLimiter) setRate(maxUnits int) {
	e.mu.Lock()
	defer e.mu.Unlock()

	// Cleanup Limiter Lama untuk primitif ini (mencegah goroutine leak)
	if e.cancelFunc != nil {
		e.cancelFunc()
		e.cancelFunc = nil
	}

	// Jika ratelimit <= 0, anggap tidak ada limit
	if maxUnits <= 0 {
		e.limiter = nil
		return
	}

	// Buat Lifecycle Baru terturun dari rootCtx daemon
	ctx, cancel := context.WithCancel(e.ctx)
	e.cancelFunc = cancel

	e.limiter = ratelimit.New(ctx, uint(maxUnits), time.Second)
}

// UpdatePrimitiveRate mempermudah pembaruan dari modul lain berdasarkan key primitif.
func UpdatePrimitiveRate(req packet.RequestPacket) {
	SetPrimitiveRate(req.Primitive, req.RateLimit)
}

// Take menahan eksekusi berdasarkan primitif tertentu.
func Take(primitiveKey string) {
	if globalManager == nil {
		return
	}

	globalManager.mu.RLock()
	limiter, exists := globalManager.limiters[primitiveKey]
	globalManager.mu.RUnlock()

	if !exists || limiter == nil {
		return
	}

	limiter.mu.RLock()
	l := limiter.limiter
	limiter.mu.RUnlock()

	if l != nil {
		l.Take()
	}
}

// Stop membersihkan seluruh background goroutine dari *seluruh* primitif aktif 
// saat daemon menangkap SIGTERM.
func Stop() {
	if globalManager == nil {
		return
	}

	globalManager.mu.Lock()
	defer globalManager.mu.Unlock()

	for _, limiter := range globalManager.limiters {
		limiter.mu.Lock()
		if limiter.cancelFunc != nil {
			limiter.cancelFunc()
			limiter.cancelFunc = nil
		}
		limiter.mu.Unlock()
	}
}
