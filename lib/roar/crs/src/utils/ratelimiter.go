// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy (Core Rate Limiter Engine)
package utils

import (
	"context"
	"sync"
	"time"

	"github.com/projectdiscovery/ratelimit"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

// EngineRateLimiter adalah arsitektur standar untuk kontrol RPS pada scanner.
// Mendukung eksekusi konkuren yang aman dan penyesuaian limit dinamis (Adaptive Backoff).
type EngineRateLimiter struct {
	mu      sync.RWMutex
	limiter *ratelimit.Limiter
	ctx     context.Context
}

var (
	globalLimiter *EngineRateLimiter
	limiterOnce   sync.Once
)

// InitGlobalRateLimiter menginisialisasi Rate Limiter.
// WAJIB menerima context dari caller (misal: context engine utama) untuk 
// mencegah memory/goroutine leak saat proses scan dibatalkan atau selesai.
func InitGlobalRateLimiter(ctx context.Context, req packet.RequestPacket) {
	limiterOnce.Do(func() {
		globalLimiter = &EngineRateLimiter{
			ctx: ctx,
		}
		// Inisialisasi state awal
		globalLimiter.SetRate(req.RateLimit)
	})
}

// SetRate memungkinkan penyesuaian limit secara on-the-fly (Runtime).
// Fitur krusial bagi scanner untuk melakukan "Adaptive Rate Limiting" 
// (misalnya: menurunkan limit secara otomatis jika mendeteksi HTTP 429 atau WAF block).
func (e *EngineRateLimiter) SetRate(maxUnits int) {
	e.mu.Lock()
	defer e.mu.Unlock()

	// Re-inisialisasi limiter baru. Limiter lama akan di-garbage collect
	// dan tickernya akan mati saat `e.ctx` utama dibatalkan.
	if maxUnits <= 0 {
		e.limiter = ratelimit.NewUnlimited(e.ctx)
		return
	}

	e.limiter = ratelimit.New(e.ctx, uint(maxUnits), time.Second)
}

// UpdateGlobalRate mempermudah pemanggilan SetRate dari luar package
// tanpa mengekspos struct internal.
func UpdateGlobalRate(newLimit int) {
	if globalLimiter != nil {
		globalLimiter.SetRate(newLimit)
	}
}

// Take menahan eksekusi (blocking) hingga token rate limit tersedia.
// Harus dipanggil SEBELUM koneksi socket/HTTP dibuka.
func Take() {
	if globalLimiter == nil {
		return // Fail-safe (Graceful return) jika limiter belum di-init
	}

	// Gunakan Read Lock agar eksekusi ribuan worker (goroutine) 
	// tidak saling blocking (lock contention), kecuali saat SetRate() dipanggil.
	globalLimiter.mu.RLock()
	limiter := globalLimiter.limiter
	globalLimiter.mu.RUnlock()

	if limiter != nil {
		limiter.Take()
	}
}
