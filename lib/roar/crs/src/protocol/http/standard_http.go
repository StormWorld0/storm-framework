package http

import (
	"crypto/x509"
	"net/http"
	"errors"
	"time"
	"net"
	utls "github.com/refraction-networking/utls"
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

	// Transport Architecture for resource optimization
	tr := &http.Transport{
		Proxy:                 http.ProxyFromEnvironment,
		MaxIdleConns:          100,
		MaxIdleConnsPerHost:   10,
		IdleConnTimeout:       90 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	}

	tr.DialTLSContext = func(ctx context.Context, network, addr string) (net.Conn, error) {
		// Runs the transport's built-in TCP dial (automatically handles ProxyFromEnvironment)
		rawConn, err := tr.DialContext(ctx, network, addr)
		if err != nil {
			return nil, err
		}

		// Extract hostname for SNI
		host, _, err := net.SplitHostPort(addr)
		if err != nil {
			host = addr
		}

		// utls.Config configuration
		uConfig := &utls.Config{
			RootCAs:            tlsCA,
			InsecureSkipVerify: !req.Verify,
			MinVersion:         utls.VersionTLS10,
			ServerName:         host,
		}

		clientHello := utls.HelloChrome_Auto // Disguised as Chromium
		uConn := utls.UClient(rawConn, uConfig, clientHello)

		// Manually execute uTLS Handshake
		if err := uConn.Handshake(); err != nil {
			rawConn.Close()
			return nil, err
		}

		return uConn, nil
	}

	// Install custom transport to retryablehttp
	client.HTTPClient.Transport = tr

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
