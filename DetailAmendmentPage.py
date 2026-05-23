from flask import Flask, render_template_string, redirect, url_for
import User
import Database
from Amendment import Amendment
import difflib


def _escape_html(text):
    """Minimal HTML escape for diff lines."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _generate_diff_html(original_title, original_desc, amended_title, amended_desc):
    """Real visual green/red diff using difflib.SequenceMatcher (now includes title).
    Returns full labeled section HTML. Title subsection shown only when title actually differs.
    Description diff uses the original compact logic. Legend removed ( +/- and colors are self-explanatory).
    Long single-line titles/descriptions are wrapped via pre-wrap + word-wrap (prepares for future multiline).
    """
    # Titles treated as single logical line each
    orig_title_lines = [(original_title or "").strip()]
    new_title_lines = [(amended_title or "").strip()]
    orig_desc_lines = (original_desc or "").splitlines()
    new_desc_lines = (amended_desc or "").splitlines()

    # Fast path: nothing at all
    if (not orig_title_lines[0] and not new_title_lines[0]) and (not orig_desc_lines and not new_desc_lines):
        return ""

    title_changed = orig_title_lines != new_title_lines
    desc_changed = orig_desc_lines != new_desc_lines

    if not title_changed and not desc_changed:
        return (
            '<div style="margin:12px 0 8px;">'
            '<div class="section-label">Diff vs Original Policy</div>'
            '<div style="font-size:0.85em;color:#666;font-style:italic;padding:6px 8px;background:#f9f9f9;border:1px solid #eee;border-radius:4px;">No textual changes to the policy title or description.</div>'
            '</div>'
        )

    parts = []
    parts.append('<div style="margin:12px 0 8px;">')
    parts.append('<div class="section-label">Diff vs Original Policy</div>')

    # Shared scroll container for all change blocks (title + desc)
    parts.append('<div style="font-family:monospace;font-size:0.82em;line-height:1.38;background:#fff;border:1px solid #e5e5e5;border-radius:6px;padding:8px 10px;max-height:280px;overflow:auto;">')

    # --- Title subsection (only when changed, single-line in practice) ---
    if title_changed:
        parts.append('<div style="font-size:0.72em;color:#555;margin:2px 0 4px 2px;font-weight:600;">Title</div>')
        t_matcher = difflib.SequenceMatcher(None, orig_title_lines, new_title_lines)
        for tag, i1, i2, j1, j2 in t_matcher.get_opcodes():
            if tag == "equal":
                continue
            if tag == "replace":
                for line in orig_title_lines[i1:i2]:
                    parts.append(f'<div style="background:#ffebee;color:#b71c1c;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">- {_escape_html(line)}</div>')
                for line in new_title_lines[j1:j2]:
                    parts.append(f'<div style="background:#e8f5e9;color:#1b5e20;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">+ {_escape_html(line)}</div>')
            elif tag == "delete":
                for line in orig_title_lines[i1:i2]:
                    parts.append(f'<div style="background:#ffebee;color:#b71c1c;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">- {_escape_html(line)}</div>')
            elif tag == "insert":
                for line in new_title_lines[j1:j2]:
                    parts.append(f'<div style="background:#e8f5e9;color:#1b5e20;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">+ {_escape_html(line)}</div>')

    # --- Description changes (existing compact logic, now with wrap safety) ---
    if desc_changed:
        if not title_changed:
            # Description changed but title did not — show explicit note first
            parts.append('<div style="color:#666;font-style:italic;margin-bottom:4px;">Title unchanged.</div>')
        if title_changed:
            # visual separator when both are present
            parts.append('<div style="height:1px;background:#eee;margin:6px 0;"></div>')
            parts.append('<div style="font-size:0.72em;color:#555;margin:2px 0 4px 2px;font-weight:600;">Description</div>')
        d_matcher = difflib.SequenceMatcher(None, orig_desc_lines, new_desc_lines)
        has_desc_change = False
        for tag, i1, i2, j1, j2 in d_matcher.get_opcodes():
            if tag == "equal":
                continue
            has_desc_change = True
            if tag == "replace":
                for line in orig_desc_lines[i1:i2]:
                    parts.append(f'<div style="background:#ffebee;color:#b71c1c;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">- {_escape_html(line)}</div>')
                for line in new_desc_lines[j1:j2]:
                    parts.append(f'<div style="background:#e8f5e9;color:#1b5e20;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">+ {_escape_html(line)}</div>')
            elif tag == "delete":
                for line in orig_desc_lines[i1:i2]:
                    parts.append(f'<div style="background:#ffebee;color:#b71c1c;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">- {_escape_html(line)}</div>')
            elif tag == "insert":
                for line in new_desc_lines[j1:j2]:
                    parts.append(f'<div style="background:#e8f5e9;color:#1b5e20;padding:1px 4px;white-space:pre-wrap;word-wrap:break-word;">+ {_escape_html(line)}</div>')
        if not has_desc_change:
            parts.append('<div style="color:#666;font-style:italic;">No line-level differences in description.</div>')
    elif title_changed:
        # Title changed but description did not — show explicit unchanged note
        parts.append('<div style="color:#666;font-style:italic;margin-top:4px;">Description unchanged.</div>')

    parts.append('</div>')  # close the scroll container
    parts.append('</div>')  # close the outer diff wrapper
    return "".join(parts)


def render(user, amendmentId):
    if(not User.validateUser(user)):
        user = None
    amendment = Database.getAmendment(user, amendmentId)
    policy = None
    if(amendment != None):
        policy = Database.getPolicy(user, amendment.getPolicyId())

    # Compute real diff (title + description) only for canidate/official
    diff_html = None
    if amendment is not None and policy is not None and getattr(amendment, "amendmentType", None) in ("canidate", "official"):
        diff_html = _generate_diff_html(
            policy.getTitle(), policy.getDescription(),
            amendment.getTitle(), amendment.getDescription()
        )

    return render_template_string('''
        <!doctype html>
        <title>The Internet Party — Amendment Detail</title>
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
            .menu-item.active {
                color: #ff6600;
                font-weight: bold;
            }

            /* Production amendment detail styles — fully aligned with DraftsPage, PolicyPage, VotePage, and the new Policy Detail */
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
                font-size: 0.82em;
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
                font-size: 0.75em;
                padding: 3px 10px;
                border-radius: 999px;
                font-weight: 600;
                vertical-align: middle;
            }
            .status-Draft { background:#f0f0f0; color:#555; }
            .status-Candidate { background:#fff3e0; color:#c60; }
            .status-Official { background:#e6f4e6; color:#0a7; }

            .policy-text pre, .amendment-text pre {
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

            /* Target policy summary card (used on amendment pages) */
            .target-policy {
                background: #f9f9f9;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                padding: 12px 14px;
                margin-bottom: 18px;
            }
            .target-policy h4 {
                margin: 0 0 6px;
                font-size: 0.95em;
                color: #555;
            }

            /* Legacy draft form — styled to match DraftsPage while preserving exact IDs for detail-amendment.js */
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
                font-size: 0.8em;
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
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar (standard duplicated, Policy active as parent section) -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item.active">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                {% if amendment %}
                    <div class="detail-header">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <h2 style="margin:0;font-size:1.05em;color:#666;">Amendment Detail</h2>
                            {% if amendment.amendmentType == "draft" %}
                                <span class="status-pill status-Draft">Draft</span>
                            {% elif amendment.amendmentType == "canidate" %}
                                <span class="status-pill status-Candidate">Candidate</span>
                            {% else %}
                                <span class="status-pill status-Official">Official</span>
                            {% endif %}
                        </div>
                        <h3 style="font-size:1.55em;font-weight:700;color:#111;margin:8px 0 4px;">{{ amendment.getTitle() }}</h3>
                        <div class="detail-meta">
                            <span><strong>ID:</strong> <span id="amendmentId">{{ amendment.getId() }}</span></span>
                            <span><strong>Created:</strong> {{ amendment.getCreatedDate() }}</span>
                            <span><strong>Updated:</strong> {{ amendment.getUpdatedDate() }}</span>
                        </div>
                    </div>

                    {% if amendment.amendmentType == "draft" %}
                        <div class="promotion-banner">
                            <strong>📝 Private Amendment Draft.</strong>
                            <a href="{{ url_for('drafts') }}">Edit this draft in the rich Drafts hub (recommended) →</a>
                            <span style="color:#666;font-size:0.85em;">(legacy form below preserved for compatibility)</span>
                        </div>
                    {% endif %}

                    <div class="detail-card">
                        {% if policy and amendment.amendmentType == "draft" %}
                        <!-- Target policy kept before the form (reference while editing) for draft type -->
                        <div class="target-policy">
                            <h4>Targets Policy</h4>
                            <div>
                                <strong><a href="{{ url_for('detail', policyId=policy.getId()) }}" style="color:#222;text-decoration:none;">{{ policy.getTitle() }}</a></strong>
                                <span style="font-size:0.8em;color:#888;"> (ID: <span id="policyId">{{ policy.getId() }}</span>)</span>
                            </div>
                            <a href="{{ url_for('detail', policyId=policy.getId()) }}" style="font-size:0.85em;color:#ff6600;font-weight:600;">View full policy detail →</a>
                        </div>
                        {% elif not policy %}
                            <p style="color:#c00;">Linked policy could not be loaded.</p>
                        {% endif %}

                        {% if amendment.amendmentType == "draft" %}
                            <!-- Legacy draft form for amendment (exact IDs preserved: amendmentId, policyId, title, description, save/remove/submitDraft for detail-amendment.js) -->
                            <div class="section-label">Legacy Editor — Save / Submit / Remove Amendment Draft</div>
                            <form id="draftForm">
                                <label for="title">Proposed Title</label>
                                <input type="text" id="title" value="{{ amendment.getTitle() }}">

                                <label for="description">Proposed Description</label>
                                <textarea id="description">{{ amendment.getDescription() }}</textarea>

                                <div class="button-row">
                                    <button type="button" id="saveDraft" class="btn-primary">Save Draft</button>
                                    <button type="button" id="removeDraft" class="btn-danger">Remove Draft</button>
                                    <button type="button" id="submitDraft" class="btn-secondary">Submit Amendment Draft to Canidate</button>
                                </div>
                            </form>
                            <p style="margin:12px 0 0;font-size:0.82em;color:#666;">
                                Prefer the <a href="{{ url_for('drafts') }}" style="color:#ff6600;font-weight:600;">Drafts hub</a> for rich editing and pre-filled amend flows.
                            </p>
                        {% elif amendment.amendmentType == "canidate" %}
                            <div class="section-label">Candidate Amendment on the weekly ballot</div>
                            <div class="amendment-text">
                                <pre>{{ amendment.getDescription() }}</pre>
                            </div>

                            {% if diff_html %}{{ diff_html | safe }}{% endif %}

                            {% if policy %}
                            <!-- Targets Policy grey box moved below the amendment description area for "canidate" and "official" types -->
                            <div class="target-policy">
                                <h4>Targets Policy</h4>
                                <div>
                                    <strong><a href="{{ url_for('detail', policyId=policy.getId()) }}" style="color:#222;text-decoration:none;">{{ policy.getTitle() }}</a></strong>
                                    <span style="font-size:0.8em;color:#888;"> (ID: <span id="policyId">{{ policy.getId() }}</span>)</span>
                                </div>
                                <a href="{{ url_for('detail', policyId=policy.getId()) }}" style="font-size:0.85em;color:#ff6600;font-weight:600;">View full policy detail →</a>
                            </div>
                            {% endif %}

                            <div class="action-bar">
                                <a href="{{ url_for('vote') }}" class="primary">Vote on this amendment →</a>
                                <a href="{{ url_for('policy') }}">Browse the Congressional Library →</a>
                            </div>
                        {% elif amendment.amendmentType == "official" %}
                            <div class="section-label">Official enacted amendment</div>
                            <div class="amendment-text">
                                <pre>{{ amendment.getDescription() }}</pre>
                            </div>

                            {% if diff_html %}{{ diff_html | safe }}{% endif %}

                            {% if policy %}
                            <!-- Targets Policy grey box moved below the amendment description area for "canidate" and "official" types -->
                            <div class="target-policy">
                                <h4>Targets Policy</h4>
                                <div>
                                    <strong><a href="{{ url_for('detail', policyId=policy.getId()) }}" style="color:#222;text-decoration:none;">{{ policy.getTitle() }}</a></strong>
                                    <span style="font-size:0.8em;color:#888;"> (ID: <span id="policyId">{{ policy.getId() }}</span>)</span>
                                </div>
                                <a href="{{ url_for('detail', policyId=policy.getId()) }}" style="font-size:0.85em;color:#ff6600;font-weight:600;">View full policy detail →</a>
                            </div>
                            {% endif %}

                            <div class="action-bar">
                                <a href="{{ url_for('policy') }}">Browse the full Congressional Library →</a>
                            </div>
                        {% endif %}
                    </div>

                {% else %}
                    <div class="detail-header">
                        <h2>Amendment Detail</h2>
                    </div>
                    <div class="detail-card not-found">
                        <h3>Amendment not found</h3>
                        <p>This amendment does not exist, or it is a private draft that requires you to be logged in as its owner.</p>
                        <a href="{{ url_for('policy') }}" class="btn-back">← Back to the Congressional Library</a>
                    </div>
                {% endif %}

                <a href="{{ url_for('policy') }}" class="btn-back">← Back to Congressional Library</a>
            </div>

            <script src="{{ url_for('static', filename='js/detail-amendment.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, amendment=amendment, policy=policy, diff_html=diff_html)