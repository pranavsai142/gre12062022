"""
Full give-up / product discontinued — drives the real Flask app entry.

Asserts shut-down HTML on former product paths and 410 on mutating routes.
Does not re-implement ShutdownPage; hits PlotterApp:app like gunicorn.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client():
    from product_status import is_discontinued

    assert is_discontinued(), "give-up tests require PRODUCT_DISCONTINUED default on"
    from PlotterApp import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_home_is_shutdown_html_not_operating_party(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "data-shutdown-title" in body
    assert "The Internet Party has shut down" in body
    assert "Service discontinued" in body or "discontinued" in body.lower()
    assert "Public give-up notice" in body
    # Must not present live vote UX as primary surface
    assert "Cast your ballot" not in body
    assert "data-window-id" not in body
    assert r.headers.get("X-Product-Status") == "discontinued"


def test_former_product_paths_converge_on_shutdown(client):
    for path in ("/vote", "/about", "/policy", "/login", "/register", "/drafts", "/account"):
        r = client.get(path)
        assert r.status_code == 200, path
        body = r.data.decode("utf-8")
        assert "The Internet Party has shut down" in body, path
        assert 'data-requested-path="1"' in body or path in body


def test_mutators_return_410_discontinued(client):
    paths = (
        "/create-draft",
        "/submit-ballot",
        "/validate-token",
        "/dev-tools/seed",
        "/close-window",
    )
    for path in paths:
        r = client.post(path, json={"title": "x", "description": "y", "idToken": "fake"})
        assert r.status_code == 410, f"{path} -> {r.status_code}"
        data = r.get_json()
        assert data is not None
        assert data.get("discontinued") is True
        assert data.get("success") is False
        assert "discontinued" in (data.get("error") or "").lower() or data.get("code") == "PRODUCT_DISCONTINUED"


def test_product_json_apis_gone(client):
    for path in ("/ballot-items", "/voting-clock", "/status"):
        r = client.get(path)
        assert r.status_code == 410, path
        assert r.get_json().get("discontinued") is True


def test_healthz_reports_discontinued_still_up(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.get_json()
    assert body.get("discontinued") is True
    assert body.get("status") == "discontinued"
    assert body.get("revision")


def test_shutdown_page_module_markers():
    """Direct unit check of shipped ShutdownPage.render (same function gate uses)."""
    import ShutdownPage

    html = ShutdownPage.render(None, path="/vote")
    assert "data-shutdown-badge" in html
    assert "data-shutdown-panel=\"give-up\"" in html
    assert "parallel process" in html.lower() or "Process without power" in html
    assert "/vote" in html


def test_shutdown_path_is_html_escaped_against_reflected_xss(client):
    """Regression: request path must not inject raw tags into the shut-down page."""
    evil = "/<script>alert(1)</script>"
    r = client.get(evil)
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    # Unescaped script must not appear as executable HTML
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    # Same via the shipped render function directly
    import ShutdownPage

    rendered = ShutdownPage.render(None, path=evil)
    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_investigation_archive_has_required_sections():
    archive = REPO_ROOT / "notes" / "GROK" / "SOCIETAL_GIVE_UP_INVESTIGATION.md"
    assert archive.is_file()
    text = archive.read_text(encoding="utf-8")
    assert "Societal realizations" in text or "## 1. Societal realizations" in text
    assert "Key conflicts" in text or "## 2. Key conflicts" in text
    assert "Exploration pathway" in text or "## 3. Exploration pathway" in text
    assert "parallel process without parallel power" in text.lower()
    assert "optional polish" in text.lower() or "software is optional polish" in text.lower()
