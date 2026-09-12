#!/usr/bin/env python3
"""Strict Reconciliation and Merge of 56 User-Approved Human Labels.

Requirements:
1. Match records ONLY by exact original_text first, with tweet_id and conversation_id as additional integrity checks.
2. Do not alter any of the 114 previously recovered human decisions.
3. For the 56 cases, set:
   - human_decision = approved decision from unrecovered_56_model_adjudication.json
   - human_intent = approved proposed_intent
   - review_status = "REVIEWED"
   - human_reviewed = true
   - adjudication_type = "HUMAN_LABEL"
   - provenance = "HUMAN_REVIEWED_BY_USER"
4. Do NOT use "RECOVERED_FROM_CHAT" for these 56.
5. Do NOT change customer text, tweet_id, conversation_id, candidate_intent, or case identity.
6. Update metadata/header counts so they accurately reflect the merged records.
7. Verify post-merge conditions:
   - total cases = 170
   - reviewed cases = 170
   - unreviewed cases = 0
   - ACCEPT = 115
   - REJECT = 55
   - UNCERTAIN = 0
   - 56 records have provenance HUMAN_REVIEWED_BY_USER
   - 114 records have provenance RECOVERED_FROM_CHAT
   - 0 records have null human_decision
   - 0 stale taxonomy IDs
   - 0 duplicate case IDs/tweet IDs
   - 0 text mismatches
   - 0 tweet_id mismatches
   - 0 conversation_id mismatches
8. Preserve immutable backup.
9. Report SHA-256 hashes.
"""

import os
import sys
import json
import hashlib
from datetime import datetime

PRE_MERGE_BACKUP = "artifacts/backups/human_review_labels_backup_20260912_085214_pre_56_user_approval.json"
TARGET_LABELS = "artifacts/human_review_labels.json"
SOURCE_56 = "artifacts/unrecovered_56_model_adjudication.json"
CANONICAL_SAMPLE = "artifacts/taxonomy_human_review_sample.json"
CANDIDATE_TAX = "artifacts/taxonomy_v1_candidate.json"


