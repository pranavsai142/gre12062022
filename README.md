# gre12062022
gre12062022

## Quick Start (Current Primary Experience)
**Run the live site + operator tools (recommended):**
```bash
pipenv shell
pipenv install
pipenv run python PlotterApp.py
```
Then open http://localhost:5000 (register/login) → /account (or /admin) and scroll to the **Operator & Dev Tools** panel at the bottom for live seed/clear/promote/inspection.

The legacy reproduction notes below are historical.

DIRECTIONS FOR DATA REPRODUCTION:
Google how to:
Install python 3.10
Install pipenv
Install git command line (Xcode command line tools has git included)

once python and pipenv are installed run following commands in mac terminal:
git clone https://github.com/pranavsai142/gre12062022.git
cd gre12062022
pipenv shell
pipenv install
python Plotter.py

## Dev Tools & Admin Console (Post-Voting Engine) — Website is now PRIMARY

**Primary live operator surface (recommended — real-time, what you asked for):**
- Run the site: `pipenv run python PlotterApp.py` (or `pipenv run python -m PlotterApp`)
- Open http://localhost:5000/account and log in (or register)
- Scroll to **"Operator & Dev Tools — Live Control Surface"** at the bottom of your Account page.
- Inspect live windows / ballot / tallies, Seed test votes, Clear, Promote winners — all buttons produce instant visible results on the site itself. No extra dashboards or memorized commands.

**Secondary power tools (for agents / scripts / separate visual):**
- CLI (agent-first): `pipenv run python -m dev_tools.cli --help`
- Visual: `pipenv run prefab serve dev_tools/dev_dashboard.py` (and the admin_console)

All three paths (website, CLI, Prefab) use the exact same Database.py + Vote.py logic.

See `notes/GROK/SOUL_DRIVER.md` (north star) and `notes/GROK/DEV_NOTES.md` (current reality + open items) for the living project truth. The old comprehensive `DEV_NOTES_AND_IMPLEMENTATION_STATUS.md` has been retired into `notes/GROK/ARCHIVE/`.

The auth pages (Login/Register) and amendment details were polished to production standard in the 2026-05 iteration; the voting governance engine + live Operator Tools on `/account` are the major delivered capability.