"""Patch to make pydantic_ai.models.openai.OpenAIModel robust to responses with `created=None`.

This patch is applied automatically when the module is imported (import archon.openai_patch or via archon package import).
It monkey-patches the `_process_response` method so that if the response object returned by the
OpenAI client is missing the required `created` attribute (or it is `None`), it replaces it with the
current UTC timestamp before delegating back to the original implementation.
"""
from __future__ import annotations

import datetime
from types import SimpleNamespace
from typing import Any


def _ensure_response_created(response: Any) -> None:  # noqa: D401 – simple helper
    """Ensure ``response.created`` has a sensible integer value.

    The original implementation of ``pydantic_ai.models.openai.OpenAIModel._process_response`` assumes
    that ``response.created`` is always an ``int`` Unix timestamp. In practice the OpenAI Python
    client can occasionally return ``None`` (e.g. if the header is missing or a partial failure
    occurs).  Attempting to convert ``None`` to a ``datetime`` via ``datetime.fromtimestamp`` raises a
    ``TypeError``.  This helper mutates the response in-place, replacing ``None`` with the current UTC
    timestamp (in seconds) before the original processing continues.

    Args:
        response (Any): The HTTP response object returned by the OpenAI client.
    """
    created = getattr(response, "created", None)
    if created is None:
        fallback_ts = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
        # Using setattr handles cases where ``created`` is a property without a setter – in such cases
        # we fall back to updating ``__dict__`` directly via ``vars``.
        try:
            setattr(response, "created", fallback_ts)
        except AttributeError:
            # Last-ditch effort if the attribute is read-only
            if isinstance(response, SimpleNamespace):
                response.created = fallback_ts  # type: ignore[attr-defined]
            else:
                # ``vars`` works for most plain objects where ``__dict__`` is writable.
                try:
                    vars(response)["created"] = fallback_ts
                except Exception:
                    # If we still can't set it, we just ignore – the original implementation will
                    # raise a *different* error at that point, but we did our best.
                    pass


def _patch_openai_model() -> None:  # noqa: D401 – imperative helper
    """Monkey-patch ``OpenAIModel._process_response`` once, idempotently."""
    try:
        from pydantic_ai.models.openai import OpenAIModel  # type: ignore
    except Exception:  # pragma: no cover – library may be absent in some envs
        return

    # Prevent double-patching – useful during hot-reloads.
    if getattr(OpenAIModel, "_archon_created_patch_applied", False):  # pragma: no cover
        return

    original_process_response = OpenAIModel._process_response  # type: ignore[attr-defined]

    def _safe_process_response(self, response):  # type: ignore[override]
        _ensure_response_created(response)
        return original_process_response(self, response)

    # Monkey-patch in place.
    OpenAIModel._process_response = _safe_process_response  # type: ignore[assignment]
    OpenAIModel._archon_created_patch_applied = True  # type: ignore[attr-defined]


# Apply the patch immediately upon import.
_patch_openai_model() 