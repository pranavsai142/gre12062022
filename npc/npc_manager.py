"""NPCManager: batch operations for provisioning, listing, and cleaning synthetic NPC users.

- Batch create real authenticated NPCs (via NPCClient)
- List NPCs by email prefix or custom claims (synthetic/npc tags)
- Delete test NPCs (auth users)
- Reuses Database.ensure_firebase_initialized()
- Lightweight: intended for scale / automated test harnesses
- Tagging: custom claims + email prefix convention ("npc-scale-")
- NPCs created are full citizens: own private drafts (by uid), cast real uid votes

Do not use on production data without extreme caution (delete is destructive on Auth records).
"""

import uuid
from typing import List, Dict, Any, Optional

import Database
from firebase_admin import auth as admin_auth

from .npc_client import NPCClient


class NPCManager:
    """Orchestrates synthetic test users at scale."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        Database.ensure_firebase_initialized()

    def provision_batch(self, count: int = 5, prefix: str = "npc-scale-") -> List[NPCClient]:
        clients: List[NPCClient] = []
        for i in range(count):
            email = f"{prefix}{uuid.uuid4().hex[:8]}@e2e-test.theinternetparty.local"
            name = f"NPC {prefix}{i}"
            client = NPCClient(base_url=self.base_url, email=email, name=name)
            uid = client.ensure_user()
            client.signin_and_establish_session()
            clients.append(client)
        return clients

    def delete_all_test(self, prefix: str = "npc-scale-") -> int:
        """Delete Auth users whose email starts with the prefix. Returns count deleted."""
        deleted = 0
        for user in admin_auth.list_users().iterate_all():
            if user.email and user.email.startswith(prefix):
                try:
                    admin_auth.delete_user(user.uid)
                    deleted += 1
                except Exception:
                    pass
        return deleted

    def list_active(self, prefix: str = "npc-scale-") -> List[Dict[str, Any]]:
        out = []
        for user in admin_auth.list_users().iterate_all():
            if user.email and user.email.startswith(prefix):
                out.append({"uid": user.uid, "email": user.email, "display_name": user.display_name})
        return out
