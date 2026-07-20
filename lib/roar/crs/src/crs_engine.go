// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/protocol"
)

func main() {
	// Membaca input baris per baris dari Python (Subprocess stdin)
	scanner := bufio.NewScanner(os.Stdin)

	for scanner.Scan() {
		line := scanner.Bytes()

		var req packet.RequestPacket
		if err := json.Unmarshal(line, &req); err != nil {
			sendResponse(packet.ResponsePacket{Status: "ERROR", Message: "Invalid JSON"})
			continue
		}
		
		var res packet.ResponsePacket

		handler, ok := protocol.Handlers[req.Primitive]
		if !ok {
			res = packet.ResponsePacket{
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
func sendResponse(res packet.ResponsePacket) {
	out, err := json.Marshal(res)
	if err != nil {
		fmt.Println(`{"status":"ERROR","message":"Failed to marshal response"}`)
		return
	}
	fmt.Println(string(out))
}
