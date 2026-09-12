#!/usr/bin/env python3
"""Regression tests for Human Review API endpoints and error handling."""

import unittest
import os
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:3000"

class TestHumanReviewAPI(unittest.TestCase):

    def test_get_cases_returns_json_and_preserves_structure(self):
        req = urllib.request.Request(f"{BASE_URL}/api/review/cases", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))
            data = json.loads(resp.read().decode())
            self.assertIn("cases", data)
            self.assertIn("metadata", data)
            self.assertEqual(len(data["cases"]), 170)
            self.assertIn("intents", data)
            self.assertIn("valid_intents", data)

    def test_trailing_slash_returns_json(self):
        req = urllib.request.Request(f"{BASE_URL}/api/review/cases/", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))

    def test_status_endpoint_returns_json(self):
        req = urllib.request.Request(f"{BASE_URL}/api/review/status", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))
            meta = json.loads(resp.read().decode())
            self.assertEqual(meta["total_cases"], 170)

    def test_api_404_always_returns_json_not_html(self):
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/review/nonexistent-route")
            urllib.request.urlopen(req)
            self.fail("Expected 404 HTTPError")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)
            self.assertIn("application/json", e.headers.get("Content-Type", ""))
            body = json.loads(e.read().decode())
            self.assertIn("error", body)
            self.assertEqual(body.get("status"), 404)

    def test_invalid_submit_returns_json_400(self):
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/api/review/submit",
                data=json.dumps({"invalid_field": True}).encode(),
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            urllib.request.urlopen(req)
            self.fail("Expected 400 HTTPError")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)
            self.assertIn("application/json", e.headers.get("Content-Type", ""))
            body = json.loads(e.read().decode())
            self.assertIn("error", body)

    def test_case_id_string_and_number_parsing_isolated(self):
        # Test string vs numeric case_id using isolated test-submit endpoint
        test_file = "artifacts/test_human_review_persistence.json"
        synthetic_data = {
            "metadata": {"total_cases": 1, "reviewed_count": 0, "remaining_count": 1, "accept_count": 0, "reject_count": 0, "uncertain_count": 0},
            "cases": [
                {
                    "case_id": 99905,
                    "tweet_id": 999999995,
                    "conversation_id": 999999995,
                    "text": "Synthetic test inquiry",
                    "candidate_intent": "BATTERY_DRAIN_POWER_CONSUMPTION",
                    "human_decision": None,
                    "human_intent": None,
                    "focal_grievance": None,
                    "reviewer_notes": None,
                    "reviewed": False
                }
            ]
        }
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(synthetic_data, f, indent=2)

        try:
            payload = {
                "case_id": "99905",
                "human_decision": "ACCEPT",
                "human_intent": "BATTERY_DRAIN_POWER_CONSUMPTION",
                "focal_grievance": "Isolated test grievance",
                "reviewer_notes": "Isolated test note"
            }
            req = urllib.request.Request(
                f"{BASE_URL}/api/review/test-submit",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                self.assertIn("application/json", resp.headers.get("Content-Type", ""))
                result = json.loads(resp.read().decode())
                self.assertTrue(result["success"])
                self.assertEqual(result["case"]["case_id"], 99905)
                self.assertTrue(result["case"]["reviewed"])
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_backups_endpoint_returns_json(self):
        req = urllib.request.Request(f"{BASE_URL}/api/review/backups", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))
            data = json.loads(resp.read().decode())
            self.assertIn("backups", data)
            self.assertGreaterEqual(len(data["backups"]), 1)

    def test_persisted_cases_state(self):
        req = urllib.request.Request(f"{BASE_URL}/api/review/cases", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            meta = data["metadata"]
            self.assertEqual(meta["total_cases"], 170)
            self.assertEqual(meta["reviewed_count"], 170)
            self.assertEqual(meta["remaining_count"], 0)
            self.assertEqual(meta["accept_count"], 115)
            self.assertEqual(meta["reject_count"], 55)
            self.assertEqual(meta["uncertain_count"], 0)

            case2 = next(c for c in data["cases"] if c["case_id"] == 2)
            case3 = next(c for c in data["cases"] if c["case_id"] == 3)
            case5 = next(c for c in data["cases"] if c["case_id"] == 5)

            # Case 002: approved human label -> ACCEPT / BATTERY
            self.assertTrue(case2["reviewed"])
            self.assertEqual(case2["human_decision"], "ACCEPT")
            self.assertEqual(case2["human_intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
            self.assertEqual(case2.get("provenance"), "HUMAN_REVIEWED_BY_USER")

            # Case 003: recovered from chat -> ACCEPT / BATTERY
            self.assertTrue(case3["reviewed"])
            self.assertEqual(case3["human_decision"], "ACCEPT")
            self.assertEqual(case3["human_intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")

            # Case 005: recovered from chat -> REJECT / PERFORMANCE
            self.assertTrue(case5["reviewed"])
            self.assertEqual(case5["human_decision"], "REJECT")
            self.assertEqual(case5["human_intent"], "PERFORMANCE_SLOWDOWN_LATENCY")

if __name__ == "__main__":
    unittest.main()
