from firebase_admin import db
from datetime import datetime
import os
import random
import uuid

from Policy import Policy
from Amendment import Amendment
from Vote import Vote, VOTE_YES, VOTE_NO, VOTE_ABSTAIN
from Ballot import Ballot
import User

# ============================================================================
# VOTING WINDOW HELPERS (per MetaPolicies + exact dev notes priority)
# Window = current ISO week (e.g. "2026-W17"). One immutable ballot per user per window.
# MVP: always "open" when candidate items exist. Future: strict Sunday window gating.
# ============================================================================

VOTE_YES = "yes"      # Promote / approve for official platform
VOTE_NO = "no"
VOTE_ABSTAIN = "abstain"

def getCurrentVotingWindowId():
    """Returns e.g. '2026-W17' — natural weekly bucket matching 'Weekly (on Sunday)' MetaPolicy.

    For dev / penetration testing you can force a specific window with:
        export INTERNET_PARTY_TEST_WINDOW=2026-DEV-03
    The entire site (ballot, tallies, /vote, etc.) will treat that ID as "current".
    In production this env var is never set.
    """
    forced = os.environ.get("INTERNET_PARTY_TEST_WINDOW")
    if forced:
        return forced.strip()
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"

def isVotingOpen(window_id=None):
    """MVP: always True when there are candidate items (the ballot exists).
    In production this will check Sunday 00:00–23:59 UTC etc. per the original notes.
    """
    # For the initial website fill-out we treat any week with candidates as an active voting event.
    return True
    
    
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


# ============================================================================
# VOTING / BALLOT ENGINE  (exact priority from dev notes)
# "Add ballot generation function" + "Add voting logic to tabulate ballot
# and promote eligible canidate policies to official policies."
#
# Design:
# - Current ballot = all items in policy/canidate/* + amendment/canidate/*
# - Window = ISO week (e.g. "2026-W17") → one immutable vote per user per window
# - Storage (new, additive, audit-friendly):
#     voting/{windowId}/
#         participation/{userId} : { "voted_at": ts, "email": "..." }
#         votes/{userId}         : { "choices": { "policy-xxx": "yes", ... }, "submitted_at": ts }
# - All mutating calls go through User.validateUser + re-check live candidates.
# - Promotion (tabulate + move) is manual via close window for v1 operator control.
# ============================================================================

def _makeItemKey(policyOrAmendment):
    """Consistent key for storage and UI (e.g. 'policy-abc123' or 'amendment-def456')."""
    if isinstance(policyOrAmendment, Policy):
        return f"policy-{policyOrAmendment.getId()}"
    if isinstance(policyOrAmendment, Amendment):
        return f"amendment-{policyOrAmendment.getId()}"
    return str(policyOrAmendment)


def getBallotItems():
    """Returns the live set of items that belong on the current ballot.
    This is the 'Generate a ballot items that contains all the acceptable
    candidates to be voted on. This is so anyone can see what would be on the ballot'.
    """
    policies = getCanidatePolicies()
    amendments = getCanidateAmendments()
    return policies, amendments


def getBallotForUser(user):
    """Core ballot generation for a logged-in user (notes: 'Generate a ballot for voting.
    This ballot is specific to the user and is not created if user already voted
    and if current time outside of voting block.').
    Returns a Ballot object ready for the template, or None if the user should
    not see a voting form right now.
    """
    if not user or not User.validateUser(user):
        return None

    windowId = getCurrentVotingWindowId()
    if not isVotingOpen(windowId):
        return None

    if hasUserVotedInWindow(user["uid"], windowId):
        # User already voted — return a read-only Ballot with their choices so the page can show "you voted X"
        policies, amendments = getBallotItems()
        userVotes = getUserVotesInWindow(user["uid"], windowId)
        return Ballot(windowId, policies, amendments, userId=user["uid"], userChoices=userVotes)

    policies, amendments = getBallotItems()
    if not policies and not amendments:
        return None  # nothing to vote on yet

    return Ballot(windowId, policies, amendments, userId=user["uid"])


def hasUserVotedInWindow(userId, windowId):
    """Returns True if a participation record exists for this user+window."""
    ref = db.reference(f"voting/{windowId}/participation/{userId}")
    return ref.get() is not None


def getUserVotesInWindow(userId, windowId):
    """Returns the choices dict the user previously cast (or empty dict)."""
    ref = db.reference(f"voting/{windowId}/votes/{userId}")
    data = ref.get()
    if data and isinstance(data, dict):
        return data.get("choices", {})
    return {}


