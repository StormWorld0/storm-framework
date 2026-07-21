package packet

// RequestPacket adalah cerminan dari dictionary yang dikirim Python
type RequestPacket struct {
	Primitive string            `json:"primitive"`
	
	// Parameter HTTP
	Method    string            `json:"method,omitempty"`
	URL       string            `json:"url,omitempty"`
	Body      string            `json:"body,omitempty"`
	Headers   map[string]string `json:"headers,omitempty"`
	
	// Parameter umum
	Timeout   float64           `json:"timeout,omitempty"`
}

// ResponsePacket
type ResponsePacket struct {
	Status     string      `json:"status"`
	Message    string      `json:"message,omitempty"`
	
	// Data bebas (bisa map, array, string)
	Data       interface{} `json:"data,omitempty"`
}
