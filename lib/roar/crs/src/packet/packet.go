package packet

// RequestPacket is a mirror of the dictionary that Python sends
type RequestPacket struct {
	Primitive string            `json:"primitive"`
	
	// HTTP
	Method    string            `json:"method,omitempty"`    // GET, POST, PUT, DELETE, ...
	URL       string            `json:"url,omitempty"`       // https / http
	Body      string            `json:"body,omitempty"`      // The body can be anything including the payload
	Headers   map[string]string `json:"headers,omitempty"`   // Header can be customized if socket

	// DNS
    Domain   string             `json:"domain,omitempty"`    // example.com
    Type     string             `json:"type,omitempty"`      // A, AAAA, MX, TXT, ...
    Protocol string             `json:"protocol,omitempty"`  // udp, tcp, tls, ssl

	// Standard parameters
	Host      string            `json:"host,omitempty"`      // URL / IP / Domain
	Ip        int               `json:"ip,omitempty"`        // 127.0.0.1
	Port      int               `json:"port,omitempty"`      // PORT 1 - 65535
	
	// General parameters
	Timeout   float64           `json:"timeout,omitempty"`
	RawMode   bool              `json:"rawmode"`             // True / False
	Redirect  bool              `json:"redirect"`            // True / False
	Verify    bool              `json:"verify"`              // True / False
	InfoTLS   bool              `json:"info_tls"`            // True / False
	RateLimit int               `json:"ratelimit"`           // 0 = Unlimited
	Retry     int               `json:"retry"`               // Retry connection
	Encoding  string            `json:"encoding,omitempty"`  // Hex
	ReadSize  int               `json:"readsize"`            // Limit Read Buffer
	SessionID string            `json:"session_id,omitempty"`// Session ID to use the same connection
	KeepAlive bool              `json:"keep-alive"`          // true = do not close the socket after Read
	CloseSess bool              `json:"close-session"`       // true = force close the session in memory
	mode      string            `json:"mode"`                // duplex = default, send_only = send without read buffer, recv_only = read only buffer.
}

// ResponsePacket
type ResponsePacket struct {
	Status    string            `json:"status"`              // ERROR / SUCCESS / TIMEOUT / ...
	Message   string            `json:"message,omitempty"`   // Error message or success message
	Data      interface{}       `json:"data,omitempty"`      // Free data (can be map, array, string)
}
