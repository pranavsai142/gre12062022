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
import concurrent.futures
from typing import List, Dict, Any, Optional

import Database
from firebase_admin import auth as admin_auth

from .npc_client import NPCClient


class NPCManager:
    """Orchestrates synthetic test users at scale."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        Database.ensure_firebase_initialized()

    def provision_batch(self, count: int = 5, prefix: str = "npc-scale-", concurrency: int = 10) -> List[NPCClient]:
        """Create + sign in `count` real NPC users. Concurrent because at fleet
        sizes (100+) serial Firebase signups dominate scenario wall time."""
        def _provision(i: int) -> NPCClient:
            email = f"{prefix}{uuid.uuid4().hex[:8]}@e2e-test.theinternetparty.local"
            name = f"NPC {prefix}{i}"
            client = NPCClient(base_url=self.base_url, email=email, name=name)
            client.ensure_user()
            client.signin_and_establish_session()
            return client

        if count <= 1 or concurrency <= 1:
            return [_provision(i) for i in range(count)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
            return list(ex.map(_provision, range(count)))

    def delete_all_test(self, prefix: str = "npc-scale-") -> int:
        """Delete Auth users whose email starts with the prefix. Returns count deleted.
        Uses the batch delete API (up to 1000 uids per call) — the one-by-one loop
        was unusable after 100-NPC scale runs."""
        uids = [u.uid for u in admin_auth.list_users().iterate_all()
                if u.email and u.email.startswith(prefix)]
        deleted = 0
        for i in range(0, len(uids), 1000):
            batch = uids[i:i + 1000]
            try:
                result = admin_auth.delete_users(batch)
                deleted += len(batch) - result.failure_count
            except Exception:
                for uid in batch:
                    try:
                        admin_auth.delete_user(uid)
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
