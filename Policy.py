from datetime import datetime, timezone

class Policy:
    DRAFT = "draft"
    CANIDATE = "canidate"
    OFFICIAL = "official"
    
#     def __init__(self, policyId, userId, policyType, policyTitle, policyDescription):
#         self.policyId = policyId
#         self.userId = userId
#         self.policyType = policyType
#         self.policyTitle = policyTitle
#         self.policyDescription = policyDescription

# Use .get() for a reason. Returns None, not an error
# https://stackoverflow.com/questions/6130768/return-a-default-value-if-a-dictionary-key-is-not-available
    def __init__(self, policyId, policyData):
        self.policyId = policyId
        self.userId = policyData.get("userId")
        self.policyType = policyData.get("type")
        self.policyTitle = policyData.get("title")
        self.policyDescription = policyData.get("description")
        self.createdTimestamp = policyData.get("created")
        self.updatedTimestamp = policyData.get("updated")
        self.submittedTimestamp = policyData.get("submitted")
    
    def getTitle(self):
        return self.policyTitle
        
    def getDescription(self):
        return self.policyDescription
        
    def getId(self):
        return self.policyId
    
    def getUserId(self):
        return self.userId
        
    def getCreatedDate(self):
        return datetime.fromtimestamp(self.createdTimestamp, timezone.utc).strftime("%m/%d/%y %H:%M:%S %Z")
        
    def getUpdatedDate(self):
        return datetime.fromtimestamp(self.updatedTimestamp, timezone.utc).strftime("%m/%d/%y %H:%M:%S %Z")
        
            
    def validateForSubmission(self, userId):
#     Validate that a policy can be submitted
#         if(userId == None):
#             raise ValueError("Can't save policy. User not logged in.")
        if(self.policyType == Policy.DRAFT and self.userId == userId):
#         If validated for submission, set submitted timestamp and policyType to canidate
            self.submittedTimestamp = datetime.now().timestamp()
            self.policyType = Policy.CANIDATE
            return True
        else:
            return False
    
    def validateForBallot(self):
#     Validate that policy is an eligible canidate and has a valid user
        if(self.policyType == Policy.CANIDATE and self.userId != "0"):
            return True
        else:
            return False
            
    def toDictionary(self):
        value = {}
        value["userId"] = self.userId
        value["type"] = self.policyType
        value["title"] = self.policyTitle
        value["description"] = self.policyDescription
        value["created"] = self.createdTimestamp
        value["updated"] = self.updatedTimestamp
        value["submitted"] = self.submittedTimestamp
        return value