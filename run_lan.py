#!/usr/bin/env python
"""
LAN-accessible development runner for PlotterApp.py

This forces:
- host 0.0.0.0 so it listens on all interfaces
- no reloader (the reloader child process is a frequent cause of ALF / socketfilterfw problems)
- threaded=True (helps when browsers fetch multiple /plot and /delta images concurrently)
- explicit port

Usage (recommended):
    pipenv run python run_lan.py

Then, while it is listening on :5000, add the firewall rule for the *exact*
Python binary shown by `lsof -i :5000`.

See the firewall troubleshooting notes for the precise socketfilterfw + GUI steps.

You can still use `pipenv run python PlotterApp.py` for normal localhost-only
development (it will use the original debug+reloader behavior).
"""

from PlotterApp import app

if __name__ == "__main__":
    print("Starting PlotterApp for LAN access (no reloader, threaded)...")
    print("Listen on http://0.0.0.0:5000 (LAN IP should also work once firewall allows)")
    print("Confirm the exact process with: lsof -i :5000 -nP")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
