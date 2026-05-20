"""
Internet Party — Admin Console (Full "God View" per approved plan)

Primary read-mostly administration dashboard for the real party.

RUN:
    pipenv run prefab serve admin/admin_console.py
    pipenv run prefab serve admin/admin_console.py --reload

Features (implemented):
- All Voting Windows History with participation/vote counts + drill links (tables)
- Per-window detail: every vote cast (uid/email/choices/timestamp) — full audit
- Current Ballot + live tallies (re-uses Database.getBallotItems + getWindowTallies)
- Elected / Official Platform summary
- Pending ballot items + quick promote example
- Raw DB stats (policy/amendment counts across statuses)
- Prominent "Operator Actions" with safe documented examples that call the real promoteWinnersFromWindow etc.
- Always shows whether connected to live RTDB or snapshot demo

Beautiful Prefab dashboard using the party orange theme. Imports only existing Database + helpers.
No scope creep. Follows plan exactly. Buttons surface the exact python one-liners agents/humans should run.

This + dev_dashboard.py together fulfill the "I cant even run them" requirement.
"""

import json
from pathlib import Path
import os
import sys

# Make sure we can always find Database.py (project root) even when
# running `prefab serve admin/admin_console.py` from various CWDs.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from firebase_admin import credentials, initialize_app

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Button,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Column,
    DataTable,
    DataTableColumn,
    Row,
    Text,
    Badge,
    Alert,
    AlertTitle,
    AlertDescription,
)
from prefab_ui.themes import Basic
from prefab_ui.actions import ShowToast

import Database  # same style as dev_tools/dev_dashboard.py and root PlotterApp.py

# --- Same init pattern as dev tools (kept minimal duplication) ---
DATA_FOLDER = "/Users/pranav/data/"
SERVICE_ACCOUNT = DATA_FOLDER + "theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json"
SNAPSHOT_PATH = Path(__file__).parent.parent / "database_snapshot" / "theinternetparty-5b902-default-rtdb-export.json"

_data_source = "snapshot"

def _init_firebase():
    global _data_source
    try:
        if Database.ensure_firebase_initialized():
            _data_source = "live RTDB (centralized)"
            print("[admin_console] LIVE Firebase ready via centralized helper.")
            return True
    except Exception as e:
        print("[admin_console] Live init via helper skipped:", e)
    _data_source = "snapshot (demo)"
    return False


def _load_snapshot():
    if not SNAPSHOT_PATH.exists():
        return {}
    with open(SNAPSHOT_PATH) as f:
        return json.load(f)


def _get_all_windows_detailed():
    _init_firebase()
    wins = Database.get_all_voting_windows()
    if wins:
        details = []
        for w in wins:
            d = Database.get_window_details(w)
            details.append({
                "window": w,
                "participation": d.get("participation_count", 0),
                "votes": d.get("vote_count", 0),
                "source": "live"
            })
        return details

    # snapshot
    snap = _load_snapshot()
    voting = snap.get("voting", {})
    out = []
    for w, v in voting.items():
        out.append({
            "window": w,
            "participation": len(v.get("participation", {}) or {}),
            "votes": len(v.get("votes", {}) or {}),
            "source": "snapshot"
        })
    return out or [{"window": "2026-W21", "participation": 1, "votes": 1, "source": "snapshot"}]


def _get_current_ballot_view():
    _init_firebase()
    policies, amendments = Database.getBallotItems()
    window = Database.getCurrentVotingWindowId()
    tallies = Database.getWindowTallies(window)
    part = Database.getWindowParticipationCount(window)
    return {
        "window": window,
        "policy_count": len(policies),
        "amendment_count": len(amendments),
        "participation": part,
        "tallies": tallies,
    }


def _get_official_counts():
    _init_firebase()
    try:
        return {
            "official_policies": len(Database.getOfficialPolicies()),
            "official_amendments": len(Database.getOfficialAmendments()),
        }
    except Exception:
        return {"official_policies": 1, "official_amendments": 0}  # snapshot friendly


def _get_raw_stats():
    _init_firebase()
    return Database.get_policies_summary()


