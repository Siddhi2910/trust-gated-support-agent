"""Multi-Turn Session State Manager for AppleSupport Conversations.

Preserves conversation_id, tweet_id, parent/child topological relationships,
and chronological turn histories with bounded storage and strict cross-conversation isolation.
Enables contextual resolution of follow-up customer inquiries (e.g., "I already tried that")
while strictly enforcing all downstream Trust Gates without bypassing risk, quality,
consistency, answerability, claim verification, or human escalation.
"""

import os
import re
import json
import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from collections import OrderedDict


class ConversationTurn:
    """Represents a single turn in an AppleSupport conversation thread."""

    def __init__(
        self,
        turn_index: int,
        role: str,
        text: str,
        tweet_id: Optional[Union[int, str]] = None,
        in_response_to_tweet_id: Optional[Union[int, str]] = None,
        parent_tweet_id: Optional[Union[int, str]] = None,
        child_tweet_ids: Optional[List[Union[int, str]]] = None,
        timestamp: Optional[str] = None,
        intent: Optional[str] = None,
        confidence: Optional[float] = None,
        decision: Optional[str] = None,
        target_queue: Optional[str] = None,
        trust_receipt_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.turn_index = turn_index
        self.role = role  # "customer" or "agent"
        # Bound stored text size to prevent memory bloat
        self.text = text[:1000] if text else ""
        self.tweet_id = str(tweet_id) if tweet_id is not None else None
        self.in_response_to_tweet_id = (
            str(in_response_to_tweet_id) if in_response_to_tweet_id is not None else None
        )
        self.parent_tweet_id = (
            str(parent_tweet_id) if parent_tweet_id is not None else self.in_response_to_tweet_id
        )
        self.child_tweet_ids = [str(cid) for cid in (child_tweet_ids or [])]
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.intent = intent
        self.confidence = float(confidence) if confidence is not None else None
        self.decision = decision
        self.target_queue = target_queue
        self.trust_receipt_id = trust_receipt_id
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "role": self.role,
            "text": self.text,
            "tweet_id": self.tweet_id,
            "in_response_to_tweet_id": self.in_response_to_tweet_id,
            "parent_tweet_id": self.parent_tweet_id,
            "child_tweet_ids": list(self.child_tweet_ids),
            "timestamp": self.timestamp,
            "intent": self.intent,
            "confidence": self.confidence,
            "decision": self.decision,
            "target_queue": self.target_queue,
            "trust_receipt_id": self.trust_receipt_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationTurn":
        return cls(
            turn_index=data.get("turn_index", 0),
            role=data.get("role", "customer"),
            text=data.get("text", ""),
            tweet_id=data.get("tweet_id"),
            in_response_to_tweet_id=data.get("in_response_to_tweet_id"),
            parent_tweet_id=data.get("parent_tweet_id"),
            child_tweet_ids=data.get("child_tweet_ids", []),
            timestamp=data.get("timestamp"),
            intent=data.get("intent"),
            confidence=data.get("confidence"),
            decision=data.get("decision"),
            target_queue=data.get("target_queue"),
            trust_receipt_id=data.get("trust_receipt_id"),
            metadata=data.get("metadata", {}),
        )


class ConversationSession:
    """Manages thread state, parent/child topological linkages, and context for a single conversation."""

    # Explicit patterns indicating customer is reporting failure of previous troubleshooting
    FAILURE_PATTERNS = [
        r"\b(?:already\s+tried(?:\s+that|\s+this)?)\b",
        r"\b(?:did\s+that(?:\s+already)?)\b",
        r"\b(?:still\s+(?:doesn['’]?t|not)\s+work\w*)\b",
        r"\b(?:didn['’]?t\s+(?:work|help))\b",
        r"\b(?:it\s+doesn['’]?t\s+work)\b",
        r"\b(?:none\s+of\s+(?:that|those)\s+worked?)\b",
        r"\b(?:still\s+happening|still\s+having\s+the\s+same\s+issue|still\s+dying|still\s+freez\w*|still\s+crash\w*|still\s+won['’]?t)\b",
        r"\b(?:that\s+didn['’]?t\s+do\s+anything)\b",
        r"\b(?:no\s+use|no\s+luck|didn['’]?t\s+solve\s+it)\b",
    ]

    # Follow-up continuation patterns
    FOLLOWUP_PATTERNS = [
        r"\b(?:already|still|tried|did\s+that|what\s+else|what\s+now|next\s+step|same\s+(?:issue|thing|problem)|now\s+what)\b",
        r"\b(?:how\s+do\s+i\s+do\s+that|where\s+(?:is|do\s+i\s+find)|which\s+setting)\b",
    ]

    def __init__(
        self,
        conversation_id: Union[int, str],
        max_turns: int = 10,
        created_at: Optional[str] = None,
    ):
        self.conversation_id = str(conversation_id)
        self.max_turns = max_turns
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.turns: List[ConversationTurn] = []
        self.parent_map: Dict[str, str] = {}
        self.children_map: Dict[str, List[str]] = {}
        self.tweet_to_turn: Dict[str, int] = {}
        self.root_intent: Optional[str] = None
        self.latest_intent: Optional[str] = None
        self.active_focal_grievance: Optional[str] = None
        self.troubleshooting_offered: List[str] = []

    def _enforce_turn_bounds(self) -> None:
        """Keep turns strictly bounded to max_turns while preserving the root inquiry anchor."""
        if len(self.turns) <= self.max_turns:
            return

        # Always preserve turn 0 (root customer inquiry anchor) + the most recent (max_turns - 1) turns
        root_turn = self.turns[0]
        recent_turns = self.turns[-(self.max_turns - 1):]
        self.turns = [root_turn] + recent_turns

        # Re-index remaining turns
        for idx, t in enumerate(self.turns):
            t.turn_index = idx
            if t.tweet_id:
                self.tweet_to_turn[t.tweet_id] = idx

    def add_turn(
        self,
        role: str,
        text: str,
        tweet_id: Optional[Union[int, str]] = None,
        in_response_to_tweet_id: Optional[Union[int, str]] = None,
        intent: Optional[str] = None,
        confidence: Optional[float] = None,
        decision: Optional[str] = None,
        target_queue: Optional[str] = None,
        trust_receipt_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationTurn:
        """Add a turn with full parent/child relationship and bounds enforcement."""
        turn_index = len(self.turns)
        tid = str(tweet_id) if tweet_id is not None else f"TW-{role.upper()}-{self.conversation_id}-{turn_index}"
        pid = str(in_response_to_tweet_id) if in_response_to_tweet_id is not None else None

        # If pid not provided and there are prior turns, link to immediate preceding turn's tweet_id
        if pid is None and self.turns:
            pid = self.turns[-1].tweet_id

        turn = ConversationTurn(
            turn_index=turn_index,
            role=role,
            text=text,
            tweet_id=tid,
            in_response_to_tweet_id=pid,
            parent_tweet_id=pid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            intent=intent,
            confidence=confidence,
            decision=decision,
            target_queue=target_queue,
            trust_receipt_id=trust_receipt_id,
            metadata=metadata,
        )

        # Update topological relationships
        if tid:
            self.tweet_to_turn[tid] = turn_index
        if pid:
            self.parent_map[tid] = pid
            if pid not in self.children_map:
                self.children_map[pid] = []
            if tid not in self.children_map[pid]:
                self.children_map[pid].append(tid)

        # Update intent tracking if valid intent provided
        if intent and intent != "UNKNOWN_INSUFFICIENT_CONTEXT":
            if self.root_intent is None:
                self.root_intent = intent
            self.latest_intent = intent

        if role == "agent" and text:
            self.troubleshooting_offered.append(text[:200])

        self.turns.append(turn)
        self.updated_at = turn.timestamp
        self._enforce_turn_bounds()
        return turn

    def get_last_customer_turn(self) -> Optional[ConversationTurn]:
        for turn in reversed(self.turns):
            if turn.role == "customer":
                return turn
        return None

    def get_last_agent_turn(self) -> Optional[ConversationTurn]:
        for turn in reversed(self.turns):
            if turn.role == "agent":
                return turn
        return None

    def get_root_customer_turn(self) -> Optional[ConversationTurn]:
        for turn in self.turns:
            if turn.role == "customer":
                return turn
        return None

    def detect_followup_context(self, current_text: str) -> Dict[str, Any]:
        """Analyze current query against prior turns to detect follow-up / failure status."""
        text_lower = current_text.lower().strip()
        has_prior_turns = len(self.turns) > 0

        if not has_prior_turns:
            return {
                "is_followup": False,
                "is_troubleshooting_failure": False,
                "prior_intent": None,
                "prior_customer_text": None,
                "prior_agent_text": None,
                "combined_query": current_text,
                "turn_count": 0,
            }

        # Check for failure of troubleshooting
        is_failure = any(re.search(pat, text_lower) for pat in self.FAILURE_PATTERNS)
        is_followup_phrase = any(re.search(pat, text_lower) for pat in self.FOLLOWUP_PATTERNS)

        # Short elliptical follow-up heuristic (e.g. "still doesn't work", "what now?")
        word_count = len(text_lower.split())
        is_short_continuation = word_count <= 6 and (
            is_failure or is_followup_phrase or "still" in text_lower or "tried" in text_lower
        )

        is_followup = is_failure or is_followup_phrase or is_short_continuation

        last_cust = self.get_last_customer_turn()
        root_cust = self.get_root_customer_turn()
        last_agent = self.get_last_agent_turn()

        # Prior context anchors
        prior_customer_text = last_cust.text if last_cust else (root_cust.text if root_cust else "")
        prior_agent_text = last_agent.text if last_agent else ""
        prior_intent = self.latest_intent or self.root_intent or (last_cust.intent if last_cust else None)

        # Build contextually enriched query for search without leaking outside this thread
        if is_followup and prior_customer_text:
            combined_query = f"{prior_customer_text} {current_text}".strip()
        else:
            combined_query = current_text

        return {
            "is_followup": is_followup,
            "is_troubleshooting_failure": is_failure,
            "prior_intent": prior_intent,
            "prior_customer_text": prior_customer_text,
            "prior_agent_text": prior_agent_text,
            "combined_query": combined_query,
            "turn_count": len(self.turns),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "turn_count": len(self.turns),
            "max_turns": self.max_turns,
            "root_intent": self.root_intent,
            "latest_intent": self.latest_intent,
            "active_focal_grievance": self.active_focal_grievance,
            "turns": [t.to_dict() for t in self.turns],
            "parent_map": dict(self.parent_map),
            "children_map": {k: list(v) for k, v in self.children_map.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSession":
        session = cls(
            conversation_id=data.get("conversation_id", "0"),
            max_turns=data.get("max_turns", 10),
            created_at=data.get("created_at"),
        )
        session.updated_at = data.get("updated_at", session.created_at)
        session.root_intent = data.get("root_intent")
        session.latest_intent = data.get("latest_intent")
        session.active_focal_grievance = data.get("active_focal_grievance")
        session.parent_map = data.get("parent_map", {})
        session.children_map = data.get("children_map", {})

        turns_data = data.get("turns", [])
        for td in turns_data:
            t = ConversationTurn.from_dict(td)
            session.turns.append(t)
            if t.tweet_id:
                session.tweet_to_turn[t.tweet_id] = t.turn_index

        return session


class ConversationSessionManager:
    """Bounded, thread-safe, cross-conversation isolated session store for AppleSupport interactions."""

    _default_instance: Optional["ConversationSessionManager"] = None
    _default_lock = threading.RLock()

    def __init__(
        self,
        max_sessions: int = 500,
        max_turns_per_conversation: int = 10,
        persistence_path: Optional[str] = None,
    ):
        self.max_sessions = max_sessions
        self.max_turns_per_conversation = max_turns_per_conversation
        self.persistence_path = persistence_path
        self._sessions: OrderedDict[str, ConversationSession] = OrderedDict()
        self._lock = threading.RLock()

        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    @classmethod
    def get_default_instance(
        cls, persistence_path: Optional[str] = "artifacts/conversation_sessions.json"
    ) -> "ConversationSessionManager":
        with cls._default_lock:
            if cls._default_instance is None:
                cls._default_instance = cls(persistence_path=persistence_path)
            return cls._default_instance

    @classmethod
    def reset_default_instance(cls) -> None:
        with cls._default_lock:
            cls._default_instance = None

    def get_or_create_session(
        self, conversation_id: Optional[Union[int, str]]
    ) -> Optional[ConversationSession]:
        """Retrieve existing session or instantiate a new one.

        Returns None if conversation_id is None or empty (safe stateless fallback).
        """
        if conversation_id is None:
            return None

        cid = str(conversation_id).strip()
        if not cid:
            return None

        with self._lock:
            if cid in self._sessions:
                # Move to end (LRU touch)
                self._sessions.move_to_end(cid)
                return self._sessions[cid]

            # Evict oldest if capacity exceeded
            if len(self._sessions) >= self.max_sessions:
                self._sessions.popitem(last=False)

            session = ConversationSession(
                conversation_id=cid,
                max_turns=self.max_turns_per_conversation,
            )
            self._sessions[cid] = session
            return session

    def get_session(
        self, conversation_id: Optional[Union[int, str]]
    ) -> Optional[ConversationSession]:
        """Get session without creating a new one if absent."""
        if conversation_id is None:
            return None
        cid = str(conversation_id).strip()
        with self._lock:
            if cid in self._sessions:
                self._sessions.move_to_end(cid)
                return self._sessions[cid]
            return None

    def has_session(self, conversation_id: Optional[Union[int, str]]) -> bool:
        if conversation_id is None:
            return False
        cid = str(conversation_id).strip()
        with self._lock:
            return cid in self._sessions

    def clear_session(self, conversation_id: Optional[Union[int, str]]) -> bool:
        if conversation_id is None:
            return False
        cid = str(conversation_id).strip()
        with self._lock:
            if cid in self._sessions:
                del self._sessions[cid]
                self.save_to_disk()
                return True
            return False

    def clear_all(self) -> None:
        with self._lock:
            self._sessions.clear()
            self.save_to_disk()

    def get_active_session_count(self) -> int:
        with self._lock:
            return len(self._sessions)

    def save_to_disk(self) -> None:
        if not self.persistence_path:
            return
        with self._lock:
            try:
                os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
                data = {
                    "manifest_version": "1.0.0",
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                    "active_sessions_count": len(self._sessions),
                    "sessions": {
                        cid: session.to_dict()
                        for cid, session in self._sessions.items()
                    },
                }
                # Atomic write via temp file
                tmp_path = f"{self.persistence_path}.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                os.replace(tmp_path, self.persistence_path)
            except Exception:
                # Persistence is best-effort; avoid crashing in-memory state
                pass

    def load_from_disk(self) -> None:
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessions_data = data.get("sessions", {})
                self._sessions.clear()
                for cid, sdata in sessions_data.items():
                    if len(self._sessions) >= self.max_sessions:
                        break
                    self._sessions[cid] = ConversationSession.from_dict(sdata)
            except Exception:
                # If file corrupted, fallback to clean in-memory state
                self._sessions.clear()
