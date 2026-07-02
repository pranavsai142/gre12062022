#!/usr/bin/env python
"""
Internal-only runner (binds only to 127.0.0.1).
Use this with a relay like socat so that a stable non-Python process
is the one the macOS firewall sees on the network.

Usage:
    pipenv run python run_internal.py
"""

from PlotterApp import app

if __name__ == "__main__":
    print("Starting PlotterApp INTERNALLY on 127.0.0.1:5000 (no reloader)")
    print("A relay (socat etc.) should be listening on 0.0.0.0:5000 and forwarding here.")
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
