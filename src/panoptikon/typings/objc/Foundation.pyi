"""Minimal Foundation stub for PyObjC migration. All attributes are Any."""

from typing import Any

class NSObject:
    """Stub for Foundation.NSObject."""

    ...

def __getattr__(name: str) -> Any: ...
