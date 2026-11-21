import socket as _socket

_SOCK_PREFIXED = (
    "AF_",
    "PF_",
    "SOCK_",
    "IPPROTO_",
    "IPPORT_",
    "INADDR_",
    "SOL_",
    "SO_",
    "TCP_",
    "UDP_",
    "IP_",
    "IPV6_",
    "MSG_",
    "SHUT_",
    "SOMAXCONN",
    "AI_",
    "EAI_",
    "NI_",
)


class ConstantsMix:
    """Sub-Class Constants."""

    _CONSTANTS = {
        name: value
        for name, value in vars(_socket).items()
        if (name.startswith(_SOCK_PREFIXED) and isinstance(value, int))
    }

    def __getattr__(self, name):
        try:
            return self._CONSTANTS[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!s} has no attribute {name!r}"
            ) from None
