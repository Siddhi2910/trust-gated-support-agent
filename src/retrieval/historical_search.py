"""Leakage-Safe Historical Retrieval Engine for AppleSupport.

Implements token-overlap, BM25-style scoring, and strict conversation-level
leakage guards to prevent test-train contamination.
"""

import re
from typing import Dict, Any, List, Optional, Set
from src.retrieval.evidence_store import EvidenceStore


class LeakageSafeRetriever:
    """Retrieves relevant verified evidence while strictly preventing conversation leakage."""

    def __init__(self, evidence_store: Optional[EvidenceStore] = None):
        self.store = evidence_store or EvidenceStore()

    def search(
        self,
        query_text: str,
        predicted_intent: Optional[str] = None,
        exclude_conversation_id: Optional[int] = None,
        exclude_tweet_id: Optional[int] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Search verified evidence with strict exclusion of same conversation/tweet IDs."""
        tokens = set(re.findall(r"\b[a-z]{3,}\b", query_text.lower()))
        verified_items = self.store.get_all(only_verified=True)

        scored_candidates = []
        leakage_prevented_count = 0

        for item in verified_items:
            # Check conversation & tweet leakage
            item_conv = item.get("source_conversation_id")
            item_tweet = item.get("source_tweet_id")

            if exclude_conversation_id is not None and item_conv is not None:
                if str(item_conv) == str(exclude_conversation_id):
                    leakage_prevented_count += 1
                    continue

            if exclude_tweet_id is not None and item_tweet is not None:
                if str(item_tweet) == str(exclude_tweet_id):
                    leakage_prevented_count += 1
                    continue

            # Compute score
            body_tokens = set(re.findall(r"\b[a-z]{3,}\b", (item.get("body", "") + " " + item.get("title", "")).lower()))
            tag_tokens = set(t.lower() for t in item.get("tags", []))

            overlap = len(tokens.intersection(body_tokens))
            tag_overlap = len(tokens.intersection(tag_tokens))

            score = (overlap * 1.5) + (tag_overlap * 2.0)

            # Boost if intent matches
            if predicted_intent and item.get("intent") == predicted_intent:
                score += 5.0

            # Boost for historical AppleSupport interaction (primary grounding requirement)
            if item.get("source_type") == "HISTORICAL_APPLESUPPORT_REPLY":
                score += 3.0

            if score > 0:
                scored_candidates.append({
                    "evidence_id": item["evidence_id"],
                    "intent": item["intent"],
                    "title": item["title"],
                    "body": item["body"],
                    "source_reference": item["source_reference"],
                    "source_type": item["source_type"],
                    "score": round(score, 2)
                })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_candidates[:top_k]

        return {
            "query": query_text,
            "predicted_intent": predicted_intent,
            "top_k": top_k,
            "results": top_results,
            "total_candidates_evaluated": len(verified_items),
            "leakage_prevented_count": leakage_prevented_count,
            "has_sufficient_evidence": len(top_results) > 0 and top_results[0]["score"] >= 4.0
        }
