"""Site customizations to make optional C dependencies optional.

This module is automatically imported by the Python interpreter on startup (if
present on `sys.path`) and before any third-party packages are imported.

We provide minimal stubs for modules that are occasionally required by
plugins/dependencies during testing but are heavy or optional (e.g.
`zstandard`).
"""
from __future__ import annotations

import sys
import types
import os as _os

# Disable pytest auto plugin loading to avoid third-party plugins enforcing heavy deps.
_os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

# Stub the `zstandard` C extension if it's unavailable (common on CI without
# compilation tools). This prevents ImportErrors from libraries like
# `langsmith` which expect `zstandard` to be installed but can work without its
# full functionality.
if 'zstandard' not in sys.modules:
    zstd_module = types.ModuleType('zstandard')
    backend_c = types.ModuleType('zstandard.backend_c')
    zstd_module.backend_c = backend_c
    setattr(zstd_module, '__version__', '0.22.0')

    class _StubZstdCompressor:  # noqa: D401 – minimal stub of public API
        def __init__(self, *args, **kwargs):
            pass

        def compress(self, data):  # type: ignore[no-self-use]
            return data

    setattr(zstd_module, 'ZstdCompressor', _StubZstdCompressor)
    sys.modules['zstandard'] = zstd_module
    sys.modules['zstandard.backend_c'] = backend_c 