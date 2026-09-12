"""Trust-Gated Dual-Track End-to-End Pipeline for AppleSupport.

Orchestrates:
1. Intent Classification with Ambiguity Flagging
2. Leakage-Safe Provenance-Aware Historical Evidence Retrieval
3. Evidence Quality, Consistency, and Answerability Gates
4. Risk and Safety Escalation Gate
5. Evidence-Grounded Response Generation with Citations
6. Claim Extraction and Claim-Evidence Groundedness Verification
7. Dual-Track AUTO vs HUMAN Decision Arbitration
"""

from typing import Dict, Any, Optional
from src.taxonomy.classifier import IntentClassifier
from src.retrieval.evidence_store import EvidenceStore
from src.retrieval.historical_search import LeakageSafeRetriever
from src.trust.evidence_gates import EvidenceGates
from src.safety.risk_gate import RiskGate
from src.generation.generator import EvidenceGroundedGenerator
from src.trust.claim_verifier import ClaimVerifier
from src.trust.decision_arbiter import DecisionArbiter


class TrustGatedPipeline:
    """Production Dual-Track Support System with Multi-Layer Trust Gates."""

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        retriever: Optional[LeakageSafeRetriever] = None
    ):
        self.evidence_store = evidence_store or EvidenceStore()
        self.retriever = retriever or LeakageSafeRetriever(self.evidence_store)
        self.classifier = IntentClassifier()
        self.generator = EvidenceGroundedGenerator()

    def process(
        self,
        query_text: str,
        conversation_id: Optional[int] = None,
        tweet_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute the complete trust-gated processing loop on a customer inquiry."""
        # Step 1: Intent Classification & Focal Grievance
        intent_result = self.classifier.classify(query_text)
        predicted_intent = intent_result["intent"]

        # Step 2: Risk and Safety Screening
        risk_result = RiskGate.evaluate(query_text, predicted_intent)

        # Step 3: Leakage-Safe Historical Evidence Retrieval
        retrieval_result = self.retriever.search(
            query_text=query_text,
            predicted_intent=predicted_intent,
            exclude_conversation_id=conversation_id,
            exclude_tweet_id=tweet_id,
            top_k=3
        )
        retrieved_evidence = retrieval_result["results"]

        # Step 4: Evidence Quality, Consistency, and Answerability Gates
        gates_result = EvidenceGates.evaluate_all(
            query_text=query_text,
            predicted_intent=predicted_intent,
            retrieved_evidence=retrieved_evidence
        )

        # Step 5: Evidence-Grounded Response Generation
        gen_result = self.generator.generate(
            query_text=query_text,
            predicted_intent=predicted_intent,
            evidence_items=retrieved_evidence,
            risk_evaluation=risk_result,
            gates_evaluation=gates_result
        )

        # Step 6: Claim Extraction and Groundedness Verification
        claim_result = ClaimVerifier.verify(
            response_text=gen_result["response_text"],
            evidence_items=retrieved_evidence,
            is_abstention=gen_result.get("is_abstention", False)
        )

        # Step 7: Dual-Track Arbitration (AUTO vs HUMAN Escalation)
        arbiter_result = DecisionArbiter.arbitrate(
            intent_result=intent_result,
            gates_result=gates_result,
            risk_result=risk_result,
            claim_result=claim_result
        )

        return {
            "query": query_text,
            "conversation_id": conversation_id,
            "tweet_id": tweet_id,
            "intent": intent_result,
            "risk": risk_result,
            "retrieval": {
                "results_count": len(retrieved_evidence),
                "leakage_prevented_count": retrieval_result["leakage_prevented_count"],
                "top_evidence_id": retrieved_evidence[0]["evidence_id"] if retrieved_evidence else None
            },
            "gates": gates_result,
            "generation": gen_result,
            "claims": claim_result,
            "decision": arbiter_result
        }
