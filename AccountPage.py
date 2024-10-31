from flask import Flask, render_template_string, redirect, url_for
import User
import Database

def render(user):
    if(not User.validateUser(user)):
        user = None
    if user is None:
        return redirect(url_for('login'))
    drafts = Database.getDraftPolicies(user)
    canidates = Database.getCanidatePoliciesForUser(user)
    policies = Database.getOfficialPoliciesForUser(user)
    draftAmendments = Database.getDraftAmendments(user)
    canidateAmendments = Database.getCanidateAmendmentsForUser(user)
    amendments = Database.getOfficialAmendmentsForUser(user)
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
                <a href="{{ url_for('policy') }}" class="menu-item">Policy</a>
                <a href="{{ url_for('about') }}" class="menu-item">About</a>
                <a href="{{ url_for('index') }}" class="menu-item">Home</a>
                <a href="{{ url_for('vote') }}" class="menu-item">Vote</a>
                <a href="{{ url_for('account') }}" class="menu-item.active">{{ 'Account' if user else 'Login' }}</a>
            </div>
            <div class="content">
                <h2>Account</h2>
                <div>User Info: {{ user }}</div>
                <h2>My Policies and Amendments</h2>
                <div class="draft-list">
                    <h3>Draft Policies</h3><br>
                    {% for draft in drafts %}
                        <div class="draft-item">
                            <a href="{{ url_for('detail', policyId=draft.getId()) }}">{{ draft.getTitle() }}</a>
                        </div>
                    {% endfor %}
                    <h4>Draft Amendments</h4><br>
                    {% for draftAmendment in draftAmendments %}
                        <div class="draft-item">
                            <a href="{{ url_for('detail_amendment', amendmentId=draftAmendment.getId()) }}">{{ draftAmendment.getTitle() }}</a>
                        </div>
                    {% endfor %}
                </div>
                <div class="canidate-list">
                    <h3>Canidate Policies</h3><br>
                    {% for canidate in canidates %}
                        <div class="canidate-item">
                            <a href="{{ url_for('detail', policyId=canidate.policyId) }}">{{ canidate.getTitle() }}</a>
                        </div>
                    {% endfor %}
                    <h4>Canidate Amendments</h4><br>
                    {% for canidateAmendment in canidateAmendments %}
                        <div class="canidate-item">
                            <a href="{{ url_for('detail_amendment', amendmentId=canidateAmendment.getId()) }}">{{ canidateAmendment.getTitle() }}</a>
                        </div>
                    {% endfor %}
                </div>
                <div class="official-list">
                    <h3>Official Policies</h3><br>
                    {% for policy in policies %}
                        <div class="official-item">
                            <a href="{{ url_for('detail', policyId=policy.policyId) }}">{{ policy.getTitle() }}</a>
                        </div>
                    {% endfor %}
                    <h4>Official Amendments</h4><br>
                    {% for amendment in amendments %}
                        <div class="official-item">
                            <a href="{{ url_for('detail_amendment', amendmentId=amendment.getId()) }}">{{ amendment.getTitle() }}</a>
                        </div>
                    {% endfor %}
                </div>
            </div>
            <a href="{{ url_for('logout') }}">logout</a>
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', user=user, drafts=drafts, canidates=canidates, policies=policies, draftAmendments=draftAmendments, canidateAmendments=canidateAmendments, amendments=amendments)