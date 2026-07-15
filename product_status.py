"""
Product lifecycle for The Internet Party.

Default mode (2026-07-14+): **disclaimer demo**
  - Mission as a real national Party No. 3 is abandoned.
  - The software stays up so people can *see and use the idea*.
  - First visit forces a long disclaimer (session-gated) with the
    sociological revelations from the give-up conversation.
  - After accept: full app works; a persistent banner remains.

Optional hard shut-down (tombstone only):
  PRODUCT_DISCONTINUED=1

Disable the forced gate (local forensics only):
  FORCED_DISCLAIMER=0
"""

from __future__ import annotations

import os

# Hard shut-down: all HTML becomes tombstone; writes 410. Default OFF — demo is open
# behind the disclaimer.
_raw_disc = os.environ.get("PRODUCT_DISCONTINUED", "0").strip().lower()
PRODUCT_DISCONTINUED = _raw_disc in ("1", "true", "yes", "on")

# Forced disclaimer before explore/use. Default ON.
_raw_force = os.environ.get("FORCED_DISCLAIMER", "1").strip().lower()
FORCED_DISCLAIMER = _raw_force not in ("0", "false", "no", "off")

# Bump when the forced text materially changes — users re-read.
DISCLAIMER_VERSION = "2026-07-14-v1"
SESSION_DISCLAIMER_KEY = "disclaimer_accepted_version"

DISCONTINUED_CODE = "PRODUCT_DISCONTINUED"
DISCONTINUED_HTTP = 410

DISCONTINUED_PUBLIC_MESSAGE = (
    "The Internet Party product mission is discontinued. "
    "Hard shut-down mode is enabled (PRODUCT_DISCONTINUED=1)."
)

DISCONTINUED_JSON = {
    "success": False,
    "discontinued": True,
    "code": DISCONTINUED_CODE,
    "error": DISCONTINUED_PUBLIC_MESSAGE,
    "archive": "/disclaimer",
}

NEED_DISCLAIMER_HTTP = 403
NEED_DISCLAIMER_CODE = "DISCLAIMER_REQUIRED"
NEED_DISCLAIMER_JSON = {
    "success": False,
    "disclaimer_required": True,
    "code": NEED_DISCLAIMER_CODE,
    "error": (
        "You must open /disclaimer and accept the forced fair-warning notice "
        "before using this demo."
    ),
    "disclaimer_url": "/disclaimer",
}


def is_discontinued() -> bool:
    """Hard tombstone mode (rare)."""
    return PRODUCT_DISCONTINUED


def is_forced_disclaimer() -> bool:
    """Session-gated fair warning before explore/use."""
    return FORCED_DISCLAIMER and not PRODUCT_DISCONTINUED


def is_demo_with_disclaimer() -> bool:
    return is_forced_disclaimer()


def discontinued_payload(**extra):
    body = dict(DISCONTINUED_JSON)
    body.update(extra)
    return body


def need_disclaimer_payload(**extra):
    body = dict(NEED_DISCLAIMER_JSON)
    body.update(extra)
    return body


def session_has_accepted_disclaimer(session_obj) -> bool:
    if not session_obj:
        return False
    return session_obj.get(SESSION_DISCLAIMER_KEY) == DISCLAIMER_VERSION


def mark_disclaimer_accepted(session_obj) -> None:
    session_obj[SESSION_DISCLAIMER_KEY] = DISCLAIMER_VERSION
    session_obj.permanent = True


def product_status_header() -> str:
    if PRODUCT_DISCONTINUED:
        return "discontinued"
    if FORCED_DISCLAIMER:
        return "demo-disclaimer"
    return "open"
