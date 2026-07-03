from flask import Flask, render_template_string, url_for
import User

def render(user):
    if(not User.validateUser(user)):
        user = None
    return render_template_string('''
        <!doctype html>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Page Not Found</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            .content {
                flex: 1;
                padding: 20px;
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
                color: #ff6600; /* A vibrant orange for Grok */
            }
            /* New styles for menu bar */
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
            .content {
                flex: 1;
                padding: 20px;
                max-width: 720px;
                margin: 0 auto;
            }
            .notfound { text-align: center; padding: 40px 20px; }

            /* Mobile notfound + consistent menu */
            @media (max-width: 768px) {
                body { font-size: 16px; }
                h1 { font-size: 1.5em; margin: 8px 0 2px 12px; }
                .content { padding: 16px; }
                .menu-bar { padding: 4px 2px; flex-wrap: wrap; }
                .menu-item {
                    margin: 3px 6px; padding: 10px 12px; font-size: 0.95em;
                    min-height: 44px; display: inline-flex; align-items: center; justify-content: center; border-radius: 4px;
                }
                .notfound { padding: 24px 12px; }
            }
        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>
            <div class="content">
                <div class="notfound">
                    <h2>Page Not Found</h2>
                    <p>The page you are looking for does not exist or has moved.</p>
                    <p><a href="{{ url_for('index') }}" style="color:#ff6600;font-weight:600;">Return to Home →</a></p>
                </div>
            </div>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user)