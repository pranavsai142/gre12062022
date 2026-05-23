from flask import Flask, render_template_string
import User

def render(user):
    if(not User.validateUser(user)):
        user = None
    return render_template_string('''
        <!doctype html>
        <title>Join — The Internet Party</title>
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
            /* Revamped register styles — consistent production card + form treatment */
            .auth-header {
                background: #fff;
                border-left: 6px solid #ff6600;
                padding: 16px 20px;
                margin-bottom: 16px;
                border-radius: 0 6px 6px 0;
            }
            .auth-header h2 {
                margin: 0 0 4px;
                font-size: 1.35em;
                color: #222;
            }
            .auth-card {
                background: white;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 24px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            }
            .auth-intro {
                color: #555;
                font-size: 0.95em;
                margin-bottom: 16px;
                line-height: 1.4;
            }
            label {
                display: block;
                font-size: 0.9em;
                color: #444;
                margin-bottom: 4px;
                font-weight: 600;
            }
            input[type="email"], input[type="password"] {
                width: 100%;
                box-sizing: border-box;
                padding: 12px 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 1em;
                margin-bottom: 14px;
                transition: border-color .1s ease, box-shadow .1s ease;
            }
            input[type="email"]:focus, input[type="password"]:focus {
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
                transition: background .1s ease;
            }
            .btn-primary:hover { background: #e55a00; }
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
            .auth-links a:hover { text-decoration: underline; }
            #errorMessage {
                display: block;
                margin-top: 12px;
                padding: 10px 12px;
                background: #fff0f0;
                border: 1px solid #e88;
                color: #922;
                border-radius: 6px;
                font-size: 0.9em;
                min-height: 1em;
            }
            .form-hint {
                font-size: 0.8em;
                color: #888;
                margin-top: -4px;
                margin-bottom: 10px;
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar (consistent duplicated pattern) -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>

            <div class="content">
                <div class="auth-header">
                    <h2>Create Your Account</h2>
                    <div style="font-size:0.9em;color:#666;">Join the movement. Propose, amend, and vote on the platform that represents you.</div>
                </div>

                <div class="auth-card">
                    <div class="auth-intro">One account gives you full access to drafting policies, amending the platform, and participating in weekly votes.</div>

                    <label for="email">Email Address</label>
                    <input type="email" id="email" placeholder="you@example.com" autocomplete="email">

                    <label for="password">Password</label>
                    <input type="password" id="password" placeholder="Create a strong password" autocomplete="new-password">

                    <label for="confirmPassword">Confirm Password</label>
                    <input type="password" id="confirmPassword" placeholder="Re-enter your password" autocomplete="new-password">
                    <div class="form-hint">Passwords must match. We use secure Firebase authentication.</div>

                    <button id="registerButton" class="btn-primary">Join The Internet Party</button>

                    <div id="errorMessage"></div>

                    <div class="auth-links">
                        Already have an account? <a href="{{ url_for('login') }}">Sign in instead →</a>
                    </div>
                </div>
            </div>

            <script src="{{ url_for('static', filename='js/register.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user)