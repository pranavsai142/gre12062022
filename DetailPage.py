from flask import Flask, render_template_string, redirect, url_for
import User
import Database
from Policy import Policy

# This page is for showing a view of all the properties of any type of policy.
# This page will also house functionality for policy operations
# Nones
# Center draft Form on screen. Thanks grok. Its the margin thing
            #draftForm {
#                 max-width: 600px; /* Or whatever max-width you want */
#                 margin: 0 auto;  /* Centers the form if it's narrower than its container */
#             }
# More grok beauty tips

# /* 
#             #draftForm button {
#                 flex: 1;
#                 margin: 0 5px;
#                 padding: 10px 20px;
#                 border: none;
#                 cursor: pointer;
#                 background-color: #4CAF50;
#                 color: white;
#             }
#  */
# 
# /* 
#             #draftForm button:hover {
#                 background-color: #45a049;
#             }
# 
#             #draftForm button[type="submit"][value="submit"] {
#                 background-color: #008CBA;
#             }
# 
#             #draftForm button[type="submit"][value="submit"]:hover {
#                 background-color: #0077a8;
#             }
#  */


def render(user, policyId):
    
    if(not User.validateUser(user)):
        user = None
    policy = Database.getPolicy(user, policyId)
    body = ""
#     if(policy != None):
#         body += policy.getTitle()
#         body += '''
#             <div class="content">
#                 <form id="draftForm">
#                     <label for="title">Title:</label>
#                     <input type="text" id="title" value="{{ policy.getTitle() }}"><br><br>
#     
#                     <label for="description">Description:</label>
#                     <textarea id="description">{{ policy.policyDescription }}</textarea><br><br>
#     
#                     <button type="submit">Submit Draft</button>
#                 </form>
#             </div>
#         '''
        
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
            {% if policy %}
                {% if policy.policyType == "draft" %}
                        <h2>Draft Policy Details</h2>
                {% endif %}
            {% else %}
                <h2>Policy Details</h2>
            {% endif %}
            {% if policy %}
                    <div class="content">
                        <label for="policyId">Policy Id:</label>
                        <span id="policyId">{{ policy.getId() }}</span><br>
                        <span>Created: {{ policy.getCreatedDate() }}</span><br>
                        <span>Updated: {{ policy.getUpdatedDate() }}</span><br><br>
                        {% if policy.policyType == "draft" %}
                            <form id="draftForm">
                                <label for="title">Title:</label><br>
                                <input type="text" id="title" value="{{ policy.getTitle() }}"><br><br>

                                <label for="description">Description:</label><br>
                                <textarea id="description">{{ policy.getDescription() }}</textarea><br><br>

                                <div class="button-group">
                                    <button type="button" id="saveDraft">Save Draft</button>
                                    <button type="button" id="removeDraft">Remove Draft</button>
                                    <button type="button" id="submitDraft">Submit Draft</button>
                                </div>
                            </form>
                        {% elif policy.policyType == "canidate" %}
                            <div class="canidate-list">
                                <span>Title: {{ policy.getTitle() }}</span><br>
                                <span>Type: {{ policy.getType() }}</span><br>
                                <pre><code>{{ policy.getDescription() }}</code></pre><br>
                                
                                <a href="{{ url_for('draft_amendment', policyId=policy.getId()) }}">Draft Amendment</a>
                            </div>
                        {% elif policy.policyType == "official" %}
                            <div class="official-list">
                                <span>Title: {{ policy.getTitle() }}</span><br><br>
                                <span>Type: {{ policy.getType() }}</span><br><br>
                                <pre><code>{{ policy.getDescription() }}</code></pre><br><br>
                            </div>
                        {% endif %}
                    </div>
            {% else %}
                <div class="content">
                    <p>Policy not found or not logged in.</p>
                </div>
            {% endif %}
            <script src="{{ url_for('static', filename='js/detail.js') }}"></script>
            {% if user %}
                <br><br><a href="{{ url_for('logout') }}">logout</a>
            {% endif %}
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, policy=policy)