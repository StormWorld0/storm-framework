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
	"time"

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
		cancel() // Cancel all worker contexts if the OS sends SIGTERM
		os.Stdin.Close() // Close stdin
		utils.Stop() // Stopping ratelimiter
	}()
	
	crs := bufio.NewScanner(os.Stdin)
	const maxCapacity = 10 * 1024 * 1024 // Max 10MB per JSON line
	buf := make([]byte, 64*1024)
	crs.Buffer(buf, maxCapacity)
	
	// Global ratelimiter initialization
	utils.InitRateLimiterManager(ctx)

	// Thread-safe map for storing per-protocol Semaphores (Channels)
	// Key: req.Primitive (string), Value: chan struct{} (Semaphore)
	var semaphores sync.Map 
	var wgWorkers sync.WaitGroup

	// Channel as Fan-In to collect all responses in a thread-safe manner.
	// Buffers are allocated (1000) to prevent backpressure on the worker.
	responseChan := make(chan packet.ResponsePacket, 1000)
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

		// Unmarshal is done in the main goroutine to avoid race conditions
		// against the scanner's internal memory buffer.Bytes()
		var req packet.RequestPacket
		if err := json.Unmarshal(line, &req); err != nil {
			select {
			case responseChan <- packet.ResponsePacket{Status: "ERROR", Message: "Invalid JSON: " + err.Error()}:
			case <-ctx.Done():
				goto Shutdown
			}
			continue
		}

		// [MODE SYNCHRONOUS]: For non-thread-safe protocols
		if req.Go <= 0 {
			var res packet.ResponsePacket
			handler, ok := protocol.Handlers[req.Primitive]
			if !ok {
				res = packet.ResponsePacket{
					Status: "ERROR", 
					Message: "Unknown primitive: " + req.Primitive,
				}
			} else {
				res = handler(req) // Execution blocking loop scanner
			}

			// IMPORTANT: Copy the MsgID from Request to Response
			// so that the results that come out are not thrown away.
			res.MsgID = req.MsgID
			
			select {
			case responseChan <- res:
			case <-ctx.Done():
				goto Shutdown
			}
			continue
		}

		// [ASYNCHRONOUS MODE WITH SEMAPHORE]: For protocols that support concurrency
		// This is also used so that the primitives being executed do not block the main thread.
		// Load or initialize semaphore with req.Go capacity to be dynamic.
		var sem chan struct{}
        if semIntf, ok := semaphores.Load(req.Primitive); ok {
            sem = semIntf.(chan struct{})
        } else {
            // Memory allocation ONLY occurs when a primitive is called for the first time.
            newSem := make(chan struct{}, req.Go)
            actual, _ := semaphores.LoadOrStore(req.Primitive, newSem)
            sem = actual.(chan struct{})
        }

		// Acquire Token with Cancellation Aware
		select {
		case sem <- struct{}{}:
		case <-ctx.Done():
			goto Shutdown
		}
		
		wgWorkers.Add(1)

		// FAN-OUT WORKER GOROUTINE
		go func(r packet.RequestPacket, semaphore chan struct{}) {
			defer wgWorkers.Done()
			
			// Release Token: Returns the quota to the semaphore when execution is complete.
			defer func() { <-semaphore }()

			// Initialize Ratelimit Set
			utils.SetPrimitiveRate(r.Primitive, r.RateLimit)
			utils.Take(r.Primitive) // Take ratelimit token

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

			// Copy MsgID from Request to Response
			res.MsgID = r.MsgID

			// Safe send: Prevent deadlock if writer/main is already shutdown
			select {
			case responseChan <- res:
			case <-ctx.Done():
				return
			}
		}(req, sem)
	}
	// Stdin EOF detected -> Trigger cancellation for remaining workers
	Shutdown:
	cancel()
	
	if err := crs.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "CRS Engine Stdin Error: %v\n", err)
	}

	// Make sure Go exited before timeout and SIGKILL
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
	case <-time.After(500 * time.Millisecond):
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
