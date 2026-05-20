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

    return render_template_string('''
        <!doctype html>
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
                font-size: .72em;
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
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                {% if user %}<a href="{{ url_for('drafts') }}" class="menu-item">Drafts</a>{% endif %}
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item.active">Account</a>
            </div>

            <div class="content">
                <h2>Your Personal Command Center</h2>

                <div class="profile-card">
                    <strong>Logged in as:</strong> {{ user.email or user.uid }}<br>
                    <small>UID: {{ user.uid }}</small><br>
                    <a href="{{ url_for('logout') }}" class="logout">Log out</a>
                </div>

                {% if ballot_count > 0 %}
                <div class="ballot-notice">
                    <strong>Active ballot this week ({{ window }})</strong> — {{ ballot_count }} candidate items.
                    {% if user_participated %}
                        You have already voted this window. Thank you.
                    {% else %}
                        <a href="{{ url_for('vote') }}">Cast your vote now →</a>
                    {% endif %}
                </div>
                {% endif %}

                <div class="section">
                    <h3>My Drafts (Private)</h3>
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

                <p style="margin-top:20px"><a href="{{ url_for('policy') }}">Browse the full Congressional Library →</a></p>
            </div>

            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, drafts=drafts, canidates=canidates, policies=policies,
         draftAmendments=draftAmendments, canidateAmendments=canidateAmendments, amendments=amendments,
         window=window, ballot_count=ballot_count, user_participated=user_participated)