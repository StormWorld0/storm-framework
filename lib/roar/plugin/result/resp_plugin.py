from dataclasses import dataclass
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

@dataclass
class PluginResult(Generic[T]):
    """Standardized response container for all plugin executions."""
    
    success: bool  # Must be True or False
    data: Optional[Any] = None  # Place of results if SUCCESSFUL
    error: Optional[str] = None  # Place to order if FAIL

    @classmethod
    def ok(cls, data: Any = None) -> "PluginResult":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, msg: any) -> "PluginResult":
        return cls(success=False, error=str(msg))

    @classmethod
    def __bool__(cls) -> bool:
        return cls.ok
