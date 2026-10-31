package socket

import (
	"os"
	"net"
	"time"
	"sync"
	"context"
	"strconv"
	"strings"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
)

func handleGetAddrInfo(ctx *ExecutionContext) packet.ResponsePacket {
	h1, p2, r1, r2, e1 := GetAddrInfo(ctx)
	if e1 != nil {
		return packet.ResponsePacket{Status: "ERROR", Message: e1.Error()}
	}
	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":    h1,
			"service": p2,
			"results": r1,
			"count":   r2,
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}


const (
	ni_Numerichost = 0x01 // Don't resolve hostname, return IP as is
	ni_Numericserv = 0x02 // Do not resolve service, return numeric port
	ni_Namereqd    = 0x04 // Error if hostname cannot be resolved
	ni_Dgram       = 0x08 // Use UDP protocol for lookup service (default TCP)
	ni_Nofqdn      = 0x10 // Return only hostname without domain (before first dot)
)

func loadService(path string) (map[int]map[string]string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	result := make(map[int]map[string]string)
	lines := strings.Split(string(data), "\n")

	for _, line := range lines {
		// Hapus komentar dan spasi berlebih.
		if idx := strings.Index(line, "#"); idx != -1 {
			line = line[:idx]
		}
		fields := strings.Fields(line)
		if len(fields) < 2 {
			continue
		}

		serviceName := fields[0]
		portProto := fields[1] // contoh: "80/tcp"

		parts := strings.Split(portProto, "/")
		if len(parts) != 2 {
			continue
		}

		portNum, err := strconv.Atoi(parts[0])
		if err != nil {
			continue
		}

		protocol := parts[1]
		if protocol != "tcp" && protocol != "udp" {
			continue
		}

		if result[portNum] == nil {
			result[portNum] = make(map[string]string)
		}

		if _, exists := result[portNum][protocol]; !exists {
			result[portNum][protocol] = serviceName
		}
	}
	return result, nil
}


func handleGetNameInfo(ctx *ExecutionContext) packet.ResponsePacket {
	addr, port, err := BuildTarget(ctx.Req.Host, ctx.Req.Port)
	if err != nil {
		return packet.ResponsePacket{
			Status:  "ERROR",
			Message: "Failed build target: " + err.Error(),
		}
	}

	hostFinal := DerefString(addr, "")
	portFinal := DerefString(port, "")
	flags := ParseFlags(ctx.Req.Flags)
	
	ip := net.ParseIP(hostFinal)
	if ip == nil {
		return packet.ResponsePacket{Status: "ERROR", Message: "Invalid IP address."}
	}

	var host string
	var serv string

	// -- Host / Reverse DNS --
	if flags&ni_Numerichost != 0 {
		host = ip.String()
	} else {
		names, err := net.DefaultResolver.LookupAddr(context.Background(), ip.String())
		if err != nil || len(names) == 0 {
			if flags&ni_Namereqd != 0 {
				return packet.ResponsePacket{Status: "ERROR", Message: err.Error()}
			}
			// Fallback to IP string if name not found
			host = ip.String()
		} else {
		    host = strings.TrimSuffix(names[0], ".")
		    // Extract hostname
		    if flags&ni_Nofqdn != 0 {
			    if idx := strings.Index(host, "."); idx != -1 {
				    host = host[:idx]
			    }
		    }
		}
	}

	// -- Service / Port --
	if flags&ni_Numericserv != 0 {
		serv = portFinal
	} else {
		protocol := "tcp"
		if flags&ni_Dgram != 0 {
			protocol = "udp"
		}

		var serviceMapOnce sync.Once
		var serviceMap map[int]map[string]string
		var serviceErr error
		
		serviceMapOnce.Do(func() {
			serviceMap, serviceErr = loadService("/etc/services")
		})
		if serviceErr != nil {
			serv = portFinal // Fallback to port number
		} 
		
		portNum, _ := strconv.Atoi(portFinal)
		if proto, ok := serviceMap[portNum]; ok {
			if name, ok := proto[protocol]; ok {
				serv = name
			}
		}
	}

	return packet.ResponsePacket{
		Status: "SUCCESS",
		Data: map[string]interface{}{
			"host":    host,
			"service": serv,
			"rtt_ms":  time.Since(ctx.StartTime).Milliseconds(),
		},
	}
}

