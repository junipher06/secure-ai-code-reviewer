"""Synthetic credential screening; no real keys or network calls."""

import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from reviewer.cli import load_settings, main
from reviewer.diff import parse_diff
from reviewer.errors import ReviewError
from reviewer.groq_review import review_with_groq

ROOT = Path(__file__).resolve().parents[1]


class CredentialTests(unittest.TestCase):
    def setUp(self):
        policy, schema, prompt, _ = load_settings(ROOT)
        self.diff = (ROOT / "tests/fixtures/safe.diff").read_text()
        self.literal = 'api_key = "' + "SYNTHETIC_NOT_A_REAL_KEY_000" + '"'
        self.client = Mock()
        self.inputs = dict(
            diff=self.diff,
            policy=policy,
            schema=schema,
            prompt=prompt,
            changes=parse_diff(self.diff),
            client=self.client,
        )

    def blocked(self, **changes):
        with self.assertRaisesRegex(ReviewError, "Credential-like content") as caught:
            review_with_groq(**{**self.inputs, **changes})
        self.assertNotIn("SYNTHETIC_NOT_A_REAL_KEY_000", str(caught.exception))
        self.client.chat.completions.create.assert_not_called()

    def credential_diff(self, prefix):
        old, new = (0, 3) if prefix == "+" else (1, 2 if prefix == "-" else 3)
        return self.diff.replace("@@ -0,0 +1,2 @@", f"@@ -1,{old} +1,{new} @@", 1).replace(
            "+def normalize(value):", prefix + self.literal + "\n+def normalize(value):", 1
        )

    def test_added_deleted_context_and_metadata_block(self):
        for prefix in ["+", "-", " "]:
            diff = self.credential_diff(prefix)
            self.blocked(diff=diff, changes=parse_diff(diff))
        for prefix in ["gsk_", "ghp_", "github_pat_"]:
            self.blocked(
                diff=self.diff.replace("src/example.py", "src/" + prefix + "SYNTHETIC" * 4)
            )

    def test_other_request_fields_block(self):
        self.blocked(prompt=self.inputs["prompt"] + self.literal)
        for field in ["model", "project_context", "test_expectations", "sensitive_paths"]:
            policy = copy.deepcopy(self.inputs["policy"])
            policy[field] = [self.literal] if field == "sensitive_paths" else self.literal
            self.blocked(policy=policy)
        for schema in [{"description": self.literal}, {self.literal: {"enum": ["safe"]}}]:
            self.blocked(schema=schema)

    def test_invalid_rule_fails_closed(self):
        for rules in [[], [{"id": "credential-literal", "regex": "["}]]:
            with self.assertRaisesRegex(ReviewError, "configuration is invalid"):
                review_with_groq(
                    **{**self.inputs, "policy": {**self.inputs["policy"], "risky_patterns": rules}}
                )
            self.client.chat.completions.create.assert_not_called()

    def test_block_before_sdk_construction(self):
        with patch("groq.Groq") as sdk:
            self.blocked(diff=self.credential_diff("-"), client=None)
            sdk.assert_not_called()

    def test_blank_secret_reference_and_removed_eval_allowed(self):
        self.client.chat.completions.create.side_effect = RuntimeError("synthetic failure")
        extra = (
            "\n-GROQ_API_KEY=\n+GROQ_API_KEY="
            + "$"
            + "{{ secrets.GROQ_API_KEY }}\n-"
            + "ev"
            + "al(value)"
        )
        with self.assertRaisesRegex(ReviewError, "Groq review failed"):
            review_with_groq(**{**self.inputs, "diff": self.diff + extra})
        self.client.chat.completions.create.assert_called_once()

    def test_cli_fails_without_provider_or_leak(self):
        diff, sha = self.credential_diff("-"), "a" * 40
        api = Mock()
        api.collect.return_value = (
            diff,
            [{"filename": c.path} for c in parse_diff(diff)],
            {"reviews": [], "pr": {"user": {"login": "synthetic-author"}}},
        )
        event = {
            "number": 2,
            "pull_request": {"head": {"sha": sha}},
            "repository": {"full_name": "junipher06/secure-ai-code-reviewer"},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.json"
            path.write_text(json.dumps(event))
            with (
                patch("reviewer.cli.GitHub", return_value=api),
                patch("groq.Groq") as sdk,
                patch("sys.stdout", new=io.StringIO()) as output,
            ):
                self.assertEqual(
                    main(["--root", str(ROOT), "--event", str(path), "--post-comment"]), 1
                )
                sdk.assert_not_called()
                api.comment.assert_called_once()
                self.assertIn("Gate: FAIL", output.getvalue())
                self.assertNotIn("SYNTHETIC_NOT_A_REAL_KEY_000", api.comment.call_args.args[1])
