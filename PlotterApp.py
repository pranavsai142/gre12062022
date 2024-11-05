from flask import Flask, render_template_string, send_file, url_for, redirect, session, request, jsonify
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import os
import numpy as np
from firebase_admin import auth, credentials, initialize_app, db
from datetime import datetime
import uuid

import IndexPage, AboutPage, AccountPage, LoginPage, NotFoundPage, PolicyPage, RegisterPage, ResetPage, VotePage, DraftPage, DetailPage, DraftAmendmentPage, DetailAmendmentPage
from Policy import Policy
from Amendment import Amendment
import User
import Database

app = Flask(__name__)
DATA_FOLDER = "/data/"
# DATA_FOLDER = "../"
# Dictionary mapping state names to their abbreviations
states = {
    "Alabama": "al",
    "Alaska": "ak",
    "Arizona": "az",
    "Arkansas": "ar",
    "California": "ca",
    "Colorado": "co",
    "Connecticut": "ct",
    "Delaware": "de",
    "Florida": "fl",
    "Georgia": "ga",
    "Hawaii": "hi",
    "Idaho": "id",
    "Illinois": "il",
    "Indiana": "in",
    "Iowa": "ia",
    "Kansas": "ks",
    "Kentucky": "ky",
    "Louisiana": "la",
    "Maine": "me",
    "Maryland": "md",
    "Massachusetts": "ma",
    "Michigan": "mi",
    "Minnesota": "mn",
    "Mississippi": "ms",
    "Missouri": "mo",
    "Montana": "mt",
    "Nebraska": "ne",
    "Nevada": "nv",
    "New Hampshire": "nh",
    "New Jersey": "nj",
    "New Mexico": "nm",
    "New York": "ny",
    "North Carolina": "nc",
    "North Dakota": "nd",
    "Ohio": "oh",
    "Oklahoma": "ok",
    "Oregon": "or",
    "Pennsylvania": "pa",
    "Rhode Island": "ri",
    "South Carolina": "sc",
    "South Dakota": "sd",
    "Tennessee": "tn",
    "Texas": "tx",
    "Utah": "ut",
    "Vermont": "vt",
    "Virginia": "va",
    "Washington": "wa",
    "West Virginia": "wv",
    "Wisconsin": "wi",
    "Wyoming": "wy"
}


def animate(i, state_initial):
    """
    Animate function to handle data collection for voting data.

    Args:
    i (int): Frame count (used in animation, but not in this context)
    state_initial (str): State initial used to construct file paths

    Returns:
    tuple: Lists of times, Democratic votes, and Republican votes
    """
    times, demVotes, repVotes = [], [], []
    folder_path = os.path.join(state_initial.lower(), '')
    folder_path = DATA_FOLDER + folder_path

    try:
        with open(os.path.join(folder_path, 'demResults.txt'), 'r') as demFile:
            demLines = demFile.read().split('\n')
        with open(os.path.join(folder_path, 'repResults.txt'), 'r') as repFile:
            repLines = repFile.read().split('\n')
    except FileNotFoundError:
        print(f"WARNING: One or more results files do not exist in {folder_path}!", flush=True)
        return times, demVotes, repVotes
    
    for line in demLines:
        if len(line) > 1:
            time, demVote = line.split(',')
            times.append(round(float(time)/86400, 2))  # Convert seconds to days
            demVotes.append(int(demVote))
    
    for line in repLines:
        if len(line) > 1:
            _, repVote = line.split(',')
            repVotes.append(int(repVote))
    
    return times, demVotes, repVotes

def generate_plot(state_initial):
    """
    Generate a plot based on the state initial.

    Args:
    state_initial (str): The state abbreviation to generate the plot for.

    Returns:
    io.BytesIO: A BytesIO object containing the plot as a PNG image.
    """
    times, demVotes, repVotes = animate(0, state_initial)
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(times, demVotes, label="Dem")
    ax.plot(times, repVotes, label="Rep")
    ax.set_title(f'{state_initial.upper()} Presidency Results')
    ax.set_xlabel('Days since election start')
    ax.set_ylabel('Vote Count')
    ax.legend()

    # Convert plot to PNG image
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    return img
    
def generate_delta(state_initial):
    """
    Generate a plot based on the state initial.

    Args:
    state_initial (str): The state abbreviation to generate the plot for.

    Returns:
    io.BytesIO: A BytesIO object containing the plot as a PNG image.
    """
    times, demVotes, repVotes = animate(0, state_initial)
    demDelta = np.diff(demVotes)
    repDelta = np.diff(repVotes)
    offsetTimes = times[1:]
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(offsetTimes, demDelta, label="Dem")
    ax.plot(offsetTimes, repDelta, label="Rep")
    ax.set_title(f'{state_initial.upper()} Presidency Vote Delta')
    ax.set_xlabel('Days since election start')
    ax.set_ylabel('Average # of New Votes')
    ax.legend()

    # Convert plot to PNG image
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    return img

