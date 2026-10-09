import unittest

from customer_support.routing import route_ticket
from customer_support.security_rules import needs_human_review


class CustomerSupportTests(unittest.TestCase):
    def test_security_is_escalated_before_billing(self):
        self.assertEqual(route_ticket("SYNTHETIC: hacked account and refund"), "human-security")

    def test_security_case_insensitive(self):
        self.assertTrue(needs_human_review("SYNTHETIC PASSWORD reset"))

    def test_billing(self):
        self.assertEqual(route_ticket("SYNTHETIC invoice question"), "billing")

    def test_technical(self):
        self.assertEqual(route_ticket("SYNTHETIC broken screen"), "technical")

    def test_general(self):
        self.assertEqual(route_ticket("SYNTHETIC hello"), "general")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            route_ticket(" ")

    def test_long_rejected(self):
        with self.assertRaises(ValueError):
            route_ticket("x" * 2001)

    def test_length_boundary(self):
        self.assertEqual(route_ticket("x" * 2000), "general")
