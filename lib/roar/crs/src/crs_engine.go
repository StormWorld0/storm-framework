// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol"
)

func main() {
	// Membaca input baris per baris dari Python (Subprocess stdin)
	scanner := bufio.NewScanner(os.Stdin)

	for scanner.Scan() {
		line := scanner.Bytes()

		var req protocol.RequestPacket
		if err := json.Unmarshal(line, &req); err != nil {
			sendResponse(protocol.ResponsePacket{Status: "ERROR", Message: "Invalid JSON"})
			continue
		}
		
		var res protocol.ResponsePacket

		handler, ok := protocol.Handlers[req.Primitive]
		if !ok {
			res = protocol.ResponsePacket{
				Status:  "ERROR",
				Message: "Unknown primitive: " + req.Primitive,
			}
		} else {
			// Eksekusi handler yang cocok
			res = handler(req)
		}

		// Kirim balikan ke Python
		sendResponse(res)
	}
}

// sendResponse mengubah struct jadi JSON 1 baris lalu mencetaknya ke stdout
func sendResponse(res protocol.ResponsePacket) {
	out, err := json.Marshal(res)
	if err != nil {
		fmt.Println(`{"status":"ERROR","message":"Failed to marshal response"}`)
		return
	}
	fmt.Println(string(out))
}
