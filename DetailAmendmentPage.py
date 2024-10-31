from flask import Flask, render_template_string, redirect, url_for
import User
import Database
from Amendment import Amendment

def render(user, amendmentId):
    if(not User.validateUser(user)):
        user = None
    amendment = Database.getAmendment(user, amendmentId)
    policy = None
    if(amendment != None):
        policy = Database.getPolicy(user, amendment.getPolicyId())
        
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
            pre {
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
            .button-container {
                display: flex;
                justify-content: space-between;
                width: 100%; /* Adjust as needed */
            }
            #draftForm {
                max-width: 600px;
            }

            #draftForm label, #draftForm input, #draftForm textarea {
                display: block;
                width: 100%;
                box-sizing: border-box;
            }

            .button-group {
                display: flex;
                justify-content: space-between;
                width: 100%;
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
            {% if amendment %}
                {% if amendment.amendmentType == "draft" %}
                        <h2>Draft Amendment Details</h2>
                {% endif %}
            {% else %}
                <h2>Amendment Details</h2>
            {% endif %}
            {% if amendment %}
                    <div class="content">
                        <label for="amendmentId">Amendment Id:</label>
                        <span id="amendmentId">{{ amendment.getId() }}</span><br>
                        <span>Created: {{ amendment.getCreatedDate() }}</span><br>
                        <span>Updated: {{ amendment.getUpdatedDate() }}</span><br><br>
                        {% if policy != None %}
                            <div class="official-item">
                                <h3>Policy to Amend</h3>
                                <span id="policyId">{{ policy.getId() }}</span><br>
                                <span>Title: <a href="{{ url_for('detail', policyId=policy.getId()) }}">{{ policy.getTitle() }}</a></span><br>
                                <span>Type: {{ policy.getType() }}</span><br>
                                <pre><code>{{ policy.getDescription() }}</code></pre><br><br>
                            </div>
                            {% if amendment.amendmentType == "draft" %}
                                <form id="draftForm">
                                    <label for="title">Proposed Title:</label><br>
                                    <input type="text" id="title" value="{{ amendment.getTitle() }}"><br><br>

                                    <label for="description">Proposed Description:</label><br>
                                    <textarea id="description">{{ amendment.getDescription() }}</textarea><br><br>

                                    <div class="button-group">
                                        <button type="button" id="saveDraft">Save Draft</button>
                                        <button type="button" id="removeDraft">Remove Draft</button>
                                        <button type="button" id="submitDraft">Submit Draft</button>
                                    </div>
                                </form>
                            {% elif amendment.policyType == "canidate" %}
                                <div class="canidate-item">
                                    <span>Title: {{ amendment.getTitle() }}</span><br><br>
                                    <span>Type: {{ amendment.getType() }}</span><br><br>
                                    <span>Description: {{ amendment.getDescription() }}</span><br><br>
                            
                                </form>
                            {% elif amendment.amendmentType == "official" %}
                                <div class="official-item">
                                    <span>Title: {{ amendment.getTitle() }}</span><br><br>
                                    <span>Title: {{ amendment.getDescription() }}</span><br><br>
                                    <button type="button" id="saveDraft">Save Draft</button>
                                </form>
                            {% endif %}
                        {% else %}
                            <span>Policy not found.</span>
                        {% endif %}
                    </div>
            {% else %}
                <div class="content">
                    <p>Amendment not found or not logged in.</p>
                </div>
            {% endif %}
            <script src="{{ url_for('static', filename='js/detail-amendment.js') }}"></script>
            <a href="{{ url_for('logout') }}">logout</a>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, amendment=amendment, policy=policy)