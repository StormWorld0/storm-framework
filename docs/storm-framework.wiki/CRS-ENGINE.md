# ⚡ Connection Runtime Service (CRS)

Connection Runtime Service (CRS) is an in-house network & transport engine based on Go (Golang) designed to replace dependency on external/third-party networking libraries (like requests, http_requests, socket, etc.)

By abstracting network communications into a CRS, The system gains full control over transport behavior, memory footprint, security boundaries, and performance optimization through Go's built-in concurrency model.

### ⚙️ Architectural Motivation

- **Dependency Decoupling & Supply Chain Security:** Reduces the risk of vulnerabilities and breaking changes from third-party libraries by isolating all I/O operations into one centralized engine.
- **Performance & Low Latency:** Leverages Go's execution speed and I/O model to minimize overhead when handling high-density communications.
- **Connection Stability:** Provides custom connection pooling management, retry mechanisms, and predictable timeout handling.
- **Concurrency Management:** Leverage native Go Routines to handle concurrent I/O tasks efficiently with controlled resource consumption.

### 📝 Technical Specifications

**Tech Stack & Runtime**
- **Language:** Go (Golang)
- **Primary Paradigm:** Asynchronous / Non-blocking I/O (via Goroutines & Channels)
- **Interface Boundary:** Accessible via Wrapper & IPC Layer

**Supported Protocols & Status**  
Currently CRS implements a subset of network protocols focused on the system's core requirements. Although the protocol coverage is still being developed, the existing implementation has been optimized (tuned) and passed validation testing on various production modules.

### Some of the available;

- **http_requests**: REST API & Web Resource Delivery
- **requests**: DNS Query Resolution or DNS Resolution
- **socket**: Low-level Stream Communication

**Note on Concurrency:** Although Goroutines are widely used across engines, Some specific protocol handlers still use precise synchronous/sequential execution to avoid race conditions or out-of-order execution in stateful protocols.

---

## 🛠️ Ways of working CRS

```mermaid
sequenceDiagram
    autonumber
    participant M as Module
    participant W as API
    participant I as IPC Layer
    participant C as CRS Engine

    Note over M,W: Client Context
    M->>W: Calling High-Level API
    W->>W: Arranging the load
    W->>I: Sending cargo
    I->>I: Convert Dict payload to Json
    
    Note over I,C: Isolation Boundary
    I->>C: Sending cargo to CRS
    C->>C: CRS Core Logic Execution
    
    C-->>I: Return Result/Status
    I-->>I: Converting Json Response to Dict
    I-->>W: Sending a Response
    W-->>W: Change Dict Response to DTO
    W-->>M: Returned Result (Object)
```

**Modules:** Just need to call the required **API** and send the data to **CRS**. The module does not need to know or implement any connection or communication mechanisms with the **CRS**.

**API:** Tasked with compiling `data` received from `module` before forwarding it to **IPC**. The wrapper also handles the response `data` received from **IPC**, then transforms it into a form that is easier for the `module` to use.

**IPC:**  Responsible for managing communications between **Storm** and **CRS**. Upon receiving the first request, **IPC** will start the **CRS** process as a `daemon` if it is not already running. Next `data` is sent to **CRS** via `stdin`, while the response is received by listening to `stdout`.

**CRS:** It will read the data from `stdin` and perform certain execution then it will return the response to `stdout`. 
**CRS** Runs in a separate process from **Storm** and continues to listen to `stdin` as long as the process is active. When the **Storm** process is stopped, **Storm** send signal-15 to PID right **CRS** running, until a certain time if **CRS** is still active then **Storm** sends this signal-9 just before it exits completely.

---

## 💡 Protocol Parameters

All protocols definitely have different parameters, here you can learn what parameters the current protocols have.

### 🔌 Socket Parameters

