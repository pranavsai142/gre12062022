from flask import Flask, render_template_string
import User
import Database

def render(user):
    if(not User.validateUser(user)):
        user = None

    # Live-ish stats for the visionary home (re-uses the engine)
    try:
        window = Database.getCurrentVotingWindowId()
        pol_sum = Database.get_policies_summary()
        ballot_p, ballot_a = Database.getBallotItems()
        part = Database.getWindowParticipationCount(window)
        has_ballot = len(ballot_p) + len(ballot_a) > 0
        clock = Database.getVotingClock()
    except Exception:
        window = "2026-W21"
        pol_sum = {"draft": 2, "canidate": 5, "official": 1}
        has_ballot = True
        part = 1
        clock = {
            "windowId": window,
            "nextWindowId": "—",
            "isOverride": False,
            "phase": "open",
            "serverNow": "",
            "endsAt": "",
            "secondsToRealWeekEnd": 0,
        }

    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>The Internet Party — Truth • Freedom • Health</title>
        <meta name="description" content="Party No. 3 — weekly direct democracy on a living platform. Real ISO-week voting windows (UTC), public ballots, and majority rules.">
        <meta property="og:title" content="The Internet Party — Truth • Freedom • Health">
        <meta property="og:description" content="Parallel internet democracy. Draft policy, vote every week, watch the live countdown to the next window.">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://theinternetparty.us/">
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
                color: #333; /* explicit non-purple from palette */
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
            /* Visionary Home styles — match VotePage quality */
            .hero {
                background: linear-gradient(135deg, #fff7ed 0%, #fff1e6 100%);
                border-left: 8px solid #ff6600;
                padding: 48px 40px;
                margin-bottom: 32px;
                border-radius: 8px;
            }
            .hero h1 { font-size: 2.8em; margin: 0 0 8px 0; color: #222; }
            .hero .tagline { font-size: 1.35em; color: #444; margin-bottom: 20px; }
            .mission {
                font-size: 1.1em;
                color: #333;
                max-width: 720px;
            }
            .cta-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 14px;
                margin: 28px 0;
            }
            .cta {
                display: block;
                background: white;
                border: 2px solid #ff6600;
                color: #222;
                padding: 18px 20px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                transition: all .1s ease;
            }
            .cta:hover { background: #ff6600; color: white; transform: translateY(-1px); }
            .cta.secondary { border-color: #333; }
            .cta.secondary:hover { background: #333; color: white; }
            .stats {
                display: flex;
                gap: 24px;
                flex-wrap: wrap;
                margin: 20px 0 32px;
            }
            .stat-card {
                background: white;
                border: 1px solid #eee;
                padding: 16px 22px;
                border-radius: 6px;
                min-width: 160px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }
            .stat-card .num { font-size: 1.9em; font-weight: 700; color: #ff6600; }
            .stat-card .label { font-size: .9em; color: #666; }
            .section { margin-bottom: 36px; }
            .section h3 { border-bottom: 3px solid #ff6600; padding-bottom: 6px; color: #222; }
            .notice {
                background: #fff3e0;
                border-left: 6px solid #ff6600;
                padding: 14px 18px;
                margin: 16px 0;
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
                margin: 0 0 20px;
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

            /* Mobile-first responsive overrides — desktop appearance unchanged */
            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 16px; }
                .menu-bar {
                    padding: 8px 0; /* revised vertical padding/alignment vs prior 4px 2px — grounds the bar, less raised */
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
                    color: #333; /* non-purple, site palette */
                }
                .menu-item:hover {
                    color: #ff6600;
                    background: #fff7ed; /* vamp polish: subtle hover state using accent */
                }
                .menu-item:active {
                    color: #cc5200;
                    font-weight: bold;
                }
                .menu-item.active {
                    color: #ff6600;
                    font-weight: bold;
                }
                .hero { padding: 28px 16px; margin-bottom: 24px; }
                .hero h1 { font-size: 2.1em; }
                .hero .tagline { font-size: 1.15em; }
                .cta-grid { grid-template-columns: 1fr; gap: 10px; }
                .stats { gap: 12px; }
                .stat-card { min-width: 46%; padding: 12px 14px; }
                .stat-card .num { font-size: 1.6em; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item active">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                <div class="hero">
                    <h1>The Internet Party</h1>
                    <div class="tagline">Party No. 3 — Truth • Freedom • Health</div>
                    <p class="mission">
                        A parallel political system built for the 21st century. Weekly direct democracy on a living platform.
                        Anyone can draft policy. Every registered member votes. Majority winners become the official platform.
                    </p>
                    <div class="cta-grid">
                        <a href="{{ url_for('vote') }}" class="cta">Vote on the Current Ballot →</a>
                        <a href="{{ url_for('policy') }}" class="cta secondary">Browse the Congressional Library</a>
                        <a href="{{ url_for('drafts', new='policy') }}" class="cta secondary">Draft a New Policy</a>
                        <a href="{{ url_for('account') }}" class="cta secondary">{{ 'Your Account & History' if user else 'Login / Register' }}</a>
                    </div>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="num">{{ pol_sum.canidate + pol_sum.official }}</div>
                        <div class="label">Policies in motion or enacted</div>
                    </div>
                    <div class="stat-card">
                        <div class="num">{{ part }}</div>
                        <div class="label">Members voted this week ({{ window }})</div>
                    </div>
                    <div class="stat-card">
                        <div class="num">{{ pol_sum.official }}</div>
                        <div class="label">Official Platform items</div>
                    </div>
                    <div class="stat-card">
                        <div class="num">{{ pol_sum.draft }}</div>
                        <div class="label">Policies in private draft</div>
                    </div>
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
                    <span class="vc-countdown">Loading clock…</span>
                </div>

                {% if has_ballot %}
                <div class="section">
                    <div class="notice">
                        <strong>Active weekly ballot open now.</strong>
                        <a href="{{ url_for('vote') }}">Cast your vote for Window {{ window }} →</a>
                    </div>
                </div>
                {% endif %}

                <div class="section">
                    <h3>Why Party No. 3?</h3>
                    <p>
                        Launched from the 2020 accountability movement. We believe the only way to restore trust in governance
                        is radical transparency + continuous direct participation. No more 4-year mandates. No more gatekeepers.
                        The platform is written by the members, week after week.
                    </p>
                </div>

                <div class="section">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="{{ url_for('about') }}">Read the full MetaPolicies and how the weekly vote actually works</a></li>
                        <li><a href="{{ url_for('policy') }}">The Congressional Library — every policy and amendment, status-aware</a></li>
                        <li><a href="{{ url_for('vote') }}">This week's ballot (live tallies visible after you vote)</a></li>
                    </ul>
                </div>
            </div>

            <script src="{{ url_for('static', filename='js/voting-clock.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, window=window, pol_sum=pol_sum, part=part, has_ballot=has_ballot, clock=clock)