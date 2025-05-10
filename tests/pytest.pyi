"""Type stubs for pytest."""

from typing import Any, Callable, TypeVar

_T = TypeVar("_T", bound=Callable[..., Any])


def fixture(*args: Any, **kwargs: Any) -> Callable[[_T], _T]:
    ...


class Mark:
    @staticmethod
    def unit(func: _T) -> _T:
        ...

    @staticmethod
    def integration(func: _T) -> _T:
        ...

    @staticmethod
    def slow(func: _T) -> _T:
        ...


mark: Mark
