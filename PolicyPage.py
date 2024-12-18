from flask import Flask, render_template_string
import User
import Database

def render(user):
    if(not User.validateUser(user)):
        user = None
#     Instaed of a conditonal inside the HTML, do a conditional outside the 
#   render string and assign to a varaible that always gets displayed
        
    canidates = Database.getCanidatePolicies()
    policies = Database.getOfficialPolicies()
    canidateAmendments = Database.getCanidateAmendments()
    amendments = Database.getOfficialAmendments()
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
            <div id="content">
                <h2>Policy</h2><br>
                <span><a href="{{ url_for('draft') }}">Draft Policy</a></span>
                <div class="canidate-list">
                    <h3>Canidate Policies</h3>
                    {% for canidate in canidates %}
                        <div class="canidate-item">
                            <a href="{{ url_for('detail', policyId=canidate.policyId) }}">{{ canidate.policyTitle }}</a>
                        </div>
                    {% endfor %}
                    <h4>Canidate Amendments</h4>
                    {% for canidateAmendment in canidateAmendments %}
                        <div class="canidate-item">
                            <a href="{{ url_for('detail_amendment', amendmentId=canidateAmendment.getId()) }}">{{ canidateAmendment.getTitle() }}</a>
                        </div>
                    {% endfor %}
                </div>
                <div class="official-list">
                    <h3>Official Policies</h3>
                    {% for policy in policies %}
                        <div class="official-item">
                            <a href="{{ url_for('detail', policyId=policy.policyId) }}">{{ policy.policyTitle }}</a>
                        </div>
                    {% endfor %}
                    <h4>Official Amendments</h4>
                    {% for amendment in amendments %}
                        <div class="official-item">
                            <a href="{{ url_for('detail_amendment', amendmentId=amendment.getId()) }}">{{ amendment.getTitle() }}</a>
                        </div>
                    {% endfor %}
                </div>
            <div>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, canidates=canidates, policies=policies, canidateAmendments=canidateAmendments, amendments=amendments)