def isValidStateInitial(stateInitial):
    """
    Validates if the given two-letter initial represents a valid U.S. state.

    Args:
    stateInitial (str): A string representing a state initial (e.g., 'CA', 'ny', 'Al').

    Returns:
    bool: True if the initial is valid, False otherwise.

    Raises:
    ValueError: If the input is not exactly two letters.
    """
    
    # List of valid two-letter state abbreviations
    validStates = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]
    
    # Check if the input is two letters
    if not (len(stateInitial) == 2 and stateInitial.isalpha()):
        return False
#         raise ValueError("State initial must be exactly two letters.")
    
    # Convert to uppercase for comparison
    upperInitial = stateInitial.upper()
    
    # Check if the state initial exists in our list
    return upperInitial in validStates

# Initialize Firebase Admin SDK (you need to set up your Firebase project first)
cred = credentials.Certificate(DATA_FOLDER + "theinternetparty-5b902-firebase-adminsdk-qlzzx-dbb275210d.json")

initialize_app(cred, {
    'databaseURL': 'https://theinternetparty-5b902-default-rtdb.firebaseio.com'
})
app.secret_key = os.urandom(12).hex()

@app.route('/validate-token', methods=['POST'])
def validate_token():
    data = request.get_json()
    id_token = data.get('idToken')
    
    try:
        # Verify the token and decode it
        decoded_token = auth.verify_id_token(id_token)
#         print(decoded_token, flush=True)
        
        # Start a session for the user
        session["user"] = decoded_token
#         print("session[user]:", session["user"], flush=True)
        # Redirect to another page after successful validation
        return redirect(url_for('account'))  # Replace 'dashboard' with your actual route name
    except ValueError as e:
        # Invalid token
        return jsonify({"authenticated": False, "error": str(e)}), 401

