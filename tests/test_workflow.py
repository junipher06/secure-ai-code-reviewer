import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / ".github/workflows/ai-review.yml").read_text()
        self.workflow = yaml.safe_load(self.text)

    def test_pr_trigger_only(self):
        triggers = self.workflow.get("on", self.workflow.get(True))
        self.assertEqual(set(triggers), {"pull_request"})
        self.assertNotIn("pull_request_target", self.text)

    def test_trusted_base_secret_job(self):
        job = self.workflow["jobs"]["ai_review"]
        self.assertEqual(job["permissions"], {"contents": "read", "pull-requests": "write"})
        checkout = job["steps"][0]
        self.assertEqual(checkout["with"]["ref"], (
            "${{ github.repository == 'junipher06/secure-ai-code-reviewer' "
            "&& github.event.pull_request.number == 3 "
            "&& '72b0dd29dbc237864a4efd39f50820215ee630a1' "
            "|| github.event.pull_request.base.sha }}"
        ))
        self.assertFalse(checkout["with"]["persist-credentials"])
        self.assertNotIn("head.sha", str(job))
        steps = [s for s in job["steps"] if "GROQ_API_KEY" in s.get("env", {})]
        self.assertEqual(len(steps), 1)
        self.assertIn("reviewer.cli", steps[0]["run"])
        self.assertNotIn("echo", steps[0]["run"])

    def test_ci_has_no_secret_or_write(self):
        job = self.workflow["jobs"]["ci_checks"]
        self.assertEqual(job["permissions"], {"contents": "read"})
        self.assertNotIn("secrets.", str(job))
        self.assertNotIn("GROQ_API_KEY", str(job))
        self.assertFalse(job["steps"][0]["with"]["persist-credentials"])

    def test_gate_always_checks_both(self):
        job = self.workflow["jobs"]["gate"]
        self.assertEqual(set(job["needs"]), {"ai_review", "ci_checks"})
        self.assertIn("always()", job["if"])
        self.assertEqual(job["permissions"], {})
        self.assertIn("exit 1", job["steps"][0]["run"])

    def test_pinned_actions_blank_example_no_env(self):
        for job in self.workflow["jobs"].values():
            for step in job["steps"]:
                if "uses" in step:
                    self.assertRegex(step["uses"], r"@[a-f0-9]{40}$")
        self.assertFalse((ROOT / ".env").exists())
        self.assertIn("GROQ_API_KEY=\n", (ROOT / ".env.example").read_text())
