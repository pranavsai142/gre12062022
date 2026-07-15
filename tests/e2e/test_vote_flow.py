"""
Vote flow E2E tests (abstain default, submit once, already voted).

Uses the NPC harness for setup (real Firebase user + a canidate policy on an
isolated test window), then drives the REAL browser flow: login form → /vote →
radio defaults → cast ballot → already-voted state.
"""

import pytest

import uuid
import pytest
from playwright.sync_api import Page, expect

from tests.conftest import set_current_window_override, make_npc

@pytest.mark.e2e
def test_vote_page_public_preview_shows_ballot(page: Page, base_url: str, test_window_id):
    """Anonymous visitors see the ballot preview (items, no voting form)."""
    npc = make_npc(base_url)
    policy_id = npc.draft_and_submit_policy(
        f"E2E Preview Policy {test_window_id}", "Created by the E2E vote flow test."
    )
    set_current_window_override(test_window_id, base_url)
    try:
        page.goto(f"{base_url}/vote")
        expect(page.locator("body")).to_contain_text(f"E2E Preview Policy {test_window_id}")
        expect(page.locator("body")).to_contain_text(test_window_id)
    finally:
        _cleanup_policy(policy_id)

@pytest.mark.e2e
def test_login_vote_abstain_default_submit_and_already_voted(page: Page, base_url: str, test_window_id):
    """Full member voting flow through the real UI:
    - login via the actual login form (real Firebase JS)
    - ballot renders with Abstain pre-selected (safe default)
    - choose YES, submit (one immutable ballot), see already-voted state
    """
    npc = make_npc(base_url)
    policy_id = npc.draft_and_submit_policy(
        f"E2E Vote Policy {test_window_id}", "Created by the E2E vote flow test."
    )
    set_current_window_override(test_window_id, base_url)
    try:
        # Real login form (exact browser auth path)
        page.goto(f"{base_url}/login")
        page.fill("#email", npc.email)
        page.fill("#password", npc.password)
        page.click("#loginButton")
        page.wait_for_url("**/account", timeout=20000)

        # Ballot with Abstain as the pre-selected safe default
        page.goto(f"{base_url}/vote")
        item_key = f"policy-{policy_id}"
        abstain = page.locator(f'input[name="vote-{item_key}"][value="abstain"]')
        expect(abstain).to_be_checked()

        # Vote YES and cast the ballot (confirm dialog + result alert)
        page.check(f'input[name="vote-{item_key}"][value="yes"]')
        page.on("dialog", lambda d: d.accept())
        page.click("#submitBallot")
        page.wait_for_load_state("networkidle")

        # Immutability: the page now shows the recorded ballot instead of a form
        page.goto(f"{base_url}/vote")
        expect(page.locator("body")).to_contain_text("You voted: YES")
        expect(page.locator("#submitBallot")).to_have_count(0)
    finally:
        _cleanup_policy(policy_id)

def _cleanup_policy(policy_id: str):
    try:
        import Database
        Database.ensure_firebase_initialized()
        Database.db.reference(f"policy/canidate/{policy_id}").delete()
        Database.db.reference(f"policy/official/{policy_id}").delete()
    except Exception:
        pass
