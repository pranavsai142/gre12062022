"""
Basic smoke E2E test for The Internet Party.

Verifies the live server + Playwright integration works:
- Home loads
- Can navigate to /vote and /policy (public pages)

Run:
  pipenv run pytest tests/e2e/test_smoke.py --browser chromium -q
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_home_loads_and_navigates_to_vote_and_policy(page: Page, base_url: str):
    """Smoke: load home, verify navigation targets /vote and /policy work."""
    # Load home
    page.goto(f"{base_url}/")
    expect(page).to_have_title("The Internet Party — Truth • Freedom • Health")

    # Basic nav check: menu items / links are present
    # (menu uses url_for so links contain the paths)
    expect(page.locator('a[href*="/vote"]')).to_be_visible()
    expect(page.locator('a[href*="/policy"]')).to_be_visible()

    # Quick navigation to /vote
    page.goto(f"{base_url}/vote")
    # The vote page should have some recognizable content (ballot area or login prompt)
    expect(page.locator("body")).to_contain_text("Vote", ignore_case=True)

    # Go to library
    page.goto(f"{base_url}/policy")
    expect(page.locator("body")).to_contain_text("Library", ignore_case=True)
