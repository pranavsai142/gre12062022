from flask import Flask, render_template_string, url_for, redirect, session, request, jsonify
import os
import hashlib
from firebase_admin import auth
from datetime import datetime
import uuid

import IndexPage, AboutPage, AccountPage, LoginPage, NotFoundPage, PolicyPage, RegisterPage, ResetPage, VotePage, DetailPage, DetailAmendmentPage, DraftsPage
from Policy import Policy
from Amendment import Amendment
import User
import Database
from Ballot import Ballot
from Vote import Vote, VOTE_YES, VOTE_NO, VOTE_ABSTAIN

app = Flask(__name__)

# Firebase Admin SDK via the one centralized initializer (same path all tools use).
# Fail loudly at startup — a silently uninitialized app 500s on every request.
if not Database.ensure_firebase_initialized():
    raise RuntimeError(
        f"Firebase service account not found at {Database.get_service_account_path()}. "
        "Set DATA_FOLDER to the directory containing the admin JSON (see README)."
    )


def _stable_secret_key():
    """Session signing key that is identical across gunicorn workers and restarts.
    os.urandom-per-process breaks sessions the moment --workers > 1 (each worker
    rejects cookies signed by its siblings). Precedence:
      1. SECRET_KEY env var (recommended on Render)
      2. Deterministic digest of the private service-account file (stable, secret,
         never in the repo)
      3. Random (single-process dev fallback only)
    """
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    try:
        with open(Database.get_service_account_path(), "rb") as f:
            return hashlib.sha256(f.read() + b"internet-party-session-v1").hexdigest()
    except OSError:
        return os.urandom(32).hex()


app.secret_key = _stable_secret_key()


@app.route('/healthz')
def healthz():
    """Lightweight health endpoint for Render health checks / uptime monitors.
    Shallow by default (no RTDB roundtrip per ping); pass ?deep=1 to also
    verify database connectivity."""
    if request.args.get("deep"):
        try:
            from firebase_admin import db as _db
            _db.reference("meta").get(shallow=True)
        except Exception as e:
            return jsonify({"status": "degraded", "database": str(e)}), 503
        return jsonify({"status": "ok", "database": "ok"})
    return jsonify({"status": "ok"})

@app.route('/validate-token', methods=['POST'])
def validate_token():
    # silent=True: empty/malformed body must not AttributeError into a 500
    data = request.get_json(silent=True) or {}
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({"authenticated": False, "error": "Missing idToken"}), 401

    try:
        # Verify the token and decode it. clock_skew_seconds tolerates freshly
        # minted tokens from clients whose clock is a second or two off — without
        # it, real logins intermittently fail with "Token used too early".
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=10)

        # Start a session for the user
        session["user"] = decoded_token
        # Redirect to another page after successful validation
        return redirect(url_for('account'))
    except Exception as e:
        # Invalid/expired token. firebase-admin raises InvalidIdTokenError (a
        # FirebaseError, NOT a ValueError) — catching only ValueError turned
        # every bad token into a 500.
        return jsonify({"authenticated": False, "error": str(e)}), 401

# MetaPolicy limits (SOUL_DRIVER: "Policy titles should be less than 100
# characters. Policy descriptions should be less than 10,000 characters.")
# The Drafts UI enforces these client-side (maxlength + counters); these are
# the server-side teeth so the rule binds for ALL clients (API, NPCs, curl).
TITLE_MAX_CHARS = 100
DESCRIPTION_MAX_CHARS = 10000

def _validateMetaLimits(title, description):
    """Returns an error string if the MetaPolicy char limits are violated, else None."""
    if not title or not str(title).strip():
        return "Title is required."
    if len(str(title)) > TITLE_MAX_CHARS:
        return f"Title must be {TITLE_MAX_CHARS} characters or fewer (MetaPolicy). Yours is {len(str(title))}."
    if description and len(str(description)) > DESCRIPTION_MAX_CHARS:
        return f"Description must be {DESCRIPTION_MAX_CHARS:,} characters or fewer (MetaPolicy). Yours is {len(str(description)):,}."
    return None


