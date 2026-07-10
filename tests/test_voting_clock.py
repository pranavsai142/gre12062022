"""
Real-world voting clock — unit + HTTP entry points.

Drives Database.getVotingClock / bounds helpers and the public /voting-clock
route (same surface the countdown JS and pages use).
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

import Database

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_format_countdown_duration():
    assert Database.formatCountdownDuration(0) == "00m 00s"
    assert Database.formatCountdownDuration(65) == "01m 05s"
    assert Database.formatCountdownDuration(3661) == "01h 01m 01s"
    assert "d " in Database.formatCountdownDuration(90061)


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
    assert clock["remainingLabel"] == Database.formatCountdownDuration(clock["secondsRemaining"])
    assert "d " in clock["remainingLabel"]


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
    # Never cache live ticks
    cc = r.headers.get("Cache-Control", "")
    assert "no-store" in cc
    # Either real ISO endsAt or override with null endsAt
    if body.get("isOverride") and body.get("phase") == "override":
        assert body.get("endsAt") is None
    else:
        assert body.get("endsAt")
        assert "T" in body["endsAt"]


def test_voting_clock_js_resyncs_and_reloads_on_boundary():
    js = (REPO_ROOT / "static" / "js" / "voting-clock.js").read_text()
    assert "RESYNC_MS" in js
    assert "maybeReloadForNewWeek" in js
    assert "visibilitychange" in js
    assert "cache: \"no-store\"" in js or "cache: 'no-store'" in js
    assert "prefers-reduced-motion" in js


def test_healthz_deep_includes_window_clock(client):
    r = client.get("/healthz?deep=1")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("status") == "ok"
    assert body.get("database") == "ok"
    assert "windowId" in body
    assert "secondsRemaining" in body
    assert body.get("remainingLabel")
    assert body.get("revision")


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
    # Explicit data-window-id for vote.js (do not scrape prose)
    assert 'data-window-id="' in html
    assert 'id="ballot-root"' in html or "ballot-header" in html
    # Server-rendered human countdown (works before JS hydrates)
    assert "Closes in" in html


def test_vote_js_reads_data_window_id_not_prose():
    """Regression: fragile text match for 'Window X' broke when copy said 'window:'."""
    js = (REPO_ROOT / "static" / "js" / "vote.js").read_text()
    assert "getBallotWindowId" in js
    assert "data-window-id" in js
    assert "textContent.match" not in js


def test_home_embeds_clock(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "data-voting-clock" in html
    assert "voting-clock.js" in html
    assert "Closes in" in html


def test_about_documents_real_world_windows(client):
    r = client.get("/about")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "ISO week" in html or "Monday 00:00 UTC" in html
    assert "/voting-clock" in html
    assert "data-voting-clock" in html
    assert "Closes in" in html


def test_login_and_register_embed_compact_clock(client):
    for path in ("/login", "/register", "/reset"):
        r = client.get(path)
        assert r.status_code == 200, path
        html = r.data.decode("utf-8")
        assert "data-voting-clock" in html, path
        assert "voting-clock.js" in html, path
        assert "Closes in" in html, path


def test_status_includes_remaining_label(client):
    r = client.get("/status")
    assert r.status_code in (200, 503)
    body = r.get_json()
    if body.get("status") == "ok":
        assert body.get("remainingLabel")
        assert "m" in body["remainingLabel"] or "h" in body["remainingLabel"] or "d" in body["remainingLabel"]
