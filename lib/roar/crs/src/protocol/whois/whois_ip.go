package main

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"strings"
	"time"
)

const (
	// IANA adalah sumber kebenaran (source of truth) awal untuk blok IP
	ianaWhoisServer = "whois.iana.org:43"
	tcpTimeout = 5 * time.Second
)

// queryWhois menangani TCP socket connection ke server WHOIS yang spesifik
func queryWhois(server, query string) (string, error) {
	// Menggunakan DialTimeout sebagai best practice security/engineering
	conn, err := net.DialTimeout("tcp", server, tcpTimeout)
	if err != nil {
		return "", fmt.Errorf("Failed to connect to %s: %w", server, err)
	}
	defer conn.Close()

	// Set Deadline untuk keseluruhan proses Read/Write
	_ = conn.SetDeadline(time.Now().Add(tcpTimeout))

	// RFC 3912: Query diakhiri dengan \r\n
	_, err = conn.Write([]byte(query + "\r\n"))
	if err != nil {
		return "", fmt.Errorf("Failed to write query to %s: %w", server, err)
	}

	// Baca seluruh respons hingga EOF
	resp, err := io.ReadAll(conn)
	if err != nil {
		return "", fmt.Errorf("Failed to read response from %s: %w", server, err)
	}

	return string(resp), nil
}

// GetIPWhoisRecord mengeksekusi logical flow IANA Bootstrap -> RIR Server
func GetIPWhoisRecord(ip string) (string, error) {
	// Tahap 1: Query ke IANA
	ianaResp, err := queryWhois(ianaWhoisServer, ip)
	if err != nil {
		return "", err
	}

	// Tahap 2: Parsing respons IANA untuk mencari field 'refer:'
	var referServer string
	scanner := bufio.NewScanner(strings.NewReader(ianaResp))
	for scanner.Scan() {
		line := scanner.Text()
		// Format umumnya adalah "refer:        whois.apnic.net"
		if strings.HasPrefix(strings.ToLower(line), "refer:") {
			parts := strings.Fields(line)
			if len(parts) >= 2 {
				// Tambahkan port 43 untuk query TCP berikutnya
				referServer = parts[1] + ":43" 
				break
			}
		}
	}

	// Jika IANA tidak memberikan referral (misalnya IP private/invalid),
	// kembalikan saja raw response dari IANA
	if referServer == "" {
		return ianaResp, nil
	}

	// Tahap 3: Query ke server RIR yang otoritatif
	return queryWhois(referServer, ip)
}

func main() {
	// Contoh IP (Google Public DNS)
	targetIP := "8.8.8.8"
	
	fmt.Printf("[*] Memulai WHOIS Query untuk: %s\n", targetIP)
	
	record, err := GetIPWhoisRecord(targetIP)
	if err != nil {
		fmt.Printf("[!] Error: %v\n", err)
		return
	}
	
	fmt.Println("=== HASIL WHOIS ===")
	fmt.Println(record)
}

