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

    def __init__(self, policyId, policyData):
        self.policyId = policyId
        self.userId = policyData["userId"]
        self.policyType = policyData["type"]
        self.policyTitle = policyData["title"]
        self.policyDescription = policyData["description"]
        self.createdTimestamp = policyData["created"]
        self.updatedTimestamp = policyData["updated"]
    
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
        
    def validateForSubmission(self):
#     Validate that a policy can be submitted
#         if(userId == None):
#             raise ValueError("Can't save policy. User not logged in.")
        if(self.policyType == Policy.DRAFT and self.userId != None):
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
        return value