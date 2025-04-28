"""Tests for the `archon.openai_patch` module.

These tests focus on the helper that ensures the OpenAI response object has a
valid `created` timestamp and confirm that it behaves correctly for various
edge cases.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import archon.openai_patch as openai_patch


@pytest.mark.parametrize("initial_created", [None, 1_658_000_000])
def test_ensure_response_created_mutates_or_preserves(initial_created: Any) -> None:
    """The helper should create or preserve the `created` timestamp.

    Args:
        initial_created (Any): The starting value for `created`. Can be `None` or an int.
    """
    resp = SimpleNamespace(created=initial_created)

    openai_patch._ensure_response_created(resp)  # type: ignore[attr-defined]

    assert isinstance(resp.created, int)
    if initial_created is not None:
        # When a valid timestamp is provided, it should remain unchanged.
        assert resp.created == initial_created


def test_ensure_response_created_when_attr_missing() -> None:
    """If the response lacks a `created` attribute, it should be added."""
    resp = SimpleNamespace()
    assert not hasattr(resp, "created")

    openai_patch._ensure_response_created(resp)  # type: ignore[attr-defined]

    assert isinstance(resp.created, int)  # type: ignore[attr-defined] 