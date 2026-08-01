// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sync"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol"
)

func main() {
	crs := bufio.NewCRS(os.Stdin)
	const maxCapacity = 10 * 1024 * 1024 // Max 10MB per JSON line
	buf := make([]byte, 64*1024)
	crs.Buffer(buf, maxCapacity)

	// Channel sebagai Fan-In untuk mengumpulkan semua response secara thread-safe.
	// Buffer dialokasikan (misal 1000) untuk mencegah backpressure pada worker.
	responseChan := make(chan packet.ResponsePacket, 1000)
	
	var wgWorkers sync.WaitGroup
	// Map thread-safe untuk menyimpan Semaphore (Channel) per-protokol
	// Key: req.Primitive (string), Value: chan struct{} (Semaphore)
	var semaphores sync.Map 
	writerDone := make(chan struct{})

	// DEDICATED WRITER GOROUTINE
	// Hanya goroutine ini yang diizinkan menulis ke os.Stdout
	go func() {
		for res := range responseChan {
			sendResponse(res)
		}
		// Kirim sinyal bahwa semua data di channel sudah di-flush ke stdout
		close(writerDone) 
	}()

	// READER & DISPATCHER LOOP
	for crs.Scan() {
		line := crs.Bytes()

		// Unmarshal dilakukan di main goroutine agar aman dari race condition 
		// terhadap memory internal buffer scanner.Bytes()
		var req packet.RequestPacket
		if err := json.Unmarshal(line, &req); err != nil {
			responseChan <- packet.ResponsePacket{
				Status: "ERROR", 
				Message: "Invalid JSON: " + err.Error(),
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
			responseChan <- res
			continue
		}

		// [MODE ASYNCHRONOUS DENGAN SEMAPHORE]: Untuk protokol yang mendukung concurrency
		// Load atau inisialisasi semaphore dengan kapasitas req.Go
		semIntf, _ := semaphores.LoadOrStore(req.Primitive, make(chan struct{}, req.Go))
		sem := semIntf.(chan struct{})

		// Acquire Token: Akan memblokir scanner JIKA goroutine untuk protokol ini 
		// sudah mencapai batas maksimal (req.Go).
		sem <- struct{}{}

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

			responseChan <- res
		}(req, sem)
	}
	if err := crs.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "CRS Engine Stdin Error: %v\n", err)
	}

	// GRACEFUL SHUTDOWN
	wgWorkers.Wait()
	close(responseChan)
	<-writerDone
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
	os.Stdout.Sync() // Memastikan flush per baris untuk interaksi pipe dengan Python
}
