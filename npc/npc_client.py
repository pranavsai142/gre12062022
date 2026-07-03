"""
NPCClient — drives NPC actions using the *exact* existing HTTP API that the browser uses.

- Auth: Firebase REST sign-up / sign-in + /validate-token (exact browser API)
- Mutations use identical POSTs to /create-draft etc as static/js and PlotterApp
- TARGET_BASE_URL configurable. Pure client, no direct DB mutations.
"""

import requests
import time
import uuid
from typing import Dict, Any, Optional

class NPCClient:
    """Lightweight client that behaves like a browser tab for one NPC user."""

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
        })
        r.raise_for_status()
        id_token = r.json()["idToken"]

        # 2. Exchange at our app (exactly like the frontend does)
        resp = self.session.post(f"{self.base_url}/validate-token", json={"idToken": id_token})
        # The app sets a Flask session cookie on success
        if resp.status_code >= 400:
            raise RuntimeError(f"validate-token failed: {resp.status_code} {resp.text}")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self.session.post(url, json=payload)
        if not r.ok:
            raise RuntimeError(f"POST {path} failed: {r.status_code} {r.text}")
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

    # High-level actions mirroring the JS clients
    def create_draft(self, title: str, description: str, category: str = "") -> Dict[str, Any]:
        return self._post("/create-draft", {"title": title, "description": description, "category": category})

    def submit_draft(self, draft_id: str) -> Dict[str, Any]:
        return self._post("/submit-draft", {"draft_id": draft_id})

    def create_amendment(self, policy_id: str, title: str, description: str) -> Dict[str, Any]:
        return self._post("/create-draft-amendment", {
            "target_policy_id": policy_id,
            "title": title,
            "description": description
        })

    def submit_amendment(self, amendment_id: str) -> Dict[str, Any]:
        return self._post("/submit-draft-amendment", {"draft_amendment_id": amendment_id})

    def get_current_ballot(self, window_id: Optional[str] = None) -> Dict[str, Any]:
        # For simplicity, the /vote page or a JSON endpoint. NPC can also read via requests.
        # Many tests drive this via the page or use Database directly for assertions.
        params = {"window": window_id} if window_id else {}
        r = self.session.get(f"{self.base_url}/vote", params=params)
        return {"status": r.status_code}

    def submit_ballot(self, window_id: str, votes: Dict[str, str]) -> Dict[str, Any]:
        """votes: {"policy-xxx": "yes" | "no" | "abstain", ...}"""
        return self._post("/submit-ballot", {"windowId": window_id, "votes": votes})

    def vote_all(self, choice: str, window_id: Optional[str] = None) -> Dict[str, Any]:
        """Convenience: vote the same choice on everything currently on the ballot."""
        # In real usage the caller usually knows the items or fetches via /vote or Database.
        # Here we provide a placeholder that the scale runner will fill properly.
        if not window_id:
            window_id = "CURRENT"  # the server will have set override
        # A production implementation would call get_ballot_items and build the map.
        return {"note": "Implement ballot item fetch + map in full version", "choice": choice}

    def __repr__(self):
        return f"<NPCClient {self.email} uid={self.uid}>"
