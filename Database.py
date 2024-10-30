from firebase_admin import db
import uuid

from Policy import Policy

class Database:
    def __init__(self):
        print("Initializing Database")
        
    def retrieveAllPolicies(self, snapshot):
        policies = []
        if(snapshot != None):
            for policy in snapshot.items():
                policyId = policy[0]
                policyUserId = policy[1]["userId"]
                policyType = policy[1]["type"]
                policyTitle = policy[1]["title"]
                policyDescription = policy[1]["description"]
                policies.append(Policy(policyId, policyUserId, policyType, policyTitle, policyDescription))
        return policies
        
    def getCanidatePolicies(self):
        ref = db.reference("policy/canidate")
        snapshot = ref.order_by_key().get()
        policies = self.retrieveAllPolicies(snapshot)
        return policies
        
    def submitDraftPolicy(self, policy):
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
            
    def submitCanidatePolicy(self, policy)
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