package packet

// RequestPacket is a mirror of the dictionary that Python sends
type RequestPacket struct {
	MsgID     string            `json:"msg_id"`              // ID Requests are random and automatically generated.
	Primitive string            `json:"primitive"`           // Special flag to mark the protocol used
	Go        int               `json:"goroutine"`           // Allocate the number of Goroutines
	UA        string            `json:"user-agent"`          // User-Agent Random or Input
	
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
	Timeout   float64           `json:"timeout,omitempty"`   // float / default
	RawMode   bool              `json:"rawmode"`             // True / False
	Redirect  bool              `json:"redirect"`            // True / False
	Verify    bool              `json:"verify"`              // True / False
	InfoTLS   bool              `json:"info_tls"`            // True / False
	RateLimit int               `json:"ratelimit"`           // 0 = Unlimited
	Retry     int               `json:"retry"`               // Retry connection
	Encoding  string            `json:"encoding,omitempty"`  // Hex
	ReadSize  int               `json:"readsize"`            // Limit Read Buffer
	SessionID string            `json:"session_id,omitempty"`// Session ID to use the same connection
	KeepAlive bool              `json:"keep-alive"`          // Keep-Alive to determine whether a stream connection is active or not.
	CloseSess bool              `json:"close-session"`       // Boolean to close active session.
	Mode      string            `json:"mode"`                // To determine which mode you want to use.
	Data      string            `json:"data,omitempty"`      // This data is encoded to b64 and string before entering json
	Bool      bool              `json:"bool"`                // Determines True or False. If empty, False.
	
	// Custom TLS family
	TLSKey    string            `json:"tls-key,omitempty"`   // TLSKey = Can path can raw pem
	TLSCert   string            `json:"tls-cert,omitempty"`  // TLSCer = Can path can raw pem
	TLSCA     string            `json:"tls-ca,omitempty"`    // TLSCA  = Can path can raw pem
}

// ResponsePacket
type ResponsePacket struct {
	MsgID     string            `json:"msg_id"`              // Response ID uses the same ID as Requests.
	Status    string            `json:"status"`              // ERROR / SUCCESS / TIMEOUT / ...
	Message   string            `json:"message,omitempty"`   // Error message or success message
	Data      interface{}       `json:"data,omitempty"`      // Free data (can be map, array, string)
}
