from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class PluginResult:
    success: bool                   # Must be True or False
    data: Optional[Any] = None      # Place of results if SUCCESSFUL
    error: Optional[str] = None     # Place to order if FAIL
  
    @classmethod
    def ok(cls, data: Any = None):
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, msg: str):
        return cls(success=False, error=msg)
