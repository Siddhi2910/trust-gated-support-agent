#!/usr/bin/env python3
"""Secondary LLM-as-a-Judge Evaluation Layer for Trust-Gated Support Agent.

CRITICAL INVARIANTS:
1. Secondary Evidence Only: This layer provides qualitative secondary signals.
   It NEVER replaces or overrides deterministic classification, rule-based verification,
   or human golden set annotations.
2. No Fabricated Results: When GEMINI_API_KEY is unset or unavailable, the judge
   strictly marks itself as UNAVAILABLE and returns 0 evaluated cases. It NEVER
   synthesizes fake scores or synthetic metrics.
3. Actual Configured Provider: Uses GEMINI_API_KEY from environment with configurable
   model (LLM_JUDGE_MODEL) and versioned evaluation prompt.
4. Separate Persistence: Outputs are saved to dedicated secondary artifacts,
   keeping deterministic benchmark metrics completely distinct.
"""

import os
import sys
import json
import socket
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

PROMPT_VERSION = "v1.0.0-trust-gated-eval"
DEFAULT_MODEL = "gemini-2.5-flash"
SOCKET_TIMEOUT_SECONDS = 15.0


class SecondaryLLMJudge:
    """Secondary LLM-as-a-Judge for evaluating generated support responses."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key is None:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY") or ""
        else:
            self.api_key = api_key
        self.model = model or os.getenv("LLM_JUDGE_MODEL") or DEFAULT_MODEL
        self.prompt_version = PROMPT_VERSION
        socket.setdefaulttimeout(SOCKET_TIMEOUT_SECONDS)

    def is_available(self) -> bool:
        """Returns True only if an actual API key is present in environment."""
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    def get_status(self) -> Dict[str, Any]:
        """Returns runtime availability and configuration status."""
        return {
            "available": self.is_available(),
            "model": self.model,
            "prompt_version": self.prompt_version,
            "role": "SECONDARY_QUALITATIVE_EVALUATION",
            "primary_authority": "Deterministic Evaluation Harness + Frozen Human Golden Set"
        }

    def _build_judge_prompt(self, case_data: Dict[str, Any]) -> str:
        """Constructs the structured qualitative judging prompt."""
        query = case_data.get("customer_inquiry_text") or case_data.get("query_text", "")
        ground_truth_intent = case_data.get("ground_truth_intent", "")
        predicted_intent = case_data.get("predicted_intent") or case_data.get("intent", {}).get("intent", "")
        decision = case_data.get("decision") or case_data.get("decision", {}).get("decision", "")
        response_text = case_data.get("response_text") or case_data.get("generation", {}).get("response_text", "")
        evidence_snippets = case_data.get("evidence_used") or case_data.get("generation", {}).get("evidence_used", [])
        risk_flags = case_data.get("risk_flags") or case_data.get("risk", {})
        claims = case_data.get("claims", {})

        evidence_str = "\n".join([
            f"- [{e.get('evidence_id', 'EVID')}]: {e.get('body') or e.get('content', '')}"
            for e in evidence_snippets
        ]) if evidence_snippets else "(No evidence snippets provided / abstained)"

        return f"""You are an expert technical support evaluation judge auditing an AI customer service agent for Apple technical support.
You are evaluating a single interaction for qualitative quality as SECONDARY evidence.

Interaction Details:
- Customer Inquiry: "{query}"
- Ground Truth Intent: {ground_truth_intent}
- Predicted Intent: {predicted_intent}
- Arbiter Decision: {decision}
- Agent Response: "{response_text}"
- Risk / Ambiguity Flags: {json.dumps(risk_flags, default=str)}
- Claim Grounding Data: {json.dumps(claims, default=str)}
- Retrieved Historical Evidence:
{evidence_str}

