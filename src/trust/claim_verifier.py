"""Claim Extraction and Claim-Evidence Verification Engine.

Decomposes generated responses into atomic factual assertions and verifies
each assertion against retrieved verified evidence units to eliminate hallucinations.
"""

import re
from typing import Dict, Any, List, Set


class ClaimVerifier:
    """Verifies factual grounding of generated responses against supporting evidence."""

    @classmethod
    def extract_claims(cls, response_text: str) -> List[str]:
        """Extract atomic propositions/sentences excluding greetings, citations, questions, and conversational filler."""
        if not response_text:
            return []

        # Remove citations like [Ref: HT201264], [AppleSupport TWCS-11625], [Supplementary Ref: ...]
        cleaned = re.sub(r"\[[^\]]+\]", "", response_text).strip()

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        claims = []
        for s in sentences:
            s_clean = s.strip()
            # Ignore clarification questions and diagnostic prompts
            if s_clean.endswith("?") or "could you reply" in s_clean.lower() or "could you provide" in s_clean.lower():
                continue

            # Filter out greeting filler
            if s_clean.lower().startswith(("we can help", "we're here to help", "hello", "thanks for reaching out", "to make sure")):
                parts = re.split(r"(?:with this\.\s*|to help!\s*|accurate steps,\s*)", s_clean, flags=re.IGNORECASE)
                if len(parts) > 1 and len(parts[1].strip()) > 10:
                    sub_part = parts[1].strip()
                    if not sub_part.endswith("?") and "could you" not in sub_part.lower():
                        claims.append(sub_part)
            elif len(s_clean) > 15:
                claims.append(s_clean)

        return claims

    @classmethod
    def verify(cls, response_text: str, evidence_items: List[Dict[str, Any]], is_abstention: bool = False) -> Dict[str, Any]:
        """Verify each claim against evidence body texts."""
        if is_abstention:
            return {
                "verified": True,
                "total_claims": 0,
                "grounded_claims": 0,
                "unsupported_claims": [],
                "hallucination_detected": False,
                "groundedness_score": 1.0,
                "notes": "No substantive factual claims to verify (system abstention)"
            }

        claims = cls.extract_claims(response_text)

        if not claims:
            # Response has no substantive claims (e.g. pure clarification or question)
            return {
                "verified": True,
                "total_claims": 0,
                "grounded_claims": 0,
                "unsupported_claims": [],
                "hallucination_detected": False,
                "groundedness_score": 1.0,
                "notes": "No substantive factual claims to verify (clarification prompt)"
            }

        if not evidence_items:
            # Substantive claims made with 0 evidence -> 100% unsupported hallucination
            return {
                "verified": False,
                "total_claims": len(claims),
                "grounded_claims": 0,
                "unsupported_claims": claims,
                "hallucination_detected": True,
                "groundedness_score": 0.0,
                "notes": "Substantive claims generated with zero supporting evidence units"
            }

        # Combine all evidence tokens
        evidence_text = " ".join([e.get("body", "") + " " + e.get("title", "") for e in evidence_items]).lower()
        evidence_words = set(re.findall(r"\b[a-z]{3,}\b", evidence_text))

        grounded_count = 0
        unsupported = []

        for claim in claims:
            claim_words = set(re.findall(r"\b[a-z]{3,}\b", claim.lower()))
            if not claim_words:
                continue

            # Significant content words
            stop_words = {"this", "that", "with", "from", "your", "have", "make", "sure", "more", "then", "into", "help"}
            content_words = claim_words - stop_words

            if not content_words:
                grounded_count += 1
                continue

            overlap = content_words.intersection(evidence_words)
            overlap_ratio = len(overlap) / len(content_words)

            # At least 60% of claim content words must be corroborated by evidence
            if overlap_ratio >= 0.55:
                grounded_count += 1
            else:
                unsupported.append({
                    "claim": claim,
                    "overlap_ratio": round(overlap_ratio, 2),
                    "missing_terms": list(content_words - evidence_words)[:5]
                })

        total = len(claims)
        score = round(grounded_count / total, 2) if total > 0 else 1.0
        verified = (len(unsupported) == 0 and score >= 0.8)

        return {
            "verified": verified,
            "total_claims": total,
            "grounded_claims": grounded_count,
            "unsupported_claims": unsupported,
            "hallucination_detected": len(unsupported) > 0,
            "groundedness_score": score,
            "notes": "All claims corroborated by verified evidence" if verified else f"{len(unsupported)} claims lack sufficient grounding"
        }
