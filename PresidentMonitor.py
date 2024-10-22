import os
import time
import datetime
import requests
import matplotlib.pyplot as plt
import argparse
import sys
import os
import random

def parseArguments():
    """
    Parse command-line arguments.
    
    Returns:
    argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Framework for a Python script with command-line arguments.")
    
    # Example argument
    parser.add_argument("-s", "--states", type=str, help="States to monitor")
    
    # You can add more arguments here as needed
    
    return parser.parse_args()

def entryPoint():
    """
    Entry point of the script. Handles setup and teardown.
    """
    try:
        args = parseArguments()
        main(args)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def ensureFolderExists(folderPath):
    """
    Ensures the specified folder exists, creating it if it does not.

    Args:
    folderPath (str): The path to the folder.

    Returns:
    None
    """
    # Check if the folder exists
    if not os.path.exists(folderPath):
        # If it doesn't exist, create it
        os.makedirs(folderPath)
        print(f"Folder created at {folderPath}")
#     else:
#         print(f"Folder already exists at {folderPath}")

# Example usage

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
        raise ValueError("State initial must be exactly two letters.")
    
    # Convert to uppercase for comparison
    upperInitial = stateInitial.upper()
    
    # Check if the state initial exists in our list
    return upperInitial in validStates


def parseCanidateVotesABC(canidateData):
#     print(canidateData)
    votesStartIndex = canidateData.find(">", canidateData.rfind("ResultsTable__reactive")) + 1
    votesEndIndex = canidateData.find("<", votesStartIndex)
    canidateVotesStr = canidateData[votesStartIndex: votesEndIndex]
    canidateVotes = int(canidateVotesStr.replace(",", ""))
    return canidateVotes
    
def parseCanidateVotesReuters(canidateData):
	votesStartIndex = canidateData.find(">", canidateData.find("cand-votes")) + 1
	votesEndIndex = canidateData.find("<", votesStartIndex)
	canidateVotesStr = canidateData[votesStartIndex: votesEndIndex]
	canidateVotes = int(canidateVotesStr.replace(",", ""))
	return canidateVotes
	
def getVotesReuters(url_data, party):
	searchString = ""
	if(party == "democrat"):
		searchString = "</div>\n            Raphael Warnock"
	elif(party == "republican"):
		searchString = "</div>\n            Herschel Walker"
	searchIndexStart = url_data.find(searchString)
	searchIndexEnd = url_data.find("</tr>", searchIndexStart)
	canidateData = url_data[searchIndexStart: searchIndexEnd]
	votes = parseCanidateVotesReuters(canidateData)
	return votes
	
def getVotesABC(url_data, party):
	searchString = ""
	if(party == "democrat"):
		searchString = "ResultsTable__row--democrats"
	elif(party == "republican"):
		searchString = "ResultsTable__row--republicans"
	searchIndexStart = url_data.find(searchString)
	searchIndexEnd = url_data.find("</tr>", searchIndexStart)
# 	print(searchIndexEnd)
	canidateData = url_data[searchIndexStart: searchIndexEnd]
	votes = parseCanidateVotesABC(canidateData)
	return votes

electionStart = datetime.datetime(2024, 11, 5)


def writeResultsData(url_data):
    resultsFile = open("results.txt", "w")
    resultsFile.write(url_data)

def main(args):
    STATES = []
    if args.states:
        statesArgs = args.states.split(",")
        for state in statesArgs:
            if(isValidStateInitial(state)):
                STATES.append(state.lower())
                ensureFolderExists(state.lower())
    while(True):
        for STATE in STATES:
            print("Reading state: " + STATE, flush=True)
            ensureFolderExists(STATE)
            timedelta = (datetime.datetime.now() - electionStart)
        # 	url = "https://www.reuters.com/graphics/USA-ELECTION/RESULTS/dwvkdgzdqpm/georgia/"
        # 	url_data = requests.get(url).text
            url = "https://abcnews.go.com/widgets/generalstateresults?chamber=president&stateAbbrev=" + STATE + "&year=2020"
            url_data = requests.get(url).text
        # 	url_data = open('results.txt','r').read()
            demVotes = getVotesABC(url_data, "democrat")
            repVotes = getVotesABC(url_data, "republican")
            demFile = open(STATE + "/demResults.txt", "a")
            demFile.write(str(timedelta.total_seconds()) + "," + str(demVotes) + "\n")
            demFile.close()
            repFile = open(STATE + "/repResults.txt", "a")
            repFile.write(str(timedelta.total_seconds()) + "," + str(repVotes) + "\n")
            repFile.close()
            print("Writing to files state, delta, dem, rep:", STATE, timedelta.total_seconds(), demVotes, repVotes, flush=True)
            print()
            time.sleep(random.randint(40, 60))
        time.sleep(600)
        
if __name__ == "__main__":
    entryPoint()