#!/usr/bin/env python3
"""Interactive CLI Workflow for Human Review of 170 Opening Inquiries.

Allows the project owner to review, accept, reject (with corrected intent),
or flag as uncertain every case in artifacts/human_review_labels.json.

Usage:
  python3 scripts/review_cli.py           # Start reviewing from first unreviewed case
  python3 scripts/review_cli.py --status  # Print current progress and breakdown
  python3 scripts/review_cli.py --case 42 # Review specific case #42
"""

import os
import sys
import json
import argparse
from datetime import datetime

CANDIDATE_TAXONOMY_PATH = "artifacts/taxonomy_v1_candidate.json"
HUMAN_LABELS_PATH = "artifacts/human_review_labels.json"
REVIEW_SAMPLE_PATH = "artifacts/taxonomy_human_review_sample.json"

VALID_INTENTS = [
    "BATTERY_DRAIN_POWER_CONSUMPTION",
    "DEVICE_FREEZE_CRASH_REBOOT",
    "KEYBOARD_TYPING_AUTOCORRECT_ISSUE",
    "PERFORMANCE_SLOWDOWN_LATENCY",
    "CONNECTIVITY_WIFI_BLUETOOTH",
    "APP_SPECIFIC_MALFUNCTION",
    "DATA_LOSS_RECOVERY",
    "SCREEN_DISPLAY_TOUCH_BIOMETRICS",
    "HARDWARE_CHARGING_POWER_CABLE",
    "AUDIO_SOUND_SPEAKER_MIC",
    "ACCOUNT_APPLE_ID_ACCESS",
    "BILLING_CHARGE_REFUND_DISPUTE",
    "ORDER_PURCHASE_SHIPPING_STATUS",
    "SECURITY_PHISHING_SUSPICIOUS_CONTACT",
    "UNKNOWN_INSUFFICIENT_CONTEXT"
]


def load_data():
    if not os.path.exists(HUMAN_LABELS_PATH):
        raise FileNotFoundError(f"Missing {HUMAN_LABELS_PATH}")
    with open(HUMAN_LABELS_PATH, "r", encoding="utf-8") as f:
        labels_data = json.load(f)

    with open(CANDIDATE_TAXONOMY_PATH, "r", encoding="utf-8") as f:
        tax_data = json.load(f)

    intent_map = {it["intent_id"]: it for it in tax_data["intents"]}
    return labels_data, intent_map


def save_data(labels_data):
    # Recalculate metrics
    cases = labels_data["cases"]
    total = len(cases)
    reviewed = sum(1 for c in cases if c.get("reviewed") is True)
    accepts = sum(1 for c in cases if c.get("human_decision") == "ACCEPT")
    rejects = sum(1 for c in cases if c.get("human_decision") == "REJECT")
    uncertains = sum(1 for c in cases if c.get("human_decision") == "UNCERTAIN")

    labels_data["metadata"]["total_cases"] = total
    labels_data["metadata"]["reviewed_count"] = reviewed
    labels_data["metadata"]["remaining_count"] = total - reviewed
    labels_data["metadata"]["accept_count"] = accepts
    labels_data["metadata"]["reject_count"] = rejects
    labels_data["metadata"]["uncertain_count"] = uncertains
    labels_data["metadata"]["updated_at"] = datetime.utcnow().isoformat() + "Z"

    with open(HUMAN_LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_data, f, indent=2, ensure_ascii=False)


def print_status(labels_data):
    meta = labels_data["metadata"]
    print("\n" + "=" * 65)
    print("      HUMAN REVIEW PROGRESS STATUS (PROJECT OWNER)")
    print("=" * 65)
    print(f" Total Cases:      {meta['total_cases']}")
    print(f" Reviewed:         {meta['reviewed_count']} ({(meta['reviewed_count']/meta['total_cases'])*100:.1f}%)")
    print(f" Remaining:        {meta['remaining_count']}")
    print("-" * 65)
    print(f" Accepted:         {meta['accept_count']}")
    print(f" Rejected:         {meta['reject_count']}")
    print(f" Uncertain:        {meta['uncertain_count']}")
    print("=" * 65 + "\n")


def print_instructions():
    print("\n" + "=" * 65)
    print(" PRIMARY INTENT DECISION RULES:")
    print(" 1. Identify the customer's focal grievance / actionable need.")
    print(" 2. Explicit questions/requests take precedence over background.")
    print(" 3. For multi-symptom cases, do NOT auto-choose the most severe.")
    print(" 4. Use the priority ladder ONLY as a secondary tie-breaker.")
    print(" 5. If genuinely insufficient context, use UNKNOWN_INSUFFICIENT_CONTEXT.")
    print(" 6. If it belongs elsewhere, REJECT and choose correct intent.")
    print(" 7. UNCERTAIN is valid for genuine ambiguity. Do not force a label.")
    print("=" * 65 + "\n")


