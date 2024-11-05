import os
import time
import datetime
import requests
import matplotlib.pyplot as plt
import argparse
import sys
import os
import random
import json

import keystrokeDriver

DATA_FOLDER = "/data/"
# DATA_FOLDER = "../"
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


def ensureJsonExists(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        # If the file does not exist, create it with an empty dictionary
        with open(file_path, 'w') as file:
            json.dump({}, file)
    

def append_arrays_to_json(file_path, new_data):
    """
    Recursively appends arrays from a dictionary to the corresponding arrays in an existing JSON file,
    handling nested structures.

    :param file_path: Path to the JSON file to be modified.
    :param new_data: Dictionary potentially containing nested structures where values to append are arrays.
    :return: None
    """
    try:
        with open(file_path, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    def recursive_merge(current_existing, current_new):
        for key, value in current_new.items():
            if isinstance(value, list):
                if key in current_existing and isinstance(current_existing[key], list):
                    current_existing[key].extend(value)
                else:
                    current_existing[key] = value
            elif isinstance(value, dict):
                if key not in current_existing or not isinstance(current_existing[key], dict):
                    current_existing[key] = {}
                recursive_merge(current_existing[key], value)
            else:
                current_existing[key] = value

    recursive_merge(existing_data, new_data)

    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

# Example usage:
# new_dict = {"array_key1": ["value3", "value4"], "array_key2": ["value5", "value6"]}
# append_arrays_to_json('data.json', new_dict)

# Example usage:
# new_dict = {"key1": "value1", "key2": "value2"}
# append_to_json('data.json', new_dict)
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
                ensureFolderExists(DATA_FOLDER + state.lower())
    while(True):
        for STATE in STATES:
            print("Reading state: " + STATE, flush=True)
            ensureFolderExists(DATA_FOLDER + STATE)
            timedelta = (datetime.datetime.now() - electionStart)
        # 	url = "https://www.reuters.com/graphics/USA-ELECTION/RESULTS/dwvkdgzdqpm/georgia/"
        # 	url_data = requests.get(url).text
            url = "https://abcnews.go.com/widgets/generalstateresults?chamber=president&stateAbbrev=" + STATE + "&year=2024"
            url_data = requests.get(url).text
        # 	url_data = open('results.txt','r').read()
            demVotes = getVotesABC(url_data, "democrat")
            repVotes = getVotesABC(url_data, "republican")
            demFile = open(DATA_FOLDER + STATE + "/demResults.txt", "a")
            demFile.write(str(timedelta.total_seconds()) + "," + str(demVotes) + "\n")
            demFile.close()
            repFile = open(DATA_FOLDER + STATE + "/repResults.txt", "a")
            repFile.write(str(timedelta.total_seconds()) + "," + str(repVotes) + "\n")
            repFile.close()
            print("Writing to files state, delta, dem, rep:", STATE, timedelta.total_seconds(), demVotes, repVotes, flush=True)
            countyVoteData = keystrokeDriver.readCountyVotes(STATE)
            countyFile = DATA_FOLDER + STATE + "/countyResults.json"
            append_arrays_to_json(countyFile, countyVoteData)
            
            time.sleep(random.randint(40, 60))
        time.sleep(20)
        
if __name__ == "__main__":
    entryPoint()