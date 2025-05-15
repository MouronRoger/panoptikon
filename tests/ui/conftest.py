def pytest_ignore_collect(collection_path, config):
    """Prevent collection of UI tests when PyObjC is unavailable."""
    if collection_path.name == "test_ui_integration.py":
        try:
            __import__("objc")
            return False  # Collect the file
        except ImportError:
            return True  # Skip collection completely
    return False  # Collect other files
