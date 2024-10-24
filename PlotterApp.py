from flask import Flask, render_template_string, send_file, url_for, redirect
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import os
import numpy as np

import IndexPage
import NotFoundPage

app = Flask(__name__)
DATA_FOLDER = "/data/"
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
    ax.set_title(f'{state_initial.upper()} Presidency Delta Change')
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

@app.route('/robots.txt')
def robots_txt():
    return "fuck off"
    
@app.route('/')
def index():
    htmlString = IndexPage.render()
    return htmlString

@app.route('/monitor')
@app.route('/monitor/<state>')
def monitor(state='ga'):
    if(not isValidStateInitial(state)):
        return NotFoundPage.render()
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