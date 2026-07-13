package main

import (
	"bufio"
	"crypto/tls"
	"flag"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

var httpClient *http.Client

func init() {
	customTransport := &http.Transport{
		TLSClientConfig:     &tls.Config{InsecureSkipVerify: true},
		DisableKeepAlives:   true,
		MaxIdleConns:        1000,
		MaxIdleConnsPerHost: 100,
	}

	httpClient = &http.Client{
		Transport: customTransport,
		Timeout:   3 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 2 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}
}

type Job struct {
	URL string
}

// Worker sekarang menerima counter untuk pencatatan progres global
func worker(jobs <-chan Job, wg *sync.WaitGroup, foundCounter *int32, processedCounter *int32, totalJobs int32, lastPct *int32) {
	defer wg.Done()
	for job := range jobs {
		// Menggunakan anonymous function agar defer dijalankan setiap iterasi job selesai (baik sukses maupun gagal)
		func(j Job) {
			defer func() {
				// 1. Increment total job yang selesai diproses (termasuk error/RTO)
				processed := atomic.AddInt32(processedCounter, 1)

				if totalJobs > 0 {
					// 2. Hitung persentase progres saat ini
					pct := (processed * 100) / totalJobs

					// 3. CAS (Compare-And-Swap) Loop: Memastikan PROGRESS hanya dicetak jika nilainya naik.
					// Ini mencegah I/O flooding ke stdout ketika banyak worker selesai bersamaan di persentase yang sama.
					for {
						currentLast := atomic.LoadInt32(lastPct)
						if pct <= currentLast {
							break
						}
						if atomic.CompareAndSwapInt32(lastPct, currentLast, pct) {
							fmt.Printf("PROGRESS => %d|%d|%d\n", pct, processed, totalJobs)
							break
						}
					}
				}
			}()

			req, err := http.NewRequest("HEAD", j.URL, nil)
			if err != nil {
				return
			}
			req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

			resp, err := httpClient.Do(req)
			if err != nil {
				return
			}
			defer resp.Body.Close()

			server := resp.Header.Get("Server")
			contentType := resp.Header.Get("Content-Type")

			if server == "" {
				server = "unknown"
			}
			if contentType == "" {
				contentType = "unknown"
			}

			if resp.StatusCode < 400 || resp.StatusCode == 403 || resp.StatusCode == 401 {
				fmt.Printf("FOUND => %d | %-40s | %-10s | %s\n", resp.StatusCode, j.URL, server, contentType)
				atomic.AddInt32(foundCounter, 1)
			}
		}(job)
	}
}

func main() {
	domainFlag := flag.String("d", "", "Target domain (example: example.com)")
	wordlistFlag := flag.String("w", "", "Path to wordlist .txt file")
	concurrency := flag.Int("c", 1, "Number of concurrent workers")
	flag.Parse()

	if *domainFlag == "" || *wordlistFlag == "" {
		fmt.Println("Error: Parameters -d (domain) and -w (wordlist) are required.")
		os.Exit(1)
	}

	targetDomain := strings.TrimPrefix(strings.TrimPrefix(*domainFlag, "http://"), "https://")
	targetDomain = strings.Trim(targetDomain, "/")

	file, err := os.Open(*wordlistFlag)
	if err != nil {
		fmt.Printf("Error opening wordlist: %v", err)
		os.Exit(1)
	}
	defer file.Close()

	// --- STRATEGI O(1) MEMORY UNTUK MENGHITUNG TOTAL JOBS ---
	// Lakukan quick scan pertama untuk menghitung jumlah baris valid
	var totalLines int32 = 0
	countScanner := bufio.NewScanner(file)
	for countScanner.Scan() {
		txt := strings.TrimSpace(countScanner.Text())
		if txt != "" && !strings.HasPrefix(txt, "#") {
			totalLines++
		}
	}
	
	// Karena 1 baris wordlist dieksekusi 2 kali (http & https)
	totalJobs := totalLines * 2

	// Kembalikan pointer pembacaan file ke indeks 0 (awal file) agar bisa di-stream kembali
	_, err = file.Seek(0, 0)
	if err != nil {
		fmt.Printf("Error resetting wordlist file pointer: %v", err)
		os.Exit(1)
	}
	// --------------------------------------------------------

	jobs := make(chan Job, *concurrency)
	var wg sync.WaitGroup
	
	var activeCount int32 = 0    // Mencatat subdomain yang FOUND
	var processedCount int32 = 0 // Mencatat total request yang sudah selesai (sukses + gagal)
	var lastPct int32 = -1       // State persentase terakhir yang berhasil dicetak

	fmt.Printf("STATUS | URL | SERVER | Content-Type\n")

	// Spawning Worker Pool dengan passing pointer counter baru
	for i := 0; i < *concurrency; i++ {
		wg.Add(1)
		go worker(jobs, &wg, &activeCount, &processedCount, totalJobs, &lastPct)
	}

	// Stream Reading kedua untuk pemrosesan riil
	scanner := bufio.NewScanner(file)
	protocols := []string{"http", "https"}

	for scanner.Scan() {
		subdomain := strings.TrimSpace(scanner.Text())
		if subdomain == "" || strings.HasPrefix(subdomain, "#") {
			continue
		}

		for _, proto := range protocols {
			url := fmt.Sprintf("%s://%s.%s", proto, subdomain, targetDomain)
			jobs <- Job{URL: url}
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("Error while reading wordlist: %v", err)
	}

	close(jobs)
	wg.Wait()

	// Kirim sinyal progres 100% di akhir untuk memastikan visualisasi Python penuh
	fmt.Printf("PROGRESS => 100\n")
	fmt.Printf("Enumeration complete. Found %d active subdomain.\n", atomic.LoadInt32(&activeCount))
}
