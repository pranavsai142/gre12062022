# gre12062022
gre12062022

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

## Dev Tools & Admin Console (Post-Voting Engine)

The approved plan delivered fully runnable tooling:

- Visual dashboards: `pipenv run prefab serve dev_tools/dev_dashboard.py` and `pipenv run prefab serve admin/admin_console.py`
- Primary agent CLI (real mutations): `pipenv run python -m dev_tools.cli --help`
  (list-windows, seed, clear, simulate, promote — all wired to production Database helpers)

See DEV_NOTES_AND_IMPLEMENTATION_STATUS.md and FIREBASE_STRUCTURE.md for details.
The public site (especially /policy as the Congressional Library) is now high-quality and consistent with the Vote page.