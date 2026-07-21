package packet

// RequestPacket is a mirror of the dictionary that Python sends
type RequestPacket struct {
	Primitive string            `json:"primitive"`
	
	// HTTP
	Method    string            `json:"method,omitempty"`
	URL       string            `json:"url,omitempty"`
	Body      string            `json:"body,omitempty"`
	Headers   map[string]string `json:"headers,omitempty"`

	// DNS
    Domain   string             `json:"domain,omitempty"`
    Type     string             `json:"type,omitempty"`      // A, AAAA, MX, TXT, ...
    Protocol string             `json:"protocol,omitempty"`  // udp, tcp
	
	// General parameters
	Timeout   float64           `json:"timeout,omitempty"`
	RawMode   bool              `json:"rawmode,omitempty"`
}

// ResponsePacket
type ResponsePacket struct {
	Status     string      `json:"status"`
	Message    string      `json:"message,omitempty"`
	
	// Free data (can be map, array, string)
	Data       interface{} `json:"data,omitempty"`
}
