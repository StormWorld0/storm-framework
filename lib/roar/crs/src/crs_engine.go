// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	// Membaca input baris per baris dari Python (Subprocess stdin)
	scanner := bufio.NewScanner(os.Stdin)

	for scanner.Scan() {
		line := scanner.Bytes()

		var req RequestPacket
		// Ubah JSON string jadi struct Golang
		if err := json.Unmarshal(line, &req); err != nil {
			sendResponse(ResponsePacket{Status: "ERROR", Message: "Invalid JSON from Python"})
			continue
		}

		var res ResponsePacket

		// ROUTER: Arahkan berdasarkan nama Primitive
		switch req.Primitive {
		case "HTTP_SEND":
			res = executeHTTP(req)
    case "DNS_LOOKUP":
      res = executeDNS(req)
		default:
			res = ResponsePacket{Status: "ERROR", Message: "Unknown primitive: " + req.Primitive}
		}

		// Kirim balikan ke Python
		sendResponse(res)
	}
}

// sendResponse mengubah struct jadi JSON 1 baris lalu mencetaknya ke stdout
func sendResponse(res ResponsePacket) {
	out, err := json.Marshal(res)
	if err != nil {
		fmt.Println(`{"status":"ERROR","message":"Failed to marshal response"}`)
		return
	}
	fmt.Println(string(out))
}