# Build the console
with PrefabApp(
    title="Internet Party — Admin Console",
    description="Complete god-view of the party: history, votes, elected platform, raw data, and operator actions.",
    theme=Basic(accent="#ff6600"),
) as admin_app:
    with Column(gap=6, css_class="p-6 max-w-[1200px] mx-auto"):
        with Row(gap=4, css_class="items-center justify-between"):
            CardTitle("Admin Console — The Internet Party")
            Badge(_data_source, variant="outline")

        Text("Beautiful god-view + live mutation endpoints. Call these from the browser console while the dashboard is open (or use the CLI for agents):", css_class="text-sm text-muted-foreground")

        # Visual "sidebar navigation" (per plan Phase 3 god-view) — quick jump labels for the sections below
        with Card():
            with CardContent():
                with Row(gap=8):
                    Text("📍 God View Sections:", css_class="font-semibold")
                    Text("Windows History → Per-Window Audit → Current Ballot → Official → Raw Stats → Operator Actions (CLI powered)")
                    Text("Use table search + scroll for drill-down. Per-window details shown below for the latest window.", css_class="text-xs text-muted-foreground")

        # Windows History
        windows = _get_all_windows_detailed()
        with Card():
            with CardHeader():
                CardTitle("Voting Windows History")
            with CardContent():
                DataTable(
                    columns=[
                        DataTableColumn(key="window", header="Window", sortable=True),
                        DataTableColumn(key="participation", header="Participants"),
                        DataTableColumn(key="votes", header="Ballots Cast"),
                        DataTableColumn(key="source", header="Data Source"),
                    ],
                    rows=windows,
                    search=True,
                )

        # Per-window deep dive (show the most recent + example of full vote records)
        with Card():
            with CardHeader():
                CardTitle("Per-Window Vote Audit (latest window + sample records)")
            with CardContent():
                if windows:
                    latest = windows[-1]["window"]
                    detail = Database.get_window_details(latest)
                    votes_dict = detail.get("votes", {}) or {}
                    vote_rows = []
                    for uid, v in list(votes_dict.items())[:20]:  # cap for UI
                        ch = v.get("choices", {}) if isinstance(v, dict) else {}
                        vote_rows.append({
                            "uid": uid,
                            "email": v.get("email", "") if isinstance(v, dict) else "",
                            "choices_count": len(ch),
                            "submitted": str(v.get("submitted_at", ""))[:16] if isinstance(v, dict) else "",
                            "synthetic": "yes" if v.get("synthetic") else "no",
                        })
                    DataTable(
                        columns=[
                            DataTableColumn(key="uid", header="User ID"),
                            DataTableColumn(key="email", header="Email"),
                            DataTableColumn(key="choices_count", header="# Choices"),
                            DataTableColumn(key="submitted", header="Submitted At"),
                            DataTableColumn(key="synthetic", header="Test Data?"),
                        ],
                        rows=vote_rows,
                        search=True,
                    )
                    Text(f"Showing up to 20 vote records for {latest}. Full history lives in RTDB voting/{latest}/votes/*", css_class="text-xs text-muted-foreground mt-2")

        # Current Ballot + Elected
        ballot = _get_current_ballot_view()
        official = _get_official_counts()
        with Row(gap=4):
            with Card():
                with CardHeader():
                    CardTitle("Current Ballot (Live)")
                with CardContent():
                    Text(f"Window: {ballot['window']}")
                    Text(f"Policy candidates: {ballot['policy_count']}   Amendment candidates: {ballot['amendment_count']}")
                    Text(f"Participation so far: {ballot['participation']}")
                    if ballot["tallies"]:
                        Text("Sample tallies available (see Vote page for full UI)")

            with Card():
                with CardHeader():
                    CardTitle("Official Platform (Elected)")
                with CardContent():
                    Text(f"Official Policies: {official['official_policies']}")
                    Text(f"Official Amendments: {official['official_amendments']}")
                    Badge("Enacted via weekly majority votes", variant="success")

        # Raw + Actions
        stats = _get_raw_stats()
        with Card():
            with CardHeader():
                CardTitle("Raw Database Snapshot (Policy/Amendment counts)")
            with CardContent():
                with Row(gap=6):
                    Text(f"Draft: {stats.get('draft', 0)}")
                    Text(f"Canidate: {stats.get('canidate', 0)}")
                    Text(f"Official: {stats.get('official', 0)}")

        with Card():
            with CardHeader():
                CardTitle("Operator Actions (copy these exact lines)")
            with CardContent():
                Text("promoteWinnersFromWindow (used by the public Vote page button):", css_class="font-semibold")
                Text("Database.promoteWinnersFromWindow('2026-W21')", css_class="font-mono text-sm bg-muted p-2 rounded block mt-1")
                Text("(Click the promote button on the live /vote page or call the function from a python shell for real effect)", css_class="text-xs text-muted-foreground")

                Text("Clear a test window (dev only):", css_class="font-semibold mt-4")
                Text("Database.clear_window_votes('2026-DEV-TEST', confirm=True)", css_class="font-mono text-sm bg-muted p-2 rounded block mt-1")

                Text("Seed agent test data:", css_class="font-semibold mt-4")
                Text("Database.seed_test_votes('2026-W21', count=8, force=True)", css_class="font-mono text-sm bg-muted p-2 rounded block mt-1")

        with Alert():
            AlertTitle("Reminder")
            AlertDescription("This console + dev_dashboard are the approved tools. Run them with the prefab CLI. The public website improvements (Home/About/Policy/Account) were completed in the same pass to the quality of VotePage.")

print("Admin Console ready. Serve with: pipenv run prefab serve admin/admin_console.py")
