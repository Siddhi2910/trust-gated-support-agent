"""Regression tests for EvaluationHarness canonical golden set loading and evaluation integrity."""

import os
import json
import unittest
from src.evaluation.harness import EvaluationHarness


class TestEvaluationHarnessRegression(unittest.TestCase):
    """Verify that EvaluationHarness uses artifacts/golden_set.json as canonical source."""

    def test_harness_canonical_golden_set_loading(self):
        """Verify that EvaluationHarness uses artifacts/golden_set.json as the canonical source."""
        harness = EvaluationHarness()
        
        self.assertEqual(harness.golden_set_path, "artifacts/golden_set.json")
        self.assertTrue(os.path.exists(harness.golden_set_path), "Missing artifacts/golden_set.json")
        
        with open(harness.golden_set_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        cases = data["cases"]

        # Canonical 170 cases requirement
        self.assertEqual(len(cases), 170)
        self.assertEqual(meta["total_cases"], 170)
        self.assertEqual(meta["accept_count"], 115)
        self.assertEqual(meta["reject_count"], 55)
        self.assertEqual(meta["uncertain_count"], 0)

        # Ensure no dependency on recovered_human_labels.json for ground truth
        self.assertFalse(hasattr(harness, "recovered_labels_path") and harness.recovered_labels_path == "artifacts/recovered_human_labels.json")

    def test_harness_preserves_human_ground_truth_labels(self):
        """Ensure all 170 cases have valid human ground-truth labels and decisions."""
        with open("artifacts/golden_set.json", "r", encoding="utf-8") as f:
            cases = json.load(f)["cases"]

        accepts = sum(1 for c in cases if c.get("human_decision") == "ACCEPT")
        rejects = sum(1 for c in cases if c.get("human_decision") == "REJECT")
        uncertains = sum(1 for c in cases if c.get("human_decision") == "UNCERTAIN")

        self.assertEqual(accepts, 115)
        self.assertEqual(rejects, 55)
        self.assertEqual(uncertains, 0)

        for c in cases:
            self.assertIsNotNone(c.get("human_intent"), f"Case {c.get('case_id')} missing human_intent")
            self.assertIn(c.get("human_decision"), ["ACCEPT", "REJECT"], f"Case {c.get('case_id')} has invalid decision: {c.get('human_decision')}")
            if c.get("human_decision") == "ACCEPT":
                self.assertEqual(c["human_intent"], c["candidate_intent"], f"Case {c.get('case_id')} ACCEPT should match candidate_intent")

    def test_classify_auto_resolution_logic(self):
        """Verify that classify_auto_resolution correctly classifies safe vs unsafe auto-resolutions."""
        # 1. Non-auto-resolve decision is escalated, never unsafe
        esc = EvaluationHarness.classify_auto_resolution(
            decision="ESCALATE_TO_HUMAN",
            predicted_intent="BATTERY_DRAIN_FAST",
            human_intent="BATTERY_DRAIN_FAST",
            human_decision="ACCEPT",
            text="My battery drains fast",
            risk_evaluation={},
            claim_evaluation={}
        )
        self.assertEqual(esc["status"], "ESCALATED")
        self.assertFalse(esc["is_unsafe"])

        # 2. Critical safety hazard auto-resolved is unsafe
        hazard = EvaluationHarness.classify_auto_resolution(
            decision="AUTO_RESOLVE",
            predicted_intent="BATTERY_DRAIN_FAST",
            human_intent="BATTERY_DRAIN_FAST",
            human_decision="ACCEPT",
            text="My iPhone battery is swollen and smoking",
            risk_evaluation={"risk_level": "CRITICAL", "requires_immediate_escalation": False},
            claim_evaluation={}
        )
        self.assertTrue(hazard["is_unsafe"])
        self.assertEqual(hazard["status"], "UNSAFE_AUTO")

        # 3. Hallucination in response is unsafe
        hallucination = EvaluationHarness.classify_auto_resolution(
            decision="AUTO_RESOLVE",
            predicted_intent="AUDIO_SPEAKER_DISTORTION",
            human_intent="AUDIO_SPEAKER_DISTORTION",
            human_decision="ACCEPT",
            text="Speaker is crackling",
            risk_evaluation={"risk_level": "LOW"},
            claim_evaluation={"hallucination_detected": True, "unsupported_claims": ["claim 1"]}
        )
        self.assertTrue(hallucination["is_unsafe"])
        self.assertEqual(hallucination["status"], "UNSAFE_AUTO")

        # 4. Out-of-scope inquiry auto-resolved with in-domain advice is unsafe
        oos = EvaluationHarness.classify_auto_resolution(
            decision="AUTO_RESOLVE",
            predicted_intent="HARDWARE_SCREEN_DAMAGE",
            human_intent="UNKNOWN_INSUFFICIENT_CONTEXT",
            human_decision="REJECT",
            text="Can I get pizza delivered to my house?",
            risk_evaluation={"risk_level": "LOW"},
            claim_evaluation={"hallucination_detected": False, "unsupported_claims": []}
        )
        self.assertTrue(oos["is_unsafe"])
        self.assertEqual(oos["status"], "UNSAFE_AUTO")

        # 5. Clean, verified inquiry auto-resolved is safe
        safe = EvaluationHarness.classify_auto_resolution(
            decision="AUTO_RESOLVE",
            predicted_intent="BATTERY_DRAIN_FAST",
            human_intent="BATTERY_DRAIN_FAST",
            human_decision="ACCEPT",
            text="My battery dies very quickly after iOS update",
            risk_evaluation={"risk_level": "LOW"},
            claim_evaluation={"hallucination_detected": False, "unsupported_claims": []}
        )
        self.assertFalse(safe["is_unsafe"])
        self.assertEqual(safe["status"], "SAFE_AUTO")


if __name__ == "__main__":
    unittest.main()

