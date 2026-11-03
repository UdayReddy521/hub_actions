import unittest
from app import dashboard, qualify, sample

class LeadPilotTests(unittest.TestCase):
    def setUp(self):
        self.leads = qualify(sample())

    def test_count(self):
        self.assertEqual(len(self.leads), 8)

    def test_scores_within_range(self):
        self.assertTrue(all(0 <= x["score"] <= 100 for x in self.leads))

    def test_duplicate_blocked(self):
        x = [x for x in self.leads if x["company"] == "Rio Grande Forklift Services"]
        self.assertEqual(sum(y["review_status"] == "blocked" for y in x), 1)

    def test_customer_blocked(self):
        self.assertEqual(next(x for x in self.leads if x["company"] == "Desert Kitchen Group")["review_status"], "blocked")

    def test_outside_area_blocked(self):
        self.assertEqual(next(x for x in self.leads if x["company"] == "Alamogordo Distribution")["review_status"], "blocked")

    def test_unknown_requires_review(self):
        x = next(x for x in self.leads if x["company"] == "Southwest Metals Plant")
        self.assertIn("human verification", " ".join(x["flags"]))

    def test_dashboard_contains_sample(self):
        self.assertIn("Rio Grande", dashboard(self.leads))

if __name__ == "__main__":
    unittest.main()
