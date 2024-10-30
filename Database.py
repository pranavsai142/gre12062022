from firebase_admin import db
import uuid

from Policy import Policy
    
def getDraftPolicy(userId, policyId):
    ref = db.reference("policy/draft/" + policyId)
    policyData = ref.get()
    if(policyData != None):
#      Ensure draft polict that is being retrieved (which is private to user), is being retrieved by the user currently logged in
        if(userId == policyData["userId"]):
            return Policy(policyId, policyData)
    return None
    
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
    
def updateDraftPolicy(updatedPolicy):
    policyId = updatedPolicy.getId()
    ref = db.reference("policy/draft/" + policyId)
    print(policyId)
    policyData = ref.get()
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
    
def getAllPolicies(snapshot):
    policies = []
#     print("snapshot retrieve policies", snapshot)
    if(snapshot != None):
        for policy in snapshot.items():
            policyId = policy[0]
            policyData = policy[1]
            policies.append(Policy(policyId, policyData))
    return policies
    
def getCanidatePolicies():
    ref = db.reference("policy/canidate")
    snapshot = ref.order_by_key().get()
    policies = getAllPolicies(snapshot)
    return policies
    
def getDraftPolicies(userId):
    ref = db.reference("policy/draft")
    snapshot = ref.order_by_key().get()
    policies = getAllPolicies(snapshot)
    return policies
    
def submitDraftPolicy(policy):
#         validate for submission throws a value error if no user is logged in
    if(policy.validateForSubmission()):
        print("added policy to database")
        policyRef = db.reference("policy")
        ref = policyRef.child("draft")
        policyId = uuid.uuid4().hex
        value = {policyId: policy.toDictionary()}
        ref.update(value)
#         Catch error codes and return response
        return True
    else:
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