def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 75)
    print("    RECONCILIATION & MERGE OF 56 USER-APPROVED HUMAN LABELS")
    print("=" * 75)

    # Load baseline pre-merge file (114 reviewed, 56 unreviewed)
    with open(PRE_MERGE_BACKUP, "r", encoding="utf-8") as f:
        pre_data = json.load(f)

    # Load user-approved source
    with open(SOURCE_56, "r", encoding="utf-8") as f:
        unrec_data = json.load(f)

    # Load canonical sample
    with open(CANONICAL_SAMPLE, "r", encoding="utf-8") as f:
        sample_data = json.load(f)

    # Load candidate taxonomy for validation
    with open(CANDIDATE_TAX, "r", encoding="utf-8") as f:
        tax_data = json.load(f)

    valid_intents = {it["intent_id"] for it in tax_data["intents"]}
    sample_cases = (
        sample_data["part_1_candidate_intents"]
        + sample_data["part_2_boundary_cases"]
        + sample_data["part_3_unknown_cases"]
    )
    sample_by_text = {sc["text"]: sc for sc in sample_cases}
    sample_by_id = {sc["tweet_id"]: sc for sc in sample_cases}

    pre_cases = pre_data["cases"]
    records_56 = unrec_data["records"]

    # Pre-merge validation
    assert len(pre_cases) == 170
    assert len(records_56) == 56
    assert len(sample_cases) == 170

    pre_reviewed = [c for c in pre_cases if c.get("reviewed") is True]
    pre_unreviewed = [c for c in pre_cases if not c.get("reviewed")]
    assert len(pre_reviewed) == 114
    assert len(pre_unreviewed) == 56

    # 1. Match records ONLY by exact original_text first, with tweet_id and conversation_id checks
    print("\n--- MATCHING BY EXACT ORIGINAL TEXT ---")
    unrec_by_text = {}
    for r in records_56:
        t = r["original_text"]
        assert t not in unrec_by_text, f"Duplicate text in approved records: {t[:40]}"
        unrec_by_text[t] = r

    matched_unreviewed_count = 0
    merged_cases = []

    for c in pre_cases:
        c_text = c["text"]
        if c_text in unrec_by_text:
            # Must be one of the unreviewed cases
            assert not c.get("reviewed"), f"Collision: Case {c['case_id']} was already reviewed!"
            r = unrec_by_text[c_text]

            # Additional integrity checks
            assert c["tweet_id"] == r["tweet_id"], f"Tweet ID mismatch on case {c['case_id']}"
            assert c["conversation_id"] == r["conversation_id"], f"Conv ID mismatch on case {c['case_id']}"

            # Validate against canonical sample
            sc = sample_by_text[c_text]
            assert sc["tweet_id"] == r["tweet_id"]
            assert sc["conversation_id"] == r["conversation_id"]

            # Validate intent belongs to current 15-intent taxonomy
            assert r["proposed_intent"] in valid_intents, f"Stale intent: {r['proposed_intent']}"
            assert r["proposed_decision"] in ["ACCEPT", "REJECT", "UNCERTAIN"]

            # Create merged record with exact required fields
            merged_case = {
                "case_id": c["case_id"],
                "part": c["part"],
                "tweet_id": c["tweet_id"],
                "conversation_id": c["conversation_id"],
                "text": c["text"],
                "candidate_intent": c.get("candidate_intent"),
                "human_decision": r["proposed_decision"],
                "human_intent": r["proposed_intent"],
                "focal_grievance": r.get("focal_grievance"),
                "reviewer_notes": None,
                "reviewed": True,
                "review_status": "REVIEWED",
                "human_reviewed": True,
                "reviewed_at": "2026-09-12T09:00:00Z",
                "provenance": "HUMAN_REVIEWED_BY_USER",
                "adjudication_type": "HUMAN_LABEL",
                "historical_evidence": r.get("historical_evidence")
            }
            merged_cases.append(merged_case)
            matched_unreviewed_count += 1
        else:
            # Must be one of the 114 previously reviewed cases - preserved UNCHANGED
            assert c.get("reviewed") is True, f"Unreviewed case not in approved list: {c['case_id']}"
            assert c.get("provenance") == "RECOVERED_FROM_CHAT"
            merged_cases.append(dict(c))

    assert matched_unreviewed_count == 56, f"Matched {matched_unreviewed_count} unreviewed cases, expected 56"
    assert len(merged_cases) == 170
    print("✓ Successfully matched and merged all 56 records by exact original_text.")
    print("✓ All 114 previously recovered human decisions remain strictly unaltered.")

    # 6. Update metadata counts
    total = len(merged_cases)
    reviewed = sum(1 for c in merged_cases if c.get("reviewed") is True)
    remaining = total - reviewed
    accepts = sum(1 for c in merged_cases if c.get("human_decision") == "ACCEPT")
    rejects = sum(1 for c in merged_cases if c.get("human_decision") == "REJECT")
    uncertains = sum(1 for c in merged_cases if c.get("human_decision") == "UNCERTAIN")

    prov_chat = sum(1 for c in merged_cases if c.get("provenance") == "RECOVERED_FROM_CHAT")
    prov_user = sum(1 for c in merged_cases if c.get("provenance") == "HUMAN_REVIEWED_BY_USER")

    metadata = {
        "total_cases": total,
        "reviewed_count": reviewed,
        "remaining_count": remaining,
        "accept_count": accepts,
        "reject_count": rejects,
        "uncertain_count": uncertains,
        "reviewer": "human_project_owner",
        "taxonomy_version": "1.0",
        "created_at": pre_data["metadata"].get("created_at", "2026-09-11T10:40:00Z"),
        "updated_at": "2026-09-12T09:00:00Z",
        "provenance_summary": "114 decisions recovered from prior conversation context; 56 decisions approved via direct human review by project owner."
    }

    final_payload = {
        "metadata": metadata,
        "cases": merged_cases
    }

    # Atomic write to target file
    tmp_path = f"{TARGET_LABELS}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, TARGET_LABELS)
    print(f"\n✓ Atomically written to {TARGET_LABELS}")

    # 7. Post-merge verification
    print("\n--- POST-MERGE AUDIT & VERIFICATION ---")
    with open(TARGET_LABELS, "r", encoding="utf-8") as f:
        disk_data = json.load(f)

    d_meta = disk_data["metadata"]
    d_cases = disk_data["cases"]

    # Integrity assertions as specified in requirement 7:
    assert d_meta["total_cases"] == 170, f"Expected 170, got {d_meta['total_cases']}"
    assert d_meta["reviewed_count"] == 170, f"Expected 170, got {d_meta['reviewed_count']}"
    assert d_meta["remaining_count"] == 0, f"Expected 0, got {d_meta['remaining_count']}"
    assert d_meta["accept_count"] == 115, f"Expected 115, got {d_meta['accept_count']}"
    assert d_meta["reject_count"] == 55, f"Expected 55, got {d_meta['reject_count']}"
    assert d_meta["uncertain_count"] == 0, f"Expected 0, got {d_meta['uncertain_count']}"

    assert prov_user == 56, f"Expected 56 HUMAN_REVIEWED_BY_USER, got {prov_user}"
    assert prov_chat == 114, f"Expected 114 RECOVERED_FROM_CHAT, got {prov_chat}"

    null_decisions = [c for c in d_cases if c.get("human_decision") is None]
    assert len(null_decisions) == 0, f"Found {len(null_decisions)} null decisions!"

    # Stale taxonomy check
    stale_intents = [c for c in d_cases if c["human_intent"] not in valid_intents]
    assert len(stale_intents) == 0, f"Found stale intents: {stale_intents}"

    # Duplicate IDs check
    case_ids = [c["case_id"] for c in d_cases]
    tweet_ids = [c["tweet_id"] for c in d_cases]
    assert len(case_ids) == len(set(case_ids)) == 170
    assert len(tweet_ids) == len(set(tweet_ids)) == 170

    # Text, tweet_id, conv_id match against canonical sample
    text_mismatches = 0
    tweet_mismatches = 0
    conv_mismatches = 0
    for i, c in enumerate(d_cases):
        sc = sample_cases[i]
        assert c["case_id"] == i + 1
        if c["text"] != sc["text"]:
            text_mismatches += 1
        if c["tweet_id"] != sc["tweet_id"]:
            tweet_mismatches += 1
        if c["conversation_id"] != sc["conversation_id"]:
            conv_mismatches += 1

    assert text_mismatches == 0
    assert tweet_mismatches == 0
    assert conv_mismatches == 0

    print("✓ total cases = 170")
    print("✓ reviewed cases = 170")
    print("✓ unreviewed cases = 0")
    print("✓ ACCEPT = 115")
    print("✓ REJECT = 55")
    print("✓ UNCERTAIN = 0")
    print("✓ 56 records have provenance HUMAN_REVIEWED_BY_USER")
    print("✓ 114 records have provenance RECOVERED_FROM_CHAT")
    print("✓ 0 records have null human_decision")
    print("✓ 0 stale taxonomy IDs")
    print("✓ 0 duplicate case IDs/tweet IDs")
    print("✓ 0 text mismatches")
    print("✓ 0 tweet_id mismatches")
    print("✓ 0 conversation_id mismatches")

    # 9. Compute SHA-256 hashes
    backup_sha = compute_sha256(PRE_MERGE_BACKUP)
    final_sha = compute_sha256(TARGET_LABELS)
    source_56_sha = compute_sha256(SOURCE_56)

    print("\n--- SHA-256 HASHES ---")
    print(f"Pre-merge backup:                   {backup_sha} ({PRE_MERGE_BACKUP})")
    print(f"Final human_review_labels.json:     {final_sha} ({TARGET_LABELS})")
    print(f"unrecovered_56_model_adjudication:  {source_56_sha} ({SOURCE_56})")

    # Ensure golden set is NOT generated
    assert not os.path.exists("artifacts/golden_set.json")
    assert not os.path.exists("artifacts/golden_set_manifest.json")
    assert not os.path.exists("artifacts/taxonomy_v1_frozen.json")
    assert tax_data.get("taxonomy_frozen") is False
    print("✓ golden_set.json NOT generated; taxonomy remains unfrozen.")


if __name__ == "__main__":
    main()
