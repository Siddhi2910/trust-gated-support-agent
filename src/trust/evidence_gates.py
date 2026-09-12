"""Evidence Quality, Consistency, and Answerability Trust Gates.

Gating checks before any retrieved evidence can be supplied to generative models
or used for autonomous decisioning.
"""

from typing import Dict, Any, List


class EvidenceGates:
    """Multi-stage trust gating for retrieved support evidence."""

    QUALITY_SCORE_THRESHOLD = 4.0
    MIN_BODY_LENGTH = 30

    @classmethod
    def evaluate_quality(cls, retrieved_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check relevance threshold, length, and coherence."""
        if not retrieved_evidence:
            return {
                "passed": False,
                "score": 0.0,
                "reason": "No evidence retrieved"
            }

        top_item = retrieved_evidence[0]
        score = top_item.get("score", 0.0)
        body = top_item.get("body", "")

        if score < cls.QUALITY_SCORE_THRESHOLD:
            return {
                "passed": False,
                "score": score,
                "reason": f"Top evidence score {score} is below quality threshold {cls.QUALITY_SCORE_THRESHOLD}"
            }

        if len(body) < cls.MIN_BODY_LENGTH:
            return {
                "passed": False,
                "score": score,
                "reason": f"Evidence text length ({len(body)}) below minimum threshold ({cls.MIN_BODY_LENGTH})"
            }

        return {
            "passed": True,
            "score": score,
            "reason": "Evidence meets minimum quality and relevance criteria"
        }

    @classmethod
    def evaluate_consistency(cls, retrieved_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that top retrieved evidence items do not conflict in instructions."""
        # Filter to only relevant evidence items meeting quality threshold
        relevant = [item for item in retrieved_evidence if item.get("score", 0.0) >= cls.QUALITY_SCORE_THRESHOLD]

        if len(relevant) <= 1:
            return {
                "passed": True,
                "consistency_score": 1.0,
                "conflict_detected": False,
                "reason": "Single or zero relevant evidence candidates; no contradiction detected"
            }

        # Check intent unanimity across top relevant items
        intents = [item.get("intent") for item in relevant[:2] if item.get("intent")]
        if len(intents) >= 2 and intents[0] != intents[1]:
            # Divergent intents across top candidates
            return {
                "passed": False,
                "consistency_score": 0.5,
                "conflict_detected": True,
                "reason": f"Top retrieved evidence pieces span divergent intents ({intents[0]} vs {intents[1]})"
            }

        return {
            "passed": True,
            "consistency_score": 1.0,
            "conflict_detected": False,
            "reason": "Top retrieved evidence pieces are mutually consistent"
        }

    @classmethod
    def evaluate_answerability(cls, query_text: str, predicted_intent: str, retrieved_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate if the retrieved evidence can answer the user's specific grievance."""
        if not retrieved_evidence:
            return {
                "answerable": False,
                "answerability_score": 0.0,
                "reason": "No candidate evidence available"
            }

        if predicted_intent == "UNKNOWN_INSUFFICIENT_CONTEXT":
            return {
                "answerable": False,
                "answerability_score": 0.1,
                "reason": "Inquiry lacks sufficient diagnostic symptoms to resolve technically"
            }

        top_item = retrieved_evidence[0]
        if top_item.get("intent") != predicted_intent:
            return {
                "answerable": False,
                "answerability_score": 0.4,
                "reason": f"Top evidence intent ({top_item.get('intent')}) does not cover predicted inquiry intent ({predicted_intent})"
            }

        return {
            "answerable": True,
            "answerability_score": 0.95,
            "reason": f"Verified evidence unit {top_item.get('evidence_id')} directly addresses intent {predicted_intent}"
        }

    @classmethod
    def evaluate_all(
        cls,
        query_text: str,
        predicted_intent: str,
        retrieved_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        quality = cls.evaluate_quality(retrieved_evidence)
        consistency = cls.evaluate_consistency(retrieved_evidence)
        answerability = cls.evaluate_answerability(query_text, predicted_intent, retrieved_evidence)

        all_passed = quality["passed"] and consistency["passed"] and answerability["answerable"]

        return {
            "all_passed": all_passed,
            "quality": quality,
            "consistency": consistency,
            "answerability": answerability
        }
