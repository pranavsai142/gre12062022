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

    # Current ballot notice data + real-world voting clock
    window = Database.getCurrentVotingWindowId()
    ballot_count = len(canidates) + len(canidateAmendments)
    try:
        clock = Database.getVotingClock()
    except Exception:
        clock = {
            "windowId": window,
            "nextWindowId": "—",
            "isOverride": False,
            "phase": "open",
            "serverNow": "",
            "endsAt": "",
            "secondsToRealWeekEnd": 0,
        }

    # Prepare rich card data (title + excerpt + id + kind + sortable date)
    def _prep_cards(items, kind, status):
        out = []
        for it in items:
            title = getattr(it, 'policyTitle', None) or it.getTitle()
            desc = getattr(it, 'policyDescription', None) or it.getDescription() or ""
            excerpt = (desc[:220] + "…") if len(desc) > 220 else desc
            iid = it.getId()

            # Prefer updatedTimestamp (when the item was last touched), fall back to created
            ts = getattr(it, 'updatedTimestamp', None)
            if not ts:
                ts = getattr(it, 'createdTimestamp', 0)
            try:
                ts = float(ts)
            except (TypeError, ValueError):
                ts = 0.0

            out.append({
                "id": iid,
                "title": title,
                "excerpt": excerpt,
                "kind": kind,
                "status": status,
                "url": f"/detail/{iid}" if kind == "policy" else f"/detail/amendment/{iid}",
                "sortTimestamp": ts
            })
        return out

    lib_items = []
    lib_items += _prep_cards(canidates, "policy", "Candidate")
    lib_items += _prep_cards(canidateAmendments, "amendment", "Candidate")
    lib_items += _prep_cards(policies, "policy", "Official")
    lib_items += _prep_cards(amendments, "amendment", "Official")

    # Default render order = Newest first (policies use policy date, amendments use amendment date)
    lib_items.sort(key=lambda x: x.get("sortTimestamp", 0), reverse=True)

    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
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
                cursor: pointer;
                transition: border-color .1s ease, box-shadow .1s ease;
                overflow-wrap: break-word;
            }
            .lib-card:hover {
                border-color: #ff6600;
                box-shadow: 0 4px 10px rgba(255,102,0,0.08);
            }
            .lib-card h4 {
                margin: 0 0 8px;
                font-size: 1.05em;
                overflow-wrap: break-word;
                word-break: break-word;
            }
            .lib-card .meta {
                font-size: 0.9em;
                color: #666;
                margin-bottom: 8px;
            }
            .lib-card .excerpt {
                flex: 1;
                font-size: 0.92em;
                color: #444;
                line-height: 1.4;
                margin-bottom: 12px;
                overflow-wrap: break-word;
                word-break: break-word;
            }
            .status-pill {
                display: inline-block;
                font-size: 0.9em;
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
            .voting-clock {
                display: flex;
                flex-wrap: wrap;
                align-items: baseline;
                gap: 8px 16px;
                background: #fff7ed;
                border: 1px solid #ffcc99;
                border-left: 6px solid #ff6600;
                padding: 12px 16px;
                margin: 0 0 16px;
                border-radius: 6px;
            }
            .voting-clock .vc-countdown {
                font-size: 1.05em;
                font-weight: 700;
                color: #cc5200;
                font-variant-numeric: tabular-nums;
            }
            .voting-clock .vc-detail {
                font-size: 0.9em;
                color: #555;
            }
            .empty {
                padding: 40px;
                text-align: center;
                color: #666;
                background: #fff;
                border: 1px dashed #ccc;
                border-radius: 8px;
            }

            /* Mobile overrides for library cards + filters (desktop grid untouched) */
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
                .library-header { padding: 14px 16px; }
                .card-grid { grid-template-columns: 1fr; gap: 12px; }
                .search-box { max-width: 100%; padding: 10px 12px; }
                .filters { gap: 6px; }
                .filter-btn { padding: 8px 12px; font-size: 0.95em; }
                .lib-card { padding: 14px; }
                .empty { padding: 24px; }
                .meta { font-size: 0.9em; }
                .status-pill { font-size: 0.9em; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item active">Policy</a>
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
                        {% if clock.endsAt %}Closes in {{ clock.remainingLabel }} · next {{ clock.nextWindowId }}{% else %}Loading clock…{% endif %}
                    </span>
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
                    <button class="filter-btn" data-filter="policy" onclick="setFilter('policy', this)">Policies only</button>
                    <button class="filter-btn" data-filter="amendment" onclick="setFilter('amendment', this)">Amendments only</button>
                </div>

                <div style="margin: 8px 0 12px; font-size:0.9em; color:#666;">
                    Sort: <a href="#" onclick="sortLibrary('date'); return false;" id="sort-date" style="color:#ff6600;font-weight:600;text-decoration:none;margin-right:8px;">Newest</a>
                    <a href="#" onclick="sortLibrary('title'); return false;" id="sort-title" style="color:#666;text-decoration:none;">A–Z</a>
                </div>

                <div class="card-grid" id="library-grid">
                    {% for item in lib_items %}
                    <div class="lib-card" data-title="{{ item.title|lower }}" data-excerpt="{{ item.excerpt|lower }}" data-status="{{ item.status }}" data-kind="{{ item.kind }}" data-url="{{ item.url }}" data-timestamp="{{ item.sortTimestamp }}" onclick="goToCardDetail(this, event)">
                        <h4><a href="{{ item.url }}">{{ item.title }}</a></h4>
                        <div class="meta">
                            <span class="status-pill status-{{ item.status }}">{{ item.status }}</span>
                            &nbsp;{{ item.kind|title }}
                        </div>
                        <div class="excerpt">{{ item.excerpt }}</div>
                    </div>
                    {% endfor %}
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
                let originalCardOrder = null;

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

                function goToCardDetail(cardEl, ev) {
                    const e = ev || window.event;
                    if (e) {
                        const target = e.target || e.srcElement;
                        if (target && target.closest('a, button')) {
                            return;
                        }
                    }
                    const url = cardEl.dataset.url;
                    if (url) {
                        window.location.href = url;
                    }
                }

                function sortLibrary(mode) {
                    const grid = document.getElementById('library-grid');
                    const cards = Array.from(grid.querySelectorAll('.lib-card'));
                    const dateLink = document.getElementById('sort-date');
                    const titleLink = document.getElementById('sort-title');

                    if (mode === 'title') {
                        cards.sort((a, b) => (a.dataset.title || '').localeCompare(b.dataset.title || ''));
                        dateLink.style.color = '#666';
                        dateLink.style.fontWeight = 'normal';
                        titleLink.style.color = '#ff6600';
                        titleLink.style.fontWeight = '600';
                    } else {
                        // 'date' — real numeric sort, newest first (uses the item's own timestamp:
                        // policy cards use the policy's updated/created date, amendment cards use the amendment's)
                        cards.sort((a, b) => {
                            const ta = parseFloat(a.dataset.timestamp || '0');
                            const tb = parseFloat(b.dataset.timestamp || '0');
                            return tb - ta;   // descending = newest on top
                        });
                        dateLink.style.color = '#ff6600';
                        dateLink.style.fontWeight = '600';
                        titleLink.style.color = '#666';
                        titleLink.style.fontWeight = 'normal';
                    }

                    cards.forEach(c => grid.appendChild(c));
                    // Re-apply current filter/search after reorder
                    filterLibrary();
                }

                // Capture the original server-provided order for "Newest" resets
                document.addEventListener('DOMContentLoaded', function() {
                    const grid = document.getElementById('library-grid');
                    if (grid) {
                        originalCardOrder = Array.from(grid.querySelectorAll('.lib-card'));
                    }
                });
            </script>
            <script src="{{ url_for('static', filename='js/voting-clock.js') }}"></script>

            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, canidates=canidates, policies=policies, canidateAmendments=canidateAmendments, amendments=amendments,
         drafts=drafts, draftAmends=draftAmends, lib_items=lib_items, window=window, ballot_count=ballot_count, clock=clock)