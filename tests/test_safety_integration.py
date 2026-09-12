"""Safety Integration Tests for Trust-Gated Dual-Track System.

Verifies:
1. Unsupported claim cannot be auto-handled -> escalation
2. Failed claim verification / hallucination -> escalation
3. High intent confidence with low/unanswerable evidence -> escalation
4. Critical safety hazard -> immediate safety escalation with refusal
5. Trust receipt integrity -> accurate taxonomy and model versions
"""

import os
import shutil
import tempfile
import unittest

from src.trust.pipeline import TrustGatedPipeline
from src.retrieval.evidence_store import EvidenceStore
from src.retrieval.historical_search import LeakageSafeRetriever
from src.trust.decision_arbiter import DecisionArbiter
from src.trust.claim_verifier import ClaimVerifier
from src.safety.risk_gate import RiskGate


class TestSafetyIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_store_path = os.path.join(self.temp_dir, "test_store.json")
        if os.path.exists("artifacts/evidence_store.json"):
            shutil.copyfile("artifacts/evidence_store.json", self.temp_store_path)
        self.store = EvidenceStore(persistence_path=self.temp_store_path)
        self.retriever = LeakageSafeRetriever(self.store)
        self.pipeline = TrustGatedPipeline(evidence_store=self.store, retriever=self.retriever)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unsupported_claim_cannot_auto_handle(self):
        """When generated response contains claims unsupported by evidence, auto-resolution MUST be denied."""
        # Evidence only speaks about battery indexing time
        evidence = [{
            "evidence_id": "EVID-BATT-001",
            "title": "Post-Update Battery Drain Diagnostic & Indexing",
            "body": "Following an iOS update, background Spotlight indexing can increase battery drain for 48-72 hours. Check Settings > Battery.",
            "source_type": "OFFICIAL_KB",
            "source_reference": "HT201264",
            "intent": "BATTERY_DRAIN_POWER_CONSUMPTION"
        }]

        # Response asserts a completely unsupported replacement policy claim
        unsupported_response = (
            "We can replace your device for free at any Apple Store without an appointment today. "
            "Also check Settings > Battery for indexing."
        )

        verification = ClaimVerifier.verify(unsupported_response, evidence)
        self.assertFalse(verification["verified"], "Unsupported claim must fail verification")
        self.assertGreater(len(verification["unsupported_claims"]), 0, "Unsupported claim must be flagged")

        # Evaluate arbitration
        decision = DecisionArbiter.arbitrate(
            intent_result={"intent": "BATTERY_DRAIN_POWER_CONSUMPTION", "confidence": 0.95, "ambiguity_flag": False},
            gates_result={"all_passed": True, "quality": {"passed": True}, "consistency": {"passed": True}, "answerability": {"answerable": True}},
            risk_result={"risk_level": "LOW", "requires_immediate_escalation": False, "escalation_queue": "TIER1_SUPPORT"},
            claim_result=verification
        )

        self.assertEqual(decision["decision"], "ESCALATE_TO_HUMAN", "Must escalate when claims are unsupported")
        self.assertFalse(decision["can_auto_resolve"], "can_auto_resolve must be False")
        self.assertTrue(any("claim" in r.lower() or "unsupported" in r.lower() for r in decision["reasons"]))

    def test_failed_claim_verification_escalation(self):
        """Failed claim verification / hallucination detection forces human escalation."""
        mock_claim_result = {
            "verified": False,
            "total_claims": 2,
            "grounded_claims": 0,
            "unsupported_claims": ["Device replacement is guaranteed for all users within 1 hour."],
            "hallucination_detected": True,
            "groundedness_score": 0.0,
            "notes": "Severe hallucination of nonexistent warranty entitlement"
        }

        decision = DecisionArbiter.arbitrate(
            intent_result={"intent": "DEVICE_FREEZE_CRASH_REBOOT", "confidence": 0.98, "ambiguity_flag": False},
            gates_result={"all_passed": True},
            risk_result={"risk_level": "LOW", "requires_immediate_escalation": False},
            claim_result=mock_claim_result
        )

        self.assertEqual(decision["decision"], "ESCALATE_TO_HUMAN")
        self.assertFalse(decision["can_auto_resolve"])
        self.assertTrue(any("hallucination" in r.lower() or "claim" in r.lower() for r in decision["reasons"]))

    def test_high_intent_confidence_unanswerable_evidence_escalation(self):
        """High intent confidence (e.g. 0.96) must NOT auto-resolve if evidence is unanswerable."""
        high_conf_intent = {
            "intent": "BATTERY_DRAIN_POWER_CONSUMPTION",
            "confidence": 0.96,
            "focal_grievance": "Unusually rapid battery discharge",
            "ambiguity_flag": False
        }

        unanswerable_gates = {
            "all_passed": False,
            "quality": {"passed": True, "score": 8.0},
            "consistency": {"passed": True, "conflict_detected": False},
            "answerability": {
                "answerable": False,
                "answerability_score": 0.2,
                "reason": "Retrieved evidence does not address specific device revision"
            }
        }

        decision = DecisionArbiter.arbitrate(
            intent_result=high_conf_intent,
            gates_result=unanswerable_gates,
            risk_result={"risk_level": "LOW", "requires_immediate_escalation": False},
            claim_result={"verified": True, "groundedness_score": 1.0, "hallucination_detected": False}
        )

        self.assertEqual(decision["decision"], "ESCALATE_TO_HUMAN", "Must escalate when evidence cannot answer question")
        self.assertFalse(decision["can_auto_resolve"], "Cannot auto-resolve unanswerable query")
        self.assertTrue(any("cannot answer" in r.lower() or "answerability" in r.lower() for r in decision["reasons"]))

    def test_critical_risk_safety_hazard_escalation(self):
        """Hardware/battery swelling or smoke forces immediate safety escalation and abstention."""
        query = "My iPhone battery swelled up, cracked the case, and is smoking!"
        res = self.pipeline.process(query)

        self.assertEqual(res["risk"]["risk_level"], "CRITICAL")
        self.assertTrue(res["risk"]["requires_immediate_escalation"])
        self.assertEqual(res["decision"]["decision"], "ESCALATE_TO_HUMAN")
        self.assertFalse(res["decision"]["can_auto_resolve"])
        self.assertEqual(res["decision"]["target_queue"], "SAFETY_INCIDENT_TEAM")
        self.assertTrue(res["generation"]["is_abstention"])
        self.assertEqual(res["generation"]["generation_mode"], "SAFETY_REFUSAL_ESCALATION")

    def test_trust_receipt_metadata_and_provenance(self):
        """Trust receipt must contain exact taxonomy version, sub-model versions, and provenance audit."""
        res = self.pipeline.process("My battery is draining fast after update")
        self.assertIn("trust_receipt", res)
        receipt = res["trust_receipt"]

        self.assertEqual(receipt["taxonomy_version"], "1.0.0-frozen")
        self.assertIn("intent_classifier", receipt["model_versions"])
        self.assertIn("risk_gate", receipt["model_versions"])
        self.assertIn("generator", receipt["model_versions"])
        self.assertIn("claim_verifier", receipt["model_versions"])
        self.assertIsInstance(receipt["retrieved_evidence"], list)
        self.assertIn("excluded_untrusted_candidates_count", receipt)

    def test_battery_drain_regression_classification(self):
        """Verify demonstrated battery-drain query is correctly classified as BATTERY_DRAIN_POWER_CONSUMPTION."""
        query = "@AppleSupport My iPhone 8 battery drains from 100% to 20% in two hours after updating to iOS 11. Is there a fix?"
        intent_res = self.pipeline.classifier.classify(query)
        self.assertEqual(intent_res["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertGreaterEqual(intent_res["confidence"], 0.85)
        self.assertFalse(intent_res["ambiguity_flag"])

    def test_retrieval_intent_alignment_prevents_avoidable_conflict(self):
        """Verify retrieval aligns with predicted intent and avoids irrelevant cross-intent candidates."""
        query = "@AppleSupport My iPhone 8 battery drains from 100% to 20% in two hours after updating to iOS 11. Is there a fix?"
        retrieval = self.retriever.search(
            query_text=query,
            predicted_intent="BATTERY_DRAIN_POWER_CONSUMPTION",
            top_k=3
        )
        self.assertGreater(len(retrieval["results"]), 0)
        # All returned candidates must match the predicted intent when available
        for item in retrieval["results"]:
            self.assertEqual(item["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        
        # Ensure full pipeline does not produce avoidable consistency conflict
        pipeline_res = self.pipeline.process(query)
        self.assertFalse(pipeline_res["gates"]["consistency"]["conflict_detected"])
        self.assertEqual(pipeline_res["decision"]["decision"], "AUTO_RESOLVE")
        self.assertTrue(pipeline_res["decision"]["can_auto_resolve"])

    def test_multi_symptom_arbitration_case_2_battery_drain(self):
        """Case #2: Battery drain with reboot attempt correctly arbitrated to BATTERY_DRAIN_POWER_CONSUMPTION."""
        query = "@AppleSupport I’ve done 2 hard resets and update the software. I can’t go anywhere without an extra battery but even that can’t reboot"
        res = self.pipeline.process(query)
        self.assertEqual(res["intent"]["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertGreaterEqual(res["intent"]["confidence"], 0.85)

    def test_multi_symptom_arbitration_case_4_battery_connectivity(self):
        """Case #4: Battery drain + cellular/wifi correctly classified and escalated due to multi-symptom ambiguity."""
        query = "@AppleSupport My battery is draining quickly on my iPhone 6s when I use 3G. I lose like 5% a minute. But it’s better when I use my WiFi."
        res = self.pipeline.process(query)
        self.assertEqual(res["intent"]["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        # Multi-symptom comparison escalates safely to human
        self.assertEqual(res["decision"]["decision"], "ESCALATE_TO_HUMAN")
        self.assertFalse(res["decision"]["can_auto_resolve"])

    def test_multi_symptom_arbitration_case_9_freeze_slowdown(self):
        """Case #9: Freeze/crash + slow to open apps arbitrated to DEVICE_FREEZE_CRASH_REBOOT."""
        query = "@AppleSupport absolutely hate the new update. I don't even want to use my iPhone. Keeps freezing and very slow to open apps. Fix ASAP plz!"
        res = self.pipeline.process(query)
        self.assertEqual(res["intent"]["intent"], "DEVICE_FREEZE_CRASH_REBOOT")
        self.assertGreaterEqual(res["intent"]["confidence"], 0.85)

    def test_multi_symptom_arbitration_case_130_freeze_glitch(self):
        """Case #130: System freeze + glitch arbitrated to DEVICE_FREEZE_CRASH_REBOOT."""
        query = "@116333 the the most recent update is so bad I sold my @115858 stock. Slow/ glitch/ freezing. Please stop running company into ground!!!!!"
        res = self.pipeline.process(query)
        self.assertEqual(res["intent"]["intent"], "DEVICE_FREEZE_CRASH_REBOOT")
        self.assertGreaterEqual(res["intent"]["confidence"], 0.85)

    def test_multi_symptom_arbitration_case_137_login_data_loss(self):
        """Case #137: iCloud login failure + lost contacts arbitrated to DATA_LOSS_RECOVERY."""
        query = "Hello @AppleSupport , I can't login to my iCloud account [with right password], I also can't backup my contacts and I've lost them."
        res = self.pipeline.process(query)
        self.assertEqual(res["intent"]["intent"], "DATA_LOSS_RECOVERY")
        self.assertGreaterEqual(res["intent"]["confidence"], 0.85)


if __name__ == "__main__":
    unittest.main()
