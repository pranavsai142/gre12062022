"""Shared helper: unlock demo after forced disclaimer (real accept-disclaimer path)."""

from __future__ import annotations

REQUIRED_ACKS = {
    "ack_simulation": "1",
    "ack_polish": "1",
    "ack_lockin": "1",
    "ack_crowdsource": "1",
    "ack_demos": "1",
    "ack_demo_only": "1",
}


def accept_disclaimer(client, next_path: str = "/"):
    from product_status import DISCLAIMER_VERSION

    r = client.post(
        "/accept-disclaimer",
        data={**REQUIRED_ACKS, "next": next_path, "version": DISCLAIMER_VERSION},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303), getattr(r, "data", r)
    return r
