package http

import (
	"crypto/tls"
	"net/http"
	"time"

	"github.com/projectdiscovery/retryablehttp-go"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/packet"
	"github.com/StormWorld0/storm-framework/lib/roar/crs/src/utils"
)

func ExecuteStandard(req packet.RequestPacket, timeout time.Duration) packet.ResponsePacket {
	retryOptions := retryablehttp.DefaultOptionsSingle
	retryOptions.Timeout = timeout
	retryOptions.RetryMax = req.Retry

	client := retryablehttp.NewClient(retryOptions)

	// Arsitektur Transport untuk optimalisasi resource dan penanganan TLS bypass
	client.HTTPClient.Transport = &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: !req.Verify,
			MinVersion:         tls.VersionTLS10,
			Renegotiation:      tls.RenegotiateOnceAsClient, // Penting untuk beberapa bypass WAF
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

	bodyReader, err := ParseBody(req.Body)
	if err != nil {
		return BuildErrorResponse("ERROR", "retryablehttp", "Body parse error: "+err.Error())
	}

	httpReq, err := retryablehttp.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		return BuildErrorResponse("ERROR", "retryablehttp", "Request creation failed: "+err.Error())
	}

	httpReq.Header.Set("User-Agent", GetUserAgent(req.UA))

	resp, err := client.Do(httpReq)
	if err != nil {
		if errors.As(err, &netErr) && netErr.Timeout() {
			return BuildErrorResponse("TIMEOUT", "rawhttp", "Execution failed: "+err.Error())
		}
		return BuildErrorResponse("ERROR", "retryablehttp", "Execution failed: "+err.Error())
	}
	defer resp.Body.Close()

	if resp.StatusCode == 429 {
		utils.UpdateGlobalRate(req.Frl)
	}

	return BuildSuccessResponse(resp, req.InfoTLS, "retryablehttp")
}
