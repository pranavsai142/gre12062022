"""
Deploy readiness tests — drive the real shipped entry points and config contracts.

These are always-on (no Playwright, no RUN_SCALE). They catch regressions that would
break Render health checks, multi-worker sessions, or the CI e2e gate.
"""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client():
    """Real Flask test client for PlotterApp:app (same entry as gunicorn)."""
    # Import after DATA_FOLDER is available from the environment / defaults.
    from PlotterApp import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_healthz_shallow_returns_ok(client):
    """Render healthCheckPath is /healthz — must stay 200 (discontinued still up for probes)."""
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.get_json()
    assert body is not None
    # Full give-up: shallow reports discontinued but remains probe-friendly
    assert body.get("status") in ("ok", "discontinued")
    if body.get("status") == "discontinued":
        assert body.get("discontinued") is True
    assert body.get("revision")
    assert len(str(body.get("revision"))) >= 4


def test_healthz_deep_returns_ok_when_firebase_available(client):
    """Deep probe: under give-up, reports discontinued without thrashing hosts."""
    r = client.get("/healthz?deep=1")
    assert r.status_code == 200, r.data
    body = r.get_json()
    assert body.get("status") in ("ok", "discontinued")
    if body.get("discontinued"):
        assert body.get("status") == "discontinued"
    else:
        assert body.get("database") == "ok"


def test_public_primary_routes_ok(client):
    """Spot-check public surface: HTML shut-down pages; product JSON APIs are 410."""
    for path in ("/", "/vote", "/policy", "/about", "/login", "/register", "/reset", "/robots.txt"):
        r = client.get(path)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert r.data and len(r.data) > 10, f"{path} empty body"
        if path != "/robots.txt":
            assert b"shut down" in r.data.lower() or b"discontinued" in r.data.lower(), path
    for path in ("/ballot-items", "/voting-clock", "/status"):
        r = client.get(path)
        assert r.status_code == 410, f"{path} -> {r.status_code}"
        assert r.get_json().get("discontinued") is True


def test_robots_txt_is_professional(client):
    """Discontinued site must not ship a joke robots.txt."""
    r = client.get("/robots.txt")
    assert r.status_code == 200
    text = r.data.decode("utf-8")
    assert "User-agent:" in text
    assert "Allow:" in text
    assert "fuck" not in text.lower()
    assert "DISCONTINUED" in text.upper() or "discontinued" in text.lower()


def test_sitemap_xml_lists_public_pages(client):
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "urlset" in body
    # Give-up: home only (no invitation to live vote/library paths as live product)
    assert "https://theinternetparty.us/" in body or "<loc>" in body


def test_public_status_includes_live_window(client):
    """Under give-up, /status is Gone (not a live window feed)."""
    r = client.get("/status")
    assert r.status_code == 410
    body = r.get_json()
    assert body.get("discontinued") is True


def test_ballot_items_is_json_shape(client):
    """Under give-up, /ballot-items refuses (no live NPC ballot surface)."""
    r = client.get("/ballot-items")
    assert r.status_code == 410
    body = r.get_json()
    assert body.get("discontinued") is True
    assert body.get("success") is False


def test_validate_token_missing_body_is_401_not_500(client):
    """Under give-up, all POSTs including validate-token are 410 discontinued."""
    r = client.post("/validate-token", data=b"", content_type="application/json")
    assert r.status_code == 410
    body = r.get_json()
    assert body.get("discontinued") is True

    r2 = client.post("/validate-token", json={})
    assert r2.status_code == 410
    assert r2.get_json().get("discontinued") is True

    r3 = client.post("/validate-token", json={"idToken": ""})
    assert r3.status_code == 410


def test_api_posts_empty_body_return_json_not_html_400(client):
    """Empty JSON bodies under give-up: structured 410, never HTML error shells."""
    for path in (
        "/submit-ballot",
        "/close-window",
        "/create-draft",
        "/dev-tools/set-window",
    ):
        r = client.post(path, data=b"", content_type="application/json")
        assert r.status_code == 410, path
        assert b"<!doctype html>" not in r.data.lower(), f"{path} returned HTML: {r.status_code}"
        assert r.is_json
        body = r.get_json()
        assert body.get("discontinued") is True


def test_stable_secret_key_is_deterministic():
    """Multi-worker gunicorn requires an identical secret across processes."""
    from PlotterApp import _stable_secret_key

    a = _stable_secret_key()
    b = _stable_secret_key()
    assert a == b
    assert isinstance(a, str) and len(a) >= 16


def test_start_sh_and_render_yaml_deploy_contract():
    """render.yaml startCommand + env must match what start.sh actually consumes."""
    render = (REPO_ROOT / "render.yaml").read_text()
    start = (REPO_ROOT / "start.sh").read_text()

    assert "startCommand: ./start.sh" in render
    assert "healthCheckPath: /healthz" in render
    assert "DATA_FOLDER" in render and "/etc/secrets/" in render
    assert "SECRET_KEY" in render
    assert "WEB_CONCURRENCY" in render
    assert "GUNICORN_THREADS" in render

    assert "exec pipenv run gunicorn" in start
    assert "PlotterApp:app" in start
    assert "WEB_CONCURRENCY" in start
    assert "GUNICORN_THREADS" in start
    assert "0.0.0.0:$PORT" in start or '0.0.0.0:$PORT' in start
    # Foreground only: the gunicorn line after exec must not be backgrounded
    after_exec = start.split("exec", 1)[1]
    first_cmd_line = after_exec.strip().splitlines()[0]
    assert not first_cmd_line.rstrip().endswith("&"), (
        "start.sh must run gunicorn in the foreground for Render"
    )

    mode = (REPO_ROOT / "start.sh").stat().st_mode
    assert mode & stat.S_IXUSR, "start.sh must be executable"


def test_ci_e2e_job_if_does_not_use_same_job_env():
    """GitHub Actions: job-level if cannot see env vars defined on that same job.
    The e2e gate must key off secrets.FIREBASE_SERVICE_ACCOUNT directly."""
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    # Forbidden pattern that caused the e2e job to never schedule
    assert "env.HAS_CERT" not in ci, (
        "CI e2e job must not use env.HAS_CERT in if (same-job env is invisible to job if)"
    )
    assert "secrets.FIREBASE_SERVICE_ACCOUNT" in ci
    # Positive: job-level if on the secret
    assert re.search(
        r"if:\s*\$\{\{\s*secrets\.FIREBASE_SERVICE_ACCOUNT\s*!=\s*''\s*\}\}",
        ci,
    ), "e2e job must use if: secrets.FIREBASE_SERVICE_ACCOUNT != ''"
