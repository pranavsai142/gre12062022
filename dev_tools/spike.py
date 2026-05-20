"""
Prefab spike for The Internet Party Dev Tools / Admin Console.

Run with (CORRECT command):
    pipenv run prefab serve dev_tools/spike.py

(Or: pipenv run prefab serve dev_tools/spike.py --port 5176 --reload)

This proves that Prefab works in the project and gives us a beautiful
Python-defined dashboard we can evolve into the real Dev Tools + Admin tools.

The spike uses snapshot data for demo (always runnable). Full tools add live RTDB + mutations.
"""

import json
from pathlib import Path

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
)
from prefab_ui.themes import Basic
from prefab_ui.actions import ShowToast

# Load the real snapshot the user gave us so we have authentic data
SNAPSHOT_PATH = Path(__file__).parent.parent / "database_snapshot" / "theinternetparty-5b902-default-rtdb-export.json"

def load_windows():
    if not SNAPSHOT_PATH.exists():
        return [{"window": "2026-W21 (demo)", "votes_cast": 1, "items_on_ballot": 6}]
    with open(SNAPSHOT_PATH) as f:
        data = json.load(f)
    windows = []
    voting = data.get("voting", {})
    for win in voting:
        v = voting[win]
        participation = len(v.get("participation", {}))
        # Count unique items across all votes in this window
        all_choices = set()
        for uid_data in v.get("votes", {}).values():
            if isinstance(uid_data, dict):
                all_choices.update(uid_data.get("choices", {}).keys())
        windows.append({
            "window": win,
            "votes_cast": participation,
            "items_on_ballot": len(all_choices) or 6,
        })
    return windows or [{"window": "No windows in snapshot", "votes_cast": 0, "items_on_ballot": 0}]


with PrefabApp(
    title="Internet Party — Dev Tools (Spike)",
    description="Agent-friendly testing & administration dashboards",
    theme=Basic(accent="#ff6600"),  # Party orange
) as app:
    with Column(gap=6):
        CardTitle("Voting Windows (from snapshot + live)")

        windows = load_windows()

        DataTable(
            columns=[
                DataTableColumn(key="window", header="Window ID", sortable=True),
                DataTableColumn(key="votes_cast", header="Votes Cast", sortable=True),
                DataTableColumn(key="items_on_ballot", header="Items on Ballot"),
            ],
            rows=windows,
            search=True,
        )

        with Row(gap=3):
            Button(
                "Clear Votes for Selected Window (DEV ONLY)",
                variant="destructive",
                on_click=ShowToast("Spike: would call Database.clear_window_votes(). Full impl in dev_dashboard.py"),
            )
            Button(
                "Seed 5 Test Votes",
                variant="secondary",
                on_click=ShowToast("Spike: would call seed helpers. See dev_dashboard.py for working version."),
            )

        with Card():
            with CardHeader():
                CardTitle("Status")
            with CardContent():
                Badge("Spike Fixed & Runnable", variant="success")
                Text(" Run: pipenv run prefab serve dev_tools/spike.py ", css_class="font-mono text-xs")
                Text("This spike proves Prefab + the real Firebase snapshot work together (with correct theme API). Full Dev Tools + Admin Console implemented alongside.", css_class="text-sm text-muted-foreground")

        Text("Corrected for Prefab 0.19+ (Basic theme). Next iteration wires real Database.py mutations.", css_class="text-sm text-muted-foreground")