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
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
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


@pytest.fixture(scope="session")
def base_url(request):
    """Base URL for the app under test. Respects --base-url if provided.
    Session-scoped because pytest-base-url's session fixtures consume it.
    Only starts the in-process live server when no --base-url is given."""
    override = request.config.getoption("--base-url")
    if override:
        return override
    return request.getfixturevalue("live_server")


@pytest.fixture
def page(page: Page, base_url):
    """Provide a page already aware of our base. (playwright fixture still works)"""
    # We can do common setup here (e.g. ignore certain errors, set default timeout)
    page.set_default_timeout(15000)
    yield page


# Helper to force the entire app (Vote page etc.) to a specific window
def set_current_window_override(window_id, base_url: str = "http://127.0.0.1:5000"):
    """Direct DB write of meta/currentWindowOverride (fast test control path).
    Pass None to clear. This makes /vote + Library instantly see the test data."""
    try:
        if Database:
            Database.ensure_firebase_initialized()
            ref = Database.db.reference("meta/currentWindowOverride")
            if window_id:
                ref.set(window_id)
            else:
                ref.delete()
            return True
    except Exception:
        pass
    return False


@pytest.fixture
def test_window_id():
    """A unique throwaway window id for the test. Clears the window data AND the
    site-wide override on teardown so tests never leave the live site pointed at
    a dead test window."""
    import uuid
    wid = f"{TEST_WINDOW_PREFIX}-{uuid.uuid4().hex[:8]}"
    yield wid
    try:
        if Database:
            Database.ensure_firebase_initialized()
            Database.clear_window_votes(wid, confirm=True)
            current = Database.db.reference("meta/currentWindowOverride").get()
            if current == wid:
                Database.db.reference("meta/currentWindowOverride").delete()
    except Exception:
        pass


def make_npc(base_url: str, prefix: str = TEST_NPC_PREFIX):
    """One real authenticated NPC (Firebase user + Flask session) for test setup.
    The NPC harness is the blessed way to arrange multi-user state in E2E tests.
    All NPCs with the E2E prefix are deleted at session end (see fixture below)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from npc.npc_manager import NPCManager
    return NPCManager(base_url=base_url).provision_batch(1, prefix=prefix)[0]


@pytest.fixture(scope="session", autouse=True)
def _cleanup_e2e_npcs():
    """Delete the Firebase Auth users this suite created (prefix-based), so
    repeated runs don't accumulate synthetic accounts."""
    yield
    try:
        from npc.npc_manager import NPCManager
        deleted = NPCManager().delete_all_test(prefix=TEST_NPC_PREFIX)
        if deleted:
            print(f"\n[conftest] Deleted {deleted} {TEST_NPC_PREFIX}* NPC auth users")
    except Exception:
        pass
