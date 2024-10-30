from flask import Flask, render_template_string
import User
import Database

def render(user):
    if(not User.validateUser(user)):
        user = None
#     Instaed of a conditonal inside the HTML, do a conditional outside the 
#   render string and assign to a varaible that always gets displayed
    if user is not None:
        body = "draft policy: submission user " + user["email"]
        drafts = Database.getDraftPolicies(user["uid"])
#         for policy in policies:
#             body += policy.getTitle()
    else:
        body = 'Not logged in'
        drafts = []
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
                padding: 20px;
                display: flex;
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
            .draft-list {
                /* Position on the right side */
                order: 2;  /* This will place it after other content in flexbox */
                width: 200px;
                padding-left: 20px;
                border-left: 1px solid #ccc;
                margin-left: 20px;
                overflow-y: auto;  /* Allows scrolling if there are too many drafts */
            }

            .draft-item {
                margin-bottom: 10px;
            }

            .draft-item a {
                text-decoration: none;
                color: #333;
                display: block;
                padding: 5px;
                border-radius: 4px;
            }

            .draft-item a:hover {
                background-color: #f0f0f0;
                text-decoration: underline;
            }
            @media (max-width: 768px) {
                .content {
                    flex-direction: column;
                }
                .draft-list {
                    order: 0;  /* Reverts back to normal order for smaller screens */
                    width: 100%;
                    padding-left: 0;
                    border-left: none

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
            <h2>Draft</h2>
            {{ body }}
            <div class="content">
                <div class="draft-list">
                    {% for draft in drafts %}
                        <div class="draft-item">
                            <a href="{{ url_for('detail', policyId=draft.policyId) }}">{{ draft.policyTitle }}</a>
                        </div>
                    {% endfor %}
                </div>
                <form id="draftForm">
                    <label for="title">Title:</label><br>
                    <input type="text" id="title" required><br><br>
        
                    <label for="description">Description:</label><br>
                    <textarea id="description" required></textarea><br><br>
        
                    <button type="submit">Save Draft</button>
                </form>
            </div>
            <script src="{{ url_for('static', filename='js/detail.js') }}"></script>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, body=body, drafts=drafts)