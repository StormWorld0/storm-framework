// https://github.com/StormWorld0/storm-framework
// License SMF
// Author zxelzy
package dns

import (
	"strings"
	"net"
	"time"

	"github.com/miekg/dns"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

// DNS menangani request DNS terstandarisasi berbasis miekg/dns
func Lookup(req packet.RequestPacket) packet.ResponsePacket {
	utils.Take()
	
	target := req.Domain
    if target == "" {
        return packet.ResponsePacket{Status: "ERROR", Message: "Domain not found"}
	}

	timeout := time.Duration(req.Timeout * float64(time.Second))
	if timeout == 0 {
		timeout = 5 * time.Second
	}

	qtype, ok := dns.StringToType[req.Type]
    if !ok {
        return packet.ResponsePacket{
            Status: "ERROR",
            Message: "Unsupported DNS query type",
        }
    }

	// Konstruksi DNS Message secara native
	reqMsg := new(dns.Msg)
	reqMsg.SetQuestion(dns.Fqdn(target), qtype)
	reqMsg.RecursionDesired = true

	protocol := strings.ToLower(req.Protocol)
    if protocol == "" {
        protocol = "udp"
    }
	switch protocol {
        case "udp", "tcp": // valid
        default:
            return packet.ResponsePacket{Status: "ERROR", Message: "Unsupported DNS protocol"}
    }

	// Konfigurasi Client
	client := &dns.Client{
		Net:     protocol, // "udp" atau "tcp"
		Timeout: timeout,
	}

	// Format target address dengan port 53 jika belum ada
	targetAddr := target
	if _, _, err := net.SplitHostPort(target); err != nil {
		targetAddr = net.JoinHostPort(target, "53")
	}

	// Eksekusi query DNS
	respMsg, _, err := client.Exchange(reqMsg, targetAddr)
	if err != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "DNS Exchange failed: " + err.Error()}
	}

	// Implementasi TCP Fallback otomatis jika respons terpotong (Truncated)
	if respMsg.Truncated && client.Net != "tcp" {
		client.Net = "tcp"
		respMsg, _, err = client.Exchange(reqMsg, targetAddr)
		if err != nil {
			return packet.ResponsePacket{Status: "ERROR", Message: "TCP Fallback Exchange failed: " + err.Error()}
		}
	}

	// Ekstraksi record untuk kebutuhan rule evaluation
	answers := ParseAnswers(respMsg.Answer)

	// Return terstruktur
	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"rcode":     respMsg.Rcode,
			"rcode_str": dns.RcodeToString[respMsg.Rcode],
			"records":   answers,
			"truncated": respMsg.Truncated,
			"authoritative": respMsg.Authoritative,
		},
	}
}

