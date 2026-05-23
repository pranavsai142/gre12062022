"""
Internet Party Dev Tools CLI (secondary power tool).

PRIMARY EXPERIENCE: Use the live website instead.
  1. Run the main site: pipenv run python -m PlotterApp   (or python PlotterApp.py)
  2. Open http://localhost:5000/account  (log in or register)
  3. Scroll to "Operator & Dev Tools — Live Control Surface" at bottom.
     Seed, clear, promote, inspect windows/tallies — all in real time in your browser.
     No separate commands or dashboards needed for 95% of operator work.

This CLI is the agent/script-friendly secondary interface. All mutations delegate to Database.py.

Usage examples (from repo root, after `pipenv install`):
    pipenv run python -m dev_tools.cli list-windows
    pipenv run python -m dev_tools.cli seed --window 2026-W21 --count 5
    pipenv run python -m dev_tools.cli clear --window 2026-DEV-01 --confirm
    pipenv run python -m dev_tools.cli simulate --window 2026-W21
    pipenv run python -m dev_tools.cli promote --window 2026-W21

Requires the Firebase service account JSON at /Users/pranav/data/... (falls back to snapshot for reads).
"""

import argparse
import sys
from pathlib import Path

# Ensure parent (repo root) is on path so "import Database" works when run as -m
sys.path.insert(0, str(Path(__file__).parent.parent))

import Database

# Ensure firebase is ready (safe to call multiple times)
def _ensure_firebase():
    Database.ensure_firebase_initialized()

def cmd_list_windows(args):
    _ensure_firebase()
    wins = Database.get_all_voting_windows()
    if not wins:
        print("No voting windows found (or running in snapshot-only mode).")
        # Try snapshot parse as last resort for demo
        print("Tip: Use the Prefab dashboards for snapshot view: pipenv run prefab serve dev_tools/dev_dashboard.py")
        return
    print("Voting Windows:")
    for w in wins:
        detail = Database.get_window_details(w)
        print(f"  - {w}: participation={detail.get('participation_count',0)}, votes={detail.get('vote_count',0)}")

def cmd_seed(args):
    _ensure_firebase()
    res = Database.seed_test_votes(args.window, count=args.count, force=True)
    print(res.get("message", res))
    if res.get("success"):
        print("Success. Re-run list-windows or open the Admin Console /vote page to see effects.")

def cmd_clear(args):
    _ensure_firebase()
    if not args.confirm:
        print("ERROR: --confirm is required for destructive clear operation.")
        print("This is intentional safety (mirrors the helper).")
        sys.exit(1)
    res = Database.clear_window_votes(args.window, confirm=True)
    print(res.get("message", res))

def cmd_simulate(args):
    _ensure_firebase()
    print(f"Simulating election cycle on {args.window}...")
    seed_res = Database.seed_test_votes(args.window, count=3, force=True)
    print("  Seed:", seed_res.get("message"))
    tallies = Database.getWindowTallies(args.window)
    print(f"  Tallies computed for {len(tallies)} items.")
    # Use the real Vote module (not Database.Vote)
    from Vote import Vote
    winners = Vote.getWinners(tallies, minYes=1) if tallies else []
    print(f"  Winners that would promote: {winners}")
    print("Simulation complete. Use 'promote' command or the button on /vote to actually enact.")

def cmd_promote(args):
    _ensure_firebase()
    print(f"Promoting winners from window {args.window}...")
    res = Database.promoteWinnersFromWindow(args.window)
    print(res)

def main():
    parser = argparse.ArgumentParser(
        prog="python -m dev_tools.cli",
        description="Internet Party Dev Tools & Admin CLI (agent-friendly)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-windows", help="List all known voting windows with counts")
    p_list.set_defaults(func=cmd_list_windows)

    p_seed = sub.add_parser("seed", help="Seed synthetic test votes for a window (for agentic testing)")
    p_seed.add_argument("--window", required=True, help="Window ID e.g. 2026-W21")
    p_seed.add_argument("--count", type=int, default=5, help="Number of fake voters")
    p_seed.set_defaults(func=cmd_seed)

    p_clear = sub.add_parser("clear", help="DANGEROUS: clear all votes/participation for a window")
    p_clear.add_argument("--window", required=True)
    p_clear.add_argument("--confirm", action="store_true", help="Must pass to actually delete")
    p_clear.set_defaults(func=cmd_clear)

    p_sim = sub.add_parser("simulate", help="Run a full seed + tally simulation cycle")
    p_sim.add_argument("--window", required=True)
    p_sim.set_defaults(func=cmd_simulate)

    p_prom = sub.add_parser("promote", help="Promote winners from a window to official (real production path)")
    p_prom.add_argument("--window", required=True)
    p_prom.set_defaults(func=cmd_promote)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()