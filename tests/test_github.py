from unittest import TestCase
from unittest.mock import Mock

from reviewer.errors import ReviewError
from reviewer.github import GitHub, NoRedirect


class GitHubTests(TestCase):
    def setUp(self):
        self.api = GitHub("Junipher06/secure-ai-code-reviewer", "SYNTHETIC_AUTH_VALUE")

    def test_invalid_repository_or_missing_auth(self):
        for repo, token in [("https://evil.test", "synthetic"), ("owner/repo", "")]:
            with self.assertRaises(ReviewError):
                GitHub(repo, token)

    def test_diff_uses_api(self):
        pr = {"head": {"sha": "abc"}, "state": "open", "changed_files": 1}
        self.api.request = Mock(side_effect=[pr, [{"filename": "src/main.py"}], "diff-data", []])
        diff, files, _ = self.api.collect(1, "abc")
        self.assertEqual(diff, "diff-data")
        self.assertEqual(len(files), 1)
        self.assertEqual(
            self.api.request.call_args_list[2].kwargs["accept"], "application/vnd.github.diff"
        )

    def test_stale_sha_fails(self):
        self.api.request = Mock(return_value={"head": {"sha": "changed"}, "state": "open"})
        with self.assertRaises(ReviewError):
            self.api.collect(1, "old")

    def test_incomplete_files_fail(self):
        self.api.request = Mock(
            side_effect=[
                {"head": {"sha": "abc"}, "state": "open", "changed_files": 2},
                [{"filename": "one.py"}],
            ]
        )
        with self.assertRaises(ReviewError):
            self.api.collect(1, "abc")

    def test_pagination(self):
        self.api.request = Mock(side_effect=[[{"id": i} for i in range(100)], [{"id": 100}]])
        self.assertEqual(len(self.api.pages("/pulls/1/reviews")), 101)

    def test_redirect_refused(self):
        with self.assertRaises(ReviewError):
            NoRedirect().redirect_request(
                None, None, 302, "redirect", {}, "https://synthetic.invalid"
            )