**1. Open Socket**
```python
sock = net.Socket()
resp = sock.socket(addrf, stype, proto)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Inheritance:** `net.Socket()` will inherit all the functions below it, and all of those functions will only return Response.

**Parameter**
- **addrf:** Address Family such as: `sock.AF_INET`, `sock.AF_INET6`, etc.
- **stype:** Sock Type like: `sock.SOCK_STREAM`, `sock.SOCK_DGRAM`, etc.
- **proto:** Protocols such as: `sock.IPPROTO_IP`, etc. | Default 0 = Determined by Kernel UNIX

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **fileno:** This will return the number of File-Decryptor (FD).


**2. Connect to Socket**
```python
resp = sock.connect(host, port)
```
**Parameter**
- **host:** This can be IP:Port / Hostname.
- **port:** This is a typical Port.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.
- **checked_type:** Returns the connection status to see if the tls/tcp connection is working. | Debug.
- **status_tls:** Returns a Boolean. If True=TLS is enabled. False=TLS is disabled.
- **remote_ip:** Returns the target IP:PORT.
- **local_ip:** Returns local IP:PORT.


**3. Send Data**
```python
resp = sock.send(data, flag)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Parameter**
- **data:** Can be bytes / http request / payload etc.
- **flag:** (Optional) | Default 0

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.
- **checked_type:** Returns the connection status to see if the tls/tcp connection is working. | Debug.
- **status_tls:** Returns a Boolean. If True=TLS is enabled. False=TLS is disabled.

```python
resp = sock.sendto(data, host, port, flag)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Parameter**
- **data:** Can be bytes / http request / payload etc.
- **host:** This can be IP:Port / Hostname.
- **port:** This is a typical Port.
- **flag:** MSG_* such as: `sock.MSG_OOB`, `sock.MSG_MORE`, etc. | str & int | Default 0.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.


**4. Viewing the buffer**
```python
raw = sock.recv(readsize, flag)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Parameter**
- **readsize:** To determine how many bytes of buffer to take.
- **flag:** (Optional) | Default 0

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if raw.ok:
- **raw_bytes:** Returning Raw Bytes.
- **str_bytes:** Returns Raw Bytes as String.
- **hex_bytes:** Returns Hex Bytes.
- **int_bytes:** Returns the number of Bytes.
- **remote_ip:** Returns the target IP:PORT.
- **local_ip:** Returns local IP:PORT.
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.
- **checked_type:** Returns the connection status to see if the tls/tcp connection is working. | Debug.
- **status_tls:** Returns a Boolean. If True=TLS is active. False=TLS is disabled.

