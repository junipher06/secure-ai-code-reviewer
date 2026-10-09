"""Deterministic policy and fresh approvals using trusted base configuration."""

import fnmatch
import re
from typing import Any

from .diff import Change
from .errors import ReviewError


def matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def check_policy(changes: list[Change], policy: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers, sensitive = [], []
    paths = {c.path for c in changes} | {c.previous_path for c in changes if c.previous_path}
    if any(matches(p, pattern) for p in paths for pattern in policy["source_paths"]):
        if not any(
            c.added and any(matches(c.path, pattern) for pattern in policy["test_paths"])
            for c in changes
        ):
            blockers.append("Source code changed without added or updated tests.")
    for change in changes:
        if any(
            matches(p, pattern)
            for p in [change.path, change.previous_path or change.path]
            for pattern in policy["sensitive_paths"]
        ):
            sensitive.append(change.path)
        for line_no, text in change.added:
            for rule in policy["risky_patterns"]:
                if re.search(rule["regex"], text):
                    blockers.append(f"{rule['id']} in {change.path}:{line_no}; {rule['message']}")
    return list(dict.fromkeys(blockers)), sensitive


def owners_for(path: str, content: str) -> set[str]:
    """Restricted CODEOWNERS subset: anchored globs or *, explicit @user owners.

    Last match wins. GitHub's native CODEOWNER enforcement is separately required.
    """
    owners: set[str] = set()
    for raw in content.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        pattern, users = parts[0], parts[1:]
        if pattern != "*" and not pattern.startswith("/"):
            raise ReviewError("Use anchored path patterns in CODEOWNERS.")
        if not users or any(not re.fullmatch(r"@[A-Za-z0-9-]+", user) for user in users):
            raise ReviewError("CODEOWNERS needs explicit GitHub usernames, not teams or emails.")
        if pattern == "*" or matches(path, pattern.lstrip("/")):
            owners = {user[1:].lower() for user in users}
    if not owners or "replace-with-reviewer" in owners:
        raise ReviewError("Replace CODEOWNERS placeholder with your trusted collaborator.")
    return owners


def approval_blockers(
    paths: list[str],
    high_risk: bool,
    policy: dict[str, Any],
    codeowners: str,
    reviews: list[dict[str, Any]],
    head_sha: str,
    author: str,
) -> list[str]:
    if not paths and not high_risk:
        return []
    trusted = {login.lower() for login in policy["trusted_reviewers"]}
    latest: dict[str, dict[str, Any]] = {}
    for review in sorted(reviews, key=lambda item: item["id"]):
        if review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[review["user"]["login"].lower()] = review
    approved = {
        login
        for login, review in latest.items()
        if login in trusted
        and login != author.lower()
        and review["state"] == "APPROVED"
        and review.get("commit_id") == head_sha
    }
    blockers = []
    if high_risk and not approved:
        blockers.append("HIGH risk needs fresh approval from a configured trusted reviewer.")
    for path in paths:
        if not (owners_for(path, codeowners) & approved):
            blockers.append(f"Sensitive path {path} needs fresh approval from its CODEOWNER.")
    return blockers
