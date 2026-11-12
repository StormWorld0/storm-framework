package http

import (
	"crypto/x509"
	"crypto/tls"
	"net/http"
	"errors"
	"time"
	"net"
	"github.com/projectdiscovery/retryablehttp-go"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

func ExecuteStandard(req packet.RequestPacket, timeout time.Duration) packet.ResponsePacket {
	retryOptions := retryablehttp.DefaultOptionsSingle
	retryOptions.Timeout = timeout
	retryOptions.RetryMax = req.Retry

	client := retryablehttp.NewClient(retryOptions)

	var tlsCA *x509.CertPool
	if req.TLSCA != "" {
		var err error
	    tlsCA, err = buildCaTLS(req)
	    if err != nil {
		    return BuildErrorResponse("H-ERROR", "retryablehttp", "Failed build CA: "+err.Error())
	    }
    }

	// Transport Architecture for resource optimization and TLS handling
	client.HTTPClient.Transport = &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		TLSClientConfig: &tls.Config{
			RootCAs:            tlsCA,
			InsecureSkipVerify: !req.Verify,
			MinVersion:         tls.VersionTLS10,
			Renegotiation:      tls.RenegotiateOnceAsClient,
		},
		MaxIdleConns:          100,
		MaxIdleConnsPerHost:   10,
		IdleConnTimeout:       90 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	}

	if !req.Redirect {
		client.HTTPClient.CheckRedirect = func(r *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		}
	}

	bodyReader, err := ParseBody(req.Encoding, req.Body)
	if err != nil {
		return BuildErrorResponse("H-ERROR", "retryablehttp", "Body parse error: "+err.Error())
	}

	httpReq, err := retryablehttp.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		return BuildErrorResponse("H-ERROR", "retryablehttp", "Request creation failed: "+err.Error())
	}

	for key, value := range req.Headers {
        httpReq.Header.Set(key, value)
    }

	resp, err := client.Do(httpReq)
	if err != nil {
		var netErr net.Error
		if errors.As(err, &netErr) && netErr.Timeout() {
			return BuildErrorResponse("H-TIMEOUT", "retryablehttp", "Execution failed: "+err.Error())
		}
		return BuildErrorResponse("H-ERROR", "retryablehttp", "Execution failed: "+err.Error())
	}
	defer resp.Body.Close()

	if resp.StatusCode == 429 {
		utils.UpdateRateLimit(req)
	}

	return BuildSuccessResponse(resp, req.InfoTLS, "retryablehttp")
}
