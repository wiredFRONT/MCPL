"""Guard: no-self-lockout. Decides only; never changes anything."""

ADMIN_PATH = "/admin"


def _covers_admin(path):
    """A rule applies to its path and everything under it."""
    return path == "/" or ADMIN_PATH == path or ADMIN_PATH.startswith(path.rstrip("/") + "/")


def check(proposal, context):
    """Return "pass", "fail" or "unknown". Never "pass" on missing context."""
    if proposal.get("effect") != "block" or not _covers_admin(proposal.get("path", "")):
        return "pass"
    requester = (context or {}).get("requester") or {}
    if requester.get("is_admin") is False:
        return "pass"
    country = requester.get("country")
    if requester.get("is_admin") is None or not country:
        return "unknown"
    match = proposal.get("country", {})
    blocked = country in match["in"] if "in" in match else country not in match.get("not_in", [])
    return "fail" if blocked else "pass"
