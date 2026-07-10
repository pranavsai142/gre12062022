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
    """Render healthCheckPath is /healthz — must be 200 with status ok."""
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.get_json()
    assert body is not None
    assert body.get("status") == "ok"
    # Shallow check does not require a database key
    assert "database" not in body or body.get("database") == "ok"


def test_healthz_deep_returns_ok_when_firebase_available(client):
    """Deep probe verifies RTDB; used for ops diagnosis after deploy."""
    r = client.get("/healthz?deep=1")
    # With certs present in this project env, deep must be healthy.
    assert r.status_code == 200, r.data
    body = r.get_json()
    assert body.get("status") == "ok"
    assert body.get("database") == "ok"


def test_public_primary_routes_ok(client):
    """Spot-check the public surface that deploy traffic hits first."""
    for path in ("/", "/vote", "/policy", "/about", "/login", "/ballot-items"):
        r = client.get(path)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert r.data and len(r.data) > 20, f"{path} empty body"


def test_ballot_items_is_json_shape(client):
    """NPC/remote clients rely on /ballot-items JSON (not HTML scrape)."""
    r = client.get("/ballot-items")
    assert r.status_code == 200
    body = r.get_json()
    assert isinstance(body, dict)
    assert "windowId" in body
    assert "items" in body
    assert "count" in body
    assert isinstance(body["items"], list)
    assert body["count"] == len(body["items"])


def test_validate_token_missing_body_is_401_not_500(client):
    """Malformed login posts must not 500 (was AttributeError on None.get)."""
    r = client.post("/validate-token", data=b"", content_type="application/json")
    assert r.status_code == 401
    body = r.get_json()
    assert body.get("authenticated") is False

    r2 = client.post("/validate-token", json={})
    assert r2.status_code == 401
    assert r2.get_json().get("authenticated") is False

    r3 = client.post("/validate-token", json={"idToken": ""})
    assert r3.status_code == 401


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