Evaluate the interaction strictly on three qualitative criteria.
Return ONLY valid JSON matching this exact schema:
{{
  "groundedness_score": <float between 0.0 and 1.0>,
  "groundedness_rationale": "<explanation of whether all factual claims in the response are grounded in the retrieved evidence>",
  "response_quality_score": <float between 0.0 and 1.0>,
  "response_quality_rationale": "<explanation of tone, relevance, clarity, and helpfulness>",
  "escalation_appropriateness_score": <float between 0.0 and 1.0>,
  "escalation_appropriateness_rationale": "<explanation of whether the AUTO_RESOLVE vs ESCALATE decision was appropriate given the query risk and evidence completeness>"
}}"""

    def evaluate_single_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates a single case output against the live LLM judge.
        Raises RuntimeError if API key is not configured.
        """
        if not self.is_available():
            raise RuntimeError(
                "SecondaryLLMJudge is unavailable: GEMINI_API_KEY environment variable is missing. "
                "Per system constraints, synthetic or fabricated scores will not be generated."
            )

        prompt = self._build_judge_prompt(case_data)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        request_body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                text_content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                evaluation = json.loads(text_content)
                evaluation["case_id"] = case_data.get("case_id")
                evaluation["model"] = self.model
                evaluation["prompt_version"] = self.prompt_version
                return evaluation
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"LLM Judge API HTTP error {e.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"LLM Judge execution failed: {str(e)}")

    def run_secondary_evaluation(
        self,
        cases_outputs: List[Dict[str, Any]],
        max_cases: Optional[int] = None,
        save_artifact: bool = True
    ) -> Dict[str, Any]:
        """Runs secondary qualitative evaluation on a batch of harness outputs.
        
        If credentials are absent, accurately marks evaluation as UNAVAILABLE without
        fabricating or guessing numbers.
        """
        if not self.is_available():
            report = {
                "status": "UNAVAILABLE",
                "available": False,
                "reason": "GEMINI_API_KEY environment variable not configured. Live LLM judge cannot execute.",
                "judge_role": "SECONDARY_QUALITATIVE_EVALUATION",
                "judge_model": self.model,
                "judge_prompt_version": self.prompt_version,
                "cases_evaluated": 0,
                "cases_skipped": len(cases_outputs),
                "disclaimer": (
                    "Secondary qualitative evaluation only. Deterministic benchmark metrics "
                    "and human ground truth remain the primary source of truth."
                ),
                "evaluations": []
            }
            if save_artifact:
                self._persist_evaluation(report)
            return report

        to_eval = cases_outputs[:max_cases] if max_cases else cases_outputs
        evaluations = []
        groundedness_scores = []
        quality_scores = []
        escalation_scores = []

        for case in to_eval:
            try:
                res = self.evaluate_single_case(case)
                evaluations.append(res)
                if "groundedness_score" in res:
                    groundedness_scores.append(res["groundedness_score"])
                if "response_quality_score" in res:
                    quality_scores.append(res["response_quality_score"])
                if "escalation_appropriateness_score" in res:
                    escalation_scores.append(res["escalation_appropriateness_score"])
            except Exception as e:
                evaluations.append({
                    "case_id": case.get("case_id"),
                    "error": str(e)
                })

        valid_count = len(groundedness_scores)
        status = "COMPLETED" if valid_count > 0 else "UNAVAILABLE"
        report = {
            "status": status,
            "available": valid_count > 0,
            "judge_role": "SECONDARY_QUALITATIVE_EVALUATION",
            "judge_model": self.model,
            "judge_prompt_version": self.prompt_version,
            "cases_evaluated": valid_count,
            "cases_requested": len(to_eval),
            "reason": (
                f"Live LLM judge API call failed: {evaluations[0].get('error')}"
                if valid_count == 0 and evaluations and "error" in evaluations[0]
                else None
            ),
            "summary_metrics": {
                "mean_groundedness": sum(groundedness_scores) / valid_count if valid_count else 0.0,
                "mean_response_quality": sum(quality_scores) / valid_count if valid_count else 0.0,
                "mean_escalation_appropriateness": sum(escalation_scores) / valid_count if valid_count else 0.0,
            },
            "disclaimer": (
                "Secondary qualitative evaluation only. Deterministic benchmark metrics "
                "and human ground truth remain the primary source of truth."
            ),
            "evaluations": evaluations
        }

        if save_artifact:
            self._persist_evaluation(report)

        return report

    def _persist_evaluation(self, report: Dict[str, Any]) -> None:
        """Persists evaluation results to artifacts/ and generates a summary markdown."""
        artifact_path = os.path.join(os.getcwd(), "artifacts", "llm_judge_evaluation.json")
        report_path = os.path.join(os.getcwd(), "reports", "llm_judge_report.md")

        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        md = f"""# Secondary LLM-as-a-Judge Evaluation Report

**Evaluation Status:** `{report.get('status')}`  
**Judge Role:** `SECONDARY_QUALITATIVE_SIGNAL`  
**Judge Model:** `{report.get('judge_model')}`  
**Prompt Version:** `{report.get('judge_prompt_version')}`  
**Cases Evaluated:** `{report.get('cases_evaluated', 0)}`  

## Critical Methodological Disclaimer
This qualitative LLM-as-a-judge layer provides an ancillary, advisory signal and **NEVER** replaces, alters, or overrides the primary deterministic golden-set evaluation or human expert annotations. Deterministic accuracy, safety interception rates, and frozen ground truth remain the sole primary authorities.

"""
        if report.get("status") == "UNAVAILABLE":
            md += f"""### Operational Notice
The LLM Judge was marked **UNAVAILABLE** because `{report.get('reason')}`.
In accordance with production integrity rules, no synthetic, mock, or fabricated scores were generated.
To run live LLM judging, configure the `GEMINI_API_KEY` environment variable with valid provider credentials.
"""
        elif report.get("summary_metrics"):
            metrics = report["summary_metrics"]
            md += f"""### Qualitative Summary Metrics
- **Mean Claim Groundedness:** `{metrics.get('mean_groundedness', 0.0):.3f}`
- **Mean Response Quality:** `{metrics.get('mean_response_quality', 0.0):.3f}`
- **Mean Escalation Appropriateness:** `{metrics.get('mean_escalation_appropriateness', 0.0):.3f}`
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md)
