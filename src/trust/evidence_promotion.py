"""Human-Gated Evidence Promotion Workflow.

Ensures that new troubleshooting steps or evidence units cannot enter the
autonomous retrieval index without explicit verification and approval by a
human domain specialist.

Lifecycle:
CANDIDATE -> REVIEW_REQUIRED -> TRUSTED -> RETIRED / REJECTED
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.retrieval.evidence_store import EvidenceStore


class EvidencePromotionManager:
    """Manages promotion of candidate evidence to verified knowledge base status."""

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        audit_log_path: str = "artifacts/evidence_promotion_audit.json"
    ):
        self.store = evidence_store or EvidenceStore()
        self.audit_log_path = audit_log_path
        self._audit_log: List[Dict[str, Any]] = []
        self._load_audit_log()

    def _load_audit_log(self):
        if os.path.exists(self.audit_log_path):
            try:
                with open(self.audit_log_path, "r", encoding="utf-8") as f:
                    self._audit_log = json.load(f)
            except Exception:
                self._audit_log = []

    def _save_audit_log(self):
        os.makedirs(os.path.dirname(self.audit_log_path) or ".", exist_ok=True)
        with open(self.audit_log_path, "w", encoding="utf-8") as f:
            json.dump(self._audit_log, f, indent=2)

    def submit_candidate(
        self,
        intent: str,
        title: str,
        body: str,
        source_reference: str,
        source_type: str = "HISTORICAL_APPLESUPPORT_REPLY",
        tags: Optional[List[str]] = None,
        submitted_by: str = "agent_harvester"
    ) -> str:
        """Submit candidate evidence for review (starts as CANDIDATE / REVIEW_REQUIRED)."""
        evid_id = f"EVID-CAND-{len(self.store.items) + 1:04d}"
        candidate = {
            "evidence_id": evid_id,
            "intent": intent,
            "title": title,
            "body": body,
            "source_type": source_type,
            "source_reference": source_reference,
            "verification_status": "REVIEW_REQUIRED",
            "submitted_by": submitted_by,
            "submitted_at": datetime.utcnow().isoformat() + "Z",
            "tags": tags or []
        }
        self.store.items.append(candidate)
        self.store.save()

        self._audit_log.append({
            "action": "SUBMIT_CANDIDATE",
            "evidence_id": evid_id,
            "actor": submitted_by,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "REVIEW_REQUIRED"
        })
        self._save_audit_log()
        return evid_id

    def promote_evidence(
        self,
        evidence_id: str,
        reviewer_id: str,
        decision: str,  # "PROMOTE_TO_TRUSTED", "PROMOTE_TO_VERIFIED", or "REJECT"
        reviewer_notes: str = ""
    ) -> Dict[str, Any]:
        """Human specialist decision to promote to TRUSTED or REJECT."""
        if decision not in ["PROMOTE_TO_TRUSTED", "PROMOTE_TO_VERIFIED", "REJECT"]:
            raise ValueError(f"Invalid decision: {decision}. Must be PROMOTE_TO_TRUSTED or REJECT.")

        target = next((item for item in self.store.items if item.get("evidence_id") == evidence_id), None)
        if not target:
            raise KeyError(f"Evidence ID {evidence_id} not found.")

        if decision == "PROMOTE_TO_VERIFIED":
            new_status = "VERIFIED"
        elif decision == "PROMOTE_TO_TRUSTED":
            new_status = "TRUSTED"
        else:
            new_status = "REJECTED"
        target["verification_status"] = new_status
        target["verified_by"] = reviewer_id
        target["verified_at"] = datetime.utcnow().isoformat() + "Z"
        target["reviewer_notes"] = reviewer_notes

        self.store.save()

        audit_entry = {
            "action": decision,
            "evidence_id": evidence_id,
            "actor": reviewer_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notes": reviewer_notes,
            "resulting_status": new_status
        }
        self._audit_log.append(audit_entry)
        self._save_audit_log()

        return {
            "evidence_id": evidence_id,
            "new_status": new_status,
            "decision": decision,
            "actor": reviewer_id
        }

    def retire_evidence(
        self,
        evidence_id: str,
        reviewer_id: str,
        reason: str = ""
    ) -> Dict[str, Any]:
        """Decommission / retire previously trusted evidence so it can no longer support AUTO resolution."""
        target = next((item for item in self.store.items if item.get("evidence_id") == evidence_id), None)
        if not target:
            raise KeyError(f"Evidence ID {evidence_id} not found.")

        target["verification_status"] = "RETIRED"
        target["retired_by"] = reviewer_id
        target["retired_at"] = datetime.utcnow().isoformat() + "Z"
        target["retirement_reason"] = reason

        self.store.save()

        self._audit_log.append({
            "action": "RETIRE_EVIDENCE",
            "evidence_id": evidence_id,
            "actor": reviewer_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "resulting_status": "RETIRED"
        })
        self._save_audit_log()

        return {
            "evidence_id": evidence_id,
            "new_status": "RETIRED",
            "actor": reviewer_id,
            "reason": reason
        }