def review_case(case, intent_map):
    cid = case["case_id"]
    part = case.get("part", "UNKNOWN_PART")
    tid = case["tweet_id"]
    conv_id = case["conversation_id"]
    text = case["text"]
    cand = case["candidate_intent"]
    cand_info = intent_map.get(cand, {})

    print("\n" + "-" * 70)
    print(f" CASE {cid:03d} OF 170 | Part: {part}")
    print(f" Tweet ID: {tid} | Conversation ID: {conv_id}")
    print("-" * 70)
    print(f"\nCUSTOMER INQUIRY TEXT:\n\033[1;36m\"{text}\"\033[0m\n")

    print(f"PROVISIONAL CANDIDATE INTENT (AI Proposal): \033[1;33m{cand}\033[0m")
    if cand_info:
        print(f"Definition: {cand_info.get('definition', '')}")
        print(f"Inclusion:  {cand_info.get('inclusion_criteria', '')}")
        print(f"Exclusion:  {cand_info.get('exclusion_criteria', '')}")

    if part == "PART_2_BOUNDARY_CASES":
        print(f"\nBoundary Pair: \033[1;35m{case.get('tested_pair')}\033[0m")
        print(f"Candidate Intent A: {case.get('candidate_intent')}")
        print(f"Competing Intent B: {case.get('alternative_intent')}")
        print(f"Distinguishing Rule: {case.get('deterministic_rule')}")

    if part == "PART_3_UNKNOWN_CASES":
        print(f"\nSampled Category: \033[1;35m{case.get('category')}\033[0m")
        print(f"Reason: {case.get('reason_not_technical')}")

    if case.get("reviewed"):
        print(f"\n\033[1;32m[CURRENTLY REVIEWED]\033[0m Decision: {case.get('human_decision')} | Label: {case.get('human_intent')}")
        if case.get("focal_grievance"):
            print(f"Focal Grievance: {case.get('focal_grievance')}")
        if case.get("reviewer_notes"):
            print(f"Reviewer Notes: {case.get('reviewer_notes')}")

    print("\nSelect Decision:")
    print(" [A] ACCEPT candidate intent")
    print(" [R] REJECT candidate intent (and select corrected intent)")
    print(" [U] UNCERTAIN (genuine ambiguity, requires reviewer note)")
    print(" [S] SKIP to next case without changing")
    print(" [Q] QUIT review session")

    while True:
        choice = input("\nDecision [A/R/U/S/Q]: ").strip().upper()
        if choice == "Q":
            return "QUIT"
        if choice == "S":
            return "SKIP"
        if choice == "A":
            fg = input("Focal Grievance / Actionable Need (short summary): ").strip()
            notes = input("Reviewer Notes (optional): ").strip()
            case["human_decision"] = "ACCEPT"
            case["human_intent"] = cand
            case["focal_grievance"] = fg if fg else None
            case["reviewer_notes"] = notes if notes else None
            case["reviewed"] = True
            case["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
            print("\033[1;32m✓ Saved as ACCEPT\033[0m")
            return "SAVED"
        if choice == "R":
            print("\nSelect Corrected Intent:")
            for idx, iid in enumerate(VALID_INTENTS, 1):
                print(f" {idx:2d}. {iid}")
            while True:
                sel = input(f"Choose corrected intent (1-{len(VALID_INTENTS)}): ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(VALID_INTENTS):
                    corr_intent = VALID_INTENTS[int(sel) - 1]
                    break
                print("Invalid selection. Enter a number 1 to 15.")

            fg = input("Focal Grievance / Actionable Need (short summary): ").strip()
            notes = input("Reviewer Notes (optional explanation for rejection): ").strip()
            case["human_decision"] = "REJECT"
            case["human_intent"] = corr_intent
            case["focal_grievance"] = fg if fg else None
            case["reviewer_notes"] = notes if notes else None
            case["reviewed"] = True
            case["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
            print(f"\033[1;33m✓ Saved as REJECT (Corrected: {corr_intent})\033[0m")
            return "SAVED"
        if choice == "U":
            fg = input("Focal Grievance / Actionable Need (short summary): ").strip()
            while True:
                notes = input("Reviewer Notes (REQUIRED for UNCERTAIN explaining ambiguity): ").strip()
                if notes:
                    break
                print("Reviewer notes are required when marking a case UNCERTAIN.")
            case["human_decision"] = "UNCERTAIN"
            case["human_intent"] = None
            case["focal_grievance"] = fg if fg else None
            case["reviewer_notes"] = notes
            case["reviewed"] = True
            case["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
            print("\033[1;34m✓ Saved as UNCERTAIN\033[0m")
            return "SAVED"
        print("Invalid choice. Please enter A, R, U, S, or Q.")


def main():
    parser = argparse.ArgumentParser(description="Human Review CLI for AppleSupport Inquiries")
    parser.add_argument("--status", action="store_true", help="Show current review progress")
    parser.add_argument("--case", type=int, default=None, help="Specific case ID to review (1-170)")
    parser.add_argument("--all", action="store_true", help="Review all cases, including already reviewed ones")
    args = parser.parse_args()

    labels_data, intent_map = load_data()

    if args.status:
        print_status(labels_data)
        return

    print_instructions()
    cases = labels_data["cases"]

    if args.case is not None:
        target_case = next((c for c in cases if c["case_id"] == args.case), None)
        if not target_case:
            print(f"Error: Case ID {args.case} not found. Valid range is 1-170.")
            sys.exit(1)
        res = review_case(target_case, intent_map)
        if res == "SAVED":
            save_data(labels_data)
        print_status(labels_data)
        return

    # Sequential review
    print_status(labels_data)
    for case in cases:
        if case.get("reviewed") and not args.all:
            continue
        res = review_case(case, intent_map)
        if res == "QUIT":
            print("\nSession paused by user.")
            break
        if res == "SAVED":
            save_data(labels_data)

    print_status(labels_data)


if __name__ == "__main__":
    main()
