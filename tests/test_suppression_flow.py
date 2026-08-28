import unittest

from src.suppression_flow import decide_delivery


class SuppressionDecisionTest(unittest.TestCase):
    def test_hard_bounce_removes_subscriber_from_future_delivery(self):
        decision = decide_delivery({"subscriber": "reader@example.com", "type": "hard_bounce"})
        self.assertEqual(decision.action, "suppress")
        self.assertEqual(decision.reason, "hard bounce")

    def test_soft_event_keeps_subscriber_eligible(self):
        decision = decide_delivery({"subscriber": "reader@example.com", "type": "delivered"})
        self.assertEqual(decision.action, "keep")


if __name__ == "__main__":
    unittest.main()
