from flask import Flask, render_template_string
import User
import Database


def render(user=None):
    if not User.validateUser(user):
        user = None
    try:
        clock = Database.getVotingClock()
    except Exception:
        clock = {"endsAt": "", "remainingLabel": "", "windowId": "", "nextWindowId": ""}
    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Reset Password — The Internet Party</title>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-auth.js"></script>
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
                max-width: 520px;
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
            .footer-text { margin: 0; }
            .footer-text span { color: #ff6600; }
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
            .menu-item:visited { color: #333; }
            .menu-item:hover { color: #ff6600; }
            .menu-item:active { color: #cc5200; font-weight: bold; }
            .menu-item.active { color: #ff6600; font-weight: bold; }
            .auth-card {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 24px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            }
            .auth-header {
                background: #fff;
                border-left: 6px solid #ff6600;
                padding: 16px 20px;
                margin-bottom: 16px;
                border-radius: 0 6px 6px 0;
            }
            .auth-header h2 { margin: 0 0 4px; font-size: 1.25em; }
            .auth-header p { margin: 0; color: #555; font-size: 0.95em; }
            label {
                display: block;
                color: #444;
                margin-bottom: 4px;
                font-weight: 600;
            }
            input[type="email"] {
                width: 100%;
                box-sizing: border-box;
                padding: 12px 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                margin-bottom: 14px;
            }
            input[type="email"]:focus {
                border-color: #ff6600;
                outline: none;
                box-shadow: 0 0 0 2px rgba(255,102,0,0.12);
            }
            .btn-primary {
                background: #ff6600;
                color: white;
                border: 1px solid #ff6600;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 1em;
                cursor: pointer;
                width: 100%;
            }
            .btn-primary:hover { background: #e55a00; }
            .btn-primary:disabled { opacity: 0.6; cursor: wait; }
            .auth-links {
                margin-top: 16px;
                font-size: 0.9em;
                color: #555;
            }
            .auth-links a {
                color: #ff6600;
                font-weight: 600;
                text-decoration: none;
            }
            #errorMessage {
                display: none;
                margin-top: 12px;
                padding: 10px 12px;
                background: #fff0f0;
                border: 1px solid #e88;
                color: #922;
                border-radius: 6px;
                font-size: 0.9em;
            }
            #successMessage {
                display: none;
                margin-top: 12px;
                padding: 10px 12px;
                background: #f0fff0;
                border: 1px solid #8c8;
                color: #063;
                border-radius: 6px;
                font-size: 0.9em;
            }
            .voting-clock {
                display: flex;
                flex-wrap: wrap;
                align-items: baseline;
                gap: 8px 14px;
                background: #fff7ed;
                border: 1px solid #ffcc99;
                border-left: 6px solid #ff6600;
                padding: 10px 14px;
                margin: 0 0 14px;
                border-radius: 6px;
                font-size: 0.95em;
            }
            .voting-clock .vc-countdown {
                font-weight: 700;
                color: #cc5200;
                font-variant-numeric: tabular-nums;
            }
            .voting-clock .vc-detail { color: #555; font-size: 0.9em; }

            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 16px; }
                .menu-bar {
                    padding: 8px 0;
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
                }
                .menu-item:hover {
                    color: #ff6600;
                    background: #fff7ed;
                }
                .menu-item.active { color: #ff6600; font-weight: bold; }
                .auth-card { padding: 18px; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>
            <div class="content">
                <div class="voting-clock"
                     data-voting-clock
                     data-compact="1"
                     data-window-id="{{ clock.windowId }}"
                     data-next-window="{{ clock.nextWindowId }}"
                     data-ends-at="{{ clock.endsAt or '' }}"
                     data-server-now="{{ clock.serverNow }}"
                     data-override="{{ '1' if clock.isOverride else '0' }}"
                     data-phase="{{ clock.phase }}"
                     data-seconds-real-end="{{ clock.secondsToRealWeekEnd }}">
                    <span class="vc-countdown">{% if clock is defined and clock.endsAt %}Closes in {{ clock.remainingLabel }}{% elif clock is defined and clock.remainingLabel %}Closes in {{ clock.remainingLabel }}{% else %}Loading clock…{% endif %}</span>
                </div>
                <div class="auth-header">
                    <h2>Reset Password</h2>
                    <p>We will email you a secure Firebase reset link. Real account, real week, real membership.</p>
                </div>
                <div class="auth-card">
                    <label for="email">Email</label>
                    <input type="email" id="email" placeholder="you@example.com" autocomplete="email">
                    <button type="button" id="resetButton" class="btn-primary">Send reset link</button>
                    <div id="errorMessage" role="alert"></div>
                    <div id="successMessage" role="status"></div>
                    <div class="auth-links">
                        <a href="{{ url_for('login') }}">Back to Sign In</a>
                        &nbsp;·&nbsp;
                        <a href="{{ url_for('register') }}">Join the Party</a>
                    </div>
                </div>
            </div>
            <script src="{{ url_for('static', filename='js/reset.js') }}"></script>
            <script src="{{ url_for('static', filename='js/voting-clock.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, clock=clock)
