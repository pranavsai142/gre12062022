from datetime import datetime, timezone

# Vote choice constants (used everywhere for the ballot)
VOTE_YES = "yes"       # "Yes — Promote to Official Platform"
VOTE_NO = "no"
VOTE_ABSTAIN = "abstain"


class Vote:
    """Represents a single user's cast ballot (their complete set of choices)
    for one voting window.

    This is the persisted record of "which way each voter voted" (per original
    dev notes). Stored in RTDB under:
        voting/{windowId}/votes/{userId}

    The class follows the exact style of Policy.py / Amendment.py:
    - Constructed from a dict snapshot
    - Getters + toDictionary
    - No heavy validation here (that lives in Database.recordUserBallot)
    """

    YES = VOTE_YES
    NO = VOTE_NO
    ABSTAIN = VOTE_ABSTAIN

    def __init__(self, userId, windowId, voteData):
        """voteData is the dict stored in RTDB (or None for new)."""
        self.userId = userId
        self.windowId = windowId
        self.email = voteData.get("email") if voteData else None
        self.choices = voteData.get("choices", {}) if voteData else {}
        self.submittedAt = voteData.get("submitted_at") if voteData else None

    def getChoice(self, itemId):
        """itemId is e.g. 'policy-abc123' or the raw policyId/amendmentId."""
        return self.choices.get(itemId)

    def hasVotedOn(self, itemId):
        return itemId in self.choices

    def getSubmittedDate(self):
        if self.submittedAt:
            return datetime.fromtimestamp(self.submittedAt, timezone.utc).strftime("%m/%d/%y %H:%M:%S %Z")
        return "Not submitted"

    def toDictionary(self):
        """Exact shape stored in RTDB for audit / recount / future registered-user majority."""
        return {
            "userId": self.userId,
            "email": self.email,
            "windowId": self.windowId,
            "choices": self.choices,           # the dictionary the notes asked for
            "submitted_at": self.submittedAt,
        }

    @staticmethod
    def computeTallies(voteRecords):
        """Given a list of raw vote dicts (or Vote objects), return per-item counts.

        Returns:
            { "policy-xxx": {"yes": 3, "no": 1, "abstain": 0, "total": 4}, ... }

        This is the tabulation step before promotion. Called from Database.promoteWinnersFromWindow.
        """
        tallies = {}
        for rec in voteRecords or []:
            choices = rec.get("choices", {}) if isinstance(rec, dict) else getattr(rec, "choices", {})
            for itemId, choice in choices.items():
                if itemId not in tallies:
                    tallies[itemId] = {"yes": 0, "no": 0, "abstain": 0, "total": 0}
                if choice in (VOTE_YES, VOTE_NO, VOTE_ABSTAIN):
                    tallies[itemId][choice] += 1
                    tallies[itemId]["total"] += 1
        return tallies

    @staticmethod
    def getWinners(tallies, minYes=1):
        """Simple promotion rule for MVP (per approved plan):
        An item wins if yes_count > no_count and yes_count >= minYes.

        Returns list of winning itemIds.
        """
        winners = []
        for itemId, counts in (tallies or {}).items():
            if counts.get("yes", 0) > counts.get("no", 0) and counts.get("yes", 0) >= minYes:
                winners.append(itemId)
        return winners