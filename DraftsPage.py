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
    for da in draftAmends:
        if da and da.getTitle():
            pid = da.getPolicyId() or ""
            ptitle = ""
            try:
                p = Database.getPolicy(user, pid) if pid else None
                if p:
                    ptitle = p.getTitle() or ""
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
                "title": ptitle,           # pre-fill with the live policy title so user amends it
                "description": pdesc,      # pre-fill with live body — user edits this into their amendment
                "kind": "amendment",
                "policyId": amend,
                "policyTitle": ptitle,
                "originalDescription": pdesc   # for diff view
            }
    if selected is None and new == "policy":
        selected = {
            "id": None,
            "title": "",
            "description": "",
            "kind": "policy",
            "policyId": None,
            "policyTitle": None
        }
    if selected is None and new == "amendment":
        selected = {
            "id": None,
            "title": "",
            "description": "",
            "kind": "amendment",
            "policyId": None,
            "policyTitle": None
        }
    if selected is None and policy_drafts:
        selected = policy_drafts[0]
    elif selected is None and amend_drafts:
        selected = amend_drafts[0]

    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
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
            .new-draft-link {
                display: block;
                color: #ff6600;
                font-weight: 600;
                font-size: 0.9em;
                margin: 0 0 6px 2px;
                text-decoration: none;
            }
            .new-draft-link:hover {
                text-decoration: underline;
            }
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
                font-size: 0.9em;
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
            .amend-original-hint {
                color: #888;
                font-style: italic;
            }
            .counter {
                font-size: 0.9em;
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
            .diff-box {
                display: flex;
                gap: 12px;
                margin: 10px 0 14px;
            }
            .diff-col {
                flex: 1;
                min-width: 0;
            }
            .diff-col h5 {
                margin: 0 0 4px;
                font-size: 0.85em;
                color: #555;
            }
            .diff-col pre, .diff-col textarea {
                font-size: 0.9em;
                white-space: pre-wrap;
                background: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                min-height: 120px;
                max-height: 260px;
                overflow: auto;
            }
            .diff-col textarea {
                width: 100%;
                box-sizing: border-box;
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

            /* Critical mobile: drafts layout stacks sidebar+editor, full width inputs, touch targets */
            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 14px; max-width: 100%; }
                .menu-bar { padding: 4px 2px; flex-wrap: wrap; }
                .menu-item {
                    margin: 3px 6px; padding: 10px 12px; font-size: 0.95em;
                    min-height: 44px; display: inline-flex; align-items: center; justify-content: center; border-radius: 4px;
                }
                .drafts-layout { flex-direction: column; gap: 16px; }
                .sidebar { width: 100%; }
                .draft-list { max-height: 260px; }
                .editor-card { padding: 16px; }
                .diff-box { flex-direction: column; gap: 10px; }
                .diff-col pre, .diff-col textarea { max-height: 180px; }
                .button-row { flex-direction: column; }
                .button-row button { width: 100%; padding: 12px; }
                .login-gate { margin: 20px auto; padding: 20px; }
                input[type="text"], textarea { padding: 12px; font-size: 1em; }
                .meta { font-size: 0.9em; }
                .counter { font-size: 0.9em; }
                h5 { font-size: 0.9em; }
                .diff-col h5 { font-size: 0.95em; }
                .new-draft-link { font-size: 0.9em; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar (Drafts is primary and active here) -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
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
                        <a href="{{ url_for('drafts', new='policy') }}" class="new-draft-link">+ New policy draft</a>
                        <h3 id="draft-count">Your current drafts ({{ policy_drafts|length + amend_drafts|length }})</h3>
                        <div class="draft-list" id="draft-list">
                            {% if not policy_drafts and not amend_drafts %}
                            <div class="empty-drafts">No drafts yet. Click the button above or "Amend this" from any Library card or detail page to begin.</div>
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
                        <p style="margin-top:12px;font-size:0.9em;color:#666;">Click any draft above to load it into the editor. Changes are saved with the buttons below.</p>
                    </div>

                    <!-- RIGHT EDITOR PANE -->
                    <div class="editor" id="editor-pane">
                        <div class="editor-card" id="editor-card">
                            <div id="success-state" style="display:none;" class="success-state">
                                <h3>Submitted to canidate!</h3>
                                <p>Your proposal is now live on the weekly ballot for members to vote on.</p>
                                <p><a href="{{ url_for('policy') }}" style="color:#ff6600;font-weight:600;">See it in the Congressional Library →</a></p>
                                <p><a href="{{ url_for('vote') }}" style="color:#ff6600;font-weight:600;">Go vote this week →</a></p>
                                <button onclick="startNewDraft()" class="btn-primary" style="margin-top:12px;">Start another draft</button>
                            </div>

                            <div id="form-area">
                                <h3 id="editor-title">Editor</h3>

                                <div id="amend-context" class="amend-context" style="display:none;"></div>

                                <input type="hidden" id="draftId" value="">
                                <input type="hidden" id="draftKind" value="policy">
                                <input type="hidden" id="draftPolicyId" value="">
                                <input type="hidden" id="originalDescription" value="">

                                <label for="title">Title <span style="color:#888;">(max 100 chars)</span></label>
                                <input type="text" id="title" placeholder="Short, clear, under 100 characters" maxlength="100" oninput="updateCounters()">
                                <div class="counter" id="title-counter">0/100</div>

                                <label for="description">Description <span style="color:#888;">(max 10,000 chars)</span></label>
                                <textarea id="description" placeholder="Full text of your proposal. Be specific. What problem does it solve? What exactly should change?" maxlength="10000" oninput="updateCounters()"></textarea>
                                <div class="counter" id="desc-counter">0/10000</div>

                                <div class="button-row">
                                    <button class="btn-primary" onclick="saveDraft()">Save Draft</button>
                                    <button onclick="submitToCanidate()">Submit to Canidate</button>
                                    <button class="btn-danger" onclick="deleteDraft()">Delete Draft</button>
                                </div>
                                <a href="{{ url_for('policy') }}" class="btn-back">← Back to Congressional Library</a>
                            </div>
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

                function attachAmendHintHandler(descEl) {
                    if (!descEl || descEl.dataset.hintAttached === 'true') return;
                    descEl.dataset.hintAttached = 'true';
                    descEl.addEventListener('focus', function() {
                        if (this.classList.contains('amend-original-hint')) {
                            this.classList.remove('amend-original-hint');
                        }
                    });
                    // Click also triggers focus for textareas, but include for robustness
                    descEl.addEventListener('click', function() {
                        if (this.classList.contains('amend-original-hint')) {
                            this.classList.remove('amend-original-hint');
                        }
                    });
                }

                function populateForm(draft) {
                    if (!draft || !document.getElementById('title')) return;
                    currentDraft = draft;

                    const titleEl = document.getElementById('title');
                    const descEl = document.getElementById('description');
                    const idEl = document.getElementById('draftId');
                    const kindEl = document.getElementById('draftKind');
                    const pidEl = document.getElementById('draftPolicyId');
                    const ctx = document.getElementById('amend-context');
                    const h3 = document.getElementById('editor-title');

                    if (titleEl) titleEl.value = draft.title || '';
                    if (descEl) descEl.value = draft.description || '';
                    if (idEl) idEl.value = draft.id || '';
                    if (kindEl) kindEl.value = draft.kind || 'policy';
                    if (pidEl) pidEl.value = draft.policyId || '';

                    // Ensure handler is attached (once)
                    attachAmendHintHandler(descEl);

                    if (draft.kind === 'amendment' && draft.policyId) {
                        if (ctx) {
                            const ptitleRaw = (draft.policyTitle || draft.policyId);
                            const ptitle = ptitleRaw.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            ctx.innerHTML = 'Amendment to Policy: <a href="/detail/' + encodeURIComponent(draft.policyId) + '" style="color:#ff6600; text-decoration:none; font-weight:600; cursor:pointer;"><strong>' + ptitle + '</strong></a>';
                            ctx.style.display = 'block';
                        }
                        if (h3) h3.textContent = draft.id ? 'Edit Amendment Draft' : 'New Amendment Draft';

                        // Grey subdued hint for pre-filled original only on fresh ?amend= arrivals (where originalDescription is provided and matches the starting description)
                        const origText = draft.originalDescription || '';
                        const isFreshOriginalPrefill = origText && draft.description && (draft.description === origText);
                        if (descEl) {
                            if (isFreshOriginalPrefill) {
                                descEl.value = origText;  // ensure starting content
                                descEl.classList.add('amend-original-hint');
                                descEl.dataset.amendOriginal = origText;
                            } else {
                                descEl.classList.remove('amend-original-hint');
                                delete descEl.dataset.amendOriginal;
                            }
                        }
                        const origHidden = document.getElementById('originalDescription');
                        if (origHidden) origHidden.value = origText || (draft.description || '');
                    } else {
                        if (ctx) ctx.style.display = 'none';
                        if (h3) h3.textContent = draft.id ? 'Edit Policy Draft' : 'New Policy Draft';
                        if (descEl) {
                            descEl.classList.remove('amend-original-hint');
                            delete descEl.dataset.amendOriginal;
                        }
                    }

                    // highlight active in sidebar
                    document.querySelectorAll('#draft-list .draft-item').forEach(el => {
                        el.classList.remove('active');
                        if (el.dataset.id === (draft.id || '') && draft.id) {
                            el.classList.add('active');
                        }
                    });

                    updateCounters();
                    // show form, hide success
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
                        policyTitle: el.dataset.policytitle || null,
                        originalDescription: ''   // existing saved drafts don't carry snapshot; diff mainly for fresh amend arrivals
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
                            // Remove the just-submitted item from the sidebar so it can't be clicked again
                            const submittedId = id;
                            document.querySelectorAll('#draft-list .draft-item').forEach(el => {
                                if (el.dataset.id === submittedId) {
                                    el.remove();
                                }
                            });
                            // Clear any active highlight
                            document.querySelectorAll('#draft-list .draft-item').forEach(el => el.classList.remove('active'));

                            // Update the visible draft count in the header
                            const countEl = document.getElementById('draft-count');
                            if (countEl) {
                                const m = countEl.textContent.match(/\\((\\d+)\\)/);
                                if (m) {
                                    const n = Math.max(0, parseInt(m[1], 10) - 1);
                                    countEl.textContent = countEl.textContent.replace(/\\((\\d+)\\)/, `(${n})`);
                                }
                            }

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
    ''', user=user, policy_drafts=policy_drafts, amend_drafts=amend_drafts, selected=selected or {}, new=new, amend=amend)