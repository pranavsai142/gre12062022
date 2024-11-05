from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime

# Automatically download and set up the ChromeDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# countyData = '''Teller County Results
# Live results
# Updated: Nov. 5, 12:00 AM ET
# Candidate	Party	%	Votes
# 
# K. Harris
# 	
# D
# 0%
# 	
# 0
# 
# 
# 
# 
# D. Trump
# 	
# R
# 0%
# 	
# 0
# 
# 
# Expected Vote Reporting: 0% Jefferson County is north. El Paso County is east. Fremont County is south. Park County is west. Use arrow keys to move around the map.'''
# # print(countyData)

DATA_FOLDER = "/data/"
# DATA_FOLDER = "../"
electionStart = datetime(2024, 11, 5)

def state_to_number(state_code):
    # Dictionary mapping state codes to numbers
    state_numbers = {
        'AL': 1, 'AK': 2, 'AZ': 3, 'AR': 4, 'CA': 5, 'CO': 8, 'CT': 9, 'DE': 10, 'FL': 12, 'GA': 13,
        'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19, 'KS': 20, 'KY': 21, 'LA': 22, 'ME': 23, 
        'MD': 24, 'MA': 25, 'MI': 26, 'MN': 27, 'MS': 28, 'MO': 29, 'MT': 30, 'NE': 31, 'NV': 32, 
        'NH': 33, 'NJ': 34, 'NM': 35, 'NY': 36, 'NC': 37, 'ND': 38, 'OH': 39, 'OK': 40, 'OR': 41, 
        'PA': 42, 'RI': 44, 'SC': 45, 'SD': 46, 'TN': 47, 'TX': 48, 'UT': 49, 'VT': 50, 'VA': 51, 
        'WA': 53, 'WV': 54, 'WI': 55, 'WY': 56
    }
    
    # Convert the input to uppercase to make it case-insensitive
    state_code = state_code.upper()
    
    # Return the number if the state code exists, otherwise return None
    return state_numbers.get(state_code)
    
def parseCountyData(voteData, countiesRecorded, countyData):
    lines = countyData.split("\n")
    countyName = " "
    countyName = countyName.join(lines[0].split()[0:-2]).lower()
#     print(countyName)
    demVotes = int(lines[10].strip())
    repVotes = int(lines[20].strip())
    if(countiesRecorded.get(countyName) == None):
        countiesRecorded[countyName] = 1
        voteData[countyName] = {}
        voteData[countyName]["dem"] = [demVotes]
        voteData[countyName]["rep"] = [repVotes]
    else:
        countiesRecorded[countyName] += 1
    nextCounties = lines[23]
    nextCounties = nextCounties[nextCounties.find("%") + 2:].split(".")[:-2]
#     print(nextCounties)
#     print(demVotes, repVotes)
    navigateToCounty = None
    navigateToDirection = None
#     print(nextCounties)
# Deal with this edge case
# Some neighboring map features may be enclaves or otherwise unreachable from this location. Press the number key associated with the feature to go to it. 1 - Delta County. There are no map features west of here.
    minTimesVisited = 3
    for nextCounty in nextCounties:
        if(not "Some neighboring map features may be enclaves" in nextCounty and not "Press the number key associated with the feature to go to it" in nextCounty and not " - " in nextCounty):
#             Hit edge of map
            if(not "There are no" in nextCounty):
                nextCounty = nextCounty.strip()
                nextCountyName = " "
                nextCountyData = nextCounty.split(" ")
                nextCountyDirection = nextCountyData[-1]
                nextCounty = nextCountyName.join(nextCountyData[:-3]).lower()
#                 print(nextCounty)
                if(countiesRecorded.get(nextCounty) == None):
                    navigateToCounty = nextCounty
                    navigateToDirection = nextCountyDirection
                    break
                elif(countiesRecorded.get(nextCounty) < minTimesVisited):
                    navigateToCounty = nextCounty
                    navigateToDirection = nextCountyDirection
                    minTimesVisited = countiesRecorded.get(nextCounty)
#     print(navigateToCounty, navigateToDirection)
    return navigateToCounty, navigateToDirection
#     traversal(countyName, nextCounties)

    
# parseCountyData(countyData)


# quit()

def setup_driver():
    service = Service()
    options = Options()
    options.binary_location = "/data/chrome_install/opt/google/chrome/chrome" 
    driver = webdriver.Chrome(service=service, options=options)
    # options.add_argument('--headless')  # Uncomment to run in headless mode if needed
    return driver
    
def readCountyVotes(STATE):
    print("Reading counties for: " + STATE, flush=True)
    STATE_FOLDER = DATA_FOLDER + STATE
    stateNumber = state_to_number(STATE)
    stateNumber = str(stateNumber).zfill(2)
    try:
    #     Initialize the WebDriver
        driver = setup_driver()
    #     Open the webpage
        driver.get("https://abcnews.go.com/widgets/generalstateresults?chamber=president&stateAbbrev=" + STATE + "&year=2024")  # Replace with the URL you want to interact with
    
    #     Find the element you want to send keystrokes to
        element = driver.find_element(By.ID, "state-map-" + stateNumber + "-president")  # Replace with actual element ID
    
#     #     Text to simulate typing
#         text_to_type = "example text"
    
    #     Send an arrow to trigger the map
        element.send_keys(Keys.ARROW_RIGHT)
        time.sleep(0.5)  # Wait a bit for the page to update
    #     print(driver.page_source)  # Retrieve and print the current HTML
    
        # Optionally, you can send special keys like Enter
    #     element.send_keys(Keys.ENTER)
        voteData = {}
        timedelta = (datetime.now() - electionStart)
        voteData["times"] = [timedelta.total_seconds()]
        countiesRecorded = {}
        finishedTraversal = False
        while(not finishedTraversal):
    #         time.sleep(1)  # Wait for the page to update after Enter key press
            page = driver.page_source
            countyData = page[page.find("state-map-" + stateNumber + "-president-announcer") + 1:]
            countyData = countyData[countyData.find("state-map-" + stateNumber + "-president-announcer") + 1:]
            countyData = countyData[countyData.find(">") + 1:countyData.find("div>") - 2]
            navigateToCounty, navigateToDirection = parseCountyData(voteData, countiesRecorded, countyData)
            if(navigateToCounty == None and navigateToDirection == None):
                finishedTraversal = True
            else:
                if(navigateToDirection == "north"):
                    element.send_keys(Keys.ARROW_UP)
                if(navigateToDirection == "east"):
                    element.send_keys(Keys.ARROW_RIGHT)
                if(navigateToDirection == "west"):
                    element.send_keys(Keys.ARROW_LEFT)
                if(navigateToDirection == "south"):
                    element.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.3)
    #         print(countiesRecorded, navigateToCounty, navigateToDirection)
        print(voteData)
        return voteData
        
    
        
    
    finally:
        # Close the browser
        driver.quit()