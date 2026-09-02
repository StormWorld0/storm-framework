package waf

// Signature mendefinisikan pola (fingerprint) dari sebuah WAF.
type Signature struct {
	Name         string
	Vendor       string
	// Matchers
	Headers      map[string]string // Key header spesifik atau Key-Value
	Cookies      []string          // Prefix cookie spesifik
	BodyContains []string          // String spesifik pada response body
	StatusCodes  []int             // Status code yang sering dikembalikan (misal: 403, 406)
}

// DefaultSignatures berisi basis data WAF yang umum.
// Dalam arsitektur produksi, data ini idealnya di-load dari file JSON/YAML 
// agar tidak perlu re-compile saat ada update signature WAF baru.
var DefaultSignatures = []Signature{
	{
		Name:         "Cloudflare",
		Vendor:       "Cloudflare Inc.",
		Headers:      map[string]string{"Server": "cloudflare"},
		Cookies:      []string{"__cf_duid", "cf_clearance"},
		BodyContains: []string{"Attention Required! | Cloudflare", "Ray ID:"},
		StatusCodes:  []int{403},
	},
	{
		Name:         "ModSecurity",
		Vendor:       "SpiderLabs",
		Headers:      map[string]string{"Server": "Mod_Security", "Server": "NOYB"},
		BodyContains: []string{"Not Acceptable", "ModSecurity Action"},
		StatusCodes:  []int{406, 403},
	},
	{
		Name:         "Imperva / Incapsula",
		Vendor:       "Imperva",
		Headers:      map[string]string{"X-Iinfo": "", "X-CDN": "Incapsula"},
		Cookies:      []string{"incap_ses_"},
		BodyContains: []string{"Request Unsuccessful", "Incapsula incident ID"},
		StatusCodes:  []int{403},
	},
}
