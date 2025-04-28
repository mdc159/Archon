"""Global test configuration.

We stub modules that are optional C dependencies during testing to avoid ImportErrors when
plugins (e.g. langsmith) import them.
"""
from __future__ import annotations

import sys
import types


def pytest_configure() -> None:  # noqa: D401 – pytest hook
    """Stub problematic optional modules before tests start."""
    if "zstandard" not in sys.modules:
        zstd_module = types.ModuleType("zstandard")
        backend_c = types.ModuleType("zstandard.backend_c")
        zstd_module.backend_c = backend_c  # attribute for internal import
        sys.modules["zstandard"] = zstd_module
        sys.modules["zstandard.backend_c"] = backend_c 