```python
raw = sock.recvfrom(readsize, flag)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Parameter**
- **readsize:** To determine how many bytes of buffer to take.
- **flag:** MSG_* such as: `sock.MSG_OOB`, `sock.MSG_MORE`, etc. | str & int | Default 0.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if raw.ok:
- **raw_bytes:** Returning Raw Bytes.
- **str_bytes:** Returns Raw Bytes as String.
- **hex_bytes:** Returns Hex Bytes.
- **int_bytes:** Returns the number of Bytes.
- **remote_ip:** Returns the target IP:PORT.
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.


**5. TLS Upgrade**
```python
resp = sock.uptls(cert, key, ca, verify)
```
**Parameter**
- **cert:** Path to the certificate file.
- **key:** Path to the Key certificate file.
- **ca:** Path to the CA certificate file.
- **verify:** Boolean. True=Verifying client certificate. False=Skip verification. | Default True.

**Inheritance**  
Automatically inherits TLS connections to send/recv and send/recv usage remains the same.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **raw_bytes:** Returning Raw Bytes.
- **str_bytes:** Returns Raw Bytes as UTF-8.
- **hex_bytes:** Returns Hex Bytes.
- **int_bytes:** Returns the number of Bytes.
- **remote_ip:** Returns the server IP:PORT.
- **local_ip:** Returns local IP:PORT.
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.
- **checked_type:** Returns the connection status to see if the tls/tcp connection is working. | Debug.
- **status_tls:** Returns a Boolean. True=TLS is enabled. False=TLS is disabled.
- **tls:** Responses that inherit TLS information.

**TLS Information**
- **version:** Returns TLS Version 1.0/1.1/1.2/1.3.
- **cipher:** Returning Cipher Suite.
- **protocol:** Returns TLS protocols like h1/h2/h3.
- **hostname:** Returns Host like (example.com).
- **handshake:** Returns a Boolean. True=Handshake succeeded. False=Handshake failed.
- **session_resume:** Returns a Boolean. True=If the TLS session was resumed. False=If the handshake was complete.
- **subject:** Returns the (CN) of the server certificate.
- **issuer:** Returns the (CN) of the (CA) that issued the certificate. Examples: R13, ISRG Root X1, etc.
- **dns_name:** Returns a list of hostnames in the Subject Alternative Name (SAN) extension.
- **expires:** Returns the certificate Expiration Time in RFC3339 format.
- **cert_chain:** Returns the number of certificate chains that were successfully verified.


**6. Socket Options**
```python
resp = sock.setsockopt(level, name, value)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Parameter**
- **level:** OptLevel such as: `sock.SOL_SOCKET`, etc.
- **name:** OptName such as: `sock.SO_REUSEADDR`, `sock.TCP_NODELAY`, etc.
- **value:** OptVal it is the value of a pointer to a Buffer Memory | int

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.
- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:


**7. Bind**
```python
resp = sock.bind(host, port)
```
**Parameter**
- **host:** This can be IP:Port / Hostname.
- **port:** This is a typical Port.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **local_ip:** Returns local IP:PORT.


**8. Listen**
```python
resp = sock.listen(backlog)
```
**Parameter**
- **backlog:** Maximum limit of inbound connection queue allowed to hang before `accept()`.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.
- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:


**9. Accept**
```python
resp = sock.accept()
```
**Parameter:** There isn't any.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **is_reused:** Returns a Boolean. True=Using the same connection. False=Create a new connection.
- **rtt_ms:** Returns the Round Trip Time in milliseconds.


**10. Timeout**
```python
sock.timeout(value)
```
**Description:** The timeout function is created to set a default timeout for all functions executed after it, eliminating the need to apply timeouts repeatedly in each function.

**Value:** In this parameter, the input must be in the form of a float such as: 1.0, 10.5, etc.


**11. Creating Connection**
```python
resp = sock.create_connection(host, port)
```
**Description:** This function is used to immediately open a connection quickly without having to perform socket() and connect() literacy because this is done automatically by the binary CRS. This makes it faster and requires less code. Send, receive, and uptls still require manual processing afterward.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.
- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:


