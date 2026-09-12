"""Failure Analysis Tooling for Support Automation & Trust Gates.

Systematically audits pipeline outputs, categorizes operational and semantic
failure modes, and surfaces targeted remediation recommendations.
"""

import json
import os
from typing import Dict, Any, List
from src.trust.pipeline import TrustGatedPipeline


class FailureAnalyzer:
    """Categorizes and diagnoses failure modes across the customer support lifecycle."""

    def __init__(self, pipeline: TrustGatedPipeline = None):
        self.pipeline = pipeline or TrustGatedPipeline()

    def run_analysis(self, test_cases_path: str = "artifacts/taxonomy_human_review_sample.json") -> Dict[str, Any]:
        return self.analyze(test_cases_path=test_cases_path)

    def analyze(self, test_cases_path: str = "artifacts/taxonomy_human_review_sample.json") -> Dict[str, Any]:
        with open(test_cases_path, "r", encoding="utf-8") as f:
            sample_data = json.load(f)

        part1 = sample_data.get("part_1_candidate_intents", [])
        part2 = sample_data.get("part_2_boundary_cases", [])
        part3 = sample_data.get("part_3_unknown_cases", [])
        cases = part1 + part2 + part3

        taxonomy_mismatches = []
        unsupported_claims = []
        safety_escalations = []
        abstentions = []
        ambiguities = []
        clean_auto_resolutions = []

        for c in cases:
            res = self.pipeline.process(
                query_text=c["text"],
                conversation_id=c.get("conversation_id"),
                tweet_id=c.get("tweet_id")
            )

            cid = c.get("tweet_id")
            text = c["text"]
            cand_intent = c.get("candidate_intent")
            pred_intent = res["intent"]["intent"]
            decision = res["decision"]["decision"]

            # 1. Ambiguity flag
            if res["intent"]["ambiguity_flag"]:
                ambiguities.append({
                    "tweet_id": cid,
                    "text": text,
                    "candidate_intent": cand_intent,
                    "predicted_intent": pred_intent,
                    "matched_intents": res["intent"]["matched_intents"]
                })

            # 2. Safety escalation
            if res["risk"]["risk_level"] in ["HIGH", "CRITICAL"]:
                safety_escalations.append({
                    "tweet_id": cid,
                    "text": text,
                    "risk_level": res["risk"]["risk_level"],
                    "risk_category": res["risk"]["risk_category"],
                    "queue": res["decision"]["target_queue"]
                })

            # 3. Abstentions
            if res["generation"]["is_abstention"]:
                abstentions.append({
                    "tweet_id": cid,
                    "text": text,
                    "reason": res["generation"]["abstention_reason"]
                })

            # 4. Unsupported claims
            if res["claims"]["unsupported_claims"]:
                unsupported_claims.append({
                    "tweet_id": cid,
                    "text": text,
                    "unsupported": res["claims"]["unsupported_claims"]
                })

            # 5. Clean auto-resolutions
            if decision == "AUTO_RESOLVE":
                clean_auto_resolutions.append({
                    "tweet_id": cid,
                    "intent": pred_intent,
                    "confidence": res["decision"]["confidence_score"]
                })

        analysis_result = {
            "total_evaluated": len(cases),
            "clean_auto_resolutions_count": len(clean_auto_resolutions),
            "safety_escalations_count": len(safety_escalations),
            "ambiguities_flagged_count": len(ambiguities),
            "abstentions_count": len(abstentions),
            "unsupported_claims_count": len(unsupported_claims),
            "ambiguities_sample": ambiguities[:10],
            "safety_escalations_sample": safety_escalations[:10],
            "unsupported_claims_sample": unsupported_claims[:10]
        }

        # Save JSON artifact
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/failure_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2)

        # Generate report
        self._write_markdown_report(analysis_result)
        return analysis_result

    def _write_markdown_report(self, data: Dict[str, Any]):
        md = f"""# System Failure Analysis & Edge-Case Audit Report

**Total Inquiries Audited:** `{data['total_evaluated']}`  
**Autonomous Resolutions:** `{data['clean_auto_resolutions_count']}`  
**Safety & Risk Escalations:** `{data['safety_escalations_count']}`  
**Multi-Symptom Ambiguities Detected:** `{data['ambiguities_flagged_count']}`  
**Grounded Abstentions / Clarifications:** `{data['abstentions_count']}`  
**Unsupported Claim Incidents:** `{data['unsupported_claims_count']}`  

---

## 1. Safety and Hazard Escalation Analysis
Inquiries with physical safety concerns, account theft, or legal threats are immediately intercepted by the `RiskGate` and routed to dedicated specialist queues.
- Total Intercepted: `{data['safety_escalations_count']}`
- Remediation: No automated response or workaround is dispatched; human oversight is mandatory.

## 2. Multi-Symptom Boundary Ambiguity
Cases where customers present multiple competing symptoms (e.g. battery drain AND device lag):
- Detected & Flagged: `{data['ambiguities_flagged_count']}`
- Resolution Strategy: Evaluated through the 9-level Deterministic Tie-Breaker Ladder.

## 3. Evidence Grounding & Hallucination Prevention
- Unsupported Claims Count: `{data['unsupported_claims_count']}`
- Trust Gate Action: Any claim with <55% lexical-semantic support in the verified knowledge base causes automatic escalation to human tier.
"""
        os.makedirs("reports", exist_ok=True)
        with open("reports/failure_analysis_report.md", "w", encoding="utf-8") as f:
            f.write(md)
