from typing import TYPE_CHECKING, Dict, Any, Optional, Union

if TYPE_CHECKING:
    from .state_build import HTTPState


class RawHttp:
    """
    Sub-module RawHttp untuk membangun state HTTP request (Fluent Interface).
    Setiap method HTTP akan memperbarui `self.state` dan mengembalikan instance `HTTPState` (HTTPR).
    """

    def __init__(self, state: "HTTPState"):
        self.state = state

    def _set_state(
        self,
        method: str,
        url: str,
        body: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> "HTTPState":
        """
        Internal dispatcher untuk memvalidasi dan memperbarui HTTPState secara terpusat.
        """
        if headers is None:
            headers = {}

        if not isinstance(headers, dict):
            raise TypeError(f"Headers must be a Dict, got {type(headers).__name__}")

        # Set metadata HTTP
        self.state._method = method.upper()
        self.state._rawhttp = True
        self.state._url = url
        self.state._body = body

        # Merge headers
        default_headers = getattr(self.state, "_headers", {}) or {}
        if isinstance(default_headers, dict):
            merged_headers = default_headers.copy()
            merged_headers.update(headers)
            self.state._headers = merged_headers
        else:
            self.state._headers = headers

        return self.state

    # ------------------------------------------------------------------
    # HTTP Method Interfaces
    # ------------------------------------------------------------------

    def get(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> "HTTPState":
        return self._set_state("GET", url, body=None, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        body: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> "HTTPState":
        return self._set_state("POST", url, body=body, headers=headers, **kwargs)

    def put(
        self,
        url: str,
        body: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> "HTTPState":
        return self._set_state("PUT", url, body=body, headers=headers, **kwargs)

    def patch(
        self,
        url: str,
        body: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> "HTTPState":
        return self._set_state("PATCH", url, body=body, headers=headers, **kwargs)

    def delete(
        self,
        url: str,
        body: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> "HTTPState":
        return self._set_state("DELETE", url, body=body, headers=headers, **kwargs)

    def head(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> "HTTPState":
        return self._set_state("HEAD", url, body=None, headers=headers, **kwargs)

    def options(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> "HTTPState":
        return self._set_state("OPTIONS", url, body=None, headers=headers, **kwargs)

    def trace(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> "HTTPState":
        return self._set_state("TRACE", url, body=None, headers=headers, **kwargs)

    def connect(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> "HTTPState":
        return self._set_state("CONNECT", url, body=None, headers=headers, **kwargs)
