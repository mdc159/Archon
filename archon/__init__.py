import sys
import types

# Stub zstandard to satisfy optional dependencies like langsmith during tests when the
# C extension is not available.
if 'zstandard' not in sys.modules:
    zstd_module = types.ModuleType('zstandard')
    backend_c = types.ModuleType('zstandard.backend_c')

    class _StubZstdCompressor:  # noqa: D401 – minimal stub
        def __init__(self, *args, **kwargs):
            pass

        def compress(self, data):  # type: ignore[no-self-use]
            return data

    setattr(zstd_module, 'ZstdCompressor', _StubZstdCompressor)
    sys.modules['zstandard'] = zstd_module
    sys.modules['zstandard.backend_c'] = backend_c  # satisfy `from .backend_c import *`
    setattr(zstd_module, '__version__', '0.22.0')

from importlib import import_module

# Ensure OpenAIModel response patch is applied automatically
import_module("archon.openai_patch")