@app.route("/create-draft", methods=["POST"])
def create_draft():
    data = request.get_json()
    policyData = {}
    policyData["title"] = data.get("title")
    policyData["description"] = data.get("description")
    policyData["type"] = Policy.DRAFT
    sessionUserData = session.get("user")
    currentTimestamp = datetime.now().timestamp()
    policyData["created"] = currentTimestamp
    policyData["updated"] = currentTimestamp
    policyData["userId"] = None
    if(User.validateUser(sessionUserData)):
        policyData["userId"] = sessionUserData["uid"]
        policyId = uuid.uuid4().hex
        policy = Policy(policyId, policyData)
        if(Database.createDraftPolicy(policy)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish.."}), 500
    else:
        return jsonify({"success": False, "error": "Can't create draft policy. No user logged in."}), 500


@app.route("/update-draft", methods=["POST"])
def update_draft():
    data = request.get_json()
    policyData = {}
    policyId = data.get("id")
    policyData["title"] = data.get("title")
    policyData["description"] = data.get("description")
    policyData["type"] = Policy.DRAFT
    sessionUserData = session.get("user")
    policyData["userId"] = None
    currentTimestamp = datetime.now().timestamp()
    policyData["created"] = currentTimestamp
    policyData["updated"] = currentTimestamp
    if(User.validateUser(sessionUserData)):
        policyData["userId"] = sessionUserData["uid"]
        policy = Policy(policyId, policyData)
        print("Updating policy", policy.toDictionary())
        if(Database.updateDraftPolicy(policy)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't update draft policy. No user logged in."}), 500
        
@app.route("/remove-draft", methods=["POST"])
def remove_draft():
    data = request.get_json()
    policyId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Submitting policy", policyId)
        if(Database.removeDraftPolicy(sessionUserData, policyId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't remove draft policy. No user logged in."}), 500
        
@app.route("/submit-draft", methods=["POST"])
def submit_draft():
    data = request.get_json()
    policyId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Submitting policy", policyId)
        if(Database.submitDraftPolicy(sessionUserData, policyId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't submit draft policy. No user logged in."}), 500
        
@app.route("/create-draft-amendment", methods=["POST"])
def create_draft_amendment():
    data = request.get_json()
    amendmentData = {}
    amendmentData["policyId"] = data.get("policyId")
    amendmentData["title"] = data.get("title")
    amendmentData["description"] = data.get("description")
    amendmentData["type"] = Amendment.DRAFT
    sessionUserData = session.get("user")
    currentTimestamp = datetime.now().timestamp()
    amendmentData["created"] = currentTimestamp
    amendmentData["updated"] = currentTimestamp
    amendmentData["userId"] = None
    if(User.validateUser(sessionUserData)):
        amendmentData["userId"] = sessionUserData["uid"]
        amendmentId = uuid.uuid4().hex
        amendment = Amendment(amendmentId, amendmentData)
        if(Database.createDraftAmendment(amendment)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish.."}), 500
    else:
        return jsonify({"success": False, "error": "Can't create draft policy. No user logged in."}), 500


@app.route("/update-draft-amendment", methods=["POST"])
def update_draft_amendment():
    data = request.get_json()
    amendmentData = {}
    amendmentId = data.get("id")
    amendmentData["policyId"] = data.get("policyId")
    amendmentData["title"] = data.get("title")
    amendmentData["description"] = data.get("description")
    amendmentData["type"] = Amendment.DRAFT
    sessionUserData = session.get("user")
    currentTimestamp = datetime.now().timestamp()
    amendmentData["created"] = currentTimestamp
    amendmentData["updated"] = currentTimestamp
    amendmentData["userId"] = None
    if(User.validateUser(sessionUserData)):
        amendmentData["userId"] = sessionUserData["uid"]
        amendment = Amendment(amendmentId, amendmentData)
        if(Database.updateDraftAmendment(amendment)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish.."}), 500
    else:
        return jsonify({"success": False, "error": "Can't update draft policy. No user logged in."}), 500
        
@app.route("/remove-draft-amendment", methods=["POST"])
def remove_draft_amendment():
    data = request.get_json()
    amendmentId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Removing amendment", amendmentId)
        if(Database.removeDraftAmendment(sessionUserData, amendmentId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't remove draft policy. No user logged in."}), 500
        
        
@app.route("/submit-draft-amendment", methods=["POST"])
def submit_draft_amendment():
    data = request.get_json()
    amendmentId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Submitting amendment", amendmentId)
        if(Database.submitDraftAmendment(sessionUserData, amendmentId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't submit draft policy. No user logged in."}), 500


@app.route('/robots.txt')
def robots_txt():
    return "fuck off"
    
@app.route('/')
def index():
    htmlString = IndexPage.render(session.get("user"))
    return htmlString

@app.route('/about')
def about():
    htmlString = AboutPage.render(session.get("user"))
    return htmlString

@app.route('/account')
def account():
    htmlString = AccountPage.render(session.get("user"))
    return htmlString
    
@app.route('/login')
def login():
    htmlString = LoginPage.render(session.get("user"))
    return htmlString

@app.route('/policy')
def policy():
    htmlString = PolicyPage.render(session.get("user"))
    return htmlString
    
@app.route('/draft')
def draft():
    htmlString = DraftPage.render(session.get("user"))
    return htmlString
    
@app.route('/draft/amendment/<policyId>')
def draft_amendment(policyId):
    htmlString = DraftAmendmentPage.render(session.get("user"), policyId)
    return htmlString
    
@app.route('/detail/<policyId>')
def detail(policyId):
    htmlString = DetailPage.render(session.get("user"), policyId)
    return htmlString

@app.route('/detail/amendment/<amendmentId>')
def detail_amendment(amendmentId):
    htmlString = DetailAmendmentPage.render(session.get("user"), amendmentId)
    return htmlString

@app.route('/register')
def register():
    htmlString = RegisterPage.render(session.get("user"))
    return htmlString

@app.route('/reset')
def reset():
    htmlString = ResetPage.render(session.get("user"))
    return htmlString

@app.route('/vote')
def vote():
    htmlString = VotePage.render(session.get("user"))
    return htmlString
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/monitor')
@app.route('/monitor/<state>')
def monitor(state='ga'):
    if(not isValidStateInitial(state)):
        return NotFoundPage.render(session.get("user"))
    """
    Render the landing page with the plot based on the state from the URL,
    including a list of all states for navigation.

    Args:
    state (str): The state abbreviation from the URL, default to 'ga' if not provided.

    Returns:
    str: Rendered HTML string with the plot image tag and a state navigation list.
    """
    # Dynamically generate the src for the image based on the state
    plot_src = f"/plot/{state.lower()}"
    delta_src = f"/delta/{state.lower()}"
    # Generate HTML for the state links
    state_links = '<ul>\n'
    for full_state, abbr in states.items():
        state_links += f'<li><a href="{url_for("monitor", state=abbr)}">{full_state}</a></li>\n'
    state_links += '</ul>'

    return render_template_string('''
        <!doctype html>
        <title>{{ state.upper() }} Timeseries</title>
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
        </style>
        <body>
            <h1>{{ state.upper() }} Timeseries (updates every 10 min)</h1>
            <img src="{{ plot_src }}" />
            <img src="{{ delta_src }}" />
            <h2>Select Another State:</h2>
            {{ state_links|safe }}
            <footer>
                <p class="footer-text">Brought to you by <a href="{{ url_for('index') }}"><span>The Internet Party</span></a></p>
                <p class="footer-text">Powered by <span>Grok</span></p>
            </footer>
        </body>
    ''', state=state, plot_src=plot_src, delta_src=delta_src, state_links=state_links)

@app.route('/plot/<state>')
def plot(state):
    """
    Route to serve the plot image for a given state.

    Args:
    state (str): The state abbreviation to fetch data for.

    Returns:
    Response: A Flask response object containing the plot image.
    """
    img = generate_plot(state.lower())
    return send_file(img, mimetype='image/png')
    
@app.route('/delta/<state>')
def delta(state):
    """
    Route to serve the delta image for a given state.

    Args:
    state (str): The state abbreviation to fetch data for.

    Returns:
    Response: A Flask response object containing the plot image.
    """
    img = generate_delta(state.lower())
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0")