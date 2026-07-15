"""
Forced fair-warning disclaimer gate — drives real Flask app entry.

Default product mode: demo unlocks only after accepting the full disclaimer
(with all revelation checkboxes). Not hard 410 shut-down.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ACKS = {
    "ack_simulation": "1",
    "ack_polish": "1",
    "ack_lockin": "1",
    "ack_crowdsource": "1",
    "ack_demos": "1",
    "ack_demo_only": "1",
}


@pytest.fixture
def client():
    from product_status import is_forced_disclaimer, is_discontinued

    assert is_forced_disclaimer(), "forced disclaimer should be default on"
    assert not is_discontinued(), "hard shut-down should be default off"
    from PlotterApp import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def accepted_client(client):
    from product_status import DISCLAIMER_VERSION

    r = client.post(
        "/accept-disclaimer",
        data={**REQUIRED_ACKS, "next": "/", "version": DISCLAIMER_VERSION},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303), r.data
    return client


def test_home_redirects_to_disclaimer_until_accepted(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 303)
    assert "/disclaimer" in (r.headers.get("Location") or "")


def test_disclaimer_page_has_revelations_and_examples(client):
    r = client.get("/disclaimer")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert 'data-disclaimer-page="1"' in body
    assert "parallel process without parallel power is a simulation" in body.lower()
    assert "optional polish" in body.lower()
    assert "power is not crowdsourced" in body.lower()
    assert "industrial two-party" in body.lower() or "two-party" in body.lower()
    assert "demos" in body.lower()
    assert "fragment" in body.lower()
    # Clear failure examples
    assert "example of failure" in body.lower()
    assert "data-ack=\"simulation\"" in body
    assert "data-ack=\"crowdsource\"" in body
    assert "data-disclaimer-submit" in body


def test_partial_accept_rejected(client):
    from product_status import DISCLAIMER_VERSION

    r = client.post(
        "/accept-disclaimer",
        data={"ack_simulation": "1", "next": "/vote", "version": DISCLAIMER_VERSION},
    )
    assert r.status_code == 400
    assert b"data-disclaimer-error" in r.data
    # Still gated
    r2 = client.get("/vote", follow_redirects=False)
    assert r2.status_code in (302, 303)


def test_full_accept_unlocks_system(accepted_client):
    r = accepted_client.get("/", follow_redirects=False)
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    # Real home, not shut-down tombstone
    assert "The Internet Party has shut down" not in body
    assert "data-shutdown-title" not in body
    # Persistent banner
    assert "data-give-up-banner" in body
    assert "simulation" in body.lower() or "abandoned mission" in body.lower()


def test_vote_usable_after_accept(accepted_client):
    r = accepted_client.get("/vote")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "data-give-up-banner" in html
    # Live vote surface markers (pre-give-up product)
    assert "data-voting-clock" in html or "Vote" in html or "ballot" in html.lower()


def test_apis_blocked_before_accept_unlocked_after(client):
    from product_status import DISCLAIMER_VERSION

    r = client.get("/voting-clock")
    assert r.status_code == 403
    assert r.get_json().get("disclaimer_required") is True

    r_acc = client.post(
        "/accept-disclaimer",
        data={**REQUIRED_ACKS, "next": "/", "version": DISCLAIMER_VERSION},
    )
    assert r_acc.status_code in (302, 303)

    r2 = client.get("/voting-clock")
    assert r2.status_code == 200
    body = r2.get_json()
    assert "windowId" in body


def test_mutators_blocked_before_accept(client):
    r = client.post("/create-draft", json={"title": "x", "description": "y"})
    assert r.status_code == 403
    assert r.get_json().get("disclaimer_required") is True


def test_healthz_ok_with_forced_disclaimer_flag(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("status") == "ok"
    assert body.get("forced_disclaimer") is True
    assert body.get("mode") == "demo-disclaimer"


def test_disclaimer_next_path_escaped():
    import DisclaimerPage

    html = DisclaimerPage.render(next_path='/"/><script>alert(1)</script>')
    assert "<script>alert(1)</script>" not in html
    assert "&lt;" in html or "&#" in html or "&quot;" in html


def test_investigation_archive_still_present():
    archive = REPO_ROOT / "notes" / "GROK" / "SOCIETAL_GIVE_UP_INVESTIGATION.md"
    assert archive.is_file()
    text = archive.read_text(encoding="utf-8")
    assert "parallel process without parallel power" in text.lower()
