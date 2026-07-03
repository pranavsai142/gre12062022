"""
NPCClient — drives NPC actions using the *exact* existing HTTP API that the browser uses.

- Auth: Firebase REST sign-up / sign-in + /validate-token (exact browser API)
- Mutations use identical POSTs to /create-draft etc as static/js and PlotterApp
  (payload keys mirror DraftsPage.py / vote.js exactly: "id", "policyId", "votes")
- Ballot discovery uses the public read-only /ballot-items JSON route
- TARGET_BASE_URL configurable. Pure HTTP client, no direct DB mutations.
"""

import requests
import uuid
from typing import Dict, Any, Optional

class NPCClient:
    """Lightweight client that behaves like a browser tab for one NPC user."""

    # Same public web API key the browser uses (static/js/login.js)
    FIREBASE_API_KEY = "AIzaSyAQ5Sty_qAzOBtd_h2gFTGEC5sHH3_fNWE"
    SIGNUP_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={key}"
    SIGNIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={key}"

    def __init__(self, base_url: str = "http://localhost:5000", email: Optional[str] = None, password: Optional[str] = None, name: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.uid: Optional[str] = None
        self.email = email or f"npc-{uuid.uuid4().hex[:8]}@e2e-test.theinternetparty.local"
        self.password = password or "NPC_Test_Pass_123!"
        self.name = name or "NPC Tester"

    def ensure_user(self) -> str:
        """Create the user in Firebase Auth if it doesn't exist (via Admin SDK)."""
        import Database
        Database.ensure_firebase_initialized()
        from firebase_admin import auth as admin_auth

        try:
            user = admin_auth.get_user_by_email(self.email)
            self.uid = user.uid
        except admin_auth.UserNotFoundError:
            user = admin_auth.create_user(
                email=self.email,
                password=self.password,
                display_name=self.name
            )
            self.uid = user.uid

        # Tag as synthetic for easy cleanup
        try:
            admin_auth.set_custom_user_claims(self.uid, {"synthetic": True, "npc": True})
        except Exception:
            pass

        return self.uid

    def signin_and_establish_session(self) -> None:
        """Sign in via Firebase REST (same as browser) then POST to /validate-token to get Flask session."""
        # 1. Sign in with REST to get idToken
        signin_url = self.SIGNIN_URL.format(key=self.FIREBASE_API_KEY)
        r = requests.post(signin_url, json={
            "email": self.email,
            "password": self.password,
            "returnSecureToken": True
        }, timeout=30)
        r.raise_for_status()
        id_token = r.json()["idToken"]

        # 2. Exchange at our app (exactly like the frontend does).
        # One retry after a short pause: a just-issued token can trip clock-skew
        # rejection on the server during high-concurrency provisioning.
        import time as _time
        for attempt in range(2):
            resp = self.session.post(f"{self.base_url}/validate-token", json={"idToken": id_token}, timeout=30)
            if resp.status_code < 400:
                return
            if attempt == 0:
                _time.sleep(1.5)
        raise RuntimeError(f"validate-token failed: {resp.status_code} {resp.text[:300]}")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self.session.post(url, json=payload, timeout=60)
        try:
            body = r.json()
        except Exception:
            body = {"raw": r.text}
        if not r.ok:
            raise RuntimeError(f"POST {path} failed: {r.status_code} {body.get('error', body)}")
        return body

    # ------------------------------------------------------------------
    # High-level actions mirroring the JS clients (DraftsPage.py saveDraft /
    # submitToCanidate and static/js/vote.js — identical payload keys).
    # ------------------------------------------------------------------

    def create_draft(self, title: str, description: str) -> Dict[str, Any]:
        """Returns {"success": True, "id": "<new draft policy id>"}."""
        return self._post("/create-draft", {"title": title, "description": description})

    def submit_draft(self, draft_id: str) -> Dict[str, Any]:
        return self._post("/submit-draft", {"id": draft_id})

    def create_amendment(self, policy_id: str, title: str, description: str) -> Dict[str, Any]:
        """Returns {"success": True, "id": "<new draft amendment id>"}."""
        return self._post("/create-draft-amendment", {
            "policyId": policy_id,
            "title": title,
            "description": description
        })

    def submit_amendment(self, amendment_id: str) -> Dict[str, Any]:
        return self._post("/submit-draft-amendment", {"id": amendment_id})

    def draft_and_submit_policy(self, title: str, description: str) -> str:
        """Full drafter flow: create private draft, then elevate to canidate.
        Returns the policy id."""
        created = self.create_draft(title, description)
        policy_id = created.get("id")
        if not policy_id:
            raise RuntimeError(f"create-draft did not return an id: {created}")
        self.submit_draft(policy_id)
        return policy_id

    def get_ballot_items(self) -> Dict[str, Any]:
        """Public JSON view of the live ballot: {"windowId":..., "items":[{key,kind,id,title}]}."""
        r = self.session.get(f"{self.base_url}/ballot-items", timeout=30)
        r.raise_for_status()
        return r.json()

    def submit_ballot(self, window_id: str, votes: Dict[str, str]) -> Dict[str, Any]:
        """votes: {"policy-xxx": "yes" | "no" | "abstain", ...}"""
        return self._post("/submit-ballot", {"windowId": window_id, "votes": votes})

    def vote_all(self, choice: str, window_id: Optional[str] = None) -> Dict[str, Any]:
        """Vote the same choice on everything currently on the ballot.
        Fetches the live ballot via /ballot-items (respects the window override),
        builds the full choices map, and casts one immutable ballot."""
        ballot = self.get_ballot_items()
        window_id = window_id or ballot["windowId"]
        votes = {item["key"]: choice for item in ballot["items"]}
        if not votes:
            return {"success": False, "error": "No items on the ballot to vote on."}
        return self.submit_ballot(window_id, votes)

    def close_window(self, window_id: Optional[str] = None) -> Dict[str, Any]:
        """Operator action: tabulate + promote winners (same endpoint the Vote page button hits)."""
        return self._post("/close-window", {"windowId": window_id} if window_id else {})

    def set_window_override(self, window_id: Optional[str]) -> Dict[str, Any]:
        """Operator action: point the whole live site at a window (or clear with None).
        Same endpoint the /account Target Window box uses."""
        return self._post("/dev-tools/set-window", {"window": window_id or ""})

    def __repr__(self):
        return f"<NPCClient {self.email} uid={self.uid}>"
