"""UI tests for validators and macOS app logic (headless/mocked)."""

import sys
from types import ModuleType
from typing import Any

import pytest

from panoptikon.ui import validators


def test_assert_objc_method_exists_success() -> None:
    """Test assert_objc_method_exists passes when method exists."""

    class Dummy:
        def foo(self) -> None:
            pass

    obj = Dummy()
    validators.assert_objc_method_exists(obj, "foo")


def test_assert_objc_method_exists_failure() -> None:
    """Test assert_objc_method_exists raises AssertionError when method missing."""

    class Dummy:
        pass

    obj = Dummy()
    with pytest.raises(AssertionError):
        validators.assert_objc_method_exists(obj, "bar")


def test_assert_objc_protocol_conformance_success() -> None:
    """Test assert_objc_protocol_conformance passes when all methods exist."""

    class Dummy:
        def foo(self) -> None:
            pass

        def bar(self) -> None:
            pass

    obj = Dummy()
    validators.assert_objc_protocol_conformance(obj, ["foo", "bar"])


def test_assert_objc_protocol_conformance_failure() -> None:
    """Test assert_objc_protocol_conformance raises AssertionError if missing."""

    class Dummy:
        def foo(self) -> None:
            pass

    obj = Dummy()
    with pytest.raises(AssertionError):
        validators.assert_objc_protocol_conformance(obj, ["foo", "bar"])


def test_validate_search_field_delegate_true() -> None:
    """Test validate_search_field_delegate returns True if any method exists."""

    class Dummy:
        def controlTextDidChange_(self) -> None:
            pass

    obj = Dummy()
    assert validators.validate_search_field_delegate(obj) is True


def test_validate_search_field_delegate_false() -> None:
    """Test validate_search_field_delegate returns False if no methods exist."""

    class Dummy:
        pass

    obj = Dummy()
    assert validators.validate_search_field_delegate(obj) is False


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS-only UI logic")
def test_macos_app_pyobjc_unavailable(monkeypatch: Any) -> None:
    """Test FileSearchApp disables UI if PyObjC modules are unavailable."""
    import importlib

    from panoptikon.ui.macos_app import FileSearchApp

    # Patch importlib to raise ImportError for PyObjC modules
    def fake_import_module(name: str) -> ModuleType:
        raise ImportError(f"No module named {name}")

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    app = FileSearchApp()
    assert not getattr(app, "_pyobjc_available", True)
