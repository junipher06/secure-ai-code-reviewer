"""A tiny deterministic support demo. No AI calls or customer communications."""

from .security_rules import needs_human_review


def route_ticket(message: str) -> str:
    """Return a queue name without sending, storing, or executing the message."""
    if not message.strip():
        raise ValueError("Ticket message must not be empty.")
    if len(message) > 2000:
        raise ValueError("Ticket message is too long.")
    if needs_human_review(message):
        return "human-security"
    normalized = message.casefold()
    if any(word in normalized for word in ("invoice", "refund", "billing")):
        return "billing"
    if any(word in normalized for word in ("error", "broken", "cannot log in")):
        return "technical"
    return "general"


if __name__ == "__main__":
    print("SYNTHETIC DEMO:", route_ticket("Demo request: reset my password"))
