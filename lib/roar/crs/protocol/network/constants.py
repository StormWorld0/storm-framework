# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy


class AddrFamily:
    """Address Family"""

    AF_UNSPEC = "AF_UNSPEC"
    AF_UNIX = "AF_UNIX"
    AF_INET = "AF_INET"
    AF_INET6 = "AF_INET6"


class SockType:
    """Sock Type"""

    SOCK_STREAM = "SOCK_STREAM"
    SOCK_DGRAM = "SOCK_DGRAM"
    SOCK_RAW = "SOCK_RAW"
    SOCK_SEQPACKET = "SOCK_SEQPACKET"


class IPProto:
    """Protocol"""

    IPPROTO_IP = "IPPROTO_IP"
    IPPROTO_IPV6 = "IPPROTO_IPV6"
    IPPROTO_ICMP = "IPPROTO_ICMP"
    IPPROTO_TCP = "IPPROTO_TCP"
    IPPROTO_UDP = "IPPROTO_UDP"
    IPPROTO_RAW = "IPPROTO_RAW"


class SockOptionsSO:
    """OptLevel"""

    SOL_SOCKET = "SOL_SOCKET"

    """OptName - SOL_SOCKET (Level 1)"""
    SO_DEBUG = "SO_DEBUG"
    SO_REUSEADDR = "SO_REUSEADDR"
    SO_TYPE = "SO_TYPE"
    SO_ERROR = "SO_ERROR"
    SO_DONTROUTE = "SO_DONTROUTE"
    SO_BROADCAST = "SO_BROADCAST"
    SO_SNDBUF = "SO_SNDBUF"
    SO_RCVBUF = "SO_RCVBUF"
    SO_KEEPALIVE = "SO_KEEPALIVE"
    SO_OOBINLINE = "SO_OOBINLINE"
    SO_NO_CHECK = "SO_NO_CHECK"
    SO_PRIORITY = "SO_PRIORITY"
    SO_LINGER = "SO_LINGER"
    SO_BSDCOMPAT = "SO_BSDCOMPAT"
    SO_REUSEPORT = "SO_REUSEPORT"
    SO_PASSCRED = "SO_PASSCRED"
    SO_PEERCRED = "SO_PEERCRED"
    SO_RCVLOWAT = "SO_RCVLOWAT"
    SO_SNDLOWAT = "SO_SNDLOWAT"
    SO_RCVTIMEO = "SO_RCVTIMEO"
    SO_SNDTIMEO = "SO_SNDTIMEO"
    SO_BINDTODEVICE = "SO_BINDTODEVICE"
    SO_ATTACH_FILTER = "SO_ATTACH_FILTER"
    SO_DETACH_FILTER = "SO_DETACH_FILTER"
    SO_TIMESTAMP = "SO_TIMESTAMP"
    SO_ACCEPTCONN = "SO_ACCEPTCONN"


class SockOptionsTCP:
    """OptName - IPPROTO_TCP (Level 6)"""

    TCP_NODELAY = "TCP_NODELAY"
    TCP_MAXSEG = "TCP_MAXSEG"
    TCP_CORK = "TCP_CORK"
    TCP_KEEPIDLE = "TCP_KEEPIDLE"
    TCP_KEEPINTVL = "TCP_KEEPINTVL"
    TCP_KEEPCNT = "TCP_KEEPCNT"
    TCP_SYNCNT = "TCP_SYNCNT"
    TCP_LINGER2 = "TCP_LINGER2"
    TCP_DEFER_ACCEPT = "TCP_DEFER_ACCEPT"
    TCP_WINDOW_CLAMP = "TCP_WINDOW_CLAMP"
    TCP_INFO = "TCP_INFO"
    TCP_QUICKACK = "TCP_QUICKACK"
    TCP_CONGESTION = "TCP_CONGESTION"
    TCP_MD5SIG = "TCP_MD5SIG"
    TCP_THIN_LINEAR_TIMEOUTS = "TCP_THIN_LINEAR_TIMEOUTS"
    TCP_THIN_DUPACK = "TCP_THIN_DUPACK"
    TCP_USER_TIMEOUT = "TCP_USER_TIMEOUT"
    TCP_REPAIR = "TCP_REPAIR"
    TCP_FASTOPEN = "TCP_FASTOPEN"
    TCP_TIMESTAMP = "TCP_TIMESTAMP"
    TCP_NOTSENT_LOWAT = "TCP_NOTSENT_LOWAT"


class SockOptionsIP:
    """OptName - IPPROTO_IP (Level 0)"""

    IP_TOS = "IP_TOS"
    IP_TTL = "IP_TTL"
    IP_HDRINCL = "IP_HDRINCL"
    IP_ADD_MEMBERSHIP = "IP_ADD_MEMBERSHIP"
    IP_DROP_MEMBERSHIP = "IP_DROP_MEMBERSHIP"

    """OptName - IPPROTO_IPV6 (Level 41)"""
    IPV6_UNICAST_HOPS = "IPV6_UNICAST_HOPS"
    IPV6_V6ONLY = "IPV6_V6ONLY"


class SockFlags:
    """Flags - (Level 0)"""

    MSG_DONTWAIT = "MSG_DONTWAIT"
    MSG_OOB = "MSG_OOB"
    MSG_MORE = "MSG_MORE"
    MSG_NOSIGNAL = "MSG_NOSIGNAL"
    MSG_CONFIRM = "MSG_CONFIRM"
    MSG_PEEK = "MSG_PEEK"
    MSG_WAITALL = "MSG_WAITALL"
    MSG_TRUNC = "MSG_TRUNC"


class ConstantsMix(
    AddrFamily,
    SockType,
    IPProto,
    SockOptionsSO,
    SockOptionsTCP,
    SockOptionsIP,
    SockFlags,
):
    """
    Class Pusat Integrasi Konstanta.
    Menggabungkan seluruh sub-class konstanta via Multiple Inheritance
    agar kompatibel dengan `class Socket(SocketState, ConstantsMix)`.
    """

    # Socket Arguments
    AF = AddrFamily
    Type = SockType
    IP = IPProto

    # Argument Setsockopt
    SO = SockOptionsSO
    TCP = SockOptionsTCP
    IP = SockOptionsIP

    # Sendto & Recvfrom Arguments
    Flag = SockFlags
