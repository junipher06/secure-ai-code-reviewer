"""Conservative escalation rules for synthetic support tickets."""


def needs_human_review(message: str) -> bool:
    """Security requests are handled by a human, never resolved automatically."""
    normalized = message.casefold()
    return any(word in normalized for word in ("password", "mfa", "hacked", "account takeover"))
