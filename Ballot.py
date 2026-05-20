from Policy import Policy
from Amendment import Amendment
from Vote import VOTE_YES, VOTE_NO, VOTE_ABSTAIN


class Ballot:
    """Runtime presentation object for the current ballot.

    Created fresh on every /vote render (or public preview).
    Holds the *live* list of candidate policies + amendments that anyone can
    see ("Generate a ballot items that contains all the acceptable candidates").

    When a user is logged in and has not yet voted this window, this object
    is what gets turned into the interactive form.

    Per original notes: "Ballot objects are created specific to the user.
    They can be saved in the session."

    MVP: we pass the data through Jinja; a minimal serializable form can be
    dropped into session if we later want multi-step voting or review-before-submit.
    """

    def __init__(self, windowId, policies, amendments, userId=None, userChoices=None):
        """
        Args:
            windowId: e.g. "2026-W17"
            policies: list of Policy objects (already filtered to canidate)
            amendments: list of Amendment objects (already filtered to canidate)
            userId: uid or None (public view)
            userChoices: dict {itemId: "yes"|"no"|"abstain"} if the user has already voted
        """
        self.windowId = windowId
        self.userId = userId
        self.policies = policies or []
        self.amendments = amendments or []
        self.userChoices = userChoices or {}   # only populated after a vote or for "show my vote"

    def isPublic(self):
        return self.userId is None

    def hasItems(self):
        return len(self.policies) > 0 or len(self.amendments) > 0

    def totalItems(self):
        return len(self.policies) + len(self.amendments)

    def getUserChoice(self, itemId):
        return self.userChoices.get(itemId)

    def hasUserVotedOn(self, itemId):
        return itemId in self.userChoices

    def toSessionDict(self):
        """Minimal serializable version that can be stored in Flask session
        if we ever want the exact snapshot the user saw when they started voting.
        """
        return {
            "windowId": self.windowId,
            "userId": self.userId,
            "policyIds": [p.getId() for p in self.policies],
            "amendmentIds": [a.getId() for a in self.amendments],
        }

    @staticmethod
    def fromSessionDict(data, policyLookup, amendmentLookup):
        """Rehydrate a Ballot from what was stored in session (future use)."""
        # Not wired in MVP, but the hook is here exactly as the notes requested.
        if not data:
            return None
        policies = [policyLookup(pid) for pid in data.get("policyIds", []) if policyLookup(pid)]
        amendments = [amendmentLookup(aid) for aid in data.get("amendmentIds", []) if amendmentLookup(aid)]
        return Ballot(
            data.get("windowId"),
            policies,
            amendments,
            userId=data.get("userId")
        )

    def toTemplateContext(self):
        """Convenience for the big render_template_string in VotePage."""
        return {
            "windowId": self.windowId,
            "userId": self.userId,
            "policies": self.policies,
            "amendments": self.amendments,
            "userChoices": self.userChoices,
            "totalItems": self.totalItems(),
            "isPublic": self.isPublic(),
        }