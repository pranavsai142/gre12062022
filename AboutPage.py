from flask import Flask, render_template_string
import User

def render(user):
    if(not User.validateUser(user)):
        user = None
    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>The Internet Party — About</title>
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
                max-width: 960px;
                margin: 0 auto;
                line-height: 1.6;
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
            .about-section { margin-bottom: 36px; }
            .about-section h2 { border-bottom: 3px solid #ff6600; padding-bottom: 6px; }
            .meta { background:#fff9e6; padding:16px; border-left:6px solid #cc9900; margin:16px 0; }
            ul { padding-left: 22px; }

            /* Mobile responsive — sections stack, touch targets, no desktop change */
            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 16px; max-width: 100%; }
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
                .about-section { margin-bottom: 28px; }
                .about-section h2 { font-size: 1.25em; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item active">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                <h2>About The Internet Party (Party No. 3)</h2>

                <div class="about-section">
                    <p style="font-size:1.3em;margin:8px 0 16px;"><strong>Truth • Freedom • Health</strong></p>
                    <p>
                        After 2020, it was clear the old system had failed ordinary people. So we built something new:
                        a parallel political system where <strong>anyone with internet can join</strong> and actually write the rules.
                        No insiders. No four-year waits. The platform belongs to the members — and it is rewritten every single week by majority vote.
                    </p>
                    <p><a href="{{ url_for('register') }}" style="color:#ff6600;font-weight:600;">Join the Party today</a> — it takes one minute. Or <a href="{{ url_for('login') }}">log in</a> if you already have an account.</p>
                </div>

                <div class="about-section">
                    <h2>How the Weekly Vote Works</h2>
                    <p>Simple, transparent, and powerful — and tied to the <strong>real calendar</strong>:</p>
                    <ol>
                        <li>Any registered member drafts a Policy or an Amendment in their private drafts hub.</li>
                        <li>They save it, then submit it to the canidate queue for the week.</li>
                        <li>The live ballot is the canidate pool for the <strong>current ISO week</strong> (Monday 00:00 UTC → next Monday 00:00 UTC). A live countdown on Home and Vote shows exactly when this window ends and the next one begins.</li>
                        <li>Registered members vote Yes / No / Abstain <strong>once per window</strong>. Ballots are immutable for that week.</li>
                        <li>Majority Yes (among votes cast) wins; operators promote winners to the official living platform.</li>
                        <li>The official platform is the real law of the party — visible to everyone, changed only by the people.</li>
                    </ol>
                    <p style="margin-top:12px;"><a href="{{ url_for('vote') }}" style="font-weight:600;color:#ff6600;">See this week's ballot, countdown, and vote now →</a></p>
                </div>

                <div class="about-section">
                    <h2>The Real Rules (MetaPolicies, explained plainly)</h2>
                    <ul style="line-height:1.7;">
                        <li><strong>Real-world weekly windows</strong>: ISO weeks in UTC. The site clock at <code>/voting-clock</code> and the timers on Vote/Home tick every second from server time — not fake demo timers.</li>
                        <li><strong>One immutable ballot per member per window</strong>: You cast once; your choices are final for that week.</li>
                        <li><strong>Title under 100 characters</strong>, full description under 10,000 characters (enforced server-side). Keep it tight and clear.</li>
                        <li><strong>365-day sunset + renewal</strong> (roadmap): Nothing stays official forever. Every item must be re-approved within a year or it expires.</li>
                        <li><strong>One human, one membership</strong>: Registration requires your real phone number + name carrier. No bots, no duplicates.</li>
                        <li><strong>Stay active or lose membership</strong> (roadmap): Three weeks of inactivity and you are dismissed. Participation keeps the system alive.</li>
                        <li>Every draft, vote, and promotion is public and permanent in the record.</li>
                    </ul>
                </div>

                <div class="about-section">
                    <h2>Our Platform: Truth • Freedom • Health</h2>
                    <p>These are not slogans. They are concrete promises already in motion or on the table:</p>
                    <ul style="line-height:1.65;">
                        <li><strong>Truth</strong>: Full audits of COVID death counts and vaccine data, First Amendment protections, RICO accountability, criminal justice reform (end the prohibition, class actions against bad actors), police audits.</li>
                        <li><strong>Freedom</strong>: American Basic Income / Liberty Dividend so every citizen has a floor. Employee rights. Bring the troops home. End imperial violence and foreign aid waste. "Fuck the Feds" — audit and restrain the CIA, FDA, CDC, NORAD, Fed, Pentagon, TSA. Repeal the Patriot Act.</li>
                        <li><strong>Health</strong>: Sustainable microgrids and real environmental infrastructure that actually works for communities.</li>
                        <li><strong>Voting Reform &amp; Vision</strong>: Character limits on proposals, real one-person-one-vote, and the long-term goal: Madam President Roseanne Barr leading a government of the people, by the people, on the internet.</li>
                    </ul>
                    <p style="margin-top:10px;font-style:italic;">This is the beginning. You write the rest.</p>
                </div>

                <div class="about-section" style="text-align:center; margin-top:30px;">
                    <p style="font-size:1.1em;"><strong>Ready to have a real voice?</strong></p>
                    <a href="{{ url_for('register') }}" style="display:inline-block;margin:8px;padding:12px 28px;background:#ff6600;color:white;border-radius:6px;text-decoration:none;font-weight:700;">Join the Party — Free</a>
                    <a href="{{ url_for('login') }}" style="display:inline-block;margin:8px;padding:12px 28px;background:#333;color:white;border-radius:6px;text-decoration:none;font-weight:600;">I already have an account</a>
                    <p style="margin-top:20px;"><a href="{{ url_for('policy') }}">Browse the Congressional Library</a> &nbsp;•&nbsp; <a href="{{ url_for('vote') }}">Vote on the Current Ballot</a> &nbsp;•&nbsp; <a href="{{ url_for('index') }}">Back to Home</a></p>
                </div>
            </div>

            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user)