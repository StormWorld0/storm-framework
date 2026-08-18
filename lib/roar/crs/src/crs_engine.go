// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"encoding/json"
	"os/signal"
	"syscall"
	"sync"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-sigChan
		cancel() // Batalkan semua konteks worker jika OS mengirim signal TERM/INT
		os.Stdin.Close()
	}()
	
	crs := bufio.NewScanner(os.Stdin)
	const maxCapacity = 10 * 1024 * 1024 // Max 10MB per JSON line
	buf := make([]byte, 64*1024)
	crs.Buffer(buf, maxCapacity)

	var req packet.RequestPacket
	// Inisialisasi Global ratelimiter
	utils.InitGlobalRateLimiter(req)

	// Channel sebagai Fan-In untuk mengumpulkan semua response secara thread-safe.
	// Buffer dialokasikan (misal 1000) untuk mencegah backpressure pada worker.
	responseChan := make(chan packet.ResponsePacket, 1000)
	
	var wgWorkers sync.WaitGroup
	// Map thread-safe untuk menyimpan Semaphore (Channel) per-protokol
	// Key: req.Primitive (string), Value: chan struct{} (Semaphore)
	var semaphores sync.Map 
	writerDone := make(chan struct{})

	// DEDICATED WRITER GOROUTINE
	go func() {
		defer close(writerDone)
		for res := range responseChan {
			sendResponse(res)
		}
	}()
	
	// READER & DISPATCHER LOOP
	for crs.Scan() {
		line := crs.Bytes()

		select {
		case <-ctx.Done():
			goto Shutdown
		default:
		}

		// Unmarshal dilakukan di main goroutine agar aman dari race condition 
		// terhadap memory internal buffer scanner.Bytes()
		var req packet.RequestPacket
		if err := json.Unmarshal(line, &req); err != nil {
			select {
			case responseChan <- packet.ResponsePacket{Status: "ERROR", Message: "Invalid JSON: " + err.Error()}:
			case <-ctx.Done():
				goto Shutdown
			}
			continue
		}

		// [MODE SYNCHRONOUS]: Untuk protokol yang tidak thread-safe
		if req.Go <= 0 {
			var res packet.ResponsePacket
			handler, ok := protocol.Handlers[req.Primitive]
			if !ok {
				res = packet.ResponsePacket{
					Status: "ERROR", 
					Message: "Unknown primitive: " + req.Primitive,
				}
			} else {
				res = handler(req) // Eksekusi memblokir scanner loop
			}
			select {
			case responseChan <- res:
			case <-ctx.Done():
				goto Shutdown
			}
			continue
		}

		// [MODE ASYNCHRONOUS DENGAN SEMAPHORE]: Untuk protokol yang mendukung concurrency
		// Load atau inisialisasi semaphore dengan kapasitas req.Go
		semIntf, _ := semaphores.LoadOrStore(req.Primitive, make(chan struct{}, req.Go))
		sem := semIntf.(chan struct{})

		// Acquire Token dengan Cancellation Aware
		select {
		case sem <- struct{}{}:
		case <-ctx.Done():
			goto Shutdown
		}
		
		wgWorkers.Add(1)

		// FAN-OUT WORKER GOROUTINE
		go func(r packet.RequestPacket, semaphore chan struct{}) {
			defer wgWorkers.Done()
			
			// Release Token: Mengembalikan kuota ke semaphore saat eksekusi selesai
			defer func() { <-semaphore }() 

			var res packet.ResponsePacket
			handler, ok := protocol.Handlers[r.Primitive]
			if !ok {
				res = packet.ResponsePacket{
					Status: "ERROR", 
					Message: "Unknown primitive: " + r.Primitive,
				}
			} else {
				res = handler(r)
			}

			// Safe send: Cegah deadlock jika writer/main sudah shutdown
			select {
			case responseChan <- res:
			case <-ctx.Done():
				return
			}
		}(req, sem)
	}
	// Stdin EOF terdeteksi -> Trigger cancellation untuk sisa worker
	Shutdown:
	cancel()
	
	if err := crs.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "CRS Engine Stdin Error: %v\n", err)
	}

	// Memastikan Go exited sebelum timeout dan mengirim SIGKILL
	shutdownComplete := make(chan struct{})
	go func() {
		wgWorkers.Wait()
		close(responseChan)
		<-writerDone
		close(shutdownComplete)
	}()

	select {
	case <-shutdownComplete:
		os.Exit(0)
	case <-time.After(1000 * time.Millisecond):
		fmt.Fprintf(os.Stderr, "CRS Engine: Force exit due to worker timeout\n")
		os.Exit(1)
	}
}

func sendResponse(res packet.ResponsePacket) {
	out, err := json.Marshal(res)
	if err != nil {
		os.Stdout.WriteString(`{"status":"ERROR","message":"Failed to marshal response"}` + "\n")
		os.Stdout.Sync()
		return
	}
	os.Stdout.Write(out)
	os.Stdout.WriteString("\n")
	os.Stdout.Sync()
}
