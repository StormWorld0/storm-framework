// internal/source/models.go
package packet

// RequestPacket adalah cerminan dari dictionary yang dikirim Python
type RequestPacket struct {
	Primitive string            `json:"primitive"`
	
	// Parameter HTTP
	Method    string            `json:"method,omitempty"`
	URL       string            `json:"url,omitempty"`
	Body      string            `json:"body,omitempty"`
	Headers   map[string]string `json:"headers,omitempty"`
	
	// Parameter Umum
	Timeout   float64           `json:"timeout,omitempty"`
}

// ResponsePacket adalah balasan yang akan dibaca oleh Python
type ResponsePacket struct {
	Status  string      `json:"status"`
	Message string      `json:"message,omitempty"`
	
	// Data bebas (bisa map, array, string)
	Data    interface{} `json:"data,omitempty"`
}

// Handler adalah signature untuk semua fungsi protokol
type Handler func(RequestPacket) ResponsePacket
