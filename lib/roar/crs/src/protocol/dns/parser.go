package dns

import "github.com/miekg/dns"

// ParseAnswers mengubah DNS RR menjadi data yang mudah di-JSON.
func ParseAnswers(rrs []dns.RR) []interface{} {
	answers := make([]interface{}, 0, len(rrs))

	for _, rr := range rrs {
		answers = append(answers, ParseRR(rr))
	}

	return answers
}

// ParseRR mengekstrak nilai record DNS.
func ParseRR(rr dns.RR) interface{} {
	switch r := rr.(type) {

	case *dns.A:
		return r.A.String()

	case *dns.AAAA:
		return r.AAAA.String()

	case *dns.CNAME:
		return r.Target

	case *dns.NS:
		return r.Ns

	case *dns.PTR:
		return r.Ptr

	case *dns.TXT:
        if len(r.Txt) == 1 {
            return r.Txt[0]
        }
        return r.Txt

	case *dns.MX:
		return map[string]interface{}{
			"host":       r.Mx,
			"preference": r.Preference,
		}

	case *dns.SOA:
		return map[string]interface{}{
			"ns":      r.Ns,
			"mbox":    r.Mbox,
			"serial":  r.Serial,
			"refresh": r.Refresh,
			"retry":   r.Retry,
			"expire":  r.Expire,
			"minttl":  r.Minttl,
		}

	case *dns.SRV:
		return map[string]interface{}{
			"target":   r.Target,
			"port":     r.Port,
			"priority": r.Priority,
			"weight":   r.Weight,
		}

	case *dns.CAA:
		return map[string]interface{}{
			"flag":  r.Flag,
			"tag":   r.Tag,
			"value": r.Value,
		}

	case *dns.TLSA:
		return map[string]interface{}{
			"usage":        r.Usage,
			"selector":     r.Selector,
			"matchingType": r.MatchingType,
			"certificate":  r.Certificate,
		}

	case *dns.DNSKEY:
		return map[string]interface{}{
			"flags":     r.Flags,
			"protocol":  r.Protocol,
			"algorithm": r.Algorithm,
			"publicKey": r.PublicKey,
		}

	case *dns.DS:
		return map[string]interface{}{
			"keyTag":     r.KeyTag,
			"algorithm":  r.Algorithm,
			"digestType": r.DigestType,
			"digest":     r.Digest,
		}

	case *dns.RRSIG:
		return map[string]interface{}{
			"typeCovered": dns.TypeToString[r.TypeCovered],
			"algorithm":   r.Algorithm,
			"labels":      r.Labels,
			"origTTL":     r.OrigTtl,
			"expiration":  r.Expiration,
			"inception":   r.Inception,
			"keyTag":      r.KeyTag,
			"signerName":  r.SignerName,
			"signature":   r.Signature,
		}

	case *dns.LOC:
		return map[string]interface{}{
			"latitude":  r.Latitude,
			"longitude": r.Longitude,
			"altitude":  r.Altitude,
		}

	case *dns.SSHFP:
        return map[string]interface{}{
            "algorithm":         r.Algorithm,
            "fingerprint_type":  r.Type,
            "fingerprint":       r.FingerPrint,
        }

    case *dns.CERT:
        return map[string]interface{}{
            "type":       r.Type,
            "key_tag":    r.KeyTag,
            "algorithm":  r.Algorithm,
            "certificate": r.Certificate,
        }

    case *dns.URI:
        return map[string]interface{}{
            "priority": r.Priority,
            "weight":   r.Weight,
            "target":   r.Target,
        }

    case *dns.SVCB:
        return map[string]interface{}{
            "priority": r.Priority,
            "target":   r.Target,
            "value":    r.Value,
        }

    case *dns.HTTPS:
        return map[string]interface{}{
            "priority": r.Priority,
            "target":   r.Target,
            "value":    r.Value,
        }

	default:
		return rr.String()
	}
}
