# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

class ConstantsMix:
    """Address Family"""
    AF_UNSPEC = 0
    AF_UNIX = 1
    AF_INET = 2
    AF_INET6 = 10

    """Sock Type"""
    SOCK_STREAM = 1
    SOCK_DGRAM = 2
    SOCK_RAW = 3
    SOCK_SEQPACKET = 5

    """Protocol"""
    IPPROTO_IP = 0
    IPPROTO_IPV6 = 41
    IPPROTO_ICMP = 1
    IPPROTO_TCP = 6
    IPPROTO_UDP = 17
    IPPROTO_RAW = 255

    """OptLevel"""
    SOL_SOCKET = 1
    
    """OptName - SOL_SOCKET (Level 1)"""
    SO_DEBUG = 1
    SO_REUSEADDR = 2
    SO_TYPE = 3
    SO_ERROR = 4
    SO_DONTROUTE = 5
    SO_BROADCAST = 6
    SO_SNDBUF = 7
    SO_RCVBUF = 8
    SO_KEEPALIVE = 9
    SO_OOBINLINE = 10
    SO_NO_CHECK = 11
    SO_PRIORITY = 12
    SO_LINGER = 13
    SO_BSDCOMPAT = 14
    SO_REUSEPORT = 15
    SO_PASSCRED = 16
    SO_PEERCRED = 17
    SO_RCVLOWAT = 18
    SO_SNDLOWAT = 19
    SO_RCVTIMEO = 20
    SO_SNDTIMEO = 21
    SO_BINDTODEVICE = 25
    SO_ATTACH_FILTER = 26
    SO_DETACH_FILTER = 27
    SO_TIMESTAMP = 29
    SO_ACCEPTCONN = 30

    """OptName - IPPROTO_TCP (Level 6)"""
    TCP_NODELAY = 1
    TCP_MAXSEG = 2
    TCP_CORK = 3
    TCP_KEEPIDLE = 4
    TCP_KEEPINTVL = 5
    TCP_KEEPCNT = 6
    TCP_SYNCNT = 7
    TCP_LINGER2 = 8
    TCP_DEFER_ACCEPT = 9
    TCP_WINDOW_CLAMP = 10
    TCP_INFO = 11
    TCP_QUICKACK = 12
	TCP_CONGESTION = 13
    TCP_MD5SIG = 14
    TCP_THIN_LINEAR_TIMEOUTS = 16
    TCP_THIN_DUPACK = 17
    TCP_USER_TIMEOUT = 18
    TCP_REPAIR = 19
    TCP_FASTOPEN = 23
    TCP_TIMESTAMP = 24
    TCP_NOTSENT_LOWAT = 25

    """OptName - IPPROTO_IP (Level 0)"""
    IP_TOS = 1
    IP_TTL = 2
    IP_HDRINCL = 3
    IP_ADD_MEMBERSHIP = 35
    IP_DROP_MEMBERSHIP = 36

    """OptName - IPPROTO_IPV6 (Level 41)"""
    IPV6_UNICAST_HOPS = 16
    IPV6_V6ONLY = 26
