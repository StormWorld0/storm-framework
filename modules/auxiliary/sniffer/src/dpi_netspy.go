// MIT License.
// Copyright (c) 2026 Storm Framework
// See LICENSE file in the project root for full license information.

package main
import (
	"fmt"
	"log"
	"os"
	"strings"
	"github.com/google/gopacket"
	"github.com/google/gopacket/pcap"
)
func main() {
	// Checks whether interface arguments are given
	if len(os.Args) < 2 {
		fmt.Println("[!] Use: ./sniffer <interface>")
		os.Exit(1)
	}

	device := os.Args[1] // Takes the interface from the first argument

	// Opening the device for sniffing
	handle, err := pcap.OpenLive(device, 1024, true, pcap.BlockForever)
	if err != nil {
		log.Fatalf("[!] Failed to open device %s: %v", device, err)
	}
	defer handle.Close()

	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
	fmt.Printf("[*] Storm Go-Sniffer active di %s...\n", device)

	for packet := range packetSource.Packets() {
		if appLayer := packet.ApplicationLayer(); appLayer != nil {
			payload := string(appLayer.Payload())

			// Simple payload analysis for credentials
			keywords := []string{"user", "pass", "login", "pwd", "auth"}
			for _, key := range keywords {
				if strings.Contains(strings.ToLower(payload), key) {
					fmt.Printf("\n[!] DATA DETECTED IN %s:\n%s\n", device, payload)
					break
				}
			}
		}
	}
}
