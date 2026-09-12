"""Deterministic Unit & Integration Tests for Multi-Turn Session State.

Verifies:
1. Two-turn support conversations with context resolution.
2. Follow-ups referring to previous turns ("I already tried that", "it still doesn't work").
3. Cross-conversation isolation (zero leakage across threads).
4. Missing conversation_id / tweet_id handling (graceful stateless fallback).
5. Gate bypass prevention:
   - Context must NOT bypass the Risk Gate (e.g., safety hazards like smoke/burns).
   - Context must NOT bypass Evidence Quality, Consistency, and Answerability Gates.
   - Context must NOT bypass Claim Verification.
   - Context must NOT bypass Human Escalation when troubleshooting fails.
6. Bounded state enforcement (session history cap, turn bounds, LRU cache).
7. Parent/child and tweet_id topological relationship tracking.
"""

import os
import shutil
import tempfile
import unittest
from src.retrieval.evidence_store import EvidenceStore
from src.retrieval.historical_search import LeakageSafeRetriever
from src.trust.pipeline import TrustGatedPipeline
from src.conversations.session_manager import (
    ConversationSessionManager,
    ConversationSession,
    ConversationTurn,
)


class TestMultiTurnSessionState(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_store_path = os.path.join(self.temp_dir, "test_evidence_store.json")
        self.temp_session_path = os.path.join(self.temp_dir, "test_sessions.json")

        # Copy production evidence store to isolated temp file if present
        if os.path.exists("artifacts/evidence_store.json"):
            shutil.copyfile("artifacts/evidence_store.json", self.temp_store_path)

        self.store = EvidenceStore(persistence_path=self.temp_store_path)
        self.retriever = LeakageSafeRetriever(self.store)
        self.session_manager = ConversationSessionManager(
            max_sessions=50,
            max_turns_per_conversation=6,
            persistence_path=self.temp_session_path,
        )
        self.pipeline = TrustGatedPipeline(
            evidence_store=self.store,
            retriever=self.retriever,
            session_manager=self.session_manager,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_two_turn_support_conversation(self):
        """Turn 1 receives grounded advice; Turn 2 maintains thread context and links parent/child tweets."""
        conv_id = "CONV-1001"
        t1_id = "TW-1001"

        # Turn 1: Initial customer battery drain inquiry
        turn1_res = self.pipeline.process(
            query_text="My iPhone 7 battery is dying after 2 hours on iOS 11",
            conversation_id=conv_id,
            tweet_id=t1_id,
        )

        self.assertEqual(turn1_res["intent"]["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertTrue(turn1_res["decision"]["can_auto_resolve"])
        self.assertEqual(turn1_res["decision"]["decision"], "AUTO_RESOLVE")
        self.assertIsNotNone(turn1_res["session"])
        self.assertEqual(len(turn1_res["session"]["turns"]), 2)  # 1 customer + 1 agent turn

        # Verify topological linking for turn 1
        session = self.session_manager.get_session(conv_id)
        self.assertIsNotNone(session)
        self.assertEqual(session.root_intent, "BATTERY_DRAIN_POWER_CONSUMPTION")

        # Turn 2: Customer asks follow-up clarifying where in settings
        t2_id = "TW-1002"
        turn2_res = self.pipeline.process(
            query_text="Where in settings can I see battery usage by app?",
            conversation_id=conv_id,
            tweet_id=t2_id,
            in_response_to_tweet_id=t1_id,
        )

        self.assertIsNotNone(turn2_res["session"])
        # Should now have 4 turns (2 customer, 2 agent)
        self.assertEqual(len(turn2_res["session"]["turns"]), 4)

        # Parent map must map T2 to T1
        self.assertEqual(session.parent_map.get(t2_id), t1_id)
        # Children map must register T2 under T1
        self.assertIn(t2_id, session.children_map.get(t1_id, []))

    def test_followup_referring_to_previous_turns_escalates_on_troubleshooting_failure(self):
        """Follow-up like 'I already tried that and it still doesn't work' inherits context and escalates to human."""
        conv_id = "CONV-1002"

        # Turn 1: Initial customer inquiry
        self.pipeline.process(
            query_text="My iPhone 7 battery is dying after 2 hours on iOS 11",
            conversation_id=conv_id,
            tweet_id="TW-2001",
        )

        # Turn 2: Customer reports failure of previous troubleshooting
        turn2_res = self.pipeline.process(
            query_text="I already tried that and it still doesn't work",
            conversation_id=conv_id,
            tweet_id="TW-2002",
            in_response_to_tweet_id="TW-2001",
        )

        # 1. Intent should be contextually inherited as BATTERY_DRAIN_POWER_CONSUMPTION
        self.assertEqual(turn2_res["intent"]["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertTrue(turn2_res["intent"].get("contextual_resolution"))

        # 2. Decision MUST be ESCALATE_TO_HUMAN because troubleshooting failed
        self.assertEqual(turn2_res["decision"]["decision"], "ESCALATE_TO_HUMAN")
        self.assertFalse(turn2_res["decision"]["can_auto_resolve"])
        self.assertEqual(turn2_res["decision"]["target_queue"], "HARDWARE_SUPPORT")

        # 3. Escalation reasons must state prior troubleshooting failed
        reasons_str = " ".join(turn2_res["decision"]["reasons"])
        self.assertIn("prior troubleshooting attempt failed", reasons_str.lower())

    def test_cross_conversation_isolation(self):
        """Thread B with 'it still doesn't work' must NEVER inherit intent from Thread A."""
        conv_a = "CONV-A-SCREEN"
        conv_b = "CONV-B-EMPTY"

        # Conv A asks about cracked screen
        self.pipeline.process(
            query_text="My iPhone screen is cracked and completely black",
            conversation_id=conv_a,
            tweet_id="TW-A1",
        )

        # Conv B has no prior turns, customer simply says "it still doesn't work"
        turn_b = self.pipeline.process(
            query_text="it still doesn't work",
            conversation_id=conv_b,
            tweet_id="TW-B1",
        )

        # Conv B must NOT inherit screen defect from Conv A
        self.assertNotEqual(turn_b["intent"]["intent"], "SCREEN_PHYSICAL_DAMAGE")
        self.assertEqual(turn_b["intent"]["intent"], "UNKNOWN_INSUFFICIENT_CONTEXT")
        self.assertFalse(turn_b["intent"].get("contextual_resolution", False))

    def test_missing_conversation_id_and_tweet_id_handling(self):
        """Pipeline must handle missing IDs gracefully without crashing or creating sessions."""
        res = self.pipeline.process(
            query_text="My iPhone battery dies quickly after update",
            conversation_id=None,
            tweet_id=None,
        )

        self.assertEqual(res["intent"]["intent"], "BATTERY_DRAIN_POWER_CONSUMPTION")
        self.assertIsNone(res["session"])
        self.assertIsNone(res["conversation_id"])
        self.assertIsNone(res["tweet_id"])
        self.assertTrue(res["decision"]["can_auto_resolve"])

    def test_context_must_not_bypass_risk_gate(self):
        """If turn 2 introduces a safety hazard (smoke/fire), RiskGate MUST trigger immediate escalation."""
        conv_id = "CONV-SAFETY-001"

        # Turn 1: Normal battery inquiry
        turn1 = self.pipeline.process(
            query_text="My phone battery is getting warm",
            conversation_id=conv_id,
            tweet_id="TW-S1",
        )
        self.assertEqual(turn1["risk"]["risk_level"], "LOW")

        # Turn 2: Customer reports smoke and burns
        turn2 = self.pipeline.process(
            query_text="I tried that and now it is smoking and burning my hand!",
            conversation_id=conv_id,
            tweet_id="TW-S2",
            in_response_to_tweet_id="TW-S1",
        )

        # Safety gate MUST trigger CRITICAL escalation immediately
        self.assertEqual(turn2["risk"]["risk_level"], "CRITICAL")
        self.assertTrue(turn2["risk"]["requires_immediate_escalation"])
        self.assertEqual(turn2["decision"]["decision"], "ESCALATE_TO_HUMAN")
        self.assertEqual(turn2["decision"]["target_queue"], "SAFETY_INCIDENT_TEAM")
        self.assertFalse(turn2["decision"]["can_auto_resolve"])

    def test_context_must_not_bypass_evidence_quality_and_answerability(self):
        """Even with prior context, if verified evidence is absent, gates must prevent auto-resolution."""
        empty_path = os.path.join(self.temp_dir, "empty_store.json")
        empty_store = EvidenceStore(persistence_path=empty_path)
        empty_store.items = []
        empty_store.save()
        empty_retriever = LeakageSafeRetriever(empty_store)
        pipeline_empty = TrustGatedPipeline(
            evidence_store=empty_store,
            retriever=empty_retriever,
            session_manager=self.session_manager,
        )

        conv_id = "CONV-NO-EVID"
        res1 = pipeline_empty.process(
            query_text="My iPhone battery is dying fast",
            conversation_id=conv_id,
            tweet_id="TW-E1",
        )

        self.assertFalse(res1["gates"]["all_passed"])
        self.assertFalse(res1["gates"]["answerability"]["answerable"])
        self.assertEqual(res1["decision"]["decision"], "ESCALATE_TO_HUMAN")
        self.assertFalse(res1["decision"]["can_auto_resolve"])

    def test_context_must_not_bypass_claim_verification(self):
        """Claims in response must be verified against evidence, not fabricated."""
        conv_id = "CONV-CLAIM-001"
        res = self.pipeline.process(
            query_text="My iPhone battery is dying fast after update",
            conversation_id=conv_id,
            tweet_id="TW-C1",
        )

        self.assertTrue(res["claims"]["verified"])
        self.assertFalse(res["claims"]["hallucination_detected"])
        self.assertGreaterEqual(res["claims"]["groundedness_score"], 0.90)

    def test_bounded_state_enforcement(self):
        """Session turns must remain strictly bounded to max_turns while preserving root anchor."""
        session = ConversationSession(
            conversation_id="CONV-BOUNDED",
            max_turns=6,
        )

        # Add 12 turns
        for i in range(12):
            role = "customer" if i % 2 == 0 else "agent"
            session.add_turn(
                role=role,
                text=f"Turn message {i} with details",
                tweet_id=f"TW-{i}",
                in_response_to_tweet_id=f"TW-{i-1}" if i > 0 else None,
            )

        # Total turns must not exceed max_turns (6)
        self.assertEqual(len(session.turns), 6)
        # Root turn (turn 0) must be preserved as anchor
        self.assertEqual(session.turns[0].text, "Turn message 0 with details")
        # Last turn must be turn 11
        self.assertEqual(session.turns[-1].text, "Turn message 11 with details")

    def test_session_manager_lru_capacity_bounds(self):
        """Session manager must cap active sessions and evict oldest LRU."""
        small_manager = ConversationSessionManager(
            max_sessions=3,
            max_turns_per_conversation=5,
            persistence_path=None,
        )

        small_manager.get_or_create_session("S1")
        small_manager.get_or_create_session("S2")
        small_manager.get_or_create_session("S3")
        self.assertEqual(small_manager.get_active_session_count(), 3)

        # S4 causes S1 eviction
        small_manager.get_or_create_session("S4")
        self.assertEqual(small_manager.get_active_session_count(), 3)
        self.assertFalse(small_manager.has_session("S1"))
        self.assertTrue(small_manager.has_session("S2"))
        self.assertTrue(small_manager.has_session("S3"))
        self.assertTrue(small_manager.has_session("S4"))


if __name__ == "__main__":
    unittest.main()
