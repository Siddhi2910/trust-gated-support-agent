"""Evaluation Baselines for Customer Support Automation Benchmark.

Baseline 1: Naive Un-gated Keyword Matcher (answers everything, zero trust gating).
Baseline 2: Standard RAG Pipeline (retrieves and answers with no consistency or claim gates).
"""

from typing import Dict, Any, List, Optional
from src.taxonomy.classifier import IntentClassifier
from src.retrieval.historical_search import LeakageSafeRetriever
from src.generation.generator import EvidenceGroundedGenerator


class Baseline1NaiveKeyword:
    """Baseline 1: Simple un-gated keyword matching with zero trust or safety gating."""

    def __init__(self):
        self.classifier = IntentClassifier()

    def process(self, query_text: str) -> Dict[str, Any]:
        intent_res = self.classifier.classify(query_text)
        # Always attempts to auto-resolve blindly
        return {
            "system": "BASELINE_1_NAIVE_KEYWORD",
            "query": query_text,
            "predicted_intent": intent_res["intent"],
            "decision": "AUTO_RESOLVE",  # Blind auto-resolve
            "escalated": False,
            "safety_checked": False,
            "claim_verified": False,
            "response_text": f"Thank you for contacting Apple Support. Regarding your {intent_res['intent']}, please restart your device."
        }


class Baseline2StandardRAG:
    """Baseline 2: Standard RAG pipeline without consistency, answerability, or claim verification gates."""

    def __init__(self, retriever: Optional[LeakageSafeRetriever] = None):
        self.classifier = IntentClassifier()
        self.retriever = retriever or LeakageSafeRetriever()
        self.generator = EvidenceGroundedGenerator()

    def process(self, query_text: str) -> Dict[str, Any]:
        intent_res = self.classifier.classify(query_text)
        retrieval = self.retriever.search(query_text, predicted_intent=intent_res["intent"], top_k=2)

        # Baseline 2 does NOT run evidence consistency gate, answerability gate, risk gate, or claim verification
        gen_res = self.generator.generate(
            query_text=query_text,
            predicted_intent=intent_res["intent"],
            evidence_items=retrieval["results"],
            risk_evaluation=None,
            gates_evaluation=None
        )

        # Naively auto-resolves whenever ANY evidence was found, else escalates
        decision = "AUTO_RESOLVE" if retrieval["results"] else "ESCALATE_TO_HUMAN"

        return {
            "system": "BASELINE_2_STANDARD_RAG",
            "query": query_text,
            "predicted_intent": intent_res["intent"],
            "decision": decision,
            "escalated": decision == "ESCALATE_TO_HUMAN",
            "safety_checked": False,
            "evidence_used": gen_res.get("evidence_used", []),
            "claim_verified": False,
            "response_text": gen_res["response_text"]
        }
