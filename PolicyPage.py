from flask import Flask, render_template_string
import User
import Database

def render(user):
    if(not User.validateUser(user)):
        user = None

    # Gather everything for the Congressional Library
    canidates = Database.getCanidatePolicies()
    policies = Database.getOfficialPolicies()
    canidateAmendments = Database.getCanidateAmendments()
    amendments = Database.getOfficialAmendments()

    # Drafts only for logged-in user (private)
    drafts = Database.getDraftPolicies(user) if user else []
    draftAmends = Database.getDraftAmendments(user) if user else []

    # Current ballot notice data
    window = Database.getCurrentVotingWindowId()
    ballot_count = len(canidates) + len(canidateAmendments)

    # Prepare rich card data (title + excerpt + id + kind)
    def _prep_cards(items, kind, status):
        out = []
        for it in items:
            title = getattr(it, 'policyTitle', None) or it.getTitle()
            desc = getattr(it, 'policyDescription', None) or it.getDescription() or ""
            excerpt = (desc[:220] + "…") if len(desc) > 220 else desc
            pid = getattr(it, 'policyId', None) or it.getId()
            out.append({
                "id": pid,
                "title": title,
                "excerpt": excerpt,
                "kind": kind,
                "status": status,
                "url": f"/detail/{pid}" if kind == "policy" else f"/detail/amendment/{pid}"
            })
        return out

    lib_items = []
    lib_items += _prep_cards(canidates, "policy", "Candidate")
    lib_items += _prep_cards(canidateAmendments, "amendment", "Candidate")
    lib_items += _prep_cards(policies, "policy", "Official")
    lib_items += _prep_cards(amendments, "amendment", "Official")

    return render_template_string('''
        <!doctype html>
        <title>The Internet Party — Congressional Library</title>
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
                max-width: 1100px;
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
            /* Congressional Library — high quality cards + filters */
            .library-header {
                background: #fff;
                border-left: 6px solid #ff6600;
                padding: 18px 22px;
                margin-bottom: 18px;
            }
            .filters {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin: 14px 0 20px;
            }
            .filter-btn {
                padding: 6px 14px;
                border: 1px solid #ccc;
                background: white;
                border-radius: 999px;
                font-size: 0.9em;
                cursor: pointer;
            }
            .filter-btn.active, .filter-btn:hover {
                background: #ff6600;
                color: white;
                border-color: #ff6600;
            }
            .search-box {
                width: 100%;
                max-width: 420px;
                padding: 10px 14px;
                font-size: 1em;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-bottom: 18px;
            }
            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 16px;
            }
            .lib-card {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
                display: flex;
                flex-direction: column;
            }
            .lib-card h4 {
                margin: 0 0 8px;
                font-size: 1.05em;
            }
            .lib-card .meta {
                font-size: 0.78em;
                color: #666;
                margin-bottom: 8px;
            }
            .lib-card .excerpt {
                flex: 1;
                font-size: 0.92em;
                color: #444;
                line-height: 1.4;
                margin-bottom: 12px;
            }
            .status-pill {
                display: inline-block;
                font-size: 0.75em;
                padding: 2px 9px;
                border-radius: 999px;
                font-weight: 600;
            }
            .status-Candidate { background:#fff3e0; color:#c60; }
            .status-Official { background:#e6f4e6; color:#0a7; }
            .status-Draft { background:#f0f0f0; color:#555; }
            .ballot-strip {
                background: #fff3e0;
                border: 1px solid #ffcc80;
                padding: 12px 18px;
                border-radius: 6px;
                margin: 20px 0;
            }
            .empty {
                padding: 40px;
                text-align: center;
                color: #666;
                background: #fff;
                border: 1px dashed #ccc;
                border-radius: 8px;
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item.active">Policy</a>
                {% if user %}<a href="{{ url_for('drafts') }}" class="menu-item">Drafts</a>{% endif %}
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                <div class="library-header">
                    <h2>The Congressional Library</h2>
                    <p>The complete living record of The Internet Party platform — drafts (private), candidates on the weekly ballot, and the enacted official platform.</p>
                    <p><a href="{{ url_for('drafts') }}">+ Draft a new Policy or Amendment</a></p>
                </div>

                {% if ballot_count > 0 %}
                <div class="ballot-strip">
                    <strong>This Week's Ballot (Window {{ window }}) is live</strong> — 
                    {{ ballot_count }} candidate items are currently being voted on.
                    <a href="{{ url_for('vote') }}" style="font-weight:600">Go cast your ballot →</a>
                </div>
                {% endif %}

                <input id="search" class="search-box" type="text" placeholder="Search policies and amendments by title or description..." onkeyup="filterLibrary()">

                <div class="filters">
                    <button class="filter-btn active" data-filter="all" onclick="setFilter('all', this)">All</button>
                    <button class="filter-btn" data-filter="Candidate" onclick="setFilter('Candidate', this)">On the Ballot (Candidate)</button>
                    <button class="filter-btn" data-filter="Official" onclick="setFilter('Official', this)">Official Platform</button>
                    <button class="filter-btn" data-filter="Draft" onclick="setFilter('Draft', this)">My Drafts (private)</button>
                    <button class="filter-btn" data-filter="policy" onclick="setFilter('policy', this)">Policies only</button>
                    <button class="filter-btn" data-filter="amendment" onclick="setFilter('amendment', this)">Amendments only</button>
                </div>

                <div class="card-grid" id="library-grid">
                    {% for item in lib_items %}
                    <div class="lib-card" data-title="{{ item.title|lower }}" data-excerpt="{{ item.excerpt|lower }}" data-status="{{ item.status }}" data-kind="{{ item.kind }}">
                        <h4><a href="{{ item.url }}">{{ item.title }}</a></h4>
                        <div class="meta">
                            <span class="status-pill status-{{ item.status }}">{{ item.status }}</span>
                            &nbsp;{{ item.kind|title }}
                        </div>
                        <div class="excerpt">{{ item.excerpt }}</div>
                        <a href="{{ item.url }}" style="font-size:0.85em;color:#ff6600">View full text &amp; history →</a>
                    </div>
                    {% endfor %}

                    {% if user %}
                    {% for d in drafts %}
                    {% if d and d.getTitle() %}
                    <div class="lib-card" data-title="{{ (d.getTitle() or '')|lower }}" data-excerpt="{{ (d.getDescription() or '')[:200]|lower }}" data-status="Draft" data-kind="policy">
                        <h4><a href="{{ url_for('drafts') }}">{{ d.getTitle() }}</a></h4>
                        <div class="meta"><span class="status-pill status-Draft">Draft</span> Policy (yours)</div>
                        <div class="excerpt">{{ (d.getDescription() or '')[:200] }}…</div>
                        <a href="{{ url_for('drafts') }}" style="font-size:0.85em;color:#ff6600">Edit in Drafts hub →</a>
                    </div>
                    {% endif %}
                    {% endfor %}
                    {% for d in draftAmends %}
                    {% if d and d.getTitle() %}
                    <div class="lib-card" data-title="{{ (d.getTitle() or '')|lower }}" data-excerpt="{{ (d.getDescription() or '')[:200]|lower }}" data-status="Draft" data-kind="amendment">
                        <h4><a href="{{ url_for('drafts', amend=(d.getPolicyId() or '')) }}">{{ d.getTitle() }}</a></h4>
                        <div class="meta"><span class="status-pill status-Draft">Draft</span> Amendment (yours)</div>
                        <div class="excerpt">{{ (d.getDescription() or '')[:200] }}…</div>
                        <a href="{{ url_for('drafts', amend=(d.getPolicyId() or '')) }}" style="font-size:0.85em;color:#ff6600">Edit in Drafts hub →</a>
                    </div>
                    {% endif %}
                    {% endfor %}
                    {% endif %}
                </div>

                <div id="empty-state" class="empty" style="display:none">
                    No items match your current filters and search.
                </div>

                <p style="margin-top:30px;color:#666;font-size:0.9em">
                    This is the living Congressional Library — the complete, member-voted record of policies and amendments that shape our platform.
                </p>
            </div>

            <script>
                let currentFilter = 'all';
                function setFilter(f, btn) {
                    currentFilter = f;
                    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    filterLibrary();
                }
                function filterLibrary() {
                    const q = (document.getElementById('search').value || '').toLowerCase().trim();
                    const cards = document.querySelectorAll('#library-grid .lib-card');
                    let visible = 0;
                    cards.forEach(card => {
                        const title = card.dataset.title || '';
                        const excerpt = card.dataset.excerpt || '';
                        const status = card.dataset.status || '';
                        const kind = card.dataset.kind || '';
                        const matchesSearch = !q || title.includes(q) || excerpt.includes(q);
                        let matchesFilter = true;
                        if (currentFilter === 'Candidate' || currentFilter === 'Official' || currentFilter === 'Draft') {
                            matchesFilter = status === currentFilter;
                        } else if (currentFilter === 'policy' || currentFilter === 'amendment') {
                            matchesFilter = kind === currentFilter;
                        }
                        const show = matchesSearch && matchesFilter;
                        card.style.display = show ? '' : 'none';
                        if (show) visible++;
                    });
                    document.getElementById('empty-state').style.display = visible === 0 ? 'block' : 'none';
                }
                // Keyboard friendly: focus search on / key when not typing elsewhere (light enhancement)
                document.addEventListener('keydown', function(e){
                    if (e.key === '/' && document.activeElement.tagName === 'BODY') {
                        e.preventDefault();
                        document.getElementById('search').focus();
                    }
                });
            </script>

            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, canidates=canidates, policies=policies, canidateAmendments=canidateAmendments, amendments=amendments,
         drafts=drafts, draftAmends=draftAmends, lib_items=lib_items, window=window, ballot_count=ballot_count)