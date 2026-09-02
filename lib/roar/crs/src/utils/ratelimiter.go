// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package utils

import (
	"context"
	"sync"
	"time"

	"github.com/projectdiscovery/ratelimit"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// EngineRateLimiter didesain untuk Long-Lived Daemon.
type EngineRateLimiter struct {
	mu         sync.RWMutex
	limiter    *ratelimit.Limiter
	ctx        context.Context 
	cancelFunc context.CancelFunc 
}

var (
	globalLimiter *EngineRateLimiter
	limiterOnce   sync.Once
)

// InitGlobalRateLimiter menginisialisasi Rate Limiter untuk daemon.
// rootCtx adalah context dari daemon yang terikat dengan sigterm.
func InitGlobalRateLimiter(ctx context.Context, req packet.RequestPacket) {
	limiterOnce.Do(func() {
		globalLimiter = &EngineRateLimiter{
			ctx: ctx,
		}
		globalLimiter.SetRate(req.RateLimit)
	})
}

// SetRate memungkinkan update rate secara on-the-fly untuk task baru
// TANPA menyebabkan goroutine leak pada daemon yang terus hidup.
func (e *EngineRateLimiter) SetRate(maxUnits int) {
	e.mu.Lock()
	defer e.mu.Unlock()

	// 1. Cleanup Limiter Lama:
	// Jika sebelumnya sudah ada limiter yang berjalan, batalkan context-nya.
	// Ini akan membunuh background goroutine (ticker) bawaan projectdiscovery/ratelimit.
	if e.cancelFunc != nil {
		e.cancelFunc()
	}

	// 2. Buat Lifecycle Baru:
	// Turunkan context baru dari rootCtx IPC daemon.
	// Jika daemon terkena sigterm, rootCtx mati, otomatis ctx ini juga mati.
	ctx, cancel := context.WithCancel(e.ctx)
	e.cancelFunc = cancel

	if maxUnits <= 0 {
		e.limiter = ratelimit.NewUnlimited(ctx)
		return
	}

	e.limiter = ratelimit.New(ctx, uint(maxUnits), time.Second)
}

// UpdateGlobalRate mempermudah pembaruan dari modul lain (misal saat transisi task IPC)
func UpdateGlobalRate(newLimit int) {
	if globalLimiter != nil {
		globalLimiter.SetRate(newLimit)
	}
}

// Take menahan eksekusi hingga token tersedia.
func Take() {
	if globalLimiter == nil {
		return
	}

	globalLimiter.mu.RLock()
	limiter := globalLimiter.limiter
	globalLimiter.mu.RUnlock()

	if limiter != nil {
		limiter.Take()
	}
}

// Close dipanggil HANYA saat daemon menangkap (SIGTERM).
// Untuk memastikan pembersihan akhir secara manual.
func Stop() {
	if globalLimiter != nil {
		globalLimiter.mu.Lock()
		defer globalLimiter.mu.Unlock()
		if globalLimiter.cancelFunc != nil {
			globalLimiter.cancelFunc()
		}
	}
}