@app.route("/create-draft", methods=["POST"])
def create_draft():
    data = request.get_json()
    limitError = _validateMetaLimits(data.get("title"), data.get("description"))
    if limitError:
        return jsonify({"success": False, "error": limitError}), 400
    policyData = {}
    policyData["title"] = data.get("title")
    policyData["description"] = data.get("description")
    policyData["type"] = Policy.DRAFT
    sessionUserData = session.get("user")
    currentTimestamp = datetime.now().timestamp()
    policyData["created"] = currentTimestamp
    policyData["updated"] = currentTimestamp
    policyData["userId"] = None
    if(User.validateUser(sessionUserData)):
        policyData["userId"] = sessionUserData["uid"]
        policyId = uuid.uuid4().hex
        policy = Policy(policyId, policyData)
        if(Database.createDraftPolicy(policy)):
            return jsonify({"success": True, "id": policyId})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish.."}), 500
    else:
        return jsonify({"success": False, "error": "Can't create draft policy. No user logged in."}), 500


@app.route("/update-draft", methods=["POST"])
def update_draft():
    data = request.get_json()
    limitError = _validateMetaLimits(data.get("title"), data.get("description"))
    if limitError:
        return jsonify({"success": False, "error": limitError}), 400
    policyData = {}
    policyId = data.get("id")
    policyData["title"] = data.get("title")
    policyData["description"] = data.get("description")
    policyData["type"] = Policy.DRAFT
    sessionUserData = session.get("user")
    policyData["userId"] = None
    currentTimestamp = datetime.now().timestamp()
    policyData["created"] = currentTimestamp
    policyData["updated"] = currentTimestamp
    if(User.validateUser(sessionUserData)):
        policyData["userId"] = sessionUserData["uid"]
        policy = Policy(policyId, policyData)
        print("Updating policy", policy.toDictionary())
        if(Database.updateDraftPolicy(policy)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't update draft policy. No user logged in."}), 500
        
@app.route("/remove-draft", methods=["POST"])
def remove_draft():
    data = request.get_json()
    policyId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Submitting policy", policyId)
        if(Database.removeDraftPolicy(sessionUserData, policyId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't remove draft policy. No user logged in."}), 500
        
@app.route("/submit-draft", methods=["POST"])
def submit_draft():
    data = request.get_json()
    policyId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Submitting policy", policyId)
        if(Database.submitDraftPolicy(sessionUserData, policyId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't submit draft policy. No user logged in."}), 500
        
@app.route("/create-draft-amendment", methods=["POST"])
def create_draft_amendment():
    data = request.get_json()
    limitError = _validateMetaLimits(data.get("title"), data.get("description"))
    if limitError:
        return jsonify({"success": False, "error": limitError}), 400
    amendmentData = {}
    amendmentData["policyId"] = data.get("policyId")
    amendmentData["title"] = data.get("title")
    amendmentData["description"] = data.get("description")
    amendmentData["type"] = Amendment.DRAFT
    sessionUserData = session.get("user")
    currentTimestamp = datetime.now().timestamp()
    amendmentData["created"] = currentTimestamp
    amendmentData["updated"] = currentTimestamp
    amendmentData["userId"] = None
    if(User.validateUser(sessionUserData)):
        amendmentData["userId"] = sessionUserData["uid"]
        amendmentId = uuid.uuid4().hex
        amendment = Amendment(amendmentId, amendmentData)
        if(Database.createDraftAmendment(amendment)):
            return jsonify({"success": True, "id": amendmentId})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish.."}), 500
    else:
        return jsonify({"success": False, "error": "Can't create draft policy. No user logged in."}), 500


@app.route("/update-draft-amendment", methods=["POST"])
def update_draft_amendment():
    data = request.get_json()
    limitError = _validateMetaLimits(data.get("title"), data.get("description"))
    if limitError:
        return jsonify({"success": False, "error": limitError}), 400
    amendmentData = {}
    amendmentId = data.get("id")
    amendmentData["policyId"] = data.get("policyId")
    amendmentData["title"] = data.get("title")
    amendmentData["description"] = data.get("description")
    amendmentData["type"] = Amendment.DRAFT
    sessionUserData = session.get("user")
    currentTimestamp = datetime.now().timestamp()
    amendmentData["created"] = currentTimestamp
    amendmentData["updated"] = currentTimestamp
    amendmentData["userId"] = None
    if(User.validateUser(sessionUserData)):
        amendmentData["userId"] = sessionUserData["uid"]
        amendment = Amendment(amendmentId, amendmentData)
        if(Database.updateDraftAmendment(amendment)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish.."}), 500
    else:
        return jsonify({"success": False, "error": "Can't update draft policy. No user logged in."}), 500
        
@app.route("/remove-draft-amendment", methods=["POST"])
def remove_draft_amendment():
    data = request.get_json()
    amendmentId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Removing amendment", amendmentId)
        if(Database.removeDraftAmendment(sessionUserData, amendmentId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't remove draft policy. No user logged in."}), 500
        
        
@app.route("/submit-draft-amendment", methods=["POST"])
def submit_draft_amendment():
    data = request.get_json()
    amendmentId = data.get("id")
    sessionUserData = session.get("user")
    if(User.validateUser(sessionUserData)):
        print("Submitting amendment", amendmentId)
        if(Database.submitDraftAmendment(sessionUserData, amendmentId)):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Server error! Something smells like fish..."}), 500
    else:
        return jsonify({"success": False, "error": "Can't submit draft policy. No user logged in."}), 500


def _isOperator(sessionUserData):
    """Operator gate for promote/seed/clear/set-window actions.
    If OPERATOR_EMAILS is set (comma-separated), only those logged-in accounts
    may perform operator actions. Unset = v1 behavior (any logged-in member),
    so nothing changes until the env var is configured on Render.
    """
    if not User.validateUser(sessionUserData):
        return False
    allow = os.environ.get("OPERATOR_EMAILS", "").strip()
    if not allow:
        return True
    emails = {e.strip().lower() for e in allow.split(",") if e.strip()}
    return str(sessionUserData.get("email", "")).lower() in emails


OPERATOR_DENIED = "This account is not authorized for operator actions."


# ============================================================================
# VOTING ENDPOINTS (ballot submission + window close/promote)
# Follows the exact same JSON + session + "fish" error pattern as all other
# draft/amendment submit routes.
# ============================================================================

@app.route("/submit-ballot", methods=["POST"])
def submit_ballot():
    data = request.get_json()
    currentWindowId = Database.getCurrentVotingWindowId()
    windowId = data.get("windowId") or currentWindowId
    # Window gating (MetaPolicy integrity): ballots may only be cast into the
    # effective current window (real ISO week or the operator override). Without
    # this check, "one immutable vote per window" was bypassable by POSTing
    # arbitrary past/future windowIds.
    if windowId != currentWindowId:
        return jsonify({
            "success": False,
            "error": f"Voting is only open for the current window ({currentWindowId}). Refresh the Vote page and try again."
        }), 400
    choices = data.get("votes") or data.get("choices") or {}
    sessionUserData = session.get("user")

    if(User.validateUser(sessionUserData)):
        success, message = Database.recordUserBallot(sessionUserData, windowId, choices)
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400
    else:
        return jsonify({"success": False, "error": "You must be logged in to cast a ballot."}), 401


@app.route("/ballot-items", methods=["GET"])
def ballot_items():
    """Public read-only JSON view of the current ballot (same data /vote renders).
    Lets pure-HTTP clients (the NPC harness, future mobile/API consumers) discover
    what is on the ballot without scraping HTML. Respects the window override."""
    windowId = Database.getCurrentVotingWindowId()
    policies, amendments = Database.getBallotItems()
    items = (
        [{"key": f"policy-{p.getId()}", "kind": "policy", "id": p.getId(), "title": p.getTitle()} for p in policies]
        + [{"key": f"amendment-{a.getId()}", "kind": "amendment", "id": a.getId(), "title": a.getTitle()} for a in amendments]
    )
    return jsonify({"windowId": windowId, "items": items, "count": len(items)})


@app.route("/close-window", methods=["POST"])
def close_window():
    """Manual tabulate + promote for the current (or specified) window.
    Visible to any logged-in user in v1 for operator flexibility during early use.
    Later can be restricted.
    """
    data = request.get_json() or {}
    windowId = data.get("windowId") or Database.getCurrentVotingWindowId()
    sessionUserData = session.get("user")

    if(User.validateUser(sessionUserData)):
        if not _isOperator(sessionUserData):
            return jsonify({"success": False, "error": OPERATOR_DENIED}), 403
        result = Database.promoteWinnersFromWindow(windowId)
        return jsonify({"success": True, "result": result})
    else:
        return jsonify({"success": False, "error": "You must be logged in to close a voting window."}), 401


# ============================================================================
# DEV / ADMIN TOOLS ENDPOINTS (for Prefab dashboards + agentic flows)
# These let the nice UIs actually *do* things instead of just showing copy-paste commands.
# Run from repo root with the service account present for full power.
# ============================================================================

@app.route("/dev-tools/windows", methods=["GET"])
def dev_tools_windows():
    """Return list of windows with participation/vote counts for the dashboards."""
    try:
        Database.ensure_firebase_initialized()
        wins = Database.get_all_voting_windows()
        out = []
        for w in wins or []:
            d = Database.get_window_details(w)
            out.append({
                "window": w,
                "participation": d.get("participation_count", 0),
                "votes": d.get("vote_count", 0),
            })
        return jsonify({"windows": out, "source": "live"})
    except Exception as e:
        return jsonify({"windows": [], "source": "error", "error": str(e)}), 500


@app.route("/dev-tools/seed", methods=["POST"])
def dev_tools_seed():
    """Seeding is an operator/dev action; require logged-in user.
    Supports both the original random batch and the new precise choice-based seeding
    requested for deterministic testing ("send 3 yes to all items", "send 5 no", etc.).
    """
    sessionUserData = session.get("user")
    if not User.validateUser(sessionUserData):
        return jsonify({"success": False, "error": "You must be logged in to perform dev/operator actions."}), 401
    if not _isOperator(sessionUserData):
        return jsonify({"success": False, "error": OPERATOR_DENIED}), 403
    data = request.get_json() or {}
    window = data.get("window") or Database.getCurrentVotingWindowId()

    # New precise mode (preferred for the user's test needs)
    choice = data.get("choice")
    if choice is not None:
        # Normalize common representations (1/"yes"/"1" → "yes", 0/"no"→"no", -1/"abstain"→"abstain")
        # in the endpoint so frontend (strings or legacy ints) always result in canonical DB strings.
        choice_map = {
            1: Database.VOTE_YES, "1": Database.VOTE_YES, "yes": Database.VOTE_YES, "YES": Database.VOTE_YES,
            0: Database.VOTE_NO, "0": Database.VOTE_NO, "no": Database.VOTE_NO, "NO": Database.VOTE_NO,
            -1: Database.VOTE_ABSTAIN, "-1": Database.VOTE_ABSTAIN, "abstain": Database.VOTE_ABSTAIN, "ABSTAIN": Database.VOTE_ABSTAIN,
        }
        if choice in choice_map:
            choice = choice_map[choice]
        count = int(data.get("count", 3))
        res = Database.seed_synthetic_choice_votes(window, choice, count=count, force=True)
        return jsonify(res)

    # Backwards-compatible random batch
    count = int(data.get("count", 5))
    res = Database.seed_test_votes(window, count=count, force=True)
    return jsonify(res)


@app.route("/dev-tools/clear", methods=["POST"])
def dev_tools_clear():
    """Clear is destructive; require logged-in user (matches /close-window pattern).
    The primary website operator surface now calls this; protected against unauth callers.
    """
    sessionUserData = session.get("user")
    if not User.validateUser(sessionUserData):
        return jsonify({"success": False, "error": "You must be logged in to perform dev/operator actions."}), 401
    if not _isOperator(sessionUserData):
        return jsonify({"success": False, "error": OPERATOR_DENIED}), 403
    data = request.get_json() or {}
    window = data.get("window")
    if not window:
        return jsonify({"success": False, "error": "window required"}), 400
    confirm = bool(data.get("confirm", False))
    res = Database.clear_window_votes(window, confirm=confirm)
    return jsonify(res)


@app.route("/dev-tools/promote", methods=["POST"])
def dev_tools_promote():
    """Promote is a privileged operator action; require logged-in user (matches /close-window pattern).
    Primary surface (AccountPage) + docs now route through these; auth added for safety.
    """
    sessionUserData = session.get("user")
    if not User.validateUser(sessionUserData):
        return jsonify({"success": False, "error": "You must be logged in to perform dev/operator actions."}), 401
    if not _isOperator(sessionUserData):
        return jsonify({"success": False, "error": OPERATOR_DENIED}), 403
    data = request.get_json() or {}
    window = data.get("window") or Database.getCurrentVotingWindowId()
    res = Database.promoteWinnersFromWindow(window)
    return jsonify(res)


@app.route("/dev-tools/reset-user", methods=["POST"])
def dev_tools_reset_user():
    """Reset votes for one specific user in a window. Powerful for targeted testing cleanup."""
    sessionUserData = session.get("user")
    if not User.validateUser(sessionUserData):
        return jsonify({"success": False, "error": "You must be logged in to perform dev/operator actions."}), 401
    if not _isOperator(sessionUserData):
        return jsonify({"success": False, "error": OPERATOR_DENIED}), 403
    data = request.get_json() or {}
    window = data.get("window")
    user_id = data.get("user_id") or data.get("uid")
    if not window or not user_id:
        return jsonify({"success": False, "error": "window and user_id required"}), 400
    res = Database.reset_user_votes(window, user_id)
    return jsonify(res)


@app.route("/dev-tools/set-window", methods=["POST"])
def dev_tools_set_window():
    """Allow the operator surface to set or clear a temporary current-window override.
    Used from the Target Window text box on /account so testers can point the whole site
    (Vote page, ballot, etc.) at a specific window (including empty/test windows).
    """
    sessionUserData = session.get("user")
    if not User.validateUser(sessionUserData):
        return jsonify({"success": False, "error": "You must be logged in to perform dev/operator actions."}), 401
    if not _isOperator(sessionUserData):
        return jsonify({"success": False, "error": OPERATOR_DENIED}), 403
    data = request.get_json() or {}
    window = data.get("window") or data.get("windowId")
    # empty / null / "clear" clears the override
    res = Database.setCurrentVotingWindowOverride(window if window and str(window).strip() else None)
    return jsonify(res)


@app.route('/robots.txt')
def robots_txt():
    return "fuck off"
    
@app.route('/')
def index():
    htmlString = IndexPage.render(session.get("user"))
    return htmlString

@app.route('/about')
def about():
    htmlString = AboutPage.render(session.get("user"))
    return htmlString

@app.route('/account')
def account():
    htmlString = AccountPage.render(session.get("user"))
    return htmlString
    
@app.route('/login')
def login():
    htmlString = LoginPage.render(session.get("user"))
    return htmlString

@app.route('/policy')
def policy():
    htmlString = PolicyPage.render(session.get("user"))
    return htmlString
    
@app.route('/drafts')
def drafts():
    u = session.get("user")
    if not User.validateUser(u):
        u = None
    new_param = request.args.get('new')
    amend_param = request.args.get('amend')
    htmlString = DraftsPage.render(u, new=new_param, amend=amend_param)
    return htmlString
    
@app.route('/detail/<policyId>')
def detail(policyId):
    htmlString = DetailPage.render(session.get("user"), policyId)
    return htmlString

@app.route('/detail/amendment/<amendmentId>')
def detail_amendment(amendmentId):
    htmlString = DetailAmendmentPage.render(session.get("user"), amendmentId)
    return htmlString

@app.route('/register')
def register():
    htmlString = RegisterPage.render(session.get("user"))
    return htmlString

@app.route('/reset')
def reset():
    htmlString = ResetPage.render(session.get("user"))
    return htmlString

@app.route('/admin')
def admin():
    """Operator entrypoint — delegates to the rich live Account page which now contains
    the full real-time Operator & Dev Tools control surface (seed, clear, promote, inspection).
    This fulfills the request that the website itself be the primary frictionless place to do everything.
    """
    return redirect(url_for('account'))

@app.route('/vote')
def vote():
    htmlString = VotePage.render(session.get("user"))
    return htmlString
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.errorhandler(404)
def not_found_error(e):
    """Real 404s now render the mobile-friendly NotFoundPage (with viewport, menu, responsive rules).
    Previously the default Flask 404 had none of the party UI or mobile adaptations.
    """
    return NotFoundPage.render(session.get("user")), 404

if __name__ == '__main__':
    # Respect env so we can disable reloader locally for more reliable firewall behavior
    # while keeping identical behavior in prod (where start.sh runs it).
    # Set FLASK_USE_RELOADER=0 to disable.
    use_reloader = os.environ.get("FLASK_USE_RELOADER", "1") == "1"
    app.run(host="0.0.0.0", use_reloader=use_reloader)