"""Auth client contracts + session/security headers for the live platform."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_login_js_does_not_stack_auth_listeners():
    """Regression: onAuthStateChanged inside handleLogin stacked a listener per click."""
    js = (REPO_ROOT / "static" / "js" / "login.js").read_text()
    # Must not *call* the API (comments may mention the old bug by name)
    assert "auth().onAuthStateChanged" not in js
    assert ".onAuthStateChanged(" not in js
    assert "establishServerSession" in js
    assert "showLoginError" in js
    assert "signInWithEmailAndPassword" in js


def test_register_js_does_not_stack_auth_listeners():
    js = (REPO_ROOT / "static" / "js" / "register.js").read_text()
    assert "auth().onAuthStateChanged" not in js
    assert ".onAuthStateChanged(" not in js
    assert "establishServerSession" in js
    assert "showRegisterError" in js
    assert "createUserWithEmailAndPassword" in js


def test_validate_user_tolerates_bad_session_shapes():
    import User

    assert User.validateUser(None) is False
    assert User.validateUser({}) is False
    assert User.validateUser({"exp": "not-a-number"}) is False
    assert User.validateUser({"uid": "x"}) is False  # missing exp
    # Far-future exp is valid
    assert User.validateUser({"uid": "x", "exp": 4_000_000_000}) is True
    # Expired
    assert User.validateUser({"uid": "x", "exp": 1}) is False


@pytest.fixture
def client():
    from PlotterApp import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_security_headers_present(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "strict-origin" in (r.headers.get("Referrer-Policy") or "")


def test_missing_detail_returns_http_404(client):
    """Give-up: all former product HTML (including detail) is the shut-down page."""
    r = client.get("/detail/definitely-not-a-real-policy-id-zzz")
    assert r.status_code == 200
    assert b"shut down" in r.data.lower() or b"discontinued" in r.data.lower()
    r2 = client.get("/detail/amendment/definitely-not-a-real-amendment-id-zzz")
    assert r2.status_code == 200
    assert b"shut down" in r2.data.lower() or b"discontinued" in r2.data.lower()


def test_session_cookie_config():
    from PlotterApp import app

    assert app.config.get("SESSION_COOKIE_HTTPONLY") is True
    assert app.config.get("SESSION_COOKIE_SAMESITE") == "Lax"


def test_reset_page_is_functional_not_stub(client):
    """Give-up: /reset is discontinued shut-down HTML (no live reset flow)."""
    r = client.get("/reset")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "shut down" in html.lower() or "discontinued" in html.lower()
    assert "data-shutdown-title" in html


def test_reset_js_sends_firebase_reset_email():
    js = (REPO_ROOT / "static" / "js" / "reset.js").read_text()
    assert "sendPasswordResetEmail" in js
    assert "handleReset" in js
    assert "auth/user-not-found" in js  # non-enumerating success path
