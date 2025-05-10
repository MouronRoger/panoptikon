"""Type stubs for Foundation framework."""

from typing import Any, Tuple

def NSMakeRect(x: float, y: float, width: float, height: float) -> Any: ...


def NSMakePoint(x: float, y: float) -> Any: ...


def NSMakeSize(width: float, height: float) -> Any: ...


class NSString:
    """Foundation string class."""
    
    @classmethod
    def stringWithString_(cls, string: str) -> "NSString": ...
    
    def length(self) -> int: ...


class NSArray:
    """Foundation array class."""
    
    @classmethod
    def array(cls) -> "NSArray": ...
    
    @classmethod
    def arrayWithObjects_count_(cls, objects: Tuple[Any, ...], count: int) -> "NSArray": ...
    
    def count(self) -> int: ...
    
    def objectAtIndex_(self, index: int) -> Any: ...


class NSDictionary:
    """Foundation dictionary class."""
    
    @classmethod
    def dictionary(cls) -> "NSDictionary": ...
    
    @classmethod
    def dictionaryWithObjects_forKeys_count_(
        cls, objects: Tuple[Any, ...], keys: Tuple[Any, ...], count: int
    ) -> "NSDictionary": ...
    
    def count(self) -> int: ...
    
    def objectForKey_(self, key: Any) -> Any: ... 