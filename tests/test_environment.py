import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from reviewer.environment import load_local_env
from reviewer.errors import ReviewError


class EnvironmentTests(unittest.TestCase):
    def test_local_load_preserves_existing_environment(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(os.environ, {"GROQ_API_KEY": "SYNTHETIC_EXISTING"}, clear=True),
        ):
            path = Path(directory) / ".env"
            path.write_text("GROQ_API_KEY=SYNTHETIC_LOCAL\nGITHUB_TOKEN=SYNTHETIC_TOKEN\n")
            load_local_env(path)
            self.assertEqual(os.environ["GROQ_API_KEY"], "SYNTHETIC_EXISTING")
            self.assertEqual(os.environ["GITHUB_TOKEN"], "SYNTHETIC_TOKEN")

    def test_actions_refuses_env_file(self):
        with (
            patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True),
            self.assertRaises(ReviewError),
        ):
            load_local_env(Path(".env"))

    def test_unexpected_variable_rejected_without_partial_loading(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            path = Path(directory) / ".env"
            path.write_text("GROQ_API_KEY=SYNTHETIC_LOCAL\nUNEXPECTED=value\n")
            with self.assertRaises(ReviewError):
                load_local_env(path)
            self.assertNotIn("GROQ_API_KEY", os.environ)
