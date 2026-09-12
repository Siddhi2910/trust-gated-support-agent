"""Unit and Integration Tests for Trust-Gated Dual-Track Backend Pipeline.

Verifies:
1. Taxonomy Intent Classifier & Ambiguity Flagging
2. Leakage-Safe Historical Retriever (conversation and tweet leakage rejection)
3. Provenance-Aware Evidence Store
4. Evidence Quality, Consistency, and Answerability Gates
5. Risk & Safety Escalation Gate (smoke/burns, fraud, legal)
6. Claim Extraction and Verification
7. Dual-Track Decision Arbiter (AUTO vs HUMAN)
8. Evidence Promotion Workflow
9. Comparative Baselines (Baseline 1 & Baseline 2)
10. End-to-End Pipeline Execution
"""

import unittest
from src.taxonomy.classifier import IntentClassifier
from src.retrieval.evidence_store import EvidenceStore
from src.retrieval.historical_search import LeakageSafeRetriever
from src.trust.evidence_gates import EvidenceGates
from src.safety.risk_gate import RiskGate
from src.generation.generator import EvidenceGroundedGenerator
from src.trust.claim_verifier import ClaimVerifier
from src.trust.decision_arbiter import DecisionArbiter
from src.trust.evidence_promotion import EvidencePromotionManager
from src.evaluation.baselines import Baseline1NaiveKeyword, Baseline2StandardRAG
from src.trust.pipeline import TrustGatedPipeline


class TestBackendPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = TrustGatedPipeline()
        self.classifier = IntentClassifier()
        self.store = EvidenceStore()
        self.retriever = LeakageSafeRetriever(self.store)

    def test_intent_classifier_battery_drain(self):
        res = self.classifier.classify("My iPhone battery is dying after 2 hours")
        self.assertEqual(res["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertGreaterEqual(res["confidence"], 0.85)

    def test_intent_classifier_unknown_insufficient_context(self):
        res = self.classifier.classify("help please")
        self.assertEqual(res["intent"], "UNKNOWN_INSUFFICIENT_CONTEXT")

    def test_risk_gate_safety_hazard(self):
        res = RiskGate.evaluate("The battery is swollen and smoking!")
        self.assertEqual(res["risk_level"], "CRITICAL")
        self.assertTrue(res["requires_immediate_escalation"])
        self.assertEqual(res["escalation_queue"], "SAFETY_INCIDENT_TEAM")

    def test_risk_gate_legal_threat(self):
        res = RiskGate.evaluate("I will hire a lawyer and sue Apple for this")
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertTrue(res["requires_immediate_escalation"])
        self.assertEqual(res["escalation_queue"], "EXECUTIVE_RELATIONS")

    def test_retriever_leakage_prevention(self):
        # Add item with known conversation_id
        test_conv_id = 999999
        self.store.items.append({
            "evidence_id": "EVID-TEST-LEAK",
            "intent": "BATTERY_DRAIN_POWER_CONSUMPTION",
            "title": "Leakage Test Unit",
            "body": "This is a test resolution for conversation 999999.",
            "source_type": "HISTORICAL_AGENT_RESOLUTION",
            "source_reference": "TWEET-123",
            "source_conversation_id": test_conv_id,
            "verification_status": "VERIFIED",
            "tags": ["battery"]
        })

        # Search with same conversation_id excluded
        res = self.retriever.search(
            query_text="battery test",
            exclude_conversation_id=test_conv_id
        )
        # Verify excluded item is not in results
        result_ids = [r["evidence_id"] for r in res["results"]]
        self.assertNotIn("EVID-TEST-LEAK", result_ids)
        self.assertGreaterEqual(res["leakage_prevented_count"], 1)

    def test_evidence_gates_quality_and_answerability(self):
        # Battery evidence against battery query -> pass
        battery_evidence = self.store.get_by_intent("BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertTrue(len(battery_evidence) > 0)

        gates = EvidenceGates.evaluate_all(
            query_text="My battery drains fast",
            predicted_intent="BATTERY_DRAIN_POWER_CONSUMPTION",
            retrieved_evidence=[{
                "evidence_id": battery_evidence[0]["evidence_id"],
                "intent": battery_evidence[0]["intent"],
                "body": battery_evidence[0]["body"],
                "score": 10.0
            }]
        )
        self.assertTrue(gates["all_passed"])
        self.assertTrue(gates["answerability"]["answerable"])

    def test_claim_verifier_hallucination_detection(self):
        # Substantive claims with zero evidence -> hallucination
        res = ClaimVerifier.verify(
            response_text="Apple will send you a free iPhone 15 Pro Max tomorrow.",
            evidence_items=[]
        )
        self.assertFalse(res["verified"])
        self.assertTrue(res["hallucination_detected"])
        self.assertEqual(res["groundedness_score"], 0.0)

    def test_end_to_end_pipeline_auto_resolution(self):
        res = self.pipeline.process("How do I request a refund for an App Store charge?")
        self.assertEqual(res["intent"]["intent"], "BILLING_CHARGE_REFUND_DISPUTE")
        self.assertEqual(res["decision"]["decision"], "AUTO_RESOLVE")
        self.assertTrue(res["decision"]["can_auto_resolve"])
        self.assertIn("[Ref: HT204084]", res["generation"]["citations"])

    def test_end_to_end_pipeline_safe_escalation(self):
        res = self.pipeline.process("My charger melted and started smoking in the wall socket")
        self.assertEqual(res["decision"]["decision"], "ESCALATE_TO_HUMAN")
        self.assertEqual(res["decision"]["target_queue"], "SAFETY_INCIDENT_TEAM")
        self.assertTrue(res["generation"]["is_abstention"])

    def test_evidence_promotion_workflow(self):
        promo = EvidencePromotionManager(self.store)
        cand_id = promo.submit_candidate(
            intent="CONNECTIVITY_WIFI_BLUETOOTH",
            title="Bluetooth Audio Stutter Fix",
            body="Reset Bluetooth cache by toggling Airplane Mode.",
            source_reference="AGENT-REPLY-7788",
            submitted_by="test_harvester"
        )
        self.assertTrue(cand_id.startswith("EVID-CAND-"))

        # Promote to VERIFIED
        res = promo.promote_evidence(
            evidence_id=cand_id,
            reviewer_id="human_domain_expert",
            decision="PROMOTE_TO_VERIFIED",
            reviewer_notes="Verified against engineering standard"
        )
        self.assertEqual(res["new_status"], "VERIFIED")

    def test_baselines_execution(self):
        b1 = Baseline1NaiveKeyword()
        b2 = Baseline2StandardRAG(self.retriever)

        out1 = b1.process("My phone is smoking")
        self.assertEqual(out1["decision"], "AUTO_RESOLVE")  # Naive baseline fails to escalate

        out2 = b2.process("Why does battery drain fast?")
        self.assertIn("response_text", out2)


if __name__ == "__main__":
    unittest.main()
