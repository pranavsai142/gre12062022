from datetime import datetime, timezone

class Amendment:
    DRAFT = "draft"
    CANIDATE = "canidate"
    OFFICIAL = "official"
    EMPTY_STRING = "Empty"
    
#     def __init__(self, amendmentId, userId, amendmentType, amendmentTitle, amendmentDescription):
#         self.amendmentId = amendmentId
#         self.userId = userId
#         self.amendmentType = amendmentType
#         self.amendmentTitle = amendmentTitle
#         self.amendmentDescription = amendmentDescription

# Use .get() for a reason. Returns None, not an error
# https://stackoverflow.com/questions/6130768/return-a-default-value-if-a-dictionary-key-is-not-available
    def __init__(self, amendmentId, amendmentData):
        self.amendmentId = amendmentId
        self.userId = amendmentData.get("userId")
        self.policyId = amendmentData.get("policyId")
        self.amendmentType = amendmentData.get("type")
        self.amendmentTitle = amendmentData.get("title")
        self.amendmentDescription = amendmentData.get("description")
        self.createdTimestamp = amendmentData.get("created")
        self.updatedTimestamp = amendmentData.get("updated")
        self.submittedTimestamp = amendmentData.get("submitted")
    
    def getType(self):
        return self.amendmentType
        
    def getTitle(self):
        if(len(self.amendmentTitle) > 0):
            return self.amendmentTitle
        else:
            return Amendment.EMPTY_STRING
        
    def getDescription(self):
        if(len(self.amendmentDescription) > 0):
            return self.amendmentDescription
        else:
            return Amendment.EMPTY_STRING
        
    def getId(self):
        return self.amendmentId
    
    def getUserId(self):
        return self.userId
        
    def getPolicyId(self):
        return self.policyId
        
    def getCreatedDate(self):
        return datetime.fromtimestamp(self.createdTimestamp, timezone.utc).strftime("%m/%d/%y %H:%M:%S %Z")
        
    def getUpdatedDate(self):
        return datetime.fromtimestamp(self.updatedTimestamp, timezone.utc).strftime("%m/%d/%y %H:%M:%S %Z")
        
    def validateForUpdate(self, userId):
#     Validate that a amendment can be submitted
#         if(userId == None):
#             raise ValueError("Can't save amendment. User not logged in.")
        if(self.amendmentType == Amendment.DRAFT and self.userId == userId):
#         If validated for submission, set submitted timestamp and amendmentType to canidate
            self.updatedTimestamp = datetime.now().timestamp()
            return True
        else:
            return False
            
    def validateForSubmission(self, userId):
#     Validate that a amendment can be submitted
#         if(userId == None):
#             raise ValueError("Can't save amendment. User not logged in.")
        if(self.amendmentType == Amendment.DRAFT and self.userId == userId):
#         If validated for submission, set submitted timestamp and amendmentType to canidate
            self.submittedTimestamp = datetime.now().timestamp()
            self.amendmentType = Amendment.CANIDATE
            return True
        else:
            return False
    
    def validateForBallot(self):
#     Validate that amendment is an eligible canidate and has a valid user
        if(self.amendmentType == Amendment.CANIDATE and self.userId != "0"):
            return True
        else:
            return False
            
    def toDictionary(self):
        value = {}
        value["userId"] = self.userId
        value["policyId"] = self.policyId
        value["type"] = self.amendmentType
        value["title"] = self.amendmentTitle
        value["description"] = self.amendmentDescription
        value["created"] = self.createdTimestamp
        value["updated"] = self.updatedTimestamp
        value["submitted"] = self.submittedTimestamp
        return value
        
# Generates a dictionary that only contains the updates when a user saves a draft
    def toUpdateDictionary(self):
        value = {}
        value["title"] = self.amendmentTitle
        value["description"] = self.amendmentDescription
        value["updated"] = self.updatedTimestamp
        return value