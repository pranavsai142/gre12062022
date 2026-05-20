from flask import Flask, render_template_string
import User
import Database

def render(user, new=None, amend=None):
    if(not User.validateUser(user)):
        user = None

    drafts = Database.getDraftPolicies(user) if user else []
    draftAmends = Database.getDraftAmendments(user) if user else []

    # Prepare rich list data for sidebar (with policy context for amendments)
    policy_drafts = []
    for d in drafts:
        if d and d.getTitle():
            policy_drafts.append({
                "id": d.getId(),
                "title": d.getTitle(),
                "description": d.getDescription() or "",
                "kind": "policy"
            })

    amend_drafts = []
    amend_originals = {}
    for da in draftAmends:
        if da and da.getTitle():
            pid = da.getPolicyId() or ""
            ptitle = ""
            pdesc = ""
            try:
                p = Database.getPolicy(user, pid) if pid else None
                if p:
                    ptitle = p.getTitle() or ""
                    pdesc = p.getDescription() or ""
                    if pid:
                        amend_originals[pid] = (ptitle + "\n\n" + pdesc).strip()
            except Exception:
                pass
            amend_drafts.append({
                "id": da.getId(),
                "title": da.getTitle(),
                "description": da.getDescription() or "",
                "kind": "amendment",
                "policyId": pid,
                "policyTitle": ptitle
            })

    # Determine initial selection from query params or default to first
    selected = None
    original_policy = None  # full original for amendment diff/final editor
    if amend:
        for a in amend_drafts:
            if a.get("policyId") == amend:
                selected = a
                break
        if selected is None:
            ptitle = ""
            pdesc = ""
            try:
                p = Database.getPolicy(user, amend) if amend else None
                if p:
                    ptitle = p.getTitle() or ""
                    pdesc = p.getDescription() or ""
            except Exception:
                pass
            selected = {
                "id": None,
                "title": ptitle,
                "description": "",
                "kind": "amendment",
                "policyId": amend,
                "policyTitle": ptitle
            }
            original_policy = {"id": amend, "title": ptitle, "description": pdesc}
            if amend:
                amend_originals[amend] = (ptitle + "\n\n" + pdesc).strip()
        else:
            # existing amendment draft — still load the target policy for the rich editor
            try:
                p = Database.getPolicy(user, selected.get("policyId")) if selected.get("policyId") else None
                if p:
                    original_policy = {"id": p.getId(), "title": p.getTitle() or "", "description": p.getDescription() or ""}
            except Exception:
                pass
    if original_policy is None and selected and selected.get("kind") == "amendment" and selected.get("policyId"):
        try:
            p = Database.getPolicy(user, selected.get("policyId"))
            if p:
                original_policy = {"id": p.getId(), "title": p.getTitle() or "", "description": p.getDescription() or ""}
        except Exception:
            pass
    if selected is None and new == "policy":
        selected = {
            "id": None,
            "title": "",
            "description": "",
            "kind": "policy",
            "policyId": None,
            "policyTitle": None
        }
    if selected is None and policy_drafts:
        selected = policy_drafts[0]
    elif selected is None and amend_drafts:
        selected = amend_drafts[0]

    # Ensure original_policy + map for a default-selected amendment (so rich editor is server-rendered on first paint even when no ?amend and no policy drafts)
    if selected and selected.get("kind") == "amendment" and selected.get("policyId"):
        pid = selected.get("policyId")
        if pid and not original_policy:
            try:
                p = Database.getPolicy(user, pid)
                if p:
                    original_policy = {"id": p.getId(), "title": p.getTitle() or "", "description": p.getDescription() or ""}
            except Exception:
                pass
        if pid and pid not in amend_originals and original_policy:
            t = original_policy.get("title", "")
            d = original_policy.get("description", "")
            amend_originals[pid] = (t + "\n\n" + d).strip()

    return render_template_string('''
        <!doctype html>
        <title>The Internet Party — Drafts</title>
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
                max-width: 1200px;
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
            .drafts-header {
                background: #fff;
                border-left: 6px solid #ff6600;
                padding: 16px 20px;
                margin-bottom: 16px;
                border-radius: 0 6px 6px 0;
            }
            .drafts-layout {
                display: flex;
                gap: 24px;
                align-items: flex-start;
            }
            .sidebar {
                width: 340px;
                flex-shrink: 0;
            }
            .sidebar h3 {
                margin: 0 0 8px;
                font-size: 1.1em;
                color: #222;
            }
            .create-btn {
                display: block;
                width: 100%;
                background: #ff6600;
                color: white;
                border: none;
                padding: 10px 14px;
                border-radius: 6px;
                font-weight: 600;
                margin-bottom: 12px;
                cursor: pointer;
                text-align: center;
                text-decoration: none;
            }
            .create-btn:hover { background: #e55a00; }
            .draft-list {
                max-height: 520px;
                overflow-y: auto;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                background: #fff;
                padding: 6px;
            }
            .draft-item {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                padding: 10px 12px;
                margin-bottom: 6px;
                cursor: pointer;
                transition: border-color .1s ease, box-shadow .1s ease;
            }
            .draft-item:hover {
                border-color: #ff6600;
            }
            .draft-item.active {
                border-color: #ff6600;
                box-shadow: 0 0 0 2px rgba(255,102,0,0.15);
            }
            .draft-item .meta {
                font-size: 0.75em;
                color: #888;
                margin-top: 4px;
            }
            .draft-item .title {
                font-weight: 600;
                color: #222;
                font-size: 0.95em;
                line-height: 1.3;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                max-width: 100%;
            }
            .editor {
                flex: 1;
                min-width: 0;
            }
            .editor-card {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            }
            .editor-card h3 {
                margin: 0 0 4px;
                font-size: 1.15em;
            }
            .amend-context {
                background: #fff3e0;
                border-left: 4px solid #ff6600;
                padding: 8px 12px;
                margin-bottom: 14px;
                font-size: 0.9em;
            }
            label {
                display: block;
                font-size: 0.9em;
                color: #444;
                margin-bottom: 4px;
                font-weight: 600;
            }
            input[type="text"], textarea {
                width: 100%;
                box-sizing: border-box;
                padding: 10px 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                margin-bottom: 6px;
            }
            input[type="text"]:focus, textarea:focus {
                border-color: #ff6600;
                outline: none;
                box-shadow: 0 0 0 2px rgba(255,102,0,0.1);
            }
            textarea {
                min-height: 220px;
                resize: vertical;
            }
            .counter {
                font-size: 0.8em;
                color: #666;
                text-align: right;
                margin-bottom: 12px;
            }
            .counter.over { color: #c00; font-weight: 600; }
            .button-row {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 16px;
            }
            .button-row button {
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                border: 1px solid #ccc;
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
                margin-top: 16px;
                color: #ff6600;
                text-decoration: none;
                font-weight: 600;
            }
            .success-state {
                background: #e8f5e9;
                border: 1px solid #a5d6a7;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            .success-state h3 { color: #2e7d32; margin-top: 0; }
            .empty-drafts {
                color: #666;
                font-style: italic;
                padding: 12px;
            }
            .login-gate {
                max-width: 520px;
                margin: 40px auto;
                background: white;
                padding: 32px;
                border-radius: 8px;
                border-left: 6px solid #ff6600;
                text-align: center;
            }
            .login-gate .cta {
                display: inline-block;
                margin: 8px 6px;
                padding: 10px 20px;
                background: #ff6600;
                color: white;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
            }

            /* === Amendment rich diff/final editor (Phase 7) === */
            .amend-editor {
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            .original-box {
                background: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 12px 14px;
            }
            .original-box h4 {
                margin: 0 0 6px 0;
                font-size: 0.95em;
                color: #444;
            }
            .original-box pre {
                background: #fff;
                border: 1px solid #e5e5e5;
                padding: 10px;
                border-radius: 4px;
                max-height: 240px;
                overflow: auto;
                white-space: pre-wrap;
                font-size: 0.9em;
                margin: 0;
            }
            .final-label {
                font-weight: 600;
                color: #222;
                margin-bottom: 4px;
                display: block;
            }
            .diff-toggle {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 0.9em;
                margin: 8px 0;
                cursor: pointer;
            }
            .diff-panel {
                display: none;
                background: #fff;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                padding: 12px;
                font-family: monospace;
                font-size: 0.85em;
                white-space: pre-wrap;
                max-height: 280px;
                overflow: auto;
            }
            .diff-panel.show { display: block; }
            .diff-add { background: #e6ffed; color: #1a7f37; padding: 1px 3px; border-radius: 2px; }
            .diff-del { background: #ffebe9; color: #cf222e; padding: 1px 3px; border-radius: 2px; text-decoration: line-through; }
            .diff-hint {
                font-size: 0.8em;
                color: #666;
                margin-top: 4px;
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar (Drafts is primary and active here) -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                {% if user %}<a href="{{ url_for('drafts') }}" class="menu-item.active">Drafts</a>{% endif %}
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                <div class="drafts-header">
                    <h2>My Drafts — Propose Policy &amp; Amendments</h2>
                    <p style="margin:6px 0 0;color:#555;">Draft privately, save as you go, then submit to the canidate ballot for the weekly vote. Title under 100 characters. Description under 10,000 characters.</p>
                </div>

                {% if not user %}
                <div class="login-gate">
                    <h3>Log in to draft</h3>
                    <p>Anyone with internet can join the parallel accountability system. Create your account to start shaping the platform.</p>
                    <a href="{{ url_for('login') }}" class="cta">Log In</a>
                    <a href="{{ url_for('register') }}" class="cta" style="background:#333;">Join the Party</a>
                    <p style="margin-top:16px;font-size:0.9em;"><a href="{{ url_for('policy') }}">← Back to the Congressional Library</a></p>
                </div>
                {% else %}
                <div class="drafts-layout">
                    <!-- LEFT SIDEBAR -->
                    <div class="sidebar">
                        <a href="{{ url_for('drafts', new='policy') }}" class="create-btn" style="padding:6px 10px;font-size:0.9em;width:auto;display:inline-block;">+ New draft</a>
                        <h3>Your current drafts ({{ policy_drafts|length + amend_drafts|length }})</h3>
                        <div class="draft-list" id="draft-list">
                            {% if not policy_drafts and not amend_drafts %}
                            <div class="empty-drafts">No drafts yet. Use "+ New draft" above for a policy, or go to any policy in the Congressional Library → click its title to open Detail → use the prominent "Amend in Drafts" or "Draft Amendment" link there (this opens the rich editor with the original text + diff view).</div>
                            {% endif %}
                            {% for item in policy_drafts %}
                            <div class="draft-item {% if selected and selected.id == item.id %}active{% endif %}" 
                                 data-id="{{ item.id }}" data-kind="policy" data-title="{{ item.title|replace("'", "&#39;") }}" data-description="{{ (item.description or '')[:200]|replace("'", "&#39;") }}" data-policyid="" data-policytitle="" onclick="selectDraftFromEl(this)">
                                <div class="title">{{ item.title }}</div>
                                <div class="meta">Policy draft</div>
                            </div>
                            {% endfor %}
                            {% for item in amend_drafts %}
                            <div class="draft-item {% if selected and selected.id == item.id %}active{% endif %}" 
                                 data-id="{{ item.id }}" data-kind="amendment" data-title="{{ item.title|replace("'", "&#39;") }}" data-description="{{ (item.description or '')[:200]|replace("'", "&#39;") }}" data-policyid="{{ item.policyId }}" data-policytitle="{{ item.policyTitle|replace("'", "&#39;") }}" onclick="selectDraftFromEl(this)">
                                <div class="title">{{ item.title }}</div>
                                <div class="meta">Amendment to {{ item.policyTitle or item.policyId }}</div>
                            </div>
                            {% endfor %}
                        </div>
                        <p style="margin-top:12px;font-size:0.85em;color:#666;">Click any draft above to load it into the editor. Changes are saved with the buttons below.</p>
                    </div>

                    <!-- RIGHT EDITOR PANE -->
                    <div class="editor" id="editor-pane">
                        <div class="editor-card" id="editor-card">
                            <div id="success-state" style="display:none;" class="success-state">
                                <h3>Submitted to canidate!</h3>
                                <p>Your proposal is now live on the weekly ballot for members to vote on.</p>
                                <p><a href="{{ url_for('policy') }}" style="color:#ff6600;font-weight:600;">See it in the Congressional Library →</a></p>
                                <p><a href="{{ url_for('vote') }}" style="color:#ff6600;font-weight:600;">Go vote this week →</a></p>
                                <button onclick="startNewDraft(); window.location.reload();" class="btn-primary" style="margin-top:12px;">Start another draft (refresh list)</button>
                                <button onclick="window.location.reload()" style="margin-left:8px;padding:10px 14px;border-radius:6px;">Refresh drafts list</button>
                            </div>

                            <div id="form-area">
                                <h3 id="editor-title">Editor</h3>

                                <!-- Hidden fields pre-filled from the initial selection (critical for Save/Submit to call the right endpoints) -->
                                <input type="hidden" id="draftId" value="{{ selected.id or '' }}">
                                <input type="hidden" id="draftKind" value="{{ selected.kind or 'policy' }}">
                                <input type="hidden" id="draftPolicyId" value="{{ selected.policyId or '' }}">

                                <!-- Title is always present (but hidden for amendments since they target a specific policy's title) -->
                                <div id="title-section">
                                <label for="title">Title <span style="color:#888;">(max 100 chars)</span></label>
                                <input type="text" id="title" value="{{ selected.title or '' }}" placeholder="Short, clear, under 100 characters" maxlength="100" oninput="updateCounters()">
                                <div class="counter" id="title-counter">0/100</div>
                                </div>

                                <!-- Amendment rich editor markup ALWAYS present in DOM (enables reliable first-paint rich view + client-side switching from sidebar list items regardless of whether initial selection was policy or amendment). Initial visibility set server-side; JS populateForm toggles for list clicks. -->
                                <div id="amendment-editor" class="amend-editor" style="margin-top:12px; {% if not (selected and selected.kind == 'amendment' and original_policy) %}display:none;{% endif %}">
                                    <div class="original-box">
                                        <h4>Original Policy (read-only)</h4>
                                        <pre id="original-text">{% if original_policy %}{{ (original_policy.title or '') ~ "\n\n" ~ (original_policy.description or '') }}{% else %}(original policy text will appear here when an amendment is selected){% endif %}</pre>
                                    </div>
                                    <label class="final-label" for="description">Final Version — edit this to propose the complete new policy text</label>
                                    <div class="diff-hint" style="margin-bottom:6px;">This is the primary surface voters will see as the amended policy. Use the checkbox below to inspect the diff.</div>
                                </div>

                                <label id="desc-label" for="description" style="{% if selected and selected.kind == 'amendment' %}display:none;{% endif %}">Description <span style="color:#888;">(max 10,000 chars)</span></label>
                                <textarea id="description" placeholder="{% if selected and selected.kind == 'amendment' %}The full text the policy should become after this amendment.{% else %}Full text of your proposal. Be specific. What problem does it solve? What exactly should change?{% endif %}" maxlength="10000" oninput="updateCounters(); if (typeof maybeAutoRenderDiff === 'function') maybeAutoRenderDiff();">{{ (selected.description if selected else '') or (original_policy.description if original_policy else '') }}</textarea>
                                <div class="counter" id="desc-counter">0/10000</div>

                                <div id="diff-controls" style="margin-top:8px; {% if not (selected and selected.kind == 'amendment' and original_policy) %}display:none;{% endif %}">
                                    <label class="diff-toggle">
                                        <input type="checkbox" id="show-diff" onchange="if (typeof toggleDiff === 'function') toggleDiff()" style="transform:scale(1.15)">
                                        Show diff between original and final version
                                    </label>
                                    <div id="diff-panel" class="diff-panel"></div>
                                    <div class="diff-hint">Green = added in your final version, red = removed from the original. The Final Version above is what matters most.</div>
                                </div>

                                <div class="button-row">
                                    <button class="btn-primary" onclick="saveDraft()">Save Draft</button>
                                    <button onclick="submitToCanidate()">Submit to Canidate</button>
                                    <button class="btn-danger" onclick="deleteDraft()">Delete Draft</button>
                                    <button class="btn-secondary" onclick="startNewDraft()">New Draft</button>
                                </div>
                                <a href="{{ url_for('policy') }}" class="btn-back">← Back to Congressional Library</a>
                            </div>

                            <!-- Auto-diff for initial amendment (works even if not the ?amend path; guarded) -->
                            <script>
                                // Auto-show the diff on initial arrival for amendment flows (after the main script has defined the functions)
                                if ({{ 'true' if (selected and selected.kind == 'amendment') else 'false' }}) {
                                    setTimeout(function() {
                                        var cb = document.getElementById('show-diff');
                                        var panel = document.getElementById('diff-panel');
                                        if (cb && panel && typeof renderDiff === 'function') {
                                            cb.checked = true;
                                            renderDiff();
                                            panel.classList.add('show');
                                        }
                                    }, 140);
                                }
                            </script>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>

            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>

            <script>
                let currentDraft = {{ selected|tojson }};
                let originalPolicy = {{ original_policy|tojson }};  // Phase 7: full original for amendment diff view
                let amendOriginals = {{ amend_originals|tojson }};  // policyId -> "title\n\ndesc" for all user's amendment targets (for reliable sidebar switching)

                function updateCounters() {
                    const titleEl = document.getElementById('title');
                    const descEl = document.getElementById('description');
                    const tCount = document.getElementById('title-counter');
                    const dCount = document.getElementById('desc-counter');

                    if (!titleEl || !descEl) return;

                    const tLen = titleEl.value.length;
                    const dLen = descEl.value.length;

                    tCount.textContent = tLen + '/100';
                    dCount.textContent = dLen + '/10000';

                    tCount.classList.toggle('over', tLen > 100);
                    dCount.classList.toggle('over', dLen > 10000);
                }

                function populateForm(draft) {
                    if (!draft || !document.getElementById('title')) return;
                    currentDraft = draft;

                    const titleEl = document.getElementById('title');
                    const descEl = document.getElementById('description');
                    const idEl = document.getElementById('draftId');
                    const kindEl = document.getElementById('draftKind');
                    const pidEl = document.getElementById('draftPolicyId');
                    const h3 = document.getElementById('editor-title');

                    const amendEditor = document.getElementById('amendment-editor');
                    const diffControls = document.getElementById('diff-controls');
                    const descLabel = document.getElementById('desc-label');

                    if (titleEl) titleEl.value = draft.title || '';
                    if (descEl) descEl.value = draft.description || '';
                    if (idEl) idEl.value = draft.id || '';
                    if (kindEl) kindEl.value = draft.kind || 'policy';
                    if (pidEl) pidEl.value = draft.policyId || '';

                    const isAmend = (draft.kind === 'amendment' && draft.policyId);

                    if (amendEditor) amendEditor.style.display = isAmend ? 'block' : 'none';
                    if (diffControls) diffControls.style.display = isAmend ? 'block' : 'none';
                    if (descLabel) descLabel.style.display = isAmend ? 'none' : 'block';  // hide generic label when we have the nicer "Final Version" one

                    // Hide title input entirely for amendments (per UX: no separate "new title for the amendment"; it targets the policy)
                    const titleSection = document.getElementById('title-section');
                    if (titleSection) titleSection.style.display = isAmend ? 'none' : '';

                    if (isAmend) {
                        if (h3) h3.textContent = draft.id ? 'Edit Amendment Draft' : 'New Amendment Draft';

                        // Populate original policy box using the server-provided map (works for any sidebar-clicked amendment, not just initial)
                        const origPre = document.getElementById('original-text');
                        let origText = '';
                        const pid = draft.policyId || '';
                        if (pid && amendOriginals && amendOriginals[pid]) {
                            origText = amendOriginals[pid];
                        } else if (originalPolicy && (originalPolicy.id == pid || !originalPolicy.id)) {
                            origText = ((originalPolicy.title || '') + '\n\n' + (originalPolicy.description || '')).trim();
                        } else if (draft.policyTitle) {
                            origText = draft.policyTitle;
                        }
                        if (origPre) {
                            origPre.textContent = origText || (draft.policyTitle || pid || '(original text not available — you can still edit the final version below)');
                        }

                        // For a brand new amendment, seed the Final Version (textarea) with the original policy body so diff starts clean
                        if (!draft.id && (!descEl.value || descEl.value.trim() === '') && origText) {
                            // origText is "title\n\ndesc", take after first \n\n
                            const splitAt = origText.indexOf('\n\n');
                            const odesc = (splitAt > -1) ? origText.substring(splitAt + 2) : origText;
                            if (odesc) descEl.value = odesc;
                        }
                    } else {
                        if (h3) h3.textContent = draft.id ? 'Edit Policy Draft' : 'New Policy Draft';
                    }

                    // highlight active in sidebar
                    document.querySelectorAll('#draft-list .draft-item').forEach(el => {
                        el.classList.remove('active');
                        if (el.dataset.id === (draft.id || '') && draft.id) {
                            el.classList.add('active');
                        }
                    });

                    updateCounters();
                    // hide any previous diff, show form
                    const dp = document.getElementById('diff-panel');
                    const cb = document.getElementById('show-diff');
                    if (dp) dp.classList.remove('show');
                    if (cb) cb.checked = false;
                    document.getElementById('success-state').style.display = 'none';
                    document.getElementById('form-area').style.display = '';
                }

                function selectDraftFromEl(el) {
                    const data = {
                        id: el.dataset.id || null,
                        kind: el.dataset.kind || 'policy',
                        title: el.dataset.title || '',
                        description: el.dataset.description || '',
                        policyId: el.dataset.policyid || null,
                        policyTitle: el.dataset.policytitle || null
                    };
                    populateForm(data);
                }

                function selectDraft(draft) {
                    populateForm(draft);
                }

                function startNewDraft() {
                    const fresh = { id: null, title: '', description: '', kind: 'policy', policyId: null, policyTitle: null };
                    populateForm(fresh);
                    // clear highlights
                    document.querySelectorAll('#draft-list .draft-item').forEach(el => el.classList.remove('active'));
                }

                function saveDraft() {
                    const id = document.getElementById('draftId').value || null;
                    const title = (document.getElementById('title').value || '').trim();
                    const desc = document.getElementById('description').value || '';
                    const kind = document.getElementById('draftKind').value;
                    const pid = document.getElementById('draftPolicyId').value || null;

                    if (title.length > 100) { alert('Title must be 100 characters or fewer.'); return; }
                    if (desc.length > 10000) { alert('Description must be 10,000 characters or fewer.'); return; }
                    if (!title) { alert('Title is required.'); return; }

                    const payload = { title: title, description: desc };
                    let endpoint = '';

                    if (kind === 'policy') {
                        if (id) {
                            payload.id = id;
                            endpoint = '/update-draft';
                        } else {
                            endpoint = '/create-draft';
                        }
                    } else {
                        payload.policyId = pid;
                        if (id) {
                            payload.id = id;
                            endpoint = '/update-draft-amendment';
                        } else {
                            endpoint = '/create-draft-amendment';
                        }
                    }

                    fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    }).then(r => r.json()).then(data => {
                        if (data && data.success) {
                            alert('Draft saved.');
                            window.location.reload();
                        } else {
                            alert('Save failed: ' + (data.error || 'unknown error'));
                        }
                    }).catch(() => alert('Network error while saving draft.'));
                }

                function submitToCanidate() {
                    const id = document.getElementById('draftId').value;
                    const kind = document.getElementById('draftKind').value;
                    if (!id) {
                        alert('Save the draft first before submitting to canidate.');
                        return;
                    }
                    if (!confirm('Submit this draft as a canidate for the weekly ballot?')) return;

                    const endpoint = (kind === 'policy') ? '/submit-draft' : '/submit-draft-amendment';
                    const payload = { id: id };

                    fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    }).then(r => r.json()).then(data => {
                        if (data && data.success) {
                            document.getElementById('form-area').style.display = 'none';
                            document.getElementById('success-state').style.display = 'block';
                        } else {
                            alert('Submit failed: ' + (data.error || 'unknown error'));
                        }
                    }).catch(() => alert('Network error while submitting.'));
                }

                function deleteDraft() {
                    const id = document.getElementById('draftId').value;
                    const kind = document.getElementById('draftKind').value;
                    if (!id) {
                        alert('Nothing to delete (unsaved new draft).');
                        return;
                    }
                    if (!confirm('Permanently delete this draft? This cannot be undone.')) return;

                    const endpoint = (kind === 'policy') ? '/remove-draft' : '/remove-draft-amendment';
                    const payload = { id: id };

                    fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    }).then(r => r.json()).then(data => {
                        if (data && data.success) {
                            window.location.reload();
                        } else {
                            alert('Delete failed: ' + (data.error || 'unknown error'));
                        }
                    }).catch(() => alert('Network error while deleting.'));
                }

                // === Phase 7: lightweight diff for amendment editor ===
                function toggleDiff() {
                    const panel = document.getElementById('diff-panel');
                    const cb = document.getElementById('show-diff');
                    if (!panel || !cb) return;
                    if (cb.checked) {
                        renderDiff();
                        panel.classList.add('show');
                    } else {
                        panel.classList.remove('show');
                    }
                }

                function maybeAutoRenderDiff() {
                    const cb = document.getElementById('show-diff');
                    if (cb && cb.checked) {
                        renderDiff();
                    }
                }

                function renderDiff() {
                    const panel = document.getElementById('diff-panel');
                    const origPre = document.getElementById('original-text');
                    const finalTa = document.getElementById('description');
                    if (!panel || !origPre || !finalTa) return;

                    const original = origPre.textContent || '';
                    const finalText = finalTa.value || '';

                    // Very small, dependency-free line diff (good enough for policies)
                    const diffHtml = computeLineDiffHtml(original, finalText);
                    panel.innerHTML = diffHtml || '<em>No difference yet — edit the Final Version above.</em>';
                }

                function computeLineDiffHtml(a, b) {
                    const aLines = a.split('\n');
                    const bLines = b.split('\n');
                    let html = '';
                    let i = 0, j = 0;
                    const max = 400; // safety
                    while ((i < aLines.length || j < bLines.length) && (i + j) < max) {
                        if (i < aLines.length && j < bLines.length && aLines[i] === bLines[j]) {
                            html += escapeHtml(aLines[i]) + '\n';
                            i++; j++;
                        } else if (i < aLines.length && (j >= bLines.length || aLines[i] !== bLines[j])) {
                            // try to find a match forward for a "move"
                            let found = false;
                            for (let k = j + 1; k < Math.min(j + 6, bLines.length); k++) {
                                if (aLines[i] === bLines[k]) {
                                    // deleted lines before the match
                                    for (let x = j; x < k; x++) html += '<span class="diff-del">' + escapeHtml(bLines[x]) + '</span>\n';
                                    html += escapeHtml(aLines[i]) + '\n';
                                    i++; j = k + 1;
                                    found = true;
                                    break;
                                }
                            }
                            if (!found) {
                                html += '<span class="diff-del">' + escapeHtml(aLines[i]) + '</span>\n';
                                i++;
                            }
                        } else if (j < bLines.length) {
                            html += '<span class="diff-add">' + escapeHtml(bLines[j]) + '</span>\n';
                            j++;
                        }
                    }
                    return html;
                }

                function escapeHtml(s) {
                    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                }

                // Initial load (guarded for anon gate page which omits editor elements)
                document.addEventListener('DOMContentLoaded', function() {
                    if (!document.getElementById('editor-pane')) return;  // gate view or no editor
                    const sel = {{ selected|tojson }};
                    if (sel && (sel.id || sel.kind)) {
                        // slight delay to ensure elements exist
                        setTimeout(function() { populateForm(sel); }, 10);
                    } else {
                        // default empty policy editor if no selection
                        const fresh = { id: null, title: '', description: '', kind: 'policy' };
                        setTimeout(function() { populateForm(fresh); }, 10);
                    }
                    // keyboard hint
                    console.log('%c[Drafts] Rich editor ready. All actions use existing backend POSTs.', 'color:#888');
                });

                // Allow Enter in title to focus desc (small UX)
                // (kept minimal)
            </script>
        </body>
    ''', user=user, policy_drafts=policy_drafts, amend_drafts=amend_drafts, selected=selected or {}, new=new, amend=amend, original_policy=original_policy, amend_originals=amend_originals)