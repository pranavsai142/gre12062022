import os
import time
import datetime
import requests
import matplotlib.pyplot as plt

def parseCanidateVotesABC(canidateData):
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
		searchString = "ElectionsTable__Row ResultsTable--counting ResultsTable__row--democrats"
	elif(party == "republican"):
		searchString = "ElectionsTable__Row ResultsTable--counting ResultsTable__row--republicans"
	searchIndexStart = url_data.find(searchString)
	searchIndexEnd = url_data.find("</tr>", searchIndexStart)
	canidateData = url_data[searchIndexStart: searchIndexEnd]
	votes = parseCanidateVotesABC(canidateData)
	return votes

electionStart = datetime.datetime(2022, 12, 6)


def writeResultsData(url_data):
    resultsFile = open("results.txt", "w")
    resultsFile.write(url_data)

while(True):
    timedelta = (datetime.datetime.now() - electionStart)
# 	url = "https://www.reuters.com/graphics/USA-ELECTION/RESULTS/dwvkdgzdqpm/georgia/"
# 	url_data = requests.get(url).text
    url = "https://abcnews.go.com/widgets/generalstateresults?chamber=senate&stateAbbrev=ga&year=2022&special=true"
    url_data = requests.get(url).text
# 	url_data = open('results.txt','r').read()
    demVotes = getVotesABC(url_data, "democrat")
    repVotes = getVotesABC(url_data, "republican")
    demFile = open("demResults.txt", "a")
    demFile.write(str(timedelta.total_seconds()) + "," + str(demVotes) + "\n")
    demFile.close()
    repFile = open("repResults.txt", "a")
    repFile.write(str(timedelta.total_seconds()) + "," + str(repVotes) + "\n")
    repFile.close()
    print(timedelta.total_seconds(), demVotes, repVotes)
    print()
    time.sleep(60)