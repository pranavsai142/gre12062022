from datetime import datetime


def validateUser(user):
    """True when session user dict is present and not expired.

    Firebase ID tokens store `exp` as a Unix timestamp. Missing/malformed exp
    must not raise KeyError (would 500 a page render mid-request).
    """
    if not user or not isinstance(user, dict):
        return False
    exp = user.get("exp")
    if exp is None:
        return False
    try:
        return float(exp) >= datetime.now().timestamp()
    except (TypeError, ValueError):
        return False
