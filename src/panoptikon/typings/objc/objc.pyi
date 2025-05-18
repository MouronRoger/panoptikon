"""Minimal objc stub for PyObjC migration. All attributes are Any."""

from typing import Any

def __getattr__(name: str) -> Any: ...
