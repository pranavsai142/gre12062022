from firebase_admin import db

from Policy import Policy
from Amendment import Amendment
    
    
# Get a singluar policy functions
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
  
  
  
# Get a singluar policy functions
def getDraftAmendment(userId, amendmentId):
    ref = db.reference("amendment/draft/" + amendmentId)
    amendmentData = ref.get()
    if(amendmentData != None):
#      Ensure draft polict that is being retrieved (which is private to user), is being retrieved by the user currently logged in
        if(userId == amendmentData["userId"]):
            return Amendment(amendmentId, amendmentData)
    return None
    
def getCanidateAmendment(amendmentId):
    ref = db.reference("amendment/canidate/" + amendmentId)
    amendmentData = ref.get()
    if(amendmentData != None):
        return Amendment(amendmentId, amendmentData)
    return None
    
def getOfficialAmendment(amendmentId):
    ref = db.reference("amendment/official/" + amendmentId)
    amendmentData = ref.get()
    if(amendmentData != None):
        return Amendment(amendmentId, amendmentData)
    return None
    
# This is a function to get a policy searching in all three policy types   
def getAmendment(user, amendmentId):
    if(user != None):
        potentialDraftAmendment = getDraftAmendment(user["uid"], amendmentId)
        if(potentialDraftAmendment != None):
            return potentialDraftAmendment
    potentialCanidateAmendment = getCanidateAmendment(amendmentId)
    if(potentialCanidateAmendment != None):
        return potentialCanidateAmendment
    potentialOfficialAmendment = getOfficialAmendment(amendmentId)
    if(potentialOfficialAmendment != None):
        return potentialOfficialAmendment
  
  
# Read a firebase snapshot and parse all policies. Returns list of policies in snapshot
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
   
   
   
   
# Read a firebase snapshot and parse all policies. Returns list of policies in snapshot
def readAmendmentsFromSnapshot(snapshot):
    amendments = []
#     print("snapshot retrieve policies", snapshot)
    if(snapshot != None):
        for amendment in snapshot.items():
            amendmentId = amendment[0]
            amendmentData = amendment[1]
            amendments.append(Amendment(amendmentId, amendmentData))
    return amendments
    
def getDraftAmendments(user):
    amendments = []
    if(user != None):
        userId = user["uid"]
        ref = db.reference("amendment/draft")
        snapshot = ref.order_by_child('userId').equal_to(userId).get()
#         print("query snapshot", snapshot, type(snapshot))
#         print(len(snapshot))
        print("getting draft amendments for user ", userId)
        amendments = readAmendmentsFromSnapshot(snapshot)
    return amendments
    
def getCanidateAmendments():
    ref = db.reference("amendment/canidate")
    snapshot = ref.order_by_key().get()
    amendments = readAmendmentsFromSnapshot(snapshot)
    return amendments
    
def getCanidateAmendmentsForUser(user=None):
    amendments = []
    if(user != None):
        userId = user["uid"]
        ref = db.reference("amendment/canidate")
        snapshot = ref.order_by_child('userId').equal_to(userId).get()
#         print("query snapshot", snapshot, type(snapshot))
#         print(len(snapshot))
        print("getting canidate amendments for user ", userId)
        amendments = readAmendmentsFromSnapshot(snapshot)
    return amendments

    
def getOfficialAmendments():
    ref = db.reference("amendment/official")
    snapshot = ref.order_by_key().get()
    amendments = readAmendmentsFromSnapshot(snapshot)
    return amendments
    
def getOfficialAmendmentsForUser(user):
    amendments = []
    if(user != None):
        userId = user["uid"]
        ref = db.reference("amendment/official")
        snapshot = ref.order_by_child('userId').equal_to(userId).get()
#         print("query snapshot", snapshot, type(snapshot))
#         print(len(snapshot))
        print("getting official amendments for user ", userId)
        amendments = readAmendmentsFromSnapshot(snapshot)
    return amendments
    
    
   

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
    if(updatedPolicy.validateForUpdate(policyData.get("userId"))):
#      Ensure draft polict that is being retrieved (which is private to user), is being retrieved by the user currently logged in
        ref = db.reference("policy/draft/")
        ref.child(policyId)
        updatedValue = {policyId: updatedPolicy.toUpdateDictionary()}
        ref.update(updatedValue)
        return True
    return False
    
def removeDraftPolicy(userId, policyId):
    ref = db.reference("policy/draft/" + policyId)
    ref.delete()
    return True
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
    
def createDraftAmendment(amendment):
    amendmentId = amendment.getId()
    ref = db.reference("amendment/draft")
    value = {amendmentId: amendment.toDictionary()}
    ref.update(value)
    return True
     
        
def updateDraftAmendment(updatedAmendment):
    amendmentId = updatedAmendment.getId()
    ref = db.reference("amendment/draft/" + amendmentId)
    print(amendmentId)
    amendmentData = ref.get()
#     first check if draft exists and retrieve it
    if(updatedAmendment.validateForUpdate(amendmentData.get("userId"))):
#      Ensure draft polict that is being retrieved (which is private to user), is being retrieved by the user currently logged in
        for key, value in updatedAmendment.toUpdateDictionary().items():
            ref = db.reference("amendment/draft/" + amendmentId)
            ref.update({key: value})
        return True
    return False
    
def removeDraftAmendment(userId, amendmentId):
    ref = db.reference("amendment/draft/" + amendmentId)
    ref.delete()
    return True
# submitting a draft to canidate takes an additonal user parameter
# This is to do one final check that the user logged in is the user
# who owns the policy that is getting elevated
    
def submitDraftAmendment(user, amendmentId):
    if(user != None):
        userId = user.get("uid")
        amendment = getDraftAmendment(userId, amendmentId)
        print("submit this amendment", amendment)
#         validate for submission throws a value error if no user is logged in
        if(amendment.validateForSubmission(userId)):
            print("adding policy to canidates")
            amendmentRef = db.reference("amendment")
            ref = amendmentRef.child("canidate")
            value = {amendmentId: amendment.toDictionary()}
            ref.update(value)
            if(removeDraftAmendment(userId, amendmentId)):
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