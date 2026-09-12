"""Evidence-Grounded Response Generation for AppleSupport.

Generates concise, factual customer responses strictly derived from verified evidence
with formal citation tracking and principled abstention.
"""

from typing import Dict, Any, List, Optional


class EvidenceGroundedGenerator:
    """Generates customer support responses strictly grounded in verified evidence."""

    CLARIFICATION_TEMPLATE = (
        "We're here to help! To make sure we give you the most accurate steps, could you reply with your "
        "specific device model, iOS version, and details about what you're seeing?"
    )

    SAFETY_ESCALATION_TEMPLATE = (
        "Your safety is our top priority. Please immediately disconnect the device from power and discontinue use. "
        "A senior Apple Support safety specialist is being notified and will take over this case directly."
    )

    TROUBLESHOOTING_ESCALATION_TEMPLATE = (
        "We understand that the previous troubleshooting steps did not resolve your issue. "
        "To prevent further disruption, we are transferring your case directly to an Apple Support specialist "
        "for diagnostic examination."
    )

    def generate(
        self,
        query_text: str,
        predicted_intent: str,
        evidence_items: List[Dict[str, Any]],
        risk_evaluation: Optional[Dict[str, Any]] = None,
        gates_evaluation: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate response with citations or appropriate clarification/escalation."""
        # 1. Critical safety escalation check
        if risk_evaluation and risk_evaluation.get("risk_level") == "CRITICAL":
            return {
                "response_text": self.SAFETY_ESCALATION_TEMPLATE,
                "generation_mode": "SAFETY_REFUSAL_ESCALATION",
                "evidence_used": [],
                "citations": [],
                "is_abstention": True,
                "abstention_reason": risk_evaluation.get("reason", "Critical hazard detected")
            }

        # 2. Multi-turn troubleshooting failure escalation
        if session_context and session_context.get("is_troubleshooting_failure"):
            return {
                "response_text": self.TROUBLESHOOTING_ESCALATION_TEMPLATE,
                "generation_mode": "MULTI_TURN_ESCALATION",
                "evidence_used": [],
                "citations": [],
                "is_abstention": True,
                "abstention_reason": "Customer reported prior troubleshooting step failed; transferred to human specialist"
            }

        # 3. Abstention / clarification for UNKNOWN or insufficient evidence
        if predicted_intent == "UNKNOWN_INSUFFICIENT_CONTEXT" or not evidence_items:
            return {
                "response_text": self.CLARIFICATION_TEMPLATE,
                "generation_mode": "CLARIFICATION_REQUEST",
                "evidence_used": [],
                "citations": [],
                "is_abstention": True,
                "abstention_reason": "Inquiry lacks sufficient context or verified evidence is unavailable"
            }

        # 3. Check gates evaluation
        if gates_evaluation and not gates_evaluation.get("all_passed", True):
            return {
                "response_text": self.CLARIFICATION_TEMPLATE,
                "generation_mode": "EVIDENCE_GATED_ABSTENTION",
                "evidence_used": [],
                "citations": [],
                "is_abstention": True,
                "abstention_reason": "Retrieved evidence failed quality, consistency, or answerability gate"
            }

        # 4. Synthesize response strictly from top verified evidence
        top_evid = evidence_items[0]
        body = top_evid.get("body", "")
        source_ref = top_evid.get("source_reference", "")
        evid_id = top_evid.get("evidence_id", "")
        source_type = top_evid.get("source_type", "")

        if source_type == "HISTORICAL_APPLESUPPORT_REPLY":
            citation_label = f"[AppleSupport {source_ref}]"
        else:
            citation_label = f"[Ref: {source_ref}]"

        citations = [citation_label]
        evidence_used = [
            {
                "evidence_id": evid_id,
                "title": top_evid.get("title", ""),
                "source_type": source_type,
                "source_reference": source_ref
            }
        ]

        # Include secondary supplementary official KB if available
        if len(evidence_items) > 1 and evidence_items[1].get("source_type") == "OFFICIAL_KB":
            supp_evid = evidence_items[1]
            supp_ref = supp_evid.get("source_reference", "")
            supp_label = f"[Supplementary Ref: {supp_ref}]"
            citations.append(supp_label)
            evidence_used.append({
                "evidence_id": supp_evid.get("evidence_id", ""),
                "title": supp_evid.get("title", ""),
                "source_type": "OFFICIAL_KB",
                "source_reference": supp_ref
            })

        response_text = f"We can help with this. {body} {' '.join(citations)}"

        return {
            "response_text": response_text,
            "generation_mode": "GROUNDED_EVIDENCE_SYNTHESIS",
            "evidence_used": evidence_used,
            "citations": citations,
            "is_abstention": False,
            "abstention_reason": None
        }