def recordUserBallot(user, windowId, choicesDict):
    """The setVote / submitBallot implementation.

    - Verifies user is valid and has not already voted this window.
    - Re-validates every item in choicesDict is still a live canidate (integrity).
    - Writes participation record + full vote record (the 'dictionary with the user id and voting status').
    - Returns (success: bool, message: str)
    """
    if user is None:
        return False, "No user logged in."

    userId = user.get("uid")
    email = user.get("email", "unknown")

    if not User.validateUser(user):
        return False, "Session expired. Please log in again."

    if not isVotingOpen(windowId):
        return False, "Voting window is closed."

    if hasUserVotedInWindow(userId, windowId):
        return False, "You have already cast a ballot for this voting window. Thank you."

    # Re-validate the submitted choices against the *live* candidate set (security)
    livePolicies, liveAmendments = getBallotItems()
    liveKeys = { _makeItemKey(p) for p in livePolicies } | { _makeItemKey(a) for a in liveAmendments }

    cleanedChoices = {}
    for itemKey, choice in (choicesDict or {}).items():
        if itemKey in liveKeys and choice in (VOTE_YES, VOTE_NO, VOTE_ABSTAIN):
            cleanedChoices[itemKey] = choice

    if not cleanedChoices:
        return False, "No valid votes were submitted for current ballot items."

    now = datetime.now().timestamp()

    # 1. Record participation (the "has voted" flag)
    participationRef = db.reference(f"voting/{windowId}/participation/{userId}")
    participationRef.set({
        "voted_at": now,
        "email": email,
        "windowId": windowId,
    })

    # 2. Record the full ballot (the audit record the notes required)
    voteRef = db.reference(f"voting/{windowId}/votes/{userId}")
    voteRef.set({
        "userId": userId,
        "email": email,
        "windowId": windowId,
        "choices": cleanedChoices,
        "submitted_at": now,
    })

    print(f"Ballot recorded for user {userId} in window {windowId} ({len(cleanedChoices)} items)")
    return True, "Your ballot has been recorded. Thank you for participating in The Internet Party."


def getWindowVotes(windowId):
    """Returns list of raw vote dicts for the window (used for tallies and audits)."""
    ref = db.reference(f"voting/{windowId}/votes")
    snapshot = ref.get()
    if not snapshot:
        return []
    return list(snapshot.values()) if isinstance(snapshot, dict) else []


def getWindowTallies(windowId):
    """Computes current tallies for the window using Vote.computeTallies."""
    rawVotes = getWindowVotes(windowId)
    return Vote.computeTallies(rawVotes)


def getWindowParticipationCount(windowId):
    ref = db.reference(f"voting/{windowId}/participation")
    snap = ref.get()
    return len(snap) if snap else 0


def promoteWinnersFromWindow(windowId):
    """Tabulate + promote (the #2 priority from notes).

    For every canidate item where yes > no:
      - Copy the item (policy or amendment) into the corresponding official/ bucket
      - Set submitted/enacted timestamps
      - Remove from canidate/
    Non-winners stay in canidate/ for future windows (or could be moved to a failed/ bucket later).

    Returns dict with counts and list of promoted item keys.
    This is intentionally a manual operator action in v1 (see approved plan).
    """
    tallies = getWindowTallies(windowId)
    winners = Vote.getWinners(tallies, minYes=1)

    if not winners:
        return {"promoted": 0, "message": "No items met the promotion threshold this window."}

    promoted = []
    now = datetime.now().timestamp()

    livePolicies, liveAmendments = getBallotItems()
    policyMap = {f"policy-{p.getId()}": p for p in livePolicies}
    amendmentMap = {f"amendment-{a.getId()}": a for a in liveAmendments}

    for itemKey in winners:
        if itemKey in policyMap:
            pol = policyMap[itemKey]
            # Move to official (same pattern as submitDraftPolicy but from canidate)
            polData = pol.toDictionary()
            polData["type"] = Policy.OFFICIAL
            polData["submitted"] = now
            polData["enacted"] = now
            db.reference(f"policy/official/{pol.getId()}").set(polData)
            db.reference(f"policy/canidate/{pol.getId()}").delete()
            promoted.append(itemKey)
            print(f"Promoted policy {pol.getId()} to official from window {windowId}")

        elif itemKey in amendmentMap:
            amend = amendmentMap[itemKey]
            amendData = amend.toDictionary()
            amendData["type"] = Amendment.OFFICIAL
            amendData["submitted"] = now
            db.reference(f"amendment/official/{amend.getId()}").set(amendData)
            db.reference(f"amendment/canidate/{amend.getId()}").delete()
            promoted.append(itemKey)
            print(f"Promoted amendment {amend.getId()} to official from window {windowId}")

    return {
        "promoted": len(promoted),
        "itemKeys": promoted,
        "windowId": windowId,
        "message": f"Promoted {len(promoted)} item(s) to official platform."
    }


# Convenience re-exports (so pages can do "import Database" and get the constants)
# The real definitions live in Vote.py
pass  # constants already imported and available as Database.VOTE_YES etc. via the from-import above


# ============================================================================
# FIREBASE INIT (centralized — fixes repeated initialize_app warnings across
# tools + main app. Safe to call multiple times.)
# ============================================================================
_firebase_ready = False

