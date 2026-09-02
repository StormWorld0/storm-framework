// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package utils

import (
	"sync"
	"time"

	"github.com/projectdiscovery/fastdialer/fastdialer"
)

var (
	// globalDialer menyimpan instance Fastdialer untuk digunakan seluruh modul
	globalDialer *fastdialer.Dialer
	once         sync.Once
	initErr      error
)

// InitGlobalDialer dipanggil satu kali saat framework baru menyala (bootstrap)
func InitGlobalDialer() error {
	once.Do(func() {
		options := fastdialer.DefaultOptions
		options.DialerTimeout = 5 * time.Second
		options.DialerKeepAlive = 10 * time.Second
		options.MaxRetries = 2
		options.DisableZtlsFallback = true
		options.WithDialerHistory = true      // Melacak history IP untuk debugging
		options.EnableFallback = true         // DNS fallback otomatis
		
		// Inisialisasi engine fastdialer (DNS Cache, Connection Pooler)
		dialer, err := fastdialer.NewDialer(options)
		if err != nil {
			initErr = err
			return
		}
		globalDialer = dialer
	})
	return initErr
}

// GetDialer mengembalikan instance Fastdialer yang sudah berjalan.
// Modul Socket/HTTP HANYA boleh menggunakan fungsi ini, dilarang membuat Dialer baru.
func GetDialer() *fastdialer.Dialer {
	// Jika belum diinisialisasi (misal lupa dipanggil di main.go), kita inisialisasi darurat
	if globalDialer == nil {
		_ = InitGlobalDialer()
	}
	return globalDialer
}

// Close membersihkan DNS cache dan menutup koneksi yang menggantung saat framework dimatikan
func Close() {
	if globalDialer != nil {
		globalDialer.Close()
	}
}

