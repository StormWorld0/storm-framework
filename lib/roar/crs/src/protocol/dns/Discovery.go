// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package dns

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

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	ctls "github.com/StormWorld0/storm-framework/lib/roar/crs/src/tls"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
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

func worker(jobs <-chan Job, wg *sync.WaitGroup, foundCounter *int32, req packet.RequestPacket) packet.ResponsePacket {
	defer wg.Done()
	for job := range jobs {
		// Menggunakan anonymous function agar defer (seperti body.Close) dieksekusi dengan aman per iterasi
		func(j Job) {
			req, err := http.NewRequest("HEAD", j.URL, nil)
			if err != nil {
				return
			}
			
			ua := "storm-framework/3.0 (CRS Engine)"
	        if req.UA != "" {
		        ua = req.UA
	        }
	        httpReq.Header.Set("User-Agent", ua)
			
			resp, err := httpClient.Do(httpReq)
			if err != nil {
				return
			}
			defer resp.Body.Close()

			headers := make(map[string]interface{}, len(resp.Header))
	            for k, v := range resp.Header {
	        	    if len(v) == 1 {
			            headers[k] = v[0]
		            } else {
			            headers[k] = v
		        }
	        }

			// Closure metadata
	        generateMetadata := func() map[string]interface{} {
		        meta := map[string]interface{}{
			        "status_code": resp.StatusCode,
			        "headers":     headers,
			        "protocol":    resp.Proto,
			        "active-url":  atomic.LoadInt32(&activeCount),
			        "url":         targetURL,
			        "engine":      "Discovery",
		        }
		        if req.InfoTLS && resp.TLS != nil {
					state = resp.TLS
			        meta["info_tls"] = ctls.ExtractTLSInfoFromState(state)
		        }
		        return meta
	        }
			
			if resp.StatusCode < 400 || resp.StatusCode == 403 || resp.StatusCode == 401 {
				atomic.AddInt32(foundCounter, 1)
				return packet.ResponsePacket{
			        Status: "SUCCESS",
			        Data:   generateMetadata(),
		        }
			}
		}(job)
	}
}

func Discovery(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take() // rate-limiter

	targetDomain := strings.TrimPrefix(strings.TrimPrefix(req.Domain, "http://"), "https://")
	domain = strings.Trim(targetDomain, "/")

	file, err := os.Open(req.Word)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Error opening wordlist: " + err.Error()}
	}
	defer file.Close()

	jobs := make(chan Job, req.Concurrency)
	var wg sync.WaitGroup
	
	var activeCount int32 = 0 // Mencatat subdomain yang FOUND

	// Spawning Worker Pool
	for i := 0; i < req.Concurrency; i++ {
		wg.Add(1)
		go worker(jobs, &wg, &activeCount, req)
	}

	// Stream Reading untuk pemrosesan riil
	scanner := bufio.NewScanner(file)
	protocols := []string{"http", "https"}

	for scanner.Scan() {
		subdomain := strings.TrimSpace(scanner.Text())
		if subdomain == "" || strings.HasPrefix(subdomain, "#") {
			continue
		}

		for _, proto := range protocols {
			url := fmt.Sprintf("%s://%s.%s", proto, subdomain, domain)
			jobs <- Job{URL: url}
		}
	}

	if err := scanner.Err(); err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Error while reading wordlist: " + err.Error()}
	}

	close(jobs)
	wg.Wait()
}
