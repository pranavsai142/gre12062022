from flask import Flask, render_template_string, send_file
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import os

app = Flask(__name__)

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

    try:
        with open(os.path.join(folder_path, 'demResults.txt'), 'r') as demFile:
            demLines = demFile.read().split('\n')
        with open(os.path.join(folder_path, 'repResults.txt'), 'r') as repFile:
            repLines = repFile.read().split('\n')
    except FileNotFoundError:
        print(f"WARNING: One or more results files do not exist in {folder_path}!")
        return times, demVotes, repVotes
    
    for line in demLines:
        if len(line) > 1:
            time, demVote = line.split(',')
            times.append(float(time)/86400)  # Convert seconds to days
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
    ax.set_title(f'{state_initial.upper()} Runoff Results')
    ax.set_xlabel('Days since election start')
    ax.set_ylabel('Vote Count')
    ax.legend()

    # Convert plot to PNG image
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    return img

@app.route('/')
@app.route('/<state>')
def index(state='ga'):
    """
    Render the landing page with the plot based on the state from the URL.

    Args:
    state (str): The state abbreviation from the URL, default to 'ga' if not provided.

    Returns:
    str: Rendered HTML string with the plot image tag.
    """
    # Dynamically generate the src for the image based on the state
    plot_src = f"/plot/{state.lower()}"
    return render_template_string('''
        <!doctype html>
        <title>{{ state.upper() }} Runoff Results</title>
        <body>
            <h1>{{ state.upper() }} Runoff Results</h1>
            <img src="{{ plot_src }}" />
        </body>
    ''', state=state, plot_src=plot_src)

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

if __name__ == '__main__':
    app.run(debug=True)