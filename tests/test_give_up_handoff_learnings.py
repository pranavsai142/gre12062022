"""
Structural check: the give-up "what we learned" handoff on disk is real and complete.

Reads the shipped handoff file from notes/GROK/handoffs/ — does not re-implement
or hardcode the handoff body inside the test beyond required markers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFFS = REPO_ROOT / "notes" / "GROK" / "handoffs"
GIVE_UP_LEARNINGS = HANDOFFS / "2026-07-14-what-we-learned-give-up.md"
ARCHIVE = REPO_ROOT / "notes" / "GROK" / "SOCIETAL_GIVE_UP_INVESTIGATION.md"


def test_what_we_learned_give_up_handoff_exists():
    assert GIVE_UP_LEARNINGS.is_file(), f"missing handoff: {GIVE_UP_LEARNINGS}"


def test_handoff_is_give_up_close_not_feature_continuation():
    text = GIVE_UP_LEARNINGS.read_text(encoding="utf-8")
    lower = text.lower()
    # Explicit give-up / close identity
    assert "give-up" in lower or "giving up" in lower or "given up" in lower
    assert "what we learned" in lower
    assert "no work to continue" in lower or "no feature backlog" in lower
    # Must not read as "continue building the party" as next work
    assert "continue building the party" not in lower
    # If "next sprint" appears, it must only be as an explicit refusal
    if "next sprint" in lower:
        assert "no" in lower and (
            'no “next sprint' in lower
            or 'no "next sprint' in lower
            or "no next sprint" in lower
        )


def test_handoff_has_what_we_learned_section_with_core_realizations():
    text = GIVE_UP_LEARNINGS.read_text(encoding="utf-8")
    lower = text.lower()
    assert "## what we learned" in lower
    # Core realizations (plain-text presence in the real file)
    assert "parallel process without parallel power" in lower
    assert "simulation" in lower
    assert "optional polish" in lower
    assert "two-party" in lower or "industrial two-party" in lower
    assert "not crowdsourced" in lower or "power is not crowdsourced" in lower
    assert "demos" in lower  # "no single online demos"
    assert "fragment" in lower or "fragmentation" in lower


def test_for_the_next_session_discontinued_and_points_at_archive():
    text = GIVE_UP_LEARNINGS.read_text(encoding="utf-8")
    lower = text.lower()
    assert "## for the next session" in lower
    assert "no feature backlog" in lower or "no work to continue" in lower
    assert "discontinued" in lower or "abandoned" in lower or "given up" in lower
    assert "societal_give_up_investigation.md" in lower
    assert ARCHIVE.is_file()
