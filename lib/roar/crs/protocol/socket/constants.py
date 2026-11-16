import socket as _socket

_SOCK_PREFIXED = (
    "AF_",
    "PF_",
    "SOCK_",
    "IPPROTO_",
    "SOL_",
    "SO_",
    "TCP_",
    "UDP_",
    "IP_",
    "IPV6_",
    "MSG_",
    "SHUT_",
)


class ConstantsMix:
    """Sub-Class Integrasi Konstanta."""

    _CONSTANTS = {
        name: value
        for name, value in vars(_socket).items()
        if (name.startswith(_SOCK_PREFIXED) and isinstance(value, int))
    }

    _CONSTANTS.update(
        {
            "SO_NO_CHECK": "SO_NO_CHECK",
            "SO_BSDCOMPAT": "SO_BSDCOMPAT",
            "SO_ATTACH_FILTER": "SO_ATTACH_FILTER",
            "SO_DETACH_FILTER": "SO_DETACH_FILTER",
            "SO_TIMESTAMP": "SO_TIMESTAMP",
        }
    )

    def __getattr__(self, name):
        try:
            return self._CONSTANTS[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!s} has no attribute {name!r}"
            ) from None
