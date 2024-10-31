from flask import Flask, render_template_string
import User
import Database

def render(user, policyId):
    if(not User.validateUser(user)):
        user = None
    policy = Database.getPolicy(user, policyId)
#     Instaed of a conditonal inside the HTML, do a conditional outside the 
#   render string and assign to a varaible that always gets displayed
    return render_template_string('''
        <!doctype html>
        <title>The Internet Party</title>
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
                max-width: 600px;
                padding: 20px;
            }
            .policy-item pre {
                white-space: pre-wrap; /* Ensures line breaks are preserved */
                word-wrap: break-word; /* Breaks long words or URLs onto a new line */
                overflow-x: auto; /* Adds a scrollbar if content exceeds width */
                background-color: #f4f4f4;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: monospace;
                width: 100%; /* Makes it take full width of its parent */
                box-sizing: border-box; /* Includes padding and border in element's total width */
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
                color: #ff6600;  /* Change this color to your preference */
                font-weight: bold;
            }

            @media (max-width: 768px) {
                .content {
                    flex-direction: column;
                }

        </style>
        <body>
            <h1>The Internet Party</h1>
            <!-- Menu bar -->
            <div class="menu-bar">
                <a href="{{ url_for('policy') }}" class="menu-item.active">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item">{{ 'Account' if user else 'Login' }}</a>
            </div>
            <h2>Draft Amendment</h2>
            <div class="content">
                {% if policy != None %}
                    <div class="policy-item">
                        <h3>Policy to Amend</h3>
                        <span id="policyId">{{ policy.getId() }}</span><br>
                        <span>Title: <a href="{{ url_for('detail', policyId=policy.getId()) }}">{{ policy.getTitle() }}</a></span><br>
                        <span>Type: {{ policy.getType() }}</span><br>
                        <pre><code>{{ policy.getDescription() }}</code></pre><br><br>
                    </div>
                    <form id="draftForm">
                        <label for="title">Title:</label><br>
                        <input type="text" id="title" value="{{ policy.getTitle() }}"><br><br>

                        <label for="description">Description:</label><br>
                        <textarea id="description">{{ policy.getDescription() }}</textarea><br><br>

                        <button type="button" id="createDraft">Create Draft</button>
                    </form>
                {% else %}
                    <span>Policy not found.</span>
                {% endif %}
            </div>
            {% if user %}
                <br><br><a href="{{ url_for('logout') }}">logout</a>
            {% endif %}
            <script src="{{ url_for('static', filename='js/draft-amendment.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, policy=policy)