from flask import Flask, render_template_string
import User
import Database
from datetime import datetime


def render(user):
    if(not User.validateUser(user)):
        user = None

    windowId = Database.getCurrentVotingWindowId()
    policies, amendments = Database.getBallotItems()
    ballot = Database.getBallotForUser(user) if user else None

    # Prepare simple dicts for the template so Jinja stays readable
    def _prep(items, kind):
        out = []
        for it in items:
            key = f"{kind}-{it.getId()}"
            item_dict = {
                "key": key,
                "id": it.getId(),
                "title": it.getTitle(),
                "description": it.getDescription()[:400] + ("..." if len(it.getDescription()) > 400 else ""),
                "kind": kind,
                "userChoice": ballot.getUserChoice(key) if ballot else None,
            }
            if kind == "amendment":
                pid = it.getPolicyId() if hasattr(it, "getPolicyId") else ""
                ptitle = ""
                if pid:
                    try:
                        p = Database.getPolicy(user, pid)
                        if p and hasattr(p, "getTitle"):
                            ptitle = p.getTitle() or ""
                    except Exception:
                        pass
                item_dict["targetPolicyId"] = pid
                item_dict["targetPolicyTitle"] = ptitle
            out.append(item_dict)
        return out

    policyItems = _prep(policies, "policy")
    amendmentItems = _prep(amendments, "amendment")

    hasLiveBallot = len(policyItems) + len(amendmentItems) > 0
    userCanVoteNow = bool(ballot and not ballot.userChoices and user)
    userAlreadyVoted = bool(ballot and ballot.userChoices) if ballot else False
    tallies = Database.getWindowTallies(windowId) if hasLiveBallot else {}
    participation = Database.getWindowParticipationCount(windowId)

    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>The Internet Party — Vote</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
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
                color: #ff6600; /* A vibrant orange for Grok */
            }
            /* Menu (duplicated per existing site convention) */
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
            .menu-item.active {
                color: #ff6600;
                font-weight: bold;
            }
            /* Ballot-specific styles */
            .ballot-header {
                background: #f4f4f4;
                padding: 12px 16px;
                border-left: 6px solid #ff6600;
                margin-bottom: 20px;
            }
            .ballot-item {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 14px 16px;
                margin-bottom: 14px;
                background: white;
            }
            .ballot-item h4 {
                margin: 0 0 6px 0;
                font-size: 1.05em;
            }
            .ballot-item .meta {
                font-size: 0.9em;
                color: #666;
                margin-bottom: 8px;
            }
            .ballot-item pre {
                background: #fafafa;
                padding: 8px;
                border-radius: 4px;
                font-size: 0.9em;
                white-space: pre-wrap;
                word-wrap: break-word;
                overflow-x: auto;
            }
            .vote-controls {
                display: flex;
                gap: 16px;
                margin-top: 10px;
                flex-wrap: wrap;
            }
            .vote-controls label {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 0.95em;
                cursor: pointer;
            }
            .vote-controls input[type=radio] {
                transform: scale(1.2);
            }
            .already-voted {
                color: #0a7;
                font-weight: bold;
            }
            .section {
                margin-bottom: 32px;
            }
            .section h3 {
                border-bottom: 2px solid #ff6600;
                padding-bottom: 4px;
            }
            .submit-bar {
                position: sticky;
                bottom: 0;
                background: #fff;
                padding: 16px;
                border-top: 3px solid #ff6600;
                box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
                text-align: center;
            }
            .promote-btn {
                background: #222;
                color: white;
                border: none;
                padding: 10px 18px;
                cursor: pointer;
                font-size: 0.95em;
                margin-left: 12px;
            }
            .promote-btn:hover { background: #444; }
            .empty-state {
                background: #fff9e6;
                border: 1px dashed #cc9900;
                padding: 30px;
                text-align: center;
                border-radius: 8px;
            }
            .notice {
                background: #e8f4e8;
                border-left: 5px solid #0a7;
                padding: 10px 14px;
                margin: 12px 0;
                font-size: 0.9em;
            }

            /* Mobile for ballot items, vote radios, sticky submit bar */
            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 16px; max-width: 100%; }
                .menu-bar { padding: 4px 2px; flex-wrap: wrap; }
                .menu-item {
                    margin: 3px 6px; padding: 10px 12px; font-size: 0.95em;
                    min-height: 44px; display: inline-flex; align-items: center; justify-content: center; border-radius: 4px;
                }
                .ballot-item { padding: 12px 14px; }
                .ballot-item pre { font-size: 0.95em; }
                .vote-controls { gap: 10px; }
                .vote-controls label { font-size: 1em; padding: 4px 2px; }
                .submit-bar { padding: 12px; }
                .submit-bar button { padding: 12px 20px; font-size: 1em; width: 100%; max-width: 320px; }
                .section { margin-bottom: 24px; }
                .empty-state { padding: 20px; }
                .meta { font-size: 0.9em; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar (exact pattern used on every page) -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item.active">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                <h2>Vote — Window {{ windowId }}</h2>

                <div class="ballot-header">
                    <p><strong>The Internet Party holds regular votes on candidate policies and amendments.</strong></p>
                    <p>Per our MetaPolicies: any registered member may vote once per weekly window. Policies that receive a majority of votes cast are promoted to the official platform.</p>
                    <p><small>Current window: <strong>{{ windowId }}</strong> &nbsp;•&nbsp; Participation so far: <strong>{{ participation }}</strong> members</small></p>
                </div>

                {% if not hasLiveBallot %}
                    <div class="empty-state">
                        <h3>No items are currently on the ballot</h3>
                        <p>Submit drafts from your Account or the Drafts hub (open it from your Account), then have them advanced to <em>canidate</em> status. They will appear here automatically for the next weekly vote.</p>
                        <p><a href="{{ url_for('drafts') }}">Go to Drafts hub →</a></p>
                    </div>
                {% else %}

                    <!-- POLICIES SECTION -->
                    <div class="section">
                        <h3>Candidate Policies on the Ballot ({{ policyItems|length }})</h3>
                        {% for item in policyItems %}
                            <div class="ballot-item" data-item-key="{{ item.key }}">
                                <h4><a href="{{ url_for('detail', policyId=item.id) }}">{{ item.title }}</a></h4>
                                <div class="meta">Policy</div>
                                <pre>{{ item.description }}</pre>

                                {% if item.userChoice %}
                                    <div class="already-voted">✓ You voted: <strong>{{ item.userChoice|upper }}</strong></div>
                                {% elif userCanVoteNow %}
                                    <div class="vote-controls">
                                        <label><input type="radio" name="vote-{{ item.key }}" value="yes"> Yes — Promote to Official Platform</label>
                                        <label><input type="radio" name="vote-{{ item.key }}" value="no"> No</label>
                                        <label><input type="radio" name="vote-{{ item.key }}" value="abstain" checked> Abstain</label>
                                    </div>
                                {% endif %}

                                {% if item.key in tallies %}
                                    <div style="font-size:0.9em; margin-top:6px; color:#555;">
                                        Current tally: Yes {{ tallies[item.key].yes }} • No {{ tallies[item.key].no }} • Abstain {{ tallies[item.key].abstain }}
                                    </div>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>

                    <!-- AMENDMENTS SECTION -->
                    <div class="section">
                        <h3>Candidate Amendments on the Ballot ({{ amendmentItems|length }})</h3>
                        {% for item in amendmentItems %}
                            <div class="ballot-item" data-item-key="{{ item.key }}">
                                <h4><a href="{{ url_for('detail_amendment', amendmentId=item.id) }}">{{ item.title }}</a></h4>
                                <div class="meta">Amendment{% if item.targetPolicyTitle %} to <a href="{{ url_for('detail', policyId=item.targetPolicyId) }}">{{ item.targetPolicyTitle }}</a>{% endif %}</div>
                                <pre>{{ item.description }}</pre>

                                {% if item.userChoice %}
                                    <div class="already-voted">✓ You voted: <strong>{{ item.userChoice|upper }}</strong></div>
                                {% elif userCanVoteNow %}
                                    <div class="vote-controls">
                                        <label><input type="radio" name="vote-{{ item.key }}" value="yes"> Yes — Promote to Official Platform</label>
                                        <label><input type="radio" name="vote-{{ item.key }}" value="no"> No</label>
                                        <label><input type="radio" name="vote-{{ item.key }}" value="abstain" checked> Abstain</label>
                                    </div>
                                {% endif %}

                                {% if item.key in tallies %}
                                    <div style="font-size:0.9em; margin-top:6px; color:#555;">
                                        Current tally: Yes {{ tallies[item.key].yes }} • No {{ tallies[item.key].no }} • Abstain {{ tallies[item.key].abstain }}
                                    </div>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>

                    <!-- ACTION BAR -->
                    {% if userCanVoteNow %}
                        <div class="submit-bar">
                            <button id="submitBallot" style="background:#ff6600;color:white;border:none;padding:14px 28px;font-size:1.05em;cursor:pointer;border-radius:4px;">
                                Cast My Ballot for Window {{ windowId }}
                            </button>
                            <span style="margin-left:12px;font-size:0.9em;color:#666;">You can only vote once per window. Your choices are final for this week.</span>
                        </div>
                    {% elif userAlreadyVoted %}
                        <div class="notice">
                            <strong>Thank you — your ballot for {{ windowId }} has been recorded.</strong><br>
                            You may view the live tallies above. Results will be tabulated and promoted when the window is closed.
                        </div>
                    {% else %}
                        <div class="notice">
                            {% if user %}
                                You are logged in but there is no active ballot for you right now (either the window is closed or you have already voted).
                            {% else %}
                                <a href="{{ url_for('login') }}">Log in</a> to cast your vote on the current ballot.
                            {% endif %}
                        </div>
                    {% endif %}

                    {% if user %}
                    <div style="margin-top:30px;text-align:center;">
                        <button id="closeWindowBtn" class="promote-btn">Close Window &amp; Promote Winners</button>
                        <span style="font-size:0.9em;color:#666;display:block;margin-top:4px;">(Operator action — promotes items with more Yes than No votes)</span>
                    </div>
                    {% endif %}

                {% endif %}
            </div>

            <script src="{{ url_for('static', filename='js/vote.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user,
         windowId=windowId,
         policyItems=policyItems,
         amendmentItems=amendmentItems,
         hasLiveBallot=hasLiveBallot,
         userCanVoteNow=userCanVoteNow,
         userAlreadyVoted=userAlreadyVoted,
         tallies=tallies,
         participation=participation)