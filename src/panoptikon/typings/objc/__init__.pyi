"""Type stubs for objc module."""

from typing import Any, Callable, Optional

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