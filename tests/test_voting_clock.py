"""
Real-world voting clock — unit + HTTP entry points.

Drives Database.getVotingClock / bounds helpers and the public /voting-clock
route (same surface the countdown JS and pages use).
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

import Database


def test_parse_iso_window_id():
    assert Database.parseIsoWindowId("2026-W28") == (2026, 28)
    assert Database.parseIsoWindowId("2026-W01") == (2026, 1)
    assert Database.parseIsoWindowId("SCALE-TEST-1") is None
    assert Database.parseIsoWindowId("") is None
    assert Database.parseIsoWindowId(None) is None
    assert Database.parseIsoWindowId("2026-W99") is None


def test_window_time_bounds_are_monday_to_monday_utc():
    start, end = Database.getWindowTimeBounds("2026-W28")
    assert start.tzinfo is not None
    assert start.weekday() == 0  # Monday
    assert start.hour == 0 and start.minute == 0 and start.second == 0
    assert end - start == timedelta(days=7)
    assert end.weekday() == 0
    # 2026-W28 starts 2026-07-06 (known ISO calendar)
    assert start.date().isoformat() == "2026-07-06"


def test_get_voting_clock_fixed_now_inside_week():
    # Thursday of 2026-W28
    now = datetime(2026, 7, 9, 12, 0, 0, tzinfo=timezone.utc)
    # Avoid Firebase override read issues by using pure calendar path:
    # temporarily stub override to None
    original = Database.getCurrentWindowOverride
    Database.getCurrentWindowOverride = lambda: None
    try:
        clock = Database.getVotingClock(now=now)
    finally:
        Database.getCurrentWindowOverride = original

    assert clock["windowId"] == "2026-W28"
    assert clock["realWindowId"] == "2026-W28"
    assert clock["isOverride"] is False
    assert clock["phase"] == "open"
    assert clock["timezone"] == "UTC"
    assert clock["endsAt"].startswith("2026-07-13")
    assert clock["startsAt"].startswith("2026-07-06")
    assert clock["nextWindowId"] == "2026-W29"
    # From Thu noon to next Mon 00:00 = 3.5 days = 302400 seconds
    assert clock["secondsRemaining"] == 3 * 86400 + 12 * 3600
    assert clock["secondsToRealWeekEnd"] == clock["secondsRemaining"]


def test_get_voting_clock_override_synthetic_window():
    now = datetime(2026, 7, 9, 12, 0, 0, tzinfo=timezone.utc)
    original = Database.getCurrentWindowOverride
    Database.getCurrentWindowOverride = lambda: "SCALE-DEMO-1"
    try:
        clock = Database.getVotingClock(now=now)
    finally:
        Database.getCurrentWindowOverride = original

    assert clock["windowId"] == "SCALE-DEMO-1"
    assert clock["isOverride"] is True
    assert clock["phase"] == "override"
    assert clock["startsAt"] is None
    assert clock["endsAt"] is None
    assert clock["realWindowId"] == "2026-W28"
    assert clock["secondsToRealWeekEnd"] > 0


def test_next_iso_window_id():
    assert Database.getNextIsoWindowId("2026-W28") == "2026-W29"
    # Year boundary: 2025-W01 follows 2024 last week
    nxt = Database.getNextIsoWindowId("2024-W52")
    assert nxt.startswith("2024-W") or nxt.startswith("2025-W")


@pytest.fixture
def client():
    from PlotterApp import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_voting_clock_http_endpoint(client):
    r = client.get("/voting-clock")
    assert r.status_code == 200
    body = r.get_json()
    assert "windowId" in body
    assert "serverNow" in body
    assert "secondsRemaining" in body
    assert body["timezone"] == "UTC"
    assert isinstance(body["secondsRemaining"], int)
    assert body["secondsRemaining"] >= 0
    # Either real ISO endsAt or override with null endsAt
    if body.get("isOverride") and body.get("phase") == "override":
        assert body.get("endsAt") is None
    else:
        assert body.get("endsAt")
        assert "T" in body["endsAt"]


def test_ballot_items_includes_clock(client):
    r = client.get("/ballot-items")
    assert r.status_code == 200
    body = r.get_json()
    assert "clock" in body
    assert body["clock"]["windowId"] == body["windowId"]
    assert "secondsRemaining" in body["clock"]


def test_vote_page_embeds_clock_and_script(client):
    r = client.get("/vote")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "data-voting-clock" in html
    assert "voting-clock.js" in html
    assert "data-ends-at" in html
    assert "Monday 00:00 UTC" in html


def test_home_embeds_clock(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "data-voting-clock" in html
    assert "voting-clock.js" in html
