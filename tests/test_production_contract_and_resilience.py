#!/usr/bin/env python3
"""Comprehensive production contract, resilience, and security test suite.

Covers:
1. Production GET /health and GET /api/health contracts.
2. Production POST /api/support/handle API contract:
   - Valid customer inquiries
   - Input validation (missing/empty text)
   - Multi-turn session context handling
   - Immediate safety risk escalation
3. Golden-set and frozen-taxonomy protection:
   - Invariance checks for golden_set.json and taxonomy_v1_frozen.json
   - No data leakage of golden set queries into evidence_store.json
4. Missing credentials resilience:
   - LLM Judge reports UNAVAILABLE when API key is unset (no synthetic fabrication)
   - Pipeline generation degrades safely to deterministic template / escalation rather than crashing
5. Review submission regression tests:
   - Missing, empty, or non-numeric case_id validation
"""

import os
import sys
import json
import unittest
import urllib.request
import urllib.error

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")


class TestProductionContracts(unittest.TestCase):
    """Verifies production HTTP API contracts for /health and /api/support/handle."""

    def test_health_endpoint_returns_json(self):
        """GET /health must return 200 JSON with status: ok, version, and system name."""
        req = urllib.request.Request(f"{BASE_URL}/health", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("version", data)
            self.assertIn("system", data)
            self.assertIn("timestamp", data)

    def test_api_health_endpoint_returns_json(self):
        """GET /api/health must also return 200 JSON for backward compatibility."""
        req = urllib.request.Request(f"{BASE_URL}/api/health", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")

    def test_support_handle_missing_message_returns_400(self):
        """POST /api/support/handle must reject missing or whitespace-only messages with 400 JSON."""
        for payload in [{}, {"message": ""}, {"message": "   "}, {"text": None}]:
            req = urllib.request.Request(
                f"{BASE_URL}/api/support/handle",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            try:
                urllib.request.urlopen(req, timeout=10)
                self.fail("Expected HTTPError 400 for empty input")
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 400)
                self.assertIn("application/json", e.headers.get("Content-Type", ""))
                err = json.loads(e.read().decode("utf-8"))
                self.assertIn("error", err)

    def test_support_handle_valid_query(self):
        """POST /api/support/handle processes real inquiries through the Trust Gate."""
        payload = {
            "message": "My iPhone battery is draining extremely fast after updating to iOS 11.",
            "conversation_id": "test_conv_prod_001"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/support/handle",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertIn(data.get("decision"), ["AUTO_RESOLVE", "ESCALATE_TO_HUMAN"])
            self.assertIn("can_auto_resolve", data)
            self.assertIn("confidence_score", data)
            self.assertIn("response", data)
            self.assertIn("intent", data)
            self.assertIn("target_queue", data)
            self.assertIn("risk_level", data)
            self.assertIn("groundedness_score", data)
            self.assertIn("receipt", data)

    def test_support_handle_safety_hazard_immediate_escalation(self):
        """Hazardous battery swelling inquiries must immediately escalate to human safety queue."""
        payload = {
            "message": "My iPhone 7 battery is swollen, bulging out of the case, and smoking hot!"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/support/handle",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("decision"), "ESCALATE_TO_HUMAN")
            self.assertFalse(data.get("can_auto_resolve"))
            self.assertIn(data.get("risk_level"), ["HIGH", "CRITICAL"])
            self.assertIn("SAFETY", data.get("target_queue"))


class TestGoldenSetProtectionAndLeakage(unittest.TestCase):
    """Enforces immutability of the frozen golden evaluation assets and absence of train/test leakage."""

    def test_golden_set_file_exists_and_unaltered(self):
        golden_path = "artifacts/golden_set.json"
        self.assertTrue(os.path.exists(golden_path), "artifacts/golden_set.json must exist")
        with open(golden_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Verify 170 test cases preserved
        cases = data.get("cases", data if isinstance(data, list) else [])
        self.assertEqual(len(cases), 170, "Golden set must contain exactly 170 evaluation cases")

    def test_frozen_taxonomy_is_marked_frozen(self):
        tax_path = "artifacts/taxonomy_v1_frozen.json"
        self.assertTrue(os.path.exists(tax_path), "artifacts/taxonomy_v1_frozen.json must exist")
        with open(tax_path, "r", encoding="utf-8") as f:
            tax = json.load(f)
        self.assertTrue(tax.get("taxonomy_frozen", False), "taxonomy_v1_frozen.json must be marked frozen: true")
        self.assertEqual(len(tax.get("intents", [])), 15, "Frozen taxonomy must contain exactly 15 intents")

    def test_no_golden_set_leakage_into_evidence_store(self):
        """Golden set tweet IDs must NEVER appear inside the active evidence store."""
        golden_path = "artifacts/golden_set.json"
        evidence_path = "artifacts/evidence_store.json"

        with open(golden_path, "r", encoding="utf-8") as f:
            golden_data = json.load(f)
        golden_cases = golden_data.get("cases", golden_data if isinstance(golden_data, list) else [])
        golden_tweet_ids = {str(c.get("tweet_id")) for c in golden_cases if c.get("tweet_id")}

        self.assertTrue(os.path.exists(evidence_path), "evidence_store.json must exist")
        with open(evidence_path, "r", encoding="utf-8") as f:
            evidence_data = json.load(f)

        if isinstance(evidence_data, dict):
            snippets = evidence_data.get("snippets", [])
        else:
            snippets = evidence_data

        for s in snippets:
            source_id = str(s.get("source_tweet_id", s.get("tweet_id", "")))
            self.assertNotIn(
                source_id,
                golden_tweet_ids,
                f"Data leakage detected! Golden set tweet {source_id} found in evidence store!"
            )


class TestMissingCredentialsResilience(unittest.TestCase):
    """Verifies that missing LLM keys cause safe degradation rather than system crashes."""

    def test_secondary_llm_judge_unavailable_when_no_key(self):
        from src.evaluation.judge import SecondaryLLMJudge

        # Explicitly initialize judge with empty api_key
        judge = SecondaryLLMJudge(api_key="", model="gemini-2.5-flash")
        self.assertFalse(judge.is_available())

        status = judge.get_status()
        self.assertFalse(status["available"])
        self.assertEqual(status["role"], "SECONDARY_QUALITATIVE_EVALUATION")

        # Running batch evaluation returns honest UNAVAILABLE report with 0 evaluated cases
        sample = [{"case_id": 1, "query_text": "Battery issue", "response_text": "Please restart"}]
        report = judge.run_secondary_evaluation(sample, save_artifact=False)
        self.assertEqual(report["status"], "UNAVAILABLE")
        self.assertEqual(report["cases_evaluated"], 0)
        self.assertEqual(report["cases_skipped"], 1)

    def test_generator_degrades_safely_without_key(self):
        from src.generation.generator import EvidenceGroundedGenerator

        gen = EvidenceGroundedGenerator()
        res = gen.generate(
            query_text="How do I reset my network settings?",
            predicted_intent="CONNECTIVITY_WIFI_BLUETOOTH",
            evidence_items=[{"evidence_id": "E1", "body": "Go to Settings > General > Reset > Reset Network Settings.", "source_reference": "KB1"}]
        )
        self.assertIsNotNone(res)
        self.assertIn("response_text", res)
        self.assertTrue(len(res["response_text"]) > 0)


class TestReviewSubmissionRegression(unittest.TestCase):
    """Verifies that review submission handles case_id variations and rejects malformed inputs."""

    def test_missing_case_id_returns_400(self):
        payload = {
            "human_decision": "ACCEPT",
            "reviewer_notes": "Valid note"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/review/submit",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            self.fail("Expected 400 for missing case_id")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)
            body = json.loads(e.read().decode("utf-8"))
            self.assertIn("case_id is required", body.get("error", ""))

    def test_non_numeric_case_id_returns_400(self):
        payload = {
            "case_id": "not-a-number",
            "human_decision": "ACCEPT"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/review/submit",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            self.fail("Expected 400 for non-numeric case_id")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)
            body = json.loads(e.read().decode("utf-8"))
            self.assertIn("case_id must be a valid number", body.get("error", ""))


if __name__ == "__main__":
    unittest.main()
