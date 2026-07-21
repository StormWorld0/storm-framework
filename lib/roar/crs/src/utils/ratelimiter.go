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

var (
	globalLimiter *ratelimit.Limiter
	limiterOnce   sync.Once
)

// InitGlobalRateLimiter menginisialisasi Rate Limiter global.
// maxUnits: Jumlah maksimal request (misal: 150)
// duration: Window waktu (misal: 1 * time.Second) -> Artinya max 150 RPS
func InitGlobalRateLimiter(req packet.RequestPacket, duration time.Duration) {
	limiterOnce.Do(func() {
		// ratelimit.NewUnlimited() digunakan jika user men-set rate limit = 0
    maxUnits := req.RateLimit
		if maxUnits <= 0 {
			globalLimiter = ratelimit.NewUnlimited(context.Background())
			return
		}

		// Menggunakan MultiRateLimiter/Limiter bawaan ProjectDiscovery
		globalLimiter = ratelimit.NewWithBurst(context.Background(), uint(maxUnits), duration, uint(maxUnits))
	})
}

// Take menahan eksekusi (blocking) hingga token rate limit tersedia.
// Harus dipanggil SEBELUM koneksi socket/HTTP dibuka.
func Take() {
	if globalLimiter != nil {
		globalLimiter.Take()
	}
}
