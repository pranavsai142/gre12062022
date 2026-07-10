from flask import Flask, render_template_string, redirect, url_for
import User
import Database

def render(user):
    if(not User.validateUser(user)):
        user = None
    if user is None:
        return redirect(url_for('login'))

    drafts = Database.getDraftPolicies(user)
    canidates = Database.getCanidatePoliciesForUser(user)
    policies = Database.getOfficialPoliciesForUser(user)
    draftAmendments = Database.getDraftAmendments(user)
    canidateAmendments = Database.getCanidateAmendmentsForUser(user)
    amendments = Database.getOfficialAmendmentsForUser(user)

    window = Database.getCurrentVotingWindowId()
    ballot_count = len(canidates) + len(canidateAmendments)
    user_participated = Database.hasUserVotedInWindow(user["uid"], window) if user else False
    try:
        clock = Database.getVotingClock()
    except Exception:
        clock = {
            "windowId": window,
            "realWindowId": window,
            "nextWindowId": "—",
            "isOverride": False,
            "phase": "open",
            "serverNow": "",
            "endsAt": "",
            "secondsToRealWeekEnd": 0,
        }

    # Operator / live dev tools data (fetched server-side for first paint; JS keeps it fresh)
    op_ballot_pols, op_ballot_amends = [], []
    op_tallies = {}
    op_participation = 0
    op_all_windows = []
    op_window_details = {}
    try:
        op_ballot_pols, op_ballot_amends = Database.getBallotItems()
        op_tallies = Database.getWindowTallies(window) if (op_ballot_pols or op_ballot_amends) else {}
        op_participation = Database.getWindowParticipationCount(window)
        op_all_windows = Database.get_all_voting_windows()[:10]
        for w in op_all_windows[:6]:
            op_window_details[w] = Database.get_window_details(w)
    except Exception as _e:
        pass  # graceful in snapshot / early environments

    global_ballot_count = len(op_ballot_pols) + len(op_ballot_amends)

    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>The Internet Party — Your Account</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
                background: #fafafa;
            }
            .content {
                flex: 1;
                padding: 20px;
                max-width: 980px;
                margin: 0 auto;
            }
            footer {
                background-color: #333;
                color: white;
                text-align: center;
                padding: 10px;
                font-size: 14px;
            }
            .footer-text {
                margin: 0;
            }
            .footer-text span {
                color: #ff6600;
            }
            .menu-bar {
                display: flex;
                justify-content: space-around;
                background-color: #f8f8f8;
                padding: 10px 0;
                border-bottom: 1px solid #ccc;
            }
            .menu-item {
                margin: 0 15px;
                text-decoration: none;
                color: #333;
            }
            .menu-item:link,
            .menu-item:visited {
                color: #333;
            }
            .menu-item:hover {
                color: #ff6600;
            }
            .menu-item:active {
                color: #cc5200;
                font-weight: bold;
            }
            .menu-item.active {
                color: #ff6600;
                font-weight: bold;
            }
            .profile-card {
                background: white;
                border: 1px solid #eee;
                padding: 18px 22px;
                border-radius: 8px;
                margin-bottom: 24px;
            }
            .section { margin-bottom: 28px; }
            .section h3 { border-bottom: 2px solid #ff6600; padding-bottom: 4px; }
            .item-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 12px;
            }
            .item {
                background: white;
                border: 1px solid #e5e5e5;
                padding: 12px 14px;
                border-radius: 6px;
            }
            .status {
                display: inline-block;
                font-size: 0.9em;
                padding: 1px 7px;
                border-radius: 3px;
                background: #f0f0f0;
            }
            .ballot-notice {
                background:#fff3e0;
                border-left:5px solid #ff6600;
                padding:10px 14px;
                margin-bottom:16px;
            }
            .logout { display:inline-block; margin-top:10px; color:#c00; }

            /* Operator Tools — production-grade live control surface (matches Drafts/Detail/Policy quality) */
            .operator-section {
                margin-top: 28px;
                padding-top: 8px;
            }
            .op-header {
                background: #fff;
                border-left: 6px solid #ff6600;
                padding: 14px 18px;
                margin-bottom: 14px;
                border-radius: 0 6px 6px 0;
            }
            .op-header h3 {
                margin: 0;
                font-size: 1.15em;
                color: #222;
            }
            .op-card {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 16px 18px;
                margin-bottom: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            }
            .op-card h4 {
                margin: 0 0 10px;
                font-size: 1em;
                color: #333;
                border-bottom: 1px solid #eee;
                padding-bottom: 6px;
            }
            .op-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 12px;
            }
            .op-stat {
                font-size: 0.9em;
                color: #444;
            }
            .op-stat strong { color: #222; }
            .tally-list {
                font-family: monospace;
                font-size: 0.9em;
                background: #f8f8f8;
                padding: 8px 10px;
                border-radius: 4px;
                max-height: 140px;
                overflow: auto;
            }
            .voting-clock {
                display: flex;
                flex-wrap: wrap;
                align-items: baseline;
                gap: 8px 16px;
                background: #fff7ed;
                border: 1px solid #ffcc99;
                border-left: 6px solid #ff6600;
                padding: 12px 16px;
                margin: 0 0 18px;
                border-radius: 6px;
            }
            .voting-clock .vc-countdown {
                font-size: 1.1em;
                font-weight: 700;
                color: #cc5200;
                font-variant-numeric: tabular-nums;
            }
            .voting-clock .vc-detail {
                font-size: 0.9em;
                color: #555;
            }
            .window-row {
                display: flex;
                justify-content: space-between;
                padding: 4px 0;
                border-bottom: 1px dotted #eee;
                font-size: 0.9em;
            }
            .window-row:last-child { border-bottom: none; }
            .op-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-items: center;
            }
            .op-actions input {
                width: 70px;
                padding: 6px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 0.9em;
            }
            .op-btn {
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 0.9em;
                cursor: pointer;
                border: 1px solid #ccc;
                background: white;
            }
            .op-btn.primary {
                background: #ff6600;
                color: white;
                border-color: #ff6600;
            }
            .op-btn.danger {
                background: #c33;
                color: white;
                border-color: #c33;
            }
            .op-btn:hover { filter: brightness(0.95); }
            #action-result {
                margin-top: 12px;
                padding: 10px;
                background: #f0f8ff;
                border: 1px solid #aac;
                border-radius: 6px;
                font-family: monospace;
                font-size: 0.9em;
                white-space: pre-wrap;
                max-height: 160px;
                overflow: auto;
                display: none;
            }
            .op-note {
                font-size: 0.9em;
                color: #666;
                margin-top: 8px;
            }

            /* Mobile for profile, item grids, operator tools panel */
            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 16px; }
                .menu-bar {
                    padding: 8px 0; /* revised vs 4px 2px */
                    flex-wrap: wrap;
                    align-items: center;
                }
                .menu-item {
                    margin: 2px 8px;
                    padding: 8px 10px;
                    font-size: 0.95em;
                    min-height: 44px;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    text-decoration: none;
                    color: #333;
                }
                .menu-item:link,
                .menu-item:visited {
                    color: #333;
                }
                .menu-item:hover {
                    color: #ff6600;
                    background: #fff7ed;
                }
                .menu-item:active {
                    color: #cc5200;
                    font-weight: bold;
                }
                .menu-item.active {
                    color: #ff6600;
                    font-weight: bold;
                }
                .item-grid { grid-template-columns: 1fr; gap: 10px; }
                .op-grid { grid-template-columns: 1fr; }
                .op-actions { flex-direction: column; align-items: stretch; }
                .op-actions input { width: 100%; }
                .op-btn { padding: 10px 14px; width: 100%; }
                .profile-card { padding: 14px 16px; }
                .section { margin-bottom: 22px; }
                #action-result { font-size: 0.9em; }
                .status { font-size: 0.9em; }
                .tally-list { font-size: 0.9em; }
                .window-row { font-size: 0.9em; }
                .op-note { font-size: 0.9em; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item active">Account</a>
            </div>

            <div class="content">
                <h2>Your Personal Command Center</h2>

                <div class="profile-card">
                    <strong>Logged in as:</strong> {{ user.email or user.uid }}<br>
                    <small>UID: {{ user.uid }}</small><br>
                    <a href="{{ url_for('logout') }}" class="logout">Log out</a>
                </div>

                <div class="voting-clock"
                     data-voting-clock
                     data-window-id="{{ clock.windowId }}"
                     data-next-window="{{ clock.nextWindowId }}"
                     data-ends-at="{{ clock.endsAt or '' }}"
                     data-server-now="{{ clock.serverNow }}"
                     data-override="{{ '1' if clock.isOverride else '0' }}"
                     data-phase="{{ clock.phase }}"
                     data-seconds-real-end="{{ clock.secondsToRealWeekEnd }}">
                    <span class="vc-countdown">
                        {% if clock.endsAt %}Window {{ clock.windowId }} ends {{ clock.endsAt }} (UTC){% else %}Loading clock…{% endif %}
                    </span>
                </div>

                {% if global_ballot_count > 0 %}
                <div class="ballot-notice">
                    <strong>Active ballot this week ({{ window }})</strong> — {{ global_ballot_count }} candidate items on the global ballot.
                    {% if user_participated %}
                        You have already voted this window. Thank you.
                    {% else %}
                        <a href="{{ url_for('vote') }}">Cast your vote now →</a>
                    {% endif %}
                    <span style="font-size:0.9em;color:#888;display:block;margin-top:4px;">(Your own submissions appear in the sections below.)</span>
                </div>
                {% endif %}

                <div class="section">
                    <h3>My Drafts (Private) <a href="{{ url_for('drafts') }}" style="font-size:0.9em;font-weight:400;color:#ff6600;margin-left:12px;">Open full Drafts hub →</a></h3>
                    <div class="item-grid">
                        {% for d in drafts %}
                        <div class="item">
                            <a href="{{ url_for('drafts') }}">{{ d.getTitle() }}</a>
                            <span class="status">Draft</span>
                        </div>
                        {% endfor %}
                        {% for d in draftAmendments %}
                        <div class="item">
                            <a href="{{ url_for('drafts', amend=(d.getPolicyId() or '')) }}">{{ d.getTitle() }}</a>
                            <span class="status">Draft Amendment</span>
                        </div>
                        {% endfor %}
                        {% if not drafts and not draftAmendments %}
                            <em>No drafts yet. <a href="{{ url_for('drafts', new='policy') }}">Start one</a></em>
                        {% endif %}
                    </div>
                </div>

                <div class="section">
                    <h3>On the Current Ballot (Your Submissions)</h3>
                    <div class="item-grid">
                        {% for c in canidates %}
                        <div class="item">
                            <a href="{{ url_for('detail', policyId=c.policyId) }}">{{ c.getTitle() }}</a>
                            <span class="status">Candidate</span>
                        </div>
                        {% endfor %}
                        {% for c in canidateAmendments %}
                        <div class="item">
                            <a href="{{ url_for('detail_amendment', amendmentId=c.getId()) }}">{{ c.getTitle() }}</a>
                            <span class="status">Candidate Amendment</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="section">
                    <h3>Enacted in the Official Platform (Your Contributions)</h3>
                    <div class="item-grid">
                        {% for p in policies %}
                        <div class="item">
                            <a href="{{ url_for('detail', policyId=p.policyId) }}">{{ p.getTitle() }}</a>
                            <span class="status" style="background:#e6f4e6;color:#0a7">Official</span>
                        </div>
                        {% endfor %}
                        {% for a in amendments %}
                        <div class="item">
                            <a href="{{ url_for('detail_amendment', amendmentId=a.getId()) }}">{{ a.getTitle() }}</a>
                            <span class="status" style="background:#e6f4e6;color:#0a7">Official</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <!-- =====================================================================
                     OPERATOR & DEV TOOLS — PRIMARY LIVE CONTROL SURFACE (website-first)
                     All actions hit the real Database helpers via existing /dev-tools/* and
                     /close-window endpoints. State changes are immediate; refresh or use the
                     JS refresh button to see live updates on this page. No prefab/CLI required
                     for day-to-day operator work.
                     ===================================================================== -->
                <div class="section operator-section">
                    <div class="op-header">
                        <h3>🛠️ Operator &amp; Dev Tools — Live Control Surface</h3>
                    </div>
                    <div class="op-card">
                        <div style="font-size:0.9em;color:#555;margin-bottom:10px;">
                            This is the <strong>primary real-time operator console</strong>. Open <a href="{{ url_for('account') }}" style="color:#ff6600;">/account</a> while logged in and control windows, seed test data, promote winners, and inspect everything live. Changes appear instantly across the site (Library, Vote, etc.).
                        </div>

                        <!-- Current Window Snapshot -->
                        <div class="op-card" style="background:#fafafa;border:1px solid #eee;padding:12px 14px;margin-bottom:12px;">
                            <h4 style="margin-bottom:8px;">Current Window (effective): <span style="font-family:monospace;">{{ window }}</span> <span style="font-size:0.9em;color:#888;">({{ op_participation }} participants)</span></h4>
                            <p style="margin:0 0 10px;font-size:0.9em;color:#555;">
                                Real ISO week: <code>{{ clock.realWindowId }}</code>
                                {% if clock.isOverride %} · <strong style="color:#c60;">override active</strong>{% endif %}
                                · next <code>{{ clock.nextWindowId }}</code>
                                {% if clock.endsAt %} · ends <code>{{ clock.endsAt }}</code>{% endif %}
                                · <a href="/voting-clock" style="color:#ff6600;">/voting-clock</a>
                            </p>
                            <div class="op-grid">
                                <div class="op-stat">
                                    <strong>Ballot items:</strong> {{ op_ballot_pols|length + op_ballot_amends|length }}<br>
                                    <span style="font-size:0.9em;">{{ op_ballot_pols|length }} policies + {{ op_ballot_amends|length }} amendments</span>
                                </div>
                                <div class="op-stat">
                                    <strong>Live tallies (top):</strong>
                                    <div class="tally-list">
{%- for key, t in op_tallies.items() %}
{{ key[:28] }}… Y:{{ t.yes }} N:{{ t.no }} A:{{ t.abstain }}
{%- else %}No tallies yet (seed or vote to populate)
{%- endfor %}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Windows Overview -->
                        <div class="op-card" style="background:#fafafa;border:1px solid #eee;padding:12px 14px;margin-bottom:12px;">
                            <h4>All Voting Windows (live + history)</h4>
                            <div id="windows-container">
{%- for w in op_all_windows %}
                                <div class="window-row">
                                    <span><strong>{{ w }}</strong></span>
                                    <span>
{%- if w in op_window_details %}
                                        {{ op_window_details[w].participation_count }} voters / {{ op_window_details[w].vote_count }} votes
{%- else %}—{%- endif %}
                                    </span>
                                </div>
{%- else %}
                                <em>No window data yet (run seed or vote).</em>
{%- endfor %}
                            </div>
                            <div class="op-note">Data fetched at page load. Use Refresh button below for latest.</div>
                        </div>

                        <!-- Live Action Buttons (real mutations, visible results) -->
                        <div class="op-card" style="background:#fff3e0;border-left:5px solid #ff6600;padding:14px 16px;">
                            <h4 style="margin-bottom:8px;color:#c60;">Live Operator Actions — Full Test Control</h4>

                            <div style="margin-bottom:8px;">
                                <label style="font-size:0.9em;">Target Window (edit + Set or hit Enter to override what the whole site sees as "current"):</label><br>
                                <input type="text" id="targetWindow" value="{{ window }}" style="width:100%; font-family:monospace; padding:6px;" onkeydown="if (event.key === 'Enter') { setCurrentWindowFromInput(); }">
                                <button onclick="setCurrentWindowFromInput()" class="op-btn" style="padding:10px 14px; background:#555; color:white; border:none; border-radius:4px; cursor:pointer;">Set</button>
                                <button onclick="clearCurrentWindowOverride()" class="op-btn" style="padding:10px 14px; background:#888; color:white; border:none; border-radius:4px; cursor:pointer;">Clear override</button>
                            </div>

                            <div class="op-actions" style="flex-wrap:wrap; gap:8px;">
                                <!-- Precise deterministic seeding the user requested -->
                                <button onclick="doOperatorAction('seed-yes')" class="op-btn primary">Seed 3 YES (all items)</button>
                                <button onclick="doOperatorAction('seed-no')" class="op-btn primary">Seed 5 NO (all items)</button>
                                <button onclick="doOperatorAction('seed-abstain')" class="op-btn primary">Seed 10 ABSTAIN (all items)</button>

                                <button onclick="doOperatorAction('clear')" class="op-btn danger">Clear All Votes in Window</button>

                                <button onclick="doOperatorAction('promote')" class="op-btn primary">Promote Winners</button>

                                <!-- Per-user reset -->
                                <button onclick="doOperatorAction('reset-user')" class="op-btn" style="background:#555;">Reset Specific User Votes</button>

                                <button onclick="refreshOperatorData()" class="op-btn">↻ Refresh</button>
                            </div>

                            <div id="action-result" style="margin-top:10px; white-space:pre-wrap; font-family:monospace; font-size:0.9em; padding:8px; border:1px solid #ddd; border-radius:4px; display:none;"></div>

                            <div class="op-note" style="margin-top:8px;">
                                Full clean test abilities: deterministic yes/no/abstain batches, clear, per-user reset, arbitrary window IDs for "new window" testing, promote.
                                All changes are real and instantly visible on the public site.
                            </div>
                        </div>
                    </div>
                </div>

                <p style="margin-top:20px"><a href="{{ url_for('policy') }}">Browse the full Congressional Library →</a></p>

                <!-- Operator action JS: talks to the pre-existing /dev-tools/* endpoints for real-time control -->
                <script>
                function showOpResult(text, isError) {
                    const el = document.getElementById('action-result');
                    if (!el) return;
                    el.style.display = 'block';
                    el.style.background = isError ? '#fff0f0' : '#f0fff0';
                    el.style.borderColor = isError ? '#e88' : '#8c8';
                    el.textContent = text;
                }

                async function doOperatorAction(action) {
                    let url = '';
                    let body = {};
                    let confirmMsg = '';
                    let targetWindow = document.getElementById('targetWindow') ? document.getElementById('targetWindow').value.trim() : '{{ window }}';

                    if (action === 'seed') {
                        const cnt = parseInt(document.getElementById('seedCount').value || '3', 10);
                        url = '/dev-tools/seed';
                        body = { window: targetWindow, count: cnt };
                    } else if (action === 'seed-yes') {
                        url = '/dev-tools/seed';
                        body = { window: targetWindow, count: 3, choice: "yes" };   // 3 Yes on everything
                    } else if (action === 'seed-no') {
                        url = '/dev-tools/seed';
                        body = { window: targetWindow, count: 5, choice: "no" };    // 5 No
                    } else if (action === 'seed-abstain') {
                        url = '/dev-tools/seed';
                        body = { window: targetWindow, count: 10, choice: "abstain" };  // 10 Abstain
                    } else if (action === 'clear') {
                        confirmMsg = 'PERMANENTLY DELETE all votes in this window?';
                        if (!confirm(confirmMsg)) return;
                        url = '/dev-tools/clear';
                        body = { window: targetWindow, confirm: true };
                    } else if (action === 'promote') {
                        confirmMsg = 'Tabulate and promote winners from this window?';
                        if (!confirm(confirmMsg)) return;
                        url = '/dev-tools/promote';
                        body = { window: targetWindow };
                    } else if (action === 'reset-user') {
                        const uid = prompt('Enter exact user ID (uid) to reset in this window:');
                        if (!uid) return;
                        url = '/dev-tools/reset-user';
                        body = { window: targetWindow, user_id: uid };
                    }

                    try {
                        const resp = await fetch(url, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(body)
                        });
                        const data = await resp.json();
                        const msg = (data && (data.message || JSON.stringify(data)));
                        showOpResult('[' + action.toUpperCase() + '] ' + msg, false);

                        if ((action === 'promote' || action === 'clear') && data && data.success) {
                            setTimeout(() => {
                                if (confirm('Action complete. Reload to see fresh state?')) {
                                    window.location.reload();
                                }
                            }, 600);
                        }
                    } catch (e) {
                        showOpResult('Error during ' + action + ': ' + e, true);
                    }
                }

                async function refreshOperatorData() {
                    // Simple full reload keeps it trivial and reliable (real-time enough for operator use)
                    window.location.reload();
                }

                // Keyboard nicety: allow Enter in seed count to trigger seed (elements exist; script is after markup)
                const seedInput = document.getElementById('seedCount');
                if (seedInput) {
                    seedInput.addEventListener('keypress', function(ev) {
                        if (ev.key === 'Enter') {
                            doOperatorAction('seed');
                        }
                    });
                }

                // --- Target Window override controls (new in this iteration) ---
                async function setCurrentWindowFromInput() {
                    const input = document.getElementById('targetWindow');
                    if (!input) return;
                    const val = input.value.trim();
                    try {
                        const resp = await fetch('/dev-tools/set-window', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ window: val || null })
                        });
                        const data = await resp.json();
                        const msg = (data && (data.message || JSON.stringify(data)));
                        showOpResult('[SET-WINDOW] ' + msg, false);
                        // Reload so the header "Current window: XXX" and all ballot logic reflect the new effective window
                        setTimeout(() => {
                            if (confirm('Window override applied. Reload page to see the site use the new current window?')) {
                                window.location.reload();
                            }
                        }, 400);
                    } catch (e) {
                        showOpResult('Error setting window: ' + e, true);
                    }
                }

                async function clearCurrentWindowOverride() {
                    try {
                        const resp = await fetch('/dev-tools/set-window', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ window: null })
                        });
                        const data = await resp.json();
                        const msg = (data && (data.message || JSON.stringify(data)));
                        showOpResult('[CLEAR-WINDOW] ' + msg, false);
                        setTimeout(() => {
                            if (confirm('Override cleared. Reload to use the real ISO week as current window?')) {
                                window.location.reload();
                            }
                        }, 300);
                    } catch (e) {
                        showOpResult('Error clearing window override: ' + e, true);
                    }
                }
                </script>
                <script src="{{ url_for('static', filename='js/voting-clock.js') }}"></script>
            </div>

            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, drafts=drafts, canidates=canidates, policies=policies,
         draftAmendments=draftAmendments, canidateAmendments=canidateAmendments, amendments=amendments,
         window=window, ballot_count=ballot_count, user_participated=user_participated,
         global_ballot_count=global_ballot_count, clock=clock,
         op_ballot_pols=op_ballot_pols, op_ballot_amends=op_ballot_amends, op_tallies=op_tallies,
         op_participation=op_participation, op_all_windows=op_all_windows, op_window_details=op_window_details)