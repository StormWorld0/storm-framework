# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import socket


class AddrFamily:
    """Address Family"""

    AF_UNSPEC = socket.AF_UNSPEC
    AF_UNIX = socket.AF_UNIX
    AF_INET = socket.AF_INET
    AF_INET6 = socket.AF_INET6


class SockType:
    """Sock Type"""

    SOCK_STREAM = socket.SOCK_STREAM
    SOCK_DGRAM = socket.SOCK_DGRAM
    SOCK_RAW = socket.SOCK_RAW
    SOCK_SEQPACKET = socket.SOCK_SEQPACKET


class IPProto:
    """Protocol"""

    IPPROTO_IP = socket.IPPROTO_IP
    IPPROTO_IPV6 = socket.IPPROTO_IPV6
    IPPROTO_ICMP = socket.IPPROTO_ICMP
    IPPROTO_TCP = socket.IPPROTO_TCP
    IPPROTO_UDP = socket.IPPROTO_UDP
    IPPROTO_RAW = socket.IPPROTO_RAW


class SockOptionsSO:
    """OptLevel"""

    SOL_SOCKET = socket.SOL_SOCKET

    """OptName - SOL_SOCKET (Level 1)"""
    SO_DEBUG = socket.SO_DEBUG
    SO_REUSEADDR = socket.SO_REUSEADDR
    SO_TYPE = socket.SO_TYPE
    SO_ERROR = socket.SO_ERROR
    SO_DONTROUTE = socket.SO_DONTROUTE
    SO_BROADCAST = socket.SO_BROADCAST
    SO_SNDBUF = socket.SO_SNDBUF
    SO_RCVBUF = socket.SO_RCVBUF
    SO_KEEPALIVE = socket.SO_KEEPALIVE
    SO_OOBINLINE = socket.SO_OOBINLINE
    SO_NO_CHECK = "SO_NO_CHECK"
    SO_PRIORITY = socket.SO_PRIORITY
    SO_LINGER = socket.SO_LINGER
    SO_BSDCOMPAT = socket.SO_BSDCOMPAT
    SO_REUSEPORT = socket.SO_REUSEPORT
    SO_PASSCRED = socket.SO_PASSCRED
    SO_PEERCRED = socket.SO_PEERCRED
    SO_RCVLOWAT = socket.SO_RCVLOWAT
    SO_SNDLOWAT = socket.SO_SNDLOWAT
    SO_RCVTIMEO = socket.SO_RCVTIMEO
    SO_SNDTIMEO = socket.SO_SNDTIMEO
    SO_BINDTODEVICE = socket.SO_BINDTODEVICE
    SO_ATTACH_FILTER = socket.SO_ATTACH_FILTER
    SO_DETACH_FILTER = socket.SO_DETACH_FILTER
    SO_TIMESTAMP = socket.SO_TIMESTAMP
    SO_ACCEPTCONN = socket.SO_ACCEPTCONN


class SockOptionsTCP:
    """OptName - IPPROTO_TCP (Level 6)"""

    TCP_NODELAY = socket.TCP_NODELAY
    TCP_MAXSEG = socket.TCP_MAXSEG
    TCP_CORK = socket.TCP_CORK
    TCP_KEEPIDLE = socket.TCP_KEEPIDLE
    TCP_KEEPINTVL = socket.TCP_KEEPINTVL
    TCP_KEEPCNT = socket.TCP_KEEPCNT
    TCP_SYNCNT = socket.TCP_SYNCNT
    TCP_LINGER2 = socket.TCP_LINGER2
    TCP_DEFER_ACCEPT = socket.TCP_DEFER_ACCEPT
    TCP_WINDOW_CLAMP = socket.TCP_WINDOW_CLAMP
    TCP_INFO = socket.TCP_INFO
    TCP_QUICKACK = socket.TCP_QUICKACK
    TCP_CONGESTION = socket.TCP_CONGESTION
    TCP_MD5SIG = socket.TCP_MD5SIG
    TCP_THIN_LINEAR_TIMEOUTS = socket.TCP_THIN_LINEAR_TIMEOUTS
    TCP_THIN_DUPACK = socket.TCP_THIN_DUPACK
    TCP_USER_TIMEOUT = socket.TCP_USER_TIMEOUT
    TCP_REPAIR = socket.TCP_REPAIR
    TCP_FASTOPEN = socket.TCP_FASTOPEN
    TCP_TIMESTAMP = socket.TCP_TIMESTAMP
    TCP_NOTSENT_LOWAT = socket.TCP_NOTSENT_LOWAT


class SockOptionsIP:
    """OptName - IPPROTO_IP (Level 0)"""

    IP_TOS = socket.IP_TOS
    IP_TTL = socket.IP_TTL
    IP_HDRINCL = socket.IP_HDRINCL
    IP_ADD_MEMBERSHIP = socket.IP_ADD_MEMBERSHIP
    IP_DROP_MEMBERSHIP = socket.IP_DROP_MEMBERSHIP

    """OptName - IPPROTO_IPV6 (Level 41)"""
    IPV6_UNICAST_HOPS = socket.IPV6_UNICAST_HOPS
    IPV6_V6ONLY = socket.IPV6_V6ONLY


class SockFlags:
    """Flags - (Level 0)"""

    MSG_DONTWAIT = socket.MSG_DONTWAIT
    MSG_OOB = socket.MSG_OOB
    MSG_MORE = socket.MSG_MORE
    MSG_NOSIGNAL = socket.MSG_NOSIGNAL
    MSG_CONFIRM = socket.MSG_CONFIRM
    MSG_PEEK = socket.MSG_PEEK
    MSG_WAITALL = socket.MSG_WAITALL
    MSG_TRUNC = socket.MSG_TRUNC


class SockHow:
    """How (level 0)"""

    SHUT_RD = socket.SHUT_RD
    SHUT_WR = socket.SHUT_WR
    SHUT_RDWR = socket.SHUT_RDWR


class ConstantsMix(
    AddrFamily,
    SockType,
    IPProto,
    SockOptionsSO,
    SockOptionsTCP,
    SockOptionsIP,
    SockFlags,
    SockHow,
):
    """
    Class Pusat Integrasi Konstanta.
    Menggabungkan seluruh sub-class konstanta via Multiple Inheritance
    agar kompatibel dengan `class Socket`.
    """

    family = AddrFamily
    type = SockType
    proto = IPProto
    options = (SockOptionsSO, SockOptionsTCP, SockOptionsIP)
    flag = SockFlags
    how = SockHow
