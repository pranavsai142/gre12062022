"""
Product lifecycle flag for The Internet Party.

When PRODUCT_DISCONTINUED is True (default), the public site is a shut-down
surface and all governance / membership mutating paths refuse writes.

Override only for forensic local inspection of legacy route handlers:
  PRODUCT_DISCONTINUED=0
"""

from __future__ import annotations

import os

# Default: fully given up. Explicit "0" / "false" re-enables legacy handlers.
_raw = os.environ.get("PRODUCT_DISCONTINUED", "1").strip().lower()
PRODUCT_DISCONTINUED = _raw not in ("0", "false", "no", "off")

DISCONTINUED_CODE = "PRODUCT_DISCONTINUED"
DISCONTINUED_HTTP = 410  # Gone

DISCONTINUED_PUBLIC_MESSAGE = (
    "The Internet Party has been discontinued. "
    "This service is shut down and no longer accepts participation."
)

DISCONTINUED_JSON = {
    "success": False,
    "discontinued": True,
    "code": DISCONTINUED_CODE,
    "error": DISCONTINUED_PUBLIC_MESSAGE,
    "archive": "/about",  # same shutdown page; investigation lives in repo notes
}


def is_discontinued() -> bool:
    return PRODUCT_DISCONTINUED


def discontinued_payload(**extra):
    body = dict(DISCONTINUED_JSON)
    body.update(extra)
    return body
