"""Type stubs for objc module."""

from typing import Any, Callable, Optional, Protocol, Type, TypeVar, Union, overload

T = TypeVar('T')

def selector(method: Callable[..., Any], signature: bytes) -> Any: ...


def lookUpClass(class_name: str) -> Any: ...


def protocolNamed(protocol_name: str) -> Any: ...


def registerCFSignature(
    name: str, encoding: bytes, typestring: Optional[str] = None
) -> None: ...


def createOpaquePointerType(
    name: str, typestr: bytes, doc: Optional[str] = None
) -> None: ...


def createStructType(
    name: str, typestr: bytes, fieldnames: list[str], doc: Optional[str] = None
) -> None: ...


def python_method(method: Callable[..., Any]) -> Any: ...

# Additional objc functions
def allocateBuffer(size: int) -> Any: ...

def recycle(obj: Any) -> None: ...

@overload
def super(cls: Type[Any], self: Any) -> Any: ...
@overload
def super(cls: Type[Any], self: Any, protocol: Any) -> Any: ...

def addConvenienceForClass(class_name: str, methods: list[Callable[..., Any]]) -> None: ...

def removeConvenienceForClass(class_name: str) -> None: ...

class ivar:
    """Type annotation for Objective-C instance variables."""
    def __init__(
        self, 
        name: str, 
        type: str, 
        isOutlet: bool = False, 
        isSynthesize: bool = False
    ) -> None: ...

class IBOutlet:
    """Marker for Interface Builder outlets."""
    def __init__(self, type: Optional[Any] = None) -> None: ...

class IBAction:
    """Marker for Interface Builder actions."""
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]: ...

def instancemethod(func: Callable[..., Any]) -> Callable[..., Any]: ... 