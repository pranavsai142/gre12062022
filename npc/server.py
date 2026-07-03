"""
npc/server.py

Little Python server + web dashboard for managing NPC fleets and running scale tests.

Run:
    pipenv run python -m npc.server
    # or
    pipenv run python npc/server.py

Opens a simple control panel at http://localhost:5555 (orange card aesthetic to match the site).
Target app defaults to http://localhost:5000 — override with TARGET_BASE_URL
(e.g. a deployed Render URL; window-prefix safety guards still apply).
"""

import os
import json
import time
from flask import Flask, request, render_template_string

from .npc_manager import NPCManager
from .scenarios import run_full_cycle, cleanup_scenario

app = Flask(__name__)
mgr = NPCManager(base_url=os.environ.get("TARGET_BASE_URL", "http://localhost:5000"))

DASHBOARD_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>NPC Test Harness — The Internet Party</title>
  <style>
    body { font-family: system-ui, sans-serif; background:#111; color:#ddd; padding:20px; }
    .card { background:#1f1f1f; border:1px solid #333; border-radius:8px; padding:16px; margin-bottom:16px; }
    h1, h2 { color:#ff6600; }
    button { background:#ff6600; color:#111; border:none; padding:8px 14px; border-radius:4px; cursor:pointer; font-weight:600; }
    input, select { padding:6px; background:#222; color:#ddd; border:1px solid #444; }
    table { width:100%; border-collapse: collapse; }
    th, td { padding:6px 8px; border-bottom:1px solid #333; text-align:left; }
    .metrics { font-family: monospace; background:#222; padding:8px; white-space:pre-wrap; word-wrap:break-word; }
  </style>
</head>
<body>
  <h1>NPC Scale Harness</h1>
  <p>Target: <code>{{ target }}</code> — change with TARGET_BASE_URL env</p>

  <div class="card">
    <h2>Fleet Control</h2>
    <form action="/npcs/create" method="post">
      Create <input name="count" type="number" value="5" min="1" style="width:60px"> NPCs
      <button type="submit">Spawn</button>
    </form>
    <form action="/npcs/delete" method="post" style="margin-top:8px">
      <button type="submit">Delete all test NPCs (prefix npc-scale-)</button>
    </form>
  </div>

  <div class="card">
    <h2>Active NPCs ({{ npcs|length }})</h2>
    <table>
      <tr><th>Email</th><th>UID</th></tr>
      {% for n in npcs[:25] %}
      <tr><td>{{ n.email }}</td><td>{{ n.uid }}</td></tr>
      {% endfor %}
    </table>
    {% if npcs|length > 25 %}<p><em>…and {{ npcs|length - 25 }} more.</em></p>{% endif %}
    {% if not npcs %}<p><em>No NPCs right now.</em></p>{% endif %}
  </div>

  <div class="card">
    <h2>Full Governance Cycle at Scale</h2>
    <p>Drafters propose real policies → voters cast real immutable ballots concurrently →
       integrity checks → operator promote → metrics. Runs on an isolated SCALE- window.</p>
    <form action="/scenarios/full-cycle" method="post">
      <label>Window ID: <input name="window_id" value="SCALE-TEST-{{ ts }}"></label><br><br>
      Drafters: <input name="drafters" type="number" value="3" style="width:60px">
      Voters: <input name="voters" type="number" value="12" style="width:60px">
      Concurrency: <input name="concurrency" type="number" value="20" style="width:60px">
      <label style="margin-left:8px"><input type="checkbox" name="cleanup" value="1" checked> cleanup after</label>
      <button type="submit">Run Full Cycle</button>
    </form>
    <p class="metrics">{{ last_result or '' }}</p>
  </div>

  <p><small>See npc/README.md and TESTING.md. All actions use the real public API.</small></p>
</body>
</html>
"""

@app.route("/")
def index():
    npcs = mgr.list_active()
    return render_template_string(DASHBOARD_HTML, target=mgr.base_url, npcs=npcs,
                                  ts=int(time.time()), last_result=request.args.get("result"))

@app.route("/npcs/create", methods=["POST"])
def create_npcs():
    count = int(request.form.get("count", 5))
    clients = mgr.provision_batch(count)
    return f"Created {len(clients)} NPCs. <a href='/'>Back</a>"

@app.route("/npcs/delete", methods=["POST"])
def delete_npcs():
    n = mgr.delete_all_test()
    return f"Deleted {n} test NPCs. <a href='/'>Back</a>"

@app.route("/scenarios/full-cycle", methods=["POST"])
def full_cycle():
    window = request.form.get("window_id") or f"SCALE-TEST-{int(time.time())}"
    metrics = run_full_cycle(
        base_url=mgr.base_url,
        window_id=window,
        n_drafters=int(request.form.get("drafters", 3)),
        n_voters=int(request.form.get("voters", 12)),
        concurrency=int(request.form.get("concurrency", 20)),
        cleanup=bool(request.form.get("cleanup")),
    )
    pretty = json.dumps(metrics, indent=2)
    return f"<pre style='font-family:monospace'>{pretty}</pre> <a href='/'>Back</a>"

if __name__ == "__main__":
    port = int(os.environ.get("NPC_PORT", 5555))
    print(f"NPC dashboard on http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
