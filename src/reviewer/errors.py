class ReviewError(Exception):
    """Safe failure message; never include remote response bodies or secrets."""
