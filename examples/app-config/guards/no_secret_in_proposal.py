"""Guard: no-secret-in-proposal. Enforces INCRAM rule r-4k7q2m at proposal time. Decides only.

The patterns are a small copy of the definite patterns in that rule's check. They will drift;
the rule's check is the authority.
"""
import re

DEFINITE = [
    re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY(?: BLOCK)?-----"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\b[sr]k_live_[0-9A-Za-z]{24,}\b"),
]
SECRET_KEY_NAME = re.compile(r"(?:PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY|PRIVATE_?KEY|ACCESS_?KEY)")


def check(proposal, context):
    """Return "pass" or "fail". This guard needs no context, so it never returns "unknown"."""
    value = proposal.get("value")
    if value is None:
        return "pass"
    if any(pattern.search(value) for pattern in DEFINITE):
        return "fail"
    if SECRET_KEY_NAME.search(proposal.get("key", "")):
        return "fail"
    return "pass"
