"""
E2E test configuration for The Internet Party (Playwright + pytest).
- Reuses the main website at localhost:5000 (or --base-url)
- Supports markers: e2e, scale
- Provides base_url fixture and helpers for unique test data
- Cleanup friendly via window override + dev tools actions after login
- Modifiable: change TEST_* constants or parametrize for different scales/flows
"""

import os
import time
import pytest
import threading
from playwright.sync_api import Page, expect

# For direct harness cleanup helpers (reuses Database as approved)
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    import Database
except Exception:
    Database = None  # graceful if not in path during some runs

# Modifiable test configuration (edit here for different scenarios)
TEST_BASE_EMAIL_DOMAIN = "e2e-test.theinternetparty.local"
TEST_DEFAULT_PASSWORD = "E2E_Test_Pass_123!"
TEST_WINDOW_PREFIX = "E2E-TEST"
TEST_NPC_PREFIX = "npc-e2e-"

# Global for the live server thread
_live_server_thread = None
_live_server_port = None


def _run_live_server(port: int):
    """Run PlotterApp on a specific port in this thread."""
    # Import inside to avoid side effects at collection time
    from PlotterApp import app
    # Use werkzeug development server (simple, threaded)
    # For real tests we prefer a background threaded server.
    app.run(host="127.0.0.1", port=port, use_reloader=False, threaded=True)


@pytest.fixture(scope="session")
def live_server():
    """Start a live PlotterApp on a free port. Returns the base URL."""
    global _live_server_thread, _live_server_port
    if _live_server_port is not None:
        return f"http://127.0.0.1:{_live_server_port}"

    import socket
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()

    _live_server_port = port
    _live_server_thread = threading.Thread(target=_run_live_server, args=(port,), daemon=True)
    _live_server_thread.start()

    # Give the server a moment to come up
    base = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            import urllib.request
            urllib.request.urlopen(base + "/", timeout=1)
            break
        except Exception:
            time.sleep(0.2)

    yield base

    # Teardown could kill the thread but for session scope we leave it (process end will clean)


@pytest.fixture
def base_url(live_server, request):
    """Base URL for the app under test. Respects --base-url if provided."""
    # pytest-playwright and our fixture cooperate.
    # Allow CLI override: pytest ... --base-url http://...
    return request.config.getoption("--base-url") or live_server


@pytest.fixture
def page(page: Page, base_url):
    """Provide a page already aware of our base. (playwright fixture still works)"""
    # We can do common setup here (e.g. ignore certain errors, set default timeout)
    page.set_default_timeout(15000)
    yield page


# Helper to force the entire app (Vote page etc.) to a specific window
def set_current_window_override(window_id: str, base_url: str = "http://127.0.0.1:5000"):
    """Use the operator endpoint or direct DB write to override current window for tests."""
    # Prefer the real operator path when possible, fall back to direct DB.
    # This makes /vote + Library instantly see the test data.
    try:
        import requests
        # The account operator panel hits /dev-tools/set-window-override or similar.
        # For tests we often just write it directly via Database for speed.
        if Database:
            Database.ensure_firebase_initialized()
            Database.db.reference("meta/currentWindowOverride").set(window_id)
            return True
    except Exception:
        pass
    return False


@pytest.fixture
def test_window_id():
    """A unique throwaway window id for the test."""
    import uuid
    wid = f"{TEST_WINDOW_PREFIX}-{uuid.uuid4().hex[:8]}"
    yield wid
    # Best-effort cleanup
    try:
        if Database:
            # Clear the window data
            Database.clear_window_votes(wid)  # if the helper exists / or direct
    except Exception:
        pass