**12. Get Address Information**
```python
resp = sock.getaddrinfo(host, port, addrf, stype, sproto, flag)
```
**Description:** Collection of available argument lists [here.](https://storm-framework.pages.dev/storm-framework.wiki/CONSTANTS-MIXIN-SOCKET)

**Parameter**
- **addrf:** Address Family such as: `sock.AF_INET`, `sock.AF_INET6`, etc.
- **stype:** Sock Type like: `sock.SOCK_STREAM`, `sock.SOCK_DGRAM`, etc.
- **sproto:** Protocols such as: `sock.IPPROTO_IP`, etc. | Default 0 = Determined by Kernel UNIX
- **flag:** MSG_* such as: `sock.MSG_OOB`, `sock.MSG_MORE`, etc. | Default 0.

**Response**
- **status:** SUCCESS/WARN/ERROR/TIMEOUT.
- **message:** Messages adjust to status.

- **ok:** Return boolean from SUCCESS status. Allows the syntax: if resp.ok:
- **addrinfo:** Converts 'results' data from getaddrinfo to a standard tuple list.


**13. Closing the connection**
```python
resp = sock.close()
```
**Description:** This is used to close the connection when it is finished or when an error occurs, so that the connection does not hang and to avoid OOM.

**Response**
- **status:** SUCCESS/WARN/ERROR.
- **message:** Messages adjust to status.


**14. Exception Socket**
```python
try:
    ...
except sock.STrace:
```
**Description:** This is used to stop the program script when the CRS throws an ERROR/CRITICAL. Capture the ERROR message using smflogd if necessary.

---

### ☎️ DNS

**DNS Lookup**
```python
dns = net.DNSL()
dns.query(domain, type, proto)
dns.timeout(value)
dns.setlimit(ratelimit, frate)
dns.concurrency(con)
resp = dns.run()
```
**Description:** DNSL are stateless, and you get a response immediately after each run.

**Parameter**
- **domain:** example.com | str.
- **type:** DNS query type. Example: A, AAAA, TXT, etc. | Default A | str.
- **proto:** Can TCP/UDP | Default TCP.
- **timeout:** To limit the open connection time. | Default 5s
- **ratelimit:** Blocking requests if the token runs out. | Default 150/1s | int.
- **frate:** Fixed Rate Limit untuk upgrade (ratelimit) saat terkena WAF. | Default 10/1s | int
- **con:** Number of Goroutines for Concurrency, allows to run parallel connections. | int.

**Response**
- **status:** ERROR/SUCCESS/TIMEOUT/WARNING.
- **message:** Messages adjust to status.

- **ok:** Returns a boolean of the SUCCESS status and RCODE is NOERROR (0). Allows the syntax: if resp.ok:
- **rcode:** DNS Response Code (example: 0 = NOERROR, 3 = NXDOMAIN).
- **rcode_str:** String representation of RCODE.
- **records:** List of resolution results / answers from DNS server.
- **truncated:** Indicator if the UDP payload is too large and is truncated (will trigger a retry via TCP).
- **authoritative:** Indicator whether the response comes from the Authoritative Name Server directly.


**Exception DNS**
```python
try:
    ...
except dns.DTrace:
except dns.Timeout:
except dns.NXDOMAIN:
```
**Description:** This is used to stop the program script when the CRS throws an ERROR/CRITICAL. Capture the ERROR message using smflogd if necessary.

---

### 🖇️ HTTP Requests

**Standard HTTP**
```python
http = net.HTTPR()
http.get(url, headers)
http.post(url, body, headers)
# http methods provided: get, post, put, patch, etc.
```
**Parameter**
- **url:** https://example.com | str.
- **header:** Example: {"User-Agent": "Storm-Framework/3.0 (CRS Engine)"} | Dict.
- **body:** Can be empty, can also be filled. | Default empty | str.


**Raw HTTP**
```python
http.rawhttp.get(url, headers)
http.rawhttp.post(url, body, headers)
# http methods provided: get, post, put, patch, etc.
```
**Description:** Raw HTTP freely accepts custom or malformed headers or bodies.

**Parameter**
- **url:** https://example.com | str.
- **header:** Example: {"User-Agent": "Storm-Framework/3.0 (CRS Engine)"} | Dict.
- **body:** Can be empty, can also be filled. | Default empty | str or bytes.


**HTTP Global Settings & Runing**
```python
http.setoptions(ca, retry, redirect, verify, tls)
http.timeout(value)
http.concurrency(con)
http.setlimit(ratelimit, frate)

# Only runing returns a response
resp = http.run()
```
**Description:** HTTP Requests are stateless, you can send them and get a response straight away.

**Parameter**
- **redirect:** To do a page redirect. | Default True. | Boolean.
- **tls:** To display TLS information in the Response. | Default False | Boolean.
- **verify:** True=Verifying client certificate. False=Skip verification. | Default True. | Boolean.
- **retry:** Performs Retryable http / Retry connection if failed. | Default 2. | int.
- **rl:** Blocking requests if the token runs out. | Default 150/1s. | int.
- **timeout:** To limit the open connection time. | Default 5s.
- **con:** Number of Goroutines for Concurrency, allows to run parallel connections. | int.
- **ca:** Can path, can raw pem string, can base64. | Default Empty | str.
- 
**Response**
- **status:** ERROR/SUCCESS/TIMEOUT/WARNING.
- **message:** Messages adjust to status.

- **status_code:** HTTP Status Code (Example: 200, 404, 500).
- **ok:** Returns a boolean of the SUCCESS. Allows the syntax: if resp.ok
- **body:** Returns the body string.
- **raw_bytes:** Returns the response body in raw bytes.
- **headers:** The original header dictionary from the response.
- **get_headers:** Case-insensitive lookup for HTTP Headers. Example: resp.get_headers("content-type", "unknown") will find 'Content-Type'.
- **proto:** HTTP Protocol (Example: HTTP/1.1, HTTP/2.0).
- **engine:** The connection provider engine from CRS (Example: retryablehttp).
- **tls:** Responses that inherit TLS information.
- **json:** Parses the string body into a JSON dict/list. Returns None if the body is not a valid JSON format.

**TLS Information**
- **version:** Returns TLS Version 1.0/1.1/1.2/1.3.
- **cipher:** Returning Cipher Suite.
- **protocol:** Returns TLS protocols like h1/h2/h3.
- **hostname:** Returns Host like (example.com).
- **handshake:** Returns a Boolean. True=Handshake succeeded. False=Handshake failed.
- **session_resume:** Returns a Boolean. True=If the TLS session was resumed. False=If the handshake was complete.
- **subject:** Returns the (CN) of the server certificate.
- **issuer:** Returns the (CN) of the (CA) that issued the certificate. Examples: R13, ISRG Root X1, etc.
- **dns_name:** Returns a list of hostnames in the Subject Alternative Name (SAN) extension.
- **expires:** Returns the certificate Expiration Time in RFC3339 format.
- **cert_chain:** Certificate chain successfully verified against a trusted root CA.


**Exception HTTPR**
```python
try:
    ...
except http.HTrace:
except http.Timeout:
```
**Description:** This is used to stop the program script when the CRS throws an ERROR/CRITICAL. Capture the ERROR message using smflogd if necessary.

---

### 🔌 Telnet

**1. Open koneksi**
```python
def execute(options, net):
    r = net.Telnet(host, port, timeout)
```
**Description:** Telnet is stateful, you will get inherited functions.

**Parameter**
- **host:** This can be IP / Domain.
- **port:** This is a typical port.
- **timeout:** To limit the open connection time. | Default 10.0s.

**Inheritance**  
You will get the legacy `send` and `read` functions.

**2. Send Data**
```python
res, var = r.send(command, expected, timeout, raw)
```
**Parameter**
- **command:** This can be filled with a wordlist file of username or password or a free command or bytes.
- **expected:** This can contain the desired response expectation variables.
- **timeout:** To limit the open connection time. | Default 0.3s.
- **raw:** This is a boolean if True: The first response is Bytes. If False: The first response is a UTF-8 decoded string. | Default False.

**Response**
- **res:** This will contain the raw bytes response.
- **var:** Can contain a variable number of expectation parameters. For example, there are two expectation variables, so the response variable is calculated as 0 and 1. If it is below 0 such as -1 or -2 etc. it is considered False or not found.

**3. Read Response**
```python
res, var = r.read(expected, timeout, raw)
```

**Parameter**
- **expected:** This can contain the desired response expectation variables.
- **timeout:** To limit the open connection time. | Default 0.3s.
- **raw:** This is a boolean if True: The first response is Bytes. If False: The first response is a UTF-8 decoded string. | Default False.


**Response**
- **res:** This will contain the raw bytes response.
- **var:** Can contain a variable number of expectation parameters. For example, there are two expectation variables, so the response variable is calculated as 0 and 1. If it is below 0 such as -1 or -2 etc. it is considered False or not found.

---

### 📡 Use of Response & Inheritance

**1. Socket**

- **Description:** This socket implementation adheres to POSIX standards. While some functions may be implemented differently or bear different names, the core logic remains the same; furthermore, certain features or functions may be missing either because we intentionally chose not to implement them or simply because they have not yet been implemented.

- **Status:** `Stateful`
- **Inheritance**
```python
sock = net.Socket()

# Open Socket
sock.socket(addrf, stype, proto)

# Open connection to Socket
sock.connect(host, port)

# Send Data
sock.send(data, flag)
sock.sendto(data, host, port, flag)

# Buffer Fetching
sock.recv(readsize, flag)
sock.recvfrom(readsize, flag)

# TLS Upgrade has legacy
sock.uptls(cert, key, ca, verify)

# Automatically be on a TLS encrypted connection. Except: sendto and recvfrom.
sock.send()
sock.recv()

# Closing Connection
sock.close()

# Timeout function
sock.timeout(value)

# Create a tcp stream connection
sock.create_connection(host, port)

# socket argument function
sock.AF_*
sock.SOCK_*
sock.IPPROTO_*
```
```python
# Simple call to getaddrinfo
resp = net.Socket().getaddrinfo(...)

# Explicit
sock = net.Socket()
resp = sock.getaddrinfo(...)

# The response from getaddrinfo returns a tuple with 5 elements
# that is: [0]family, [1]socktype, [2]protocol, [3]canonname, [4]sockaddr
for x in resp: # or (for x in resp.addrinfo:)
```

- **Response**
```python
# send data
r = sock.send(data, timeout)
smf.printf(r.status, r.message)
smf.printf(r.isreused, r.rtt_ms, etc.)

# read buffer
r = sock.recv(readsize)
smf.printf(r.status, r.message)
smf.printf(r.raw_bytes, r.hex_bytes, etc.)

# TLS Upgrade
r = sock.uptls(cert, key, ca, verify)
smf.printf(r.status, r.message)
smf.printf(r.tls.version, r.tls.cipher, etc.)
```

**2. DNS Lookup**

- **Status:** `Stateless`
- **Response**
```python
dns = net.DNSL()
dns.timeout(0.2)       # Set Timeout
dns.concurrency(50)    # Set Concurrency
dns.setlimit(150, 50)  # Set Ratelimit and update ratelimit

resp = dns.run() # Runing DNS and return response

# Show response
smf.printf(resp.status, resp.message)
smf.printf(resp.rcode, resp.records, etc.)

# Boolean SUCCESS
if resp.ok:
```

**3. HTTP Requests**

- **Status:** `Stateless`
- **Response**
```python
path_ca = "/path/path/cert.pem"

http = net.HTTPR(...)
http.setoptions(path_ca, 2, true, true, true) # Set CA, retry, redirect, verify tls, tls response
http.timeout(5.0)      # Set Timeout
http.concurrency(50)   # Set Concurency
http.setlimit(150, 80) # Set Ratelimit and update ratelimit

resp = http.run() # Runing HTTP and return response

# Show response
smf.printf(resp.status, resp.message)
smf.printf(resp.status_code, resp.tls.cipher, etc.)
smf.printf(resp.get_headers("server", "unknown"))

# Boolean SUCCESS
if resp.ok:
```

**4. Telnet**

- **Status:** `Stateful`
- **Inheritance**
```python
# Open Connection
r = net.Telnet(...)

# Viewing the response
raw, var = r.read(...)
smf.printf(raw) # Return raw bytes response.
smf.printf(var) # Return Amount expected.

# Sending data
raw, var = r.send(...)
smf.printf(raw) # Return raw bytes response.
smf.printf(var) # Return Amount expected.

if var < 0: # -1 = Beyond expected.
if var >= 0: # 0+ = As expected.
```









