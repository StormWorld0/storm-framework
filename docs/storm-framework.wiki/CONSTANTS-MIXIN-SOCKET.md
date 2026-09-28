# Mixin Argument Socket

We will categorize and list all available Mixins so that manual creation is unnecessary, and we will keep the list updated based on publicly available resources. We will also provide specific usage recommendations to ensure validity, particularly when the Mixins we offer are limited in scope.

### Argument Socket

```python
AF_INET
AF_INET6
AF_UNIX
AF_UNSPEC
```
```python
SOCK_STREAM
SOCK_DGRAM
SOCK_RAW
SOCK_SEQPACKET
```
```python
IPPROTO_IP
IPPROTO_ICMP
IPPROTO_TCP
IPPROTO_UDP
IPPROTO_RAW
```
**Usage:** `sock.socket(sock.AF_INET, sock.SOCK_STREAM, sock.IPPROTO_IP)`  
**Description:** For RAW users, you can create manual SYN, ACK, etc. handshakes independently, because CRS only bridges communication with the kernel.


### Argument Socket Options

**OptLevel**
```python
SOL_SOCKET
IPPROTO_TCP
IPPROTO_IP
IPPROTO_IPV6
```
**OptName - SOL_SOCKET (Level 1)**
```python
SO_DEBUG
SO_REUSEADDR
SO_TYPE
SO_ERROR
SO_DONTROUTE
SO_BROADCAST
SO_SNDBUF
SO_RCVBUF
SO_KEEPALIVE
SO_OOBINLINE
SO_NO_CHECK
SO_PRIORITY
SO_LINGER
SO_BSDCOMPAT
SO_REUSEPORT
SO_PASSCRED
SO_PEERCRED
SO_RCVLOWAT
SO_SNDLOWAT
SO_RCVTIMEO
SO_SNDTIMEO
SO_BINDTODEVICE
SO_ATTACH_FILTER
SO_DETACH_FILTER
SO_TIMESTAMP
SO_ACCEPTCONN
```
**OptName - IPPROTO_TCP (Level 6)**
```python
TCP_NODELAY
TCP_MAXSEG
TCP_CORK
TCP_KEEPIDLE
TCP_KEEPINTVL
TCP_KEEPCNT
TCP_SYNCNT
TCP_LINGER2
TCP_DEFER_ACCEPT
TCP_WINDOW_CLAMP
TCP_INFO
TCP_QUICKACK
TCP_CONGESTION
TCP_MD5SIG
TCP_THIN_LINEAR_TIMEOUTS
TCP_THIN_DUPACK
TCP_USER_TIMEOUT
TCP_REPAIR
TCP_FASTOPEN
TCP_TIMESTAMP
TCP_NOTSENT_LOWAT
```
**OptName - IPPROTO_IP (Level 0)**
```python
IP_TOS
IP_TTL
IP_HDRINCL
IP_ADD_MEMBERSHIP
IP_DROP_MEMBERSHIP
```
**OptName - IPPROTO_IPV6 (Level 41)**
```python
IPV6_UNICAST_HOPS
IPV6_V6ONLY
```
**Usage Example:** `sock.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, value=0)`


### Argument Flags Sendto & Recvfrom 

**Flags - (Level 0)**
```python
MSG_DONTWAIT
MSG_OOB
MSG_MORE
MSG_NOSIGNAL
MSG_CONFIRM
MSG_PEEK
MSG_WAITALL
MSG_TRUNC
```
**Usage Example (1):** `sock.sendto(data=b"...", host=127.0.0.1, port=80, sock.MSG_OOB, timeout=1.0)`.  
**Usage Example (2):** `sock.recvfrom(readsize=1024, sock.MSG_MORE, timeout=1.0)`.

---

> [!IMPORTANT]
> If you are using a Mixin that is not available, we recommend that you add is [here](https://github.com/StormWorld0/storm-framework/blob/main/lib/roar/crs/protocol/network/constants.py) And [here](https://github.com/StormWorld0/storm-framework/blob/main/lib/roar/crs/src/protocol/socket/parse.go)
> Alternatively, you can implement this yourself within the modules you create; ensure that you send an integer rather than a string. This is because the CRS validates input data: if the input is not found in the list, it returns a default value, whereas if the input is an integer, it returns the same value as the input.

