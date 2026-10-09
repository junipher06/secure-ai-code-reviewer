"""Escape untrusted text and redact likely credentials before reporting."""

import html
import re
from typing import Any


def clean(text: str) -> str:
    text = re.sub(r"\b(?:gsk_|ghp_|github_pat_)[A-Za-z0-9_]{12,}\b", "[REDACTED]", text)
    text = re.sub(
        r'(?i)((?:api[_-]?key|token|password|secret)\s*[:=]\s*["\x27])[^"\x27\n]{8,}',
        r"\1[REDACTED]",
        text,
    )
    text = "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)
    return html.escape(text).replace("@", "&#64;").replace("`", "&#96;").replace("::", "&#58;&#58;")


def format_report(
    review: dict[str, Any] | None, blockers: list[str], head_sha: str, synthetic: bool = False
) -> str:
    verdict = "FAIL" if blockers else "PASS"
    lines = ["## AI Code Review", f"**Gate: {verdict}**", f"Commit: `{clean(head_sha)}`"]
    if synthetic:
        lines.append("**OFFLINE SYNTHETIC DEMO: no model was called.**")
    if review:
        lines.extend([f"Risk: **{review['risk_level']}**", "### Summary"])
        lines.extend("- " + clean(item) for item in review["summary"])
    lines.append("### Blockers")
    lines.extend("- " + clean(item) for item in blockers or ["None."])
    if review:
        lines.append("### Findings")
        for item in review["findings"]:
            lines.append(
                f"- **{item['severity']}** {clean(item['file'])}:"
                f"{item['line_start']}-{item['line_end']}: {clean(item['message'])}"
            )
        lines.append("### Suggested improvements")
        lines.extend("- " + clean(item) for item in review["suggested_improvements"] or ["None."])
        lines.append("### Test plan")
        lines.extend("- " + clean(item) for item in review["test_plan"])
        for test in review["suggested_tests"]:
            lines.extend(
                [
                    "#### " + clean(test["path"]),
                    clean(test["instructions"]),
                    "<pre>" + clean(test["code"]) + "</pre>",
                ]
            )
    lines.append("Tests are suggestions only. Pattern checks do not detect every vulnerability.")
    return "\n".join(lines) + "\n"
