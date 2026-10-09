"""Text-only Groq review with strict schema and semantic validation."""

import json
import os
from typing import Any

from jsonschema import Draft202012Validator

from .diff import Change, safe_path
from .errors import ReviewError


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReviewError("Model response contains duplicate JSON keys.")
        result[key] = value
    return result


def validate_review(
    content: str | None, schema: dict[str, Any], changes: list[Change]
) -> dict[str, Any]:
    if not content or len(content.encode()) > 50000:
        raise ReviewError("Model response is missing or too large.")
    try:
        data = json.loads(content, object_pairs_hook=unique_object)
        Draft202012Validator.check_schema(schema)
        if not Draft202012Validator(schema).is_valid(data):
            raise ReviewError("Model response failed the strict JSON schema.")
    except (ValueError, TypeError, RecursionError) as exc:
        raise ReviewError("Model response is not valid JSON.") from exc

    def check_strings(value: Any) -> None:
        if isinstance(value, str) and not value.strip():
            raise ReviewError("Model response contains empty text.")
        if isinstance(value, list):
            for item in value:
                check_strings(item)
        if isinstance(value, dict):
            for item in value.values():
                check_strings(item)

    check_strings(data)
    allowed = {change.path: change.visible_lines for change in changes}
    for finding in data["findings"]:
        start, end = finding["line_start"], finding["line_end"]
        if (
            finding["file"] not in allowed
            or start < 1
            or end < start
            or end - start > 1000
            or not set(range(start, end + 1)).issubset(allowed[finding["file"]])
        ):
            raise ReviewError("Finding references a file or line outside supplied diff.")
    if not 1 <= len(data["summary"]) <= 3:
        raise ReviewError("Summary needs one to three items.")
    if not data["test_plan"]:
        raise ReviewError("Model response needs a concrete test plan.")
    for test in data["suggested_tests"]:
        safe_path(test["path"])
        if (
            not test["path"].startswith("tests/")
            or ".." in test["path"].split("/")
            or "\\" in test["path"]
            or not test["path"].endswith(".py")
        ):
            raise ReviewError("Suggested tests must use safe paths under tests/.")
    if data["verdict"] == "PASS" and (
        data["required_actions"]
        or any(item["severity"] in {"HIGH", "CRITICAL"} for item in data["findings"])
    ):
        raise ReviewError("Model PASS conflicts with blockers or required actions.")
    return data


def review_with_groq(
    diff: str,
    policy: dict[str, Any],
    schema: dict[str, Any],
    prompt: str,
    changes: list[Change],
    client: Any = None,
) -> dict[str, Any]:
    payload = json.dumps(
        {
            "untrusted_diff": diff,
            "review_policy": {
                "sensitive_paths": policy["sensitive_paths"],
                "test_expectations": policy["test_expectations"],
                "project_context": policy.get("project_context", ""),
            },
        }
    )
    request_bytes = len((prompt + payload + json.dumps(schema)).encode("utf-8"))
    if request_bytes > policy.get("max_request_bytes", 24000):
        raise ReviewError("Review request exceeds the free-tier budget; use a smaller PR.")
    if client is None:
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise ReviewError("GROQ_API_KEY missing; add it securely before live review.")
        from groq import Groq

        client = Groq(
            api_key=key,
            timeout=policy.get("request_timeout_seconds", 45),
            max_retries=policy.get("max_retries", 0),
        )
    try:
        response = client.chat.completions.create(
            model=policy["model"],
            temperature=0,
            max_completion_tokens=policy.get("max_completion_tokens", 2048),
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": payload,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "code_review", "strict": True, "schema": schema},
            },
        )
        choice = response.choices[0]
        if choice.finish_reason != "stop":
            raise ReviewError("Model review did not finish completely.")
        return validate_review(choice.message.content, schema, changes)
    except ReviewError:
        raise
    except Exception as exc:
        # Never print SDK exceptions, request data, credentials or raw model responses.
        raise ReviewError("Groq review failed; check model, quota and connectivity.") from exc
