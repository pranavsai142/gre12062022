from firebase_admin import db

from Policy import Policy
    
def getDraftPolicy(userId, policyId):
    ref = db.reference("policy/draft/" + policyId)
    policyData = ref.get()
    if(policyData != None):
#      Ensure draft polict that is being retrieved (which is private to user), is being retrieved by the user currently logged in
        if(userId == policyData["userId"]):
            return Policy(policyId, policyData)
    return None
    
def removeDraftPolicy(userId, policyId):
    ref = db.reference("policy/draft/" + policyId)
    ref.delete()
    return True
    
def getCanidatePolicy(policyId):
    ref = db.reference("policy/canidate/" + policyId)
    policyData = ref.get()
    if(policyData != None):
        return Policy(policyId, policyData)
    return None
    
def getOfficialPolicy(policyId):
    ref = db.reference("policy/official/" + policyId)
    policyData = ref.get()
    if(policyData != None):
        return Policy(policyId, policyData)
    return None
    
# This is a function to get a policy searching in all three policy types   
def getPolicy(user, policyId):
    if(user != None):
        potentialDraftPolicy = getDraftPolicy(user["uid"], policyId)
        if(potentialDraftPolicy != None):
            return potentialDraftPolicy
    potentialCanidatePolicy = getCanidatePolicy(policyId)
    if(potentialCanidatePolicy != None):
        return potentialCanidatePolicy
    potentialOfficialPolicy = getOfficialPolicy(policyId)
    if(potentialOfficialPolicy != None):
        return potentialOfficialPolicy
    
def readPoliciesFromSnapshot(snapshot):
    policies = []
#     print("snapshot retrieve policies", snapshot)
    if(snapshot != None):
        for policy in snapshot.items():
            policyId = policy[0]
            policyData = policy[1]
            policies.append(Policy(policyId, policyData))
    return policies
    
def getDraftPolicies(user):
    policies = []
    if(user != None):
        userId = user["uid"]
        ref = db.reference("policy/draft")
        snapshot = ref.order_by_child('userId').equal_to(userId).get()
#         print("query snapshot", snapshot, type(snapshot))
#         print(len(snapshot))
#         print("getting draft policies for user ", userId)
        policies = readPoliciesFromSnapshot(snapshot)
    return policies
    
def getCanidatePolicies():
    ref = db.reference("policy/canidate")
    snapshot = ref.order_by_key().get()
    policies = readPoliciesFromSnapshot(snapshot)
    return policies
    
def getCanidatePoliciesForUser(user=None):
    policies = []
    if(user != None):
        userId = user["uid"]
        ref = db.reference("policy/canidate")
        snapshot = ref.order_by_child('userId').equal_to(userId).get()
        print("getting canidate policies for user ", userId)
        policies = readPoliciesFromSnapshot(snapshot)
    return policies
    
def getOfficialPolicies():
    ref = db.reference("policy/official")
    snapshot = ref.order_by_key().get()
    policies = readPoliciesFromSnapshot(snapshot)
    return policies
    
def getOfficialPoliciesForUser(user):
    policies = []
    if(user != None):
        userId = user["uid"]
        ref = db.reference("policy/official")
        snapshot = ref.order_by_child('userId').equal_to(userId).get()
        print("getting official policies for user ", userId)
        policies = readPoliciesFromSnapshot(snapshot)
    return policies
   
def createDraftPolicy(policy):
    policyId = policy.getId()
    ref = db.reference("policy/draft")
    value = {policyId: policy.toDictionary()}
    ref.update(value)
    return True
     
        
def updateDraftPolicy(updatedPolicy):
    policyId = updatedPolicy.getId()
    ref = db.reference("policy/draft/" + policyId)
    print(policyId)
    policyData = ref.get()
#     first check if draft exists and retrieve it
    if(policyData != None):
#      Ensure draft polict that is being retrieved (which is private to user), is being retrieved by the user currently logged in
        if(updatedPolicy.getUserId() == policyData["userId"]):
            updatedPolicy.createdTimestamp = policyData["created"]
            ref = db.reference("policy/draft/")
            ref.child(policyId)
            updatedValue = {policyId: updatedPolicy.toDictionary()}
            ref.update(updatedValue)
            return True
    return False
    
# submitting a draft to canidate takes an additonal user parameter
# This is to do one final check that the user logged in is the user
# who owns the policy that is getting elevated
    
def submitDraftPolicy(user, policyId):
    if(user != None):
        userId = user["uid"]
        policy = getDraftPolicy(userId, policyId)
        print("submit this poliy", policy)
#         validate for submission throws a value error if no user is logged in
        if(policy.validateForSubmission(userId)):
            print("adding policy to canidates")
            policyRef = db.reference("policy")
            ref = policyRef.child("canidate")
            value = {policyId: policy.toDictionary()}
            ref.update(value)
            if(removeDraftPolicy(userId, policyId)):
#         Catch error codes and return response
                return True
    return False
    
def submitCanidatePolicy(policy):
    if(policy.validateForBallot()):
        print("Moved draft policy to canidate policy")
        policyRef = db.reference("policy")
        ref = policyRef.child("draft")
        policyId = uuid.uuid4().hex
        value = {policyId: policy.toDictionary()}
        ref.update(value)
#         Catch error codes and return response
        return True
    else:
        return False