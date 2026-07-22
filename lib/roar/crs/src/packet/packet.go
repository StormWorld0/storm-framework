package packet

// RequestPacket is a mirror of the dictionary that Python sends
type RequestPacket struct {
	Primitive string            `json:"primitive"`
	
	// HTTP
	Method    string            `json:"method,omitempty"`    // GET, POST, PUT, DELETE, ...
	URL       string            `json:"url,omitempty"`
	Body      string            `json:"body,omitempty"`
	Headers   map[string]string `json:"headers,omitempty"`

	// DNS
    Domain   string             `json:"domain,omitempty"`
    Type     string             `json:"type,omitempty"`      // A, AAAA, MX, TXT, ...
    Protocol string             `json:"protocol,omitempty"`  // udp, tcp, tls, ssl

	// Standard parameters
	Host      string            `json:"host,omitempty"`      // URL / IP
	Ip        int               `json:"ip,omitempty"`
	Port      int               `json:"port,omitempty"`      // PORT 1 - 65535
	
	// General parameters
	Timeout   float64           `json:"timeout,omitempty"`
	RawMode   bool              `json:"rawmode"`             // True / False
	Redirect  bool              `json:"redirect"`            // True / False
	Verify    bool              `json:"verify"`              // True / False
	InfoTLS   bool              `json:"info_tls"`            // True / False
	RateLimit int               `json:"ratelimit"`           // 0 = Unlimited
	Retry     int               `json:"retry"`               // Retry connection
	Encoding  string            `json:"encoding,omitempty"`  // Hex / Text
	ReadSize  int               `json:"readsize"`            // Limit Read Buffer
}

// ResponsePacket
type ResponsePacket struct {
	Status     string      `json:"status"`
	Message    string      `json:"message,omitempty"`
	
	// Free data (can be map, array, string)
	Data       interface{} `json:"data,omitempty"`
}