def ensure_firebase_initialized():
    """Idempotent initializer. Uses the same credential path as PlotterApp.py.
    Tools and CLI should call this early. Falls back silently for snapshot demos.
    """
    global _firebase_ready
    if _firebase_ready:
        return True
    try:
        from firebase_admin import credentials, initialize_app
        import os
        DATA_FOLDER = "/Users/pranav/data/"
        SERVICE_ACCOUNT = DATA_FOLDER + "theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json"
        if os.path.exists(SERVICE_ACCOUNT):
            cred = credentials.Certificate(SERVICE_ACCOUNT)
            initialize_app(cred, {
                'databaseURL': 'https://theinternetparty-5b902-default-rtdb.firebaseio.com'
            })
            _firebase_ready = True
            return True
    except Exception as e:
        # Expected in pure-snapshot or re-init situations
        pass
    return False


# ============================================================================
# DEV TOOLS / ADMIN HELPERS (added per approved plan for agentic + admin use)
# Small, focused, safe-by-default where possible. Callers are responsible for
# firebase_admin initialization (see PlotterApp.py pattern or tool inits).
# ============================================================================

def get_all_voting_windows():
    """Return sorted list of all window IDs that have voting data (live or empty list)."""
    try:
        ref = db.reference("voting")
        snap = ref.get()
        if snap and isinstance(snap, dict):
            return sorted(snap.keys())
    except Exception as e:
        print("get_all_voting_windows warning (may be uninitialized or no data):", e)
    return []


def get_window_details(windowId):
    """Return full structure for one window: participation count, vote count, sample vote."""
    try:
        ref = db.reference(f"voting/{windowId}")
        data = ref.get() or {}
        part = data.get("participation", {}) or {}
        votes = data.get("votes", {}) or {}
        return {
            "windowId": windowId,
            "participation_count": len(part),
            "vote_count": len(votes),
            "participation": part,
            "votes": votes,
        }
    except Exception as e:
        print("get_window_details error:", e)
        return {"windowId": windowId, "error": str(e)}


def clear_window_votes(windowId, confirm=False):
    """NUCLEAR: Delete the entire voting/{windowId} subtree (participation + votes).
    Requires explicit confirm=True. Returns dict with result.
    Used ONLY by Dev Tools. Never call from public site.
    """
    if not confirm:
        return {"success": False, "message": "Refused: set confirm=True to actually delete."}
    if not windowId or "/" in str(windowId):
        return {"success": False, "message": "Invalid windowId"}
    try:
        ref = db.reference(f"voting/{windowId}")
        ref.delete()
        print(f"DEV: Cleared voting/{windowId}")
        return {"success": True, "message": f"Cleared all data for window {windowId}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def reset_window_for_retest(windowId, confirm=False):
    """Exactly what testers need: clear only the votes + participation for a window
    so you can cast fresh votes on the *same* set of candidate policies/amendments.
    The candidates themselves are untouched. Requires confirm=True.
    """
    return clear_window_votes(windowId, confirm=confirm)


def seed_test_votes(windowId, count=5, force=False):
    """Create synthetic votes for testing (agentic flows).
    Uses fake uids + random yes/no/abstain against current ballot items.
    Idempotent-ish: if force=False, skips if participation already exists for a synthetic uid.
    Returns summary.
    """
    policies, amendments = getBallotItems()
    if not policies and not amendments:
        return {"success": False, "message": "No candidate items on ballot to vote on."}

    live_keys = []
    for p in policies:
        live_keys.append(f"policy-{p.getId()}")
    for a in amendments:
        live_keys.append(f"amendment-{a.getId()}")

    if not live_keys:
        return {"success": False, "message": "No valid item keys."}

    created = 0
    for i in range(count):
        fake_uid = f"DEVTEST-{windowId}-{i:03d}"
        if not force:
            if hasUserVotedInWindow(fake_uid, windowId):
                continue
        choices = {}
        for k in live_keys:
            choices[k] = random.choice([VOTE_YES, VOTE_NO, VOTE_ABSTAIN])
        now = datetime.now().timestamp()
        email = f"devtest{i}@example.com"
        # write
        db.reference(f"voting/{windowId}/participation/{fake_uid}").set({
            "voted_at": now, "email": email, "windowId": windowId, "synthetic": True
        })
        db.reference(f"voting/{windowId}/votes/{fake_uid}").set({
            "userId": fake_uid, "email": email, "windowId": windowId,
            "choices": choices, "submitted_at": now, "synthetic": True
        })
        created += 1

    return {
        "success": True,
        "created": created,
        "windowId": windowId,
        "message": f"Seeded {created} synthetic vote(s) for {windowId}"
    }


def get_policies_summary():
    """Quick counts across statuses for dashboards."""
    try:
        return {
            "draft": len(db.reference("policy/draft").get() or {}),
            "canidate": len(db.reference("policy/canidate").get() or {}),
            "official": len(db.reference("policy/official").get() or {}),
        }
    except Exception:
        return {"draft": 0, "canidate": 0, "official": 0}