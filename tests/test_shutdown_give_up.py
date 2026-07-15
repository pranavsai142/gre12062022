"""
Hard shut-down mode (PRODUCT_DISCONTINUED=1) — optional tombstone.

Default product mode is forced-disclaimer demo; see test_forced_disclaimer.py.
These tests only run when hard shut-down is explicitly enabled.
"""

from __future__ import annotations

import os

import pytest

# Only meaningful when env forces hard tombstone
pytestmark = pytest.mark.skipif(
    os.environ.get("PRODUCT_DISCONTINUED", "0").strip().lower()
    not in ("1", "true", "yes", "on"),
    reason="hard shut-down tests require PRODUCT_DISCONTINUED=1",
)


@pytest.fixture
def client():
    # Re-import under env is hard; skip suite documents the optional path.
    from PlotterApp import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_hard_shutdown_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"shut down" in r.data.lower() or b"discontinued" in r.data.lower()
