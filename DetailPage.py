from flask import Flask, render_template_string, redirect, url_for
import User
import Database
from Policy import Policy

# This page is for showing a view of all the properties of any type of policy.
# This page will also house functionality for policy operations
# Nones
# Center draft Form on screen. Thanks grok. Its the margin thing
            #draftForm {
#                 max-width: 600px; /* Or whatever max-width you want */
#                 margin: 0 auto;  /* Centers the form if it's narrower than its container */
#             }
# More grok beauty tips

# /* 
#             #draftForm button {
#                 flex: 1;
#                 margin: 0 5px;
#                 padding: 10px 20px;
#                 border: none;
#                 cursor: pointer;
#                 background-color: #4CAF50;
#                 color: white;
#             }
#  */
# 
# /* 
#             #draftForm button:hover {
#                 background-color: #45a049;
#             }
# 
#             #draftForm button[type="submit"][value="submit"] {
#                 background-color: #008CBA;
#             }
# 
#             #draftForm button[type="submit"][value="submit"]:hover {
#                 background-color: #0077a8;
#             }
#  */


def render(user, policyId):
    if(not User.validateUser(user)):
        user = None
    policy = Database.getPolicy(user, policyId)

    # Amendment history for official + canidate policies (filter by policyId)
    candidate_amendments = []
    official_amendments = []
    if policy:
        try:
            all_can = Database.getCanidateAmendments() or []
            all_off = Database.getOfficialAmendments() or []
            pid = policy.getId()
            candidate_amendments = [a for a in all_can if getattr(a, 'getPolicyId', lambda: None)() == pid]
            official_amendments = [a for a in all_off if getattr(a, 'getPolicyId', lambda: None)() == pid]
        except Exception:
            pass  # never break the detail page

    html = render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>The Internet Party — Policy Detail</title>
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
                width: 100%;
                box-sizing: border-box;
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

            /* Production detail styles matching DraftsPage / PolicyPage / VotePage exactly in spirit */
            .detail-header {
                background: #fff;
                border-left: 6px solid #ff6600;
                padding: 16px 20px;
                margin-bottom: 16px;
                border-radius: 0 6px 6px 0;
            }
            .detail-header h2 {
                margin: 0 0 6px;
                font-size: 1.35em;
            }
            .detail-header h3 {
                margin: 4px 0 8px;
                font-size: 1.25em;
                color: #222;
            }
            .detail-meta {
                font-size: 0.9em;
                color: #666;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                align-items: center;
            }

            .detail-card {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
                margin-bottom: 16px;
            }

            .status-pill {
                display: inline-block;
                font-size: 0.9em;
                padding: 3px 10px;
                border-radius: 999px;
                font-weight: 600;
                vertical-align: middle;
            }
            .status-Draft { background:#f0f0f0; color:#555; }
            .status-Candidate { background:#fff3e0; color:#c60; }
            .status-Official { background:#e6f4e6; color:#0a7; }

            .policy-text pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                overflow-x: auto;
                background: #f8f8f8;
                border: 1px solid #e8e8e8;
                border-radius: 6px;
                padding: 14px;
                font-family: monospace;
                font-size: 0.95em;
                line-height: 1.45;
                color: #222;
            }

            .promotion-banner {
                background: #fff3e0;
                border-left: 5px solid #ff6600;
                padding: 12px 16px;
                margin-bottom: 18px;
                border-radius: 6px;
                font-size: 0.95em;
            }
            .promotion-banner a {
                color: #ff6600;
                font-weight: 600;
                text-decoration: none;
            }
            .promotion-banner a:hover { text-decoration: underline; }

            .action-bar {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-top: 16px;
                padding-top: 14px;
                border-top: 1px solid #eee;
            }
            .action-bar a {
                display: inline-block;
                padding: 8px 14px;
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 6px;
                color: #333;
                font-size: 0.9em;
                text-decoration: none;
                font-weight: 500;
            }
            .action-bar a:hover {
                border-color: #ff6600;
                color: #ff6600;
            }
            .action-bar a.primary {
                background: #ff6600;
                color: white;
                border-color: #ff6600;
            }

            /* Legacy draft form — styled to match DraftsPage editor quality while preserving exact IDs + structure for detail.js */
            #draftForm {
                max-width: 100%;
            }
            #draftForm label {
                display: block;
                font-size: 0.9em;
                color: #444;
                margin-bottom: 4px;
                font-weight: 600;
            }
            #draftForm input[type="text"],
            #draftForm textarea {
                width: 100%;
                box-sizing: border-box;
                padding: 10px 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                margin-bottom: 10px;
            }
            #draftForm input[type="text"]:focus,
            #draftForm textarea:focus {
                border-color: #ff6600;
                outline: none;
                box-shadow: 0 0 0 2px rgba(255,102,0,0.1);
            }
            #draftForm textarea {
                min-height: 180px;
                resize: vertical;
                font-family: inherit;
            }

            .button-row {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 8px;
            }
            .button-row button {
                padding: 9px 16px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                border: 1px solid #ccc;
                font-size: 0.95em;
            }
            .btn-primary {
                background: #ff6600;
                color: white;
                border-color: #ff6600;
            }
            .btn-primary:hover { background: #e55a00; }
            .btn-secondary {
                background: white;
            }
            .btn-danger {
                background: #c00;
                color: white;
                border-color: #c00;
            }

            .btn-back {
                display: inline-block;
                margin-top: 20px;
                color: #ff6600;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.95em;
            }
            .btn-back:hover { text-decoration: underline; }

            .section-label {
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #888;
                margin: 0 0 6px;
                font-weight: 600;
            }

            .not-found {
                text-align: center;
                padding: 40px 20px;
                background: #fff;
                border: 1px dashed #ccc;
                border-radius: 8px;
            }

            /* Mobile detail: stack history, wrap text, larger taps, readable pre */
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
                .detail-header, .detail-card { padding: 14px 16px; }
                .detail-meta { font-size: 0.9em; gap: 8px; }
                .section-label { font-size: 0.9em; }
                .status-pill { font-size: 0.9em; }
                pre, .amendment-history pre { font-size: 0.9em; padding: 10px; }
                .btn { padding: 10px 14px; font-size: 0.95em; }
                .not-found { padding: 24px 12px; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar (duplicated standard on every page, Policy active) -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item active">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                {% if policy %}
                    <div class="detail-header">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <h2 style="margin:0;">Policy Detail</h2>
                            {% if policy.policyType == "draft" %}
                                <span class="status-pill status-Draft">Draft</span>
                            {% elif policy.policyType == "canidate" %}
                                <span class="status-pill status-Candidate">Candidate</span>
                            {% else %}
                                <span class="status-pill status-Official">Official</span>
                            {% endif %}
                        </div>
                        <h3>{{ policy.getTitle() }}</h3>
                        <div class="detail-meta">
                            <span><strong>ID:</strong> <span id="policyId">{{ policy.getId() }}</span></span>
                            <span><strong>Created:</strong> {{ policy.getCreatedDate() }}</span>
                            <span><strong>Updated:</strong> {{ policy.getUpdatedDate() }}</span>
                        </div>
                    </div>

                    {% if policy.policyType == "draft" %}
                        <div class="promotion-banner">
                            <strong>📝 Private Draft.</strong>
                            <a href="{{ url_for('drafts') }}">Edit this draft in the rich Drafts hub (recommended) →</a>
                            <span style="color:#666;font-size:0.9em;">(legacy form below preserved for compatibility)</span>
                        </div>
                    {% endif %}

                    <div class="detail-card">
                        {% if policy.policyType == "draft" %}
                            <!-- Legacy draft editing form (exact element IDs and button ids preserved for static/js/detail.js) -->
                            <div class="section-label">Legacy Editor — Save / Submit / Remove</div>
                            <form id="draftForm">
                                <label for="title">Title</label>
                                <input type="text" id="title" value="{{ policy.getTitle() }}">

                                <label for="description">Description</label>
                                <textarea id="description">{{ policy.getDescription() }}</textarea>

                                <div class="button-row">
                                    <button type="button" id="saveDraft" class="btn-primary">Save Draft</button>
                                    <button type="button" id="removeDraft" class="btn-danger">Remove Draft</button>
                                    <button type="button" id="submitDraft" class="btn-secondary">Submit Draft to Canidate</button>
                                </div>
                            </form>
                            <p style="margin:12px 0 0;font-size:0.9em;color:#666;">
                                For the best experience (live char counters, two-pane view, diff for amendments) use the 
                                <a href="{{ url_for('drafts') }}" style="color:#ff6600;font-weight:600;">Drafts hub</a>.
                            </p>
                        {% elif policy.policyType == "canidate" %}
                            <div class="section-label">Candidate on the weekly ballot</div>
                            <div class="policy-text">
                                <pre>{{ policy.getDescription() }}</pre>
                            </div>
                            <div class="action-bar">
                                <a href="{{ url_for('vote') }}" class="primary">Vote on this candidate →</a>
                                <a href="{{ url_for('drafts', amend=policy.getId()) }}">Propose an amendment via Drafts hub →</a>
                            </div>
                        {% elif policy.policyType == "official" %}
                            <div class="section-label">Official platform policy (enacted)</div>
                            <div class="policy-text">
                                <pre>{{ policy.getDescription() }}</pre>
                            </div>
                            <div class="action-bar">
                                <a href="{{ url_for('drafts', amend=policy.getId()) }}" class="primary">Propose an amendment to this policy →</a>
                                <a href="{{ url_for('policy') }}">Browse the full Congressional Library →</a>
                            </div>
                        {% endif %}

                        {# Amendment sections for official + canidate policies (clean history + pending) #}
                        {% if policy.policyType == "official" or policy.policyType == "canidate" %}
                        <div style="margin-top:22px;">
                            {% if candidate_amendments %}
                            <div style="margin-bottom:14px;">
                                <div class="section-label" style="color:#c60;">Pending Candidate Amendments</div>
                                {% for a in candidate_amendments %}
                                <div class="detail-card" style="padding:12px 14px;margin-bottom:8px;border-left:4px solid #ff6600;">
                                    <div style="font-weight:600;">
                                        <a href="{{ url_for('detail_amendment', amendmentId=a.getId()) }}" style="color:#111;text-decoration:none;">{{ a.getTitle() }}</a>
                                    </div>
                                    <div style="font-size:0.9em;color:#666;margin-top:2px;">Candidate • Click to see the proposed change vs current policy</div>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}

                            {% if official_amendments %}
                            <div>
                                <div class="section-label">Amendment History</div>
                                {% for a in official_amendments %}
                                <div class="detail-card" style="padding:12px 14px;margin-bottom:8px;">
                                    <div style="font-weight:600;">
                                        <a href="{{ url_for('detail_amendment', amendmentId=a.getId()) }}" style="color:#111;text-decoration:none;">{{ a.getTitle() }}</a>
                                    </div>
                                    <div style="font-size:0.9em;color:#666;margin-top:2px;">Official • Enacted change — view the diff on the amendment page</div>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>

                {% else %}
                    <div class="detail-header">
                        <h2>Policy Detail</h2>
                    </div>
                    <div class="detail-card not-found">
                        <h3>Policy not found</h3>
                        <p>This policy does not exist, or it is a private draft that requires you to be logged in as its owner.</p>
                        <a href="{{ url_for('policy') }}" class="btn-back">← Back to the Congressional Library</a>
                    </div>
                {% endif %}

                <a href="{{ url_for('policy') }}" class="btn-back">← Back to Congressional Library</a>
            </div>

            <script src="{{ url_for('static', filename='js/detail.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, policy=policy,
         candidate_amendments=candidate_amendments,
         official_amendments=official_amendments)
    # (html, found) so the route can return real HTTP 404 for missing policies
    return html, bool(policy)