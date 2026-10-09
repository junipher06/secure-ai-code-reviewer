"""Offline demonstrations or a live PR review using trusted base files."""

import argparse
import json
import os
import re
from pathlib import Path

from .diff import parse_diff
from .environment import load_local_env
from .errors import ReviewError
from .github import GitHub
from .groq_review import review_with_groq, validate_review
from .policy import approval_blockers, check_policy
from .report import format_report


def load_settings(root: Path) -> tuple[dict, dict, str, str]:
    policy = json.loads((root / ".agent/policy.json").read_text())
    schema = json.loads((root / ".agent/review.schema.json").read_text())
    prompt = (root / ".agent/reviewer_prompt.md").read_text()
    owners = (root / ".github/CODEOWNERS").read_text()
    return policy, schema, prompt, owners


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--demo", choices=["safe", "unsafe"])
    parser.add_argument("--event", type=Path)
    parser.add_argument("--env-file", type=Path, help="Explicit local-only ignored .env file")
    parser.add_argument("--post-comment", action="store_true")
    args = parser.parse_args(argv)
    blockers: list[str] = []
    review = None
    github = None
    number = 0
    head_sha = "synthetic-demo"
    synthetic = bool(args.demo)
    try:
        if args.env_file:
            load_local_env(args.env_file)
        policy, schema, prompt, owners = load_settings(args.root)
        if args.demo:
            if args.post_comment:
                raise ReviewError("Synthetic demos cannot post to GitHub.")
            diff = (args.root / f"tests/fixtures/{args.demo}.diff").read_text()
            changes = parse_diff(diff, policy["max_diff_bytes"])
            blockers, sensitive = check_policy(changes, policy)
            review = validate_review(
                (args.root / "tests/fixtures/model-pass.json").read_text(), schema, changes
            )
            blockers.extend(
                approval_blockers(sensitive, False, policy, owners, [], head_sha, "demo")
            )
        else:
            if not args.event:
                raise ReviewError("Choose --demo safe/unsafe or --event for a live PR.")
            event = json.loads(args.event.read_text())
            number = event["number"]
            if not isinstance(number, int) or number < 1:
                raise ReviewError("Invalid PR number.")
            head_sha = event["pull_request"]["head"]["sha"]
            if not isinstance(head_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", head_sha):
                raise ReviewError("Invalid PR commit SHA.")
            github = GitHub(event["repository"]["full_name"], os.environ.get("GITHUB_TOKEN", ""))
            diff, file_list, context = github.collect(number, head_sha)
            changes = parse_diff(diff, policy["max_diff_bytes"])
            if {item["filename"] for item in file_list} != {item.path for item in changes}:
                raise ReviewError(
                    "Diff omits changed files (binary/renamed); manual review needed."
                )
            blockers, sensitive = check_policy(changes, policy)
            # Prevent sending deterministically prohibited or credential-bearing code to Groq.
            hard_blockers = [
                item for item in blockers if not item.startswith("Source code changed without")
            ]
            if not hard_blockers:
                review = review_with_groq(diff, policy, schema, prompt, changes)
                if review["verdict"] == "FAIL":
                    blockers.append("AI reviewer verdict is FAIL.")
                blockers.extend(review["required_actions"])
            blockers.extend(
                approval_blockers(
                    list(
                        dict.fromkeys(
                            sensitive
                            + (
                                [c.path for c in changes]
                                if review and review["risk_level"] == "HIGH"
                                else []
                            )
                        )
                    ),
                    bool(review and review["risk_level"] == "HIGH"),
                    policy,
                    owners,
                    context["reviews"],
                    head_sha,
                    context["pr"]["user"]["login"],
                )
            )
            if github.pull_request(number)["head"]["sha"] != head_sha:
                raise ReviewError("PR changed during review; rerun for current commit.")
    except (ReviewError, OSError, ValueError, KeyError, TypeError) as exc:
        blockers.append(
            str(exc)
            if isinstance(exc, ReviewError)
            else "Inputs or trusted configuration could not be loaded; failed closed."
        )
    report = format_report(review, blockers, head_sha, synthetic)
    print(report)
    if args.post_comment and github and number:
        try:
            github.comment(number, report)
        except ReviewError:
            print("Posting review comment failed; review failed closed.")
            blockers.append("Comment could not be posted.")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
