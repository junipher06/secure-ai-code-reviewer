"""Developer-reviewed Groq suggestion; all messages are synthetic course examples."""

import unittest

from customer_support.security_rules import needs_human_review


class TestNeedsHumanReview(unittest.TestCase):
    def test_password_trigger(self):
        self.assertTrue(needs_human_review("Please reset my password"))

    def test_mfa_trigger(self):
        self.assertTrue(needs_human_review("I need to enable MFA"))

    def test_hacked_trigger(self):
        self.assertTrue(needs_human_review("My account was hacked"))

    def test_account_takeover_trigger(self):
        self.assertTrue(needs_human_review("Account takeover detected"))

    def test_pin_reset_trigger(self):
        self.assertTrue(needs_human_review("I forgot my pin reset code"))

    def test_case_insensitivity(self):
        self.assertTrue(needs_human_review("PASSWORD"))

    def test_no_trigger(self):
        self.assertFalse(needs_human_review("Just a normal message"))

    def test_substring_match(self):
        # 'pin reset' should match even if part of a longer word
        self.assertTrue(needs_human_review("pin resetting my account"))


if __name__ == "__main__":
    unittest.main()
