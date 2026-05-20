"""
Dev Tools package for The Internet Party.

Provides:
- Visual dashboards via `prefab serve dev_tools/dev_dashboard.py`
- Agentic CLI via `python -m dev_tools.cli ...`

All operations delegate to Database.py helpers for consistency with the live site.
"""

from . import cli  # makes `python -m dev_tools.cli` work after package install / path setup

__all__ = ["cli"]