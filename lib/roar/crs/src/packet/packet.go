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
	
	// General parameters
	Timeout   float64           `json:"timeout,omitempty"`
	RawMode   bool              `json:"rawmode"`             // True / False
	Redirect  bool              `json:"redirect"`            // True / False
	RateLimit int               `json:"ratelimit"`           // 0 = Unlimited
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
