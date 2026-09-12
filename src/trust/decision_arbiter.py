"""Trust-Gated Dual-Track Decision Arbiter (AUTO vs HUMAN Escalation).

Decides whether a customer support interaction can be safely auto-resolved or
must be routed to a human specialist queue.
"""

from typing import Dict, Any, Optional


class DecisionArbiter:
    """Arbiter enforcing strict trust gates before permitting automated resolution."""

    # Thresholds
    MIN_INTENT_CONFIDENCE = 0.85
    MIN_GROUNDEDNESS_SCORE = 0.90
    MIN_QUALITY_SCORE = 7.0
    MIN_ANSWERABILITY_SCORE = 0.85

    @classmethod
    def arbitrate(
        cls,
        intent_result: Dict[str, Any],
        gates_result: Dict[str, Any],
        risk_result: Dict[str, Any],
        claim_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make definitive routing decision (AUTO_RESOLVE vs ESCALATE_TO_HUMAN)."""
        reasons = []

        # 1. Immediate Safety / Legal / Fraud Risk Escalation
        if risk_result.get("requires_immediate_escalation"):
            reasons.append(f"Risk gate triggered: {risk_result.get('reason')}")
            return {
                "decision": "ESCALATE_TO_HUMAN",
                "risk_level": risk_result.get("risk_level", "HIGH"),
                "target_queue": risk_result.get("escalation_queue", "GENERAL_HUMAN_TIER2"),
                "reasons": reasons,
                "confidence_score": 0.0,
                "can_auto_resolve": False
            }

        # 2. Intent Confidence & Ambiguity Gate
        intent_conf = intent_result.get("confidence", 0.0)
        is_ambiguous = intent_result.get("ambiguity_flag", False)
        predicted_intent = intent_result.get("intent", "UNKNOWN_INSUFFICIENT_CONTEXT")

        if predicted_intent == "UNKNOWN_INSUFFICIENT_CONTEXT":
            reasons.append("Inquiry intent is UNKNOWN / lacks technical context")

        if intent_conf < cls.MIN_INTENT_CONFIDENCE:
            reasons.append(f"Intent confidence ({intent_conf}) below auto threshold ({cls.MIN_INTENT_CONFIDENCE})")

        if is_ambiguous:
            reasons.append("Multi-symptom ambiguity detected; tie-breaker priority required")

        # 3. Evidence Quality, Consistency, and Answerability Gates
        quality_score = gates_result.get("quality", {}).get("score", 0.0)
        consistency_passed = gates_result.get("consistency", {}).get("passed", True)
        conflict_detected = gates_result.get("consistency", {}).get("conflict_detected", False)
        answerability = gates_result.get("answerability", {})
        answerable = answerability.get("answerable", True)
        answerability_score = answerability.get("answerability_score", 1.0)

        if not gates_result.get("all_passed", False):
            if not gates_result.get("quality", {}).get("passed", True) or quality_score < cls.MIN_QUALITY_SCORE:
                reasons.append(f"Retrieved evidence failed quality threshold (score: {quality_score} < {cls.MIN_QUALITY_SCORE})")
            if not consistency_passed or conflict_detected:
                reasons.append("Retrieved evidence contains conflicting recommendations")
            if not answerable or answerability_score < cls.MIN_ANSWERABILITY_SCORE:
                reasons.append("Retrieved evidence cannot answer customer's specific question")
        else:
            # Stricter checks even if all_passed was marked
            if quality_score < cls.MIN_QUALITY_SCORE:
                reasons.append(f"Evidence quality score ({quality_score}) below safety threshold ({cls.MIN_QUALITY_SCORE})")
            if conflict_detected:
                reasons.append("Retrieved evidence contains conflicting recommendations")
            if not answerable or answerability_score < cls.MIN_ANSWERABILITY_SCORE:
                reasons.append(f"Answerability score ({answerability_score}) below safety threshold ({cls.MIN_ANSWERABILITY_SCORE})")

        # 4. Claim Verification & Groundedness Gate
        groundedness_score = claim_result.get("groundedness_score", 0.0)
        if not claim_result.get("verified", False):
            reasons.append(f"Response failed claim verification ({len(claim_result.get('unsupported_claims', []))} unsupported claims)")

        if groundedness_score < cls.MIN_GROUNDEDNESS_SCORE:
            reasons.append(f"Groundedness score ({groundedness_score}) below required threshold ({cls.MIN_GROUNDEDNESS_SCORE})")

        if claim_result.get("hallucination_detected", False):
            reasons.append("Potential hallucination detected in generated response")

        # Decision synthesis
        if not reasons:
            # All gates passed with high confidence
            aggregate_score = round((intent_conf * 0.4) + (claim_result.get("groundedness_score", 1.0) * 0.6), 2)
            return {
                "decision": "AUTO_RESOLVE",
                "risk_level": "LOW",
                "target_queue": "AUTONOMOUS_DELIVERY",
                "reasons": [],
                "confidence_score": aggregate_score,
                "can_auto_resolve": True
            }
        else:
            queue = risk_result.get("escalation_queue", "GENERAL_HUMAN_TIER2")
            if "ACCOUNT" in predicted_intent or "SECURITY" in predicted_intent:
                queue = "SECURITY_SPECIALIST"
            elif "BILLING" in predicted_intent or "ORDER" in predicted_intent:
                queue = "COMMERCE_SPECIALIST"

            return {
                "decision": "ESCALATE_TO_HUMAN",
                "risk_level": risk_result.get("risk_level", "MEDIUM"),
                "target_queue": queue,
                "reasons": reasons,
                "confidence_score": round(intent_conf * 0.5, 2),
                "can_auto_resolve": False
            }
