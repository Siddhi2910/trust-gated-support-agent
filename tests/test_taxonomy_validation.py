"""Tests for Taxonomy Validation Artifacts and Verbatim Integrity."""

import os
import json
import pytest
import pandas as pd


@pytest.fixture(scope="module")
def load_conversations():
    """Load conversations dataset for verbatim verification."""
    path = "data/processed/applesupport_conversations.parquet"
    assert os.path.exists(path), f"Missing {path}"
    df = pd.read_parquet(path)
    lookup = dict(zip(df["root_tweet_id"], df["customer_inquiry_text"]))
    conv_lookup = dict(zip(df["root_tweet_id"], df["conversation_id"]))
    return {"df": df, "lookup": lookup, "conv_lookup": conv_lookup}


def test_required_artifacts_exist():
    """Verify all Stage A-N required artifacts exist and are non-empty."""
    required_files = [
        "artifacts/taxonomy_stage_a_validation.json",
        "artifacts/taxonomy_stage_b_gaps.json",
        "artifacts/taxonomy_confusion_matrix.json",
        "artifacts/taxonomy_v1_candidate.json",
        "artifacts/taxonomy_provenance.json",
        "artifacts/taxonomy_human_review.json",
        "reports/taxonomy_validation_report.md"
    ]
    for path in required_files:
        assert os.path.exists(path), f"File {path} does not exist!"
        assert os.path.getsize(path) > 50, f"File {path} is empty or placeholder!"


def test_human_review_taxonomy_not_frozen():
    """Mandatory check: taxonomy_frozen must be False until human approval."""
    with open("artifacts/taxonomy_human_review.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("taxonomy_frozen") is False, "taxonomy_frozen must be False in taxonomy_human_review.json!"
    assert data.get("status") == "PROVISIONAL_PENDING_HUMAN_APPROVAL"

    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)
    assert v1.get("taxonomy_frozen") is False, "taxonomy_frozen must be False in taxonomy_v1_candidate.json!"


def test_candidate_v1_schema_and_verbatim_examples(load_conversations):
    """Verify candidate v1 schema and ensure all representative examples exist verbatim."""
    lookup = load_conversations["lookup"]
    conv_lookup = load_conversations["conv_lookup"]

    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)

    assert "intents" in v1
    assert len(v1["intents"]) == 15, f"Expected 15 candidate intents, got {len(v1['intents'])}"

    total_examples_checked = 0
    for intent in v1["intents"]:
        # Verify required keys
        required_keys = [
            "intent_id", "human_readable_name", "definition",
            "inclusion_criteria", "exclusion_criteria", "boundary_cases",
            "representative_examples", "prevalence_and_count",
            "annotation_rule", "known_ambiguity"
        ]
        for k in required_keys:
            assert k in intent, f"Missing key {k} in intent {intent.get('intent_id')}"

        # Verify representative examples count and verbatim accuracy
        examples = intent["representative_examples"]
        assert len(examples) >= 5, f"Expected at least 5 examples for {intent['intent_id']}, got {len(examples)}"

        for ex in examples:
            tid = ex["tweet_id"]
            cid = ex["conversation_id"]
            text = ex["text"]

            assert tid in lookup, f"Tweet {tid} not in source dataset!"
            assert conv_lookup[tid] == cid, f"Conversation ID mismatch for tweet {tid}: got {cid}, expected {conv_lookup[tid]}"
            assert lookup[tid] == text, f"Text mismatch for tweet {tid}!\nEXPECTED: {lookup[tid]}\nGOT: {text}"
            total_examples_checked += 1

    assert total_examples_checked >= 75, f"Total verified examples was {total_examples_checked}, expected >= 75"


def test_no_duplicate_examples_across_intents():
    """Verify that no tweet_id is reused across different intents."""
    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)

    all_tids = []
    for intent in v1["intents"]:
        for ex in intent["representative_examples"]:
            all_tids.append(ex["tweet_id"])

    assert len(all_tids) == 75, f"Expected 75 total examples, got {len(all_tids)}"
    unique_tids = set(all_tids)
    assert len(unique_tids) == 75, f"Found {len(all_tids) - len(unique_tids)} duplicate examples across intents!"


def test_representative_examples_are_inbound_customers(load_conversations):
    """Verify that every representative example is an inbound customer inquiry."""
    df = load_conversations["df"]
    inbound_map = dict(zip(df["root_tweet_id"], df["root_inbound"]))
    author_map = dict(zip(df["root_tweet_id"], df["root_author_id"]))

    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)

    for intent in v1["intents"]:
        for ex in intent["representative_examples"]:
            tid = ex["tweet_id"]
            assert inbound_map[tid] is True or inbound_map[tid] == 1, f"Tweet {tid} is not inbound!"
            assert author_map[tid] != "AppleSupport", f"Tweet {tid} authored by AppleSupport!"


def test_known_problematic_tweets_not_misclassified():
    """Verify that specifically audited problematic tweets are not assigned to mismatched intents."""
    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)

    intent_map = {it["intent_id"]: [ex["tweet_id"] for ex in it["representative_examples"]] for it in v1["intents"]}

    # Tweet 2640 is macbook power/charging failure; must NOT be in DEVICE_FREEZE_CRASH_REBOOT
    assert 2640 not in intent_map.get("DEVICE_FREEZE_CRASH_REBOOT", []), "Tweet 2640 falsely assigned to DEVICE_FREEZE_CRASH_REBOOT"

    # Tweet 714 is iOS 11 'I' autocorrect bug; must NOT be in APP_SPECIFIC_MALFUNCTION
    assert 714 not in intent_map.get("APP_SPECIFIC_MALFUNCTION", []), "Tweet 714 falsely assigned to APP_SPECIFIC_MALFUNCTION"

    # Tweet 749 is 'Has Youtube lost it?'; must NOT be in DATA_LOSS_RECOVERY
    assert 749 not in intent_map.get("DATA_LOSS_RECOVERY", []), "Tweet 749 falsely assigned to DATA_LOSS_RECOVERY"

    # Tweet 765 is Spotify on lock screen; must NOT be in SCREEN_DISPLAY_TOUCH_BIOMETRICS
    assert 765 not in intent_map.get("SCREEN_DISPLAY_TOUCH_BIOMETRICS", []), "Tweet 765 falsely assigned to SCREEN_DISPLAY_TOUCH_BIOMETRICS"
    assert 765 not in intent_map.get("SCREEN_DISPLAY_HARDWARE_SYMPTOM", []), "Tweet 765 falsely assigned to SCREEN_DISPLAY_HARDWARE_SYMPTOM"

    # Tweet 2628 is battery dying quick; must NOT be in BILLING or HARDWARE_CHARGING
    assert 2628 not in intent_map.get("BILLING_CHARGE_REFUND_DISPUTE", []), "Tweet 2628 falsely assigned to BILLING"
    assert 2628 not in intent_map.get("HARDWARE_CHARGING_POWER_CABLE", []), "Tweet 2628 falsely assigned to HARDWARE_CHARGING"

    # Tweet 4912 is battery longevity 'per charge'; must NOT be in BILLING or HARDWARE_CHARGING
    assert 4912 not in intent_map.get("BILLING_CHARGE_REFUND_DISPUTE", []), "Tweet 4912 falsely assigned to BILLING"
    assert 4912 not in intent_map.get("HARDWARE_CHARGING_POWER_CABLE", []), "Tweet 4912 falsely assigned to HARDWARE_CHARGING"

    # Tweet 12596 is virus/popups; must NOT be in ORDER_PURCHASE_SHIPPING_STATUS
    assert 12596 not in intent_map.get("ORDER_PURCHASE_SHIPPING_STATUS", []), "Tweet 12596 falsely assigned to ORDER_PURCHASE_SHIPPING_STATUS"


def test_confusion_matrix_verbatim_examples(load_conversations):
    """Verify confusion matrix pairs have valid distinguishing rules, existing intents, and verbatim examples."""
    lookup = load_conversations["lookup"]

    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)
    valid_intents = {it["intent_id"] for it in v1["intents"]}

    with open("artifacts/taxonomy_confusion_matrix.json", "r", encoding="utf-8") as f:
        cm = json.load(f)

    assert "confusable_pairs" in cm
    assert len(cm["confusable_pairs"]) >= 6

    for pair in cm["confusable_pairs"]:
        assert "pair_id" in pair
        assert "distinguishing_rule" in pair
        assert "tie_breaker" in pair

        # Ensure both intents exist in candidate taxonomy
        assert pair["intent_a"] in valid_intents, f"Confusion matrix pair {pair['pair_id']} references unknown intent_a: {pair['intent_a']}"
        assert pair["intent_b"] in valid_intents, f"Confusion matrix pair {pair['pair_id']} references unknown intent_b: {pair['intent_b']}"

        for ex_type in ["positive_example", "counterexample"]:
            assert ex_type in pair
            ex = pair[ex_type]
            tid = ex["tweet_id"]
            text = ex["text"]
            assert tid in lookup, f"Confusion matrix tweet {tid} not in dataset!"
            assert lookup[tid] == text, f"Confusion matrix text mismatch for tweet {tid}"


def test_candidate_taxonomy_no_stale_intent_references():
    """Verify that no intent definition or criteria references nonexistent or deprecated intent IDs."""
    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)

    valid_intents = {it["intent_id"] for it in v1["intents"]}
    deprecated_stale_intents = {
        "STORAGE_MANAGEMENT_DISK_SPACE",
        "HARDWARE_PHYSICAL_DEFECT",
        "HOW_TO_GENERAL_PRODUCT_QUESTION",
        "NOTIFICATION_ALERT_BADGE_ISSUE",
        "SCREEN_DISPLAY_HARDWARE_SYMPTOM",
        "UNKNOWN_OUT_OF_SCOPE"
    }

    for it in v1["intents"]:
        iid = it["intent_id"]
        assert iid not in deprecated_stale_intents, f"Intent {iid} is a deprecated intent ID!"
        for field in ["inclusion_criteria", "exclusion_criteria", "boundary_cases", "annotation_rule"]:
            vals = it.get(field, [])
            if isinstance(vals, str):
                vals = [vals]
            for v in vals:
                for stale in deprecated_stale_intents:
                    assert stale not in v, f"Intent {iid} ({field}) references stale/deprecated intent {stale}!"


def test_provenance_and_lineage_traceability():
    """Verify taxonomy provenance traces every candidate intent to provisional origins."""
    with open("artifacts/taxonomy_provenance.json", "r", encoding="utf-8") as f:
        prov = json.load(f)

    assert "source_dataset_fingerprints" in prov
    fps = prov["source_dataset_fingerprints"]
    assert "applesupport_conversations_parquet_sha256" in fps
    assert "applesupport_subset_parquet_sha256" in fps

    assert "intent_lineage" in prov
    lineage = prov["intent_lineage"]

    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)

    for intent in v1["intents"]:
        iid = intent["intent_id"]
        assert iid in lineage, f"Intent {iid} missing from provenance lineage!"
        assert "origin" in lineage[iid]
        assert "source_provisional" in lineage[iid]
        assert "justification" in lineage[iid]


def test_stage_a_counts_match_denominator(load_conversations):
    """Verify Stage A denominator matches real conversation dataset row count."""
    df_conv = load_conversations["df"]
    expected_n = len(df_conv[df_conv["root_inbound"] == True])

    with open("artifacts/taxonomy_stage_a_validation.json", "r", encoding="utf-8") as f:
        stage_a = json.load(f)

    assert stage_a["corpus_stats"]["total_opening_customer_inquiries"] == expected_n
    for item in stage_a["provisional_intents"]:
        m = item["measurement"]
        assert m["denominator_opening_inquiries"] == expected_n
        assert m["inbound_opening_inquiries_count"] <= expected_n
        assert m["inbound_opening_inquiries_count"] >= 0


def test_unknown_measurement_integrity(load_conversations):
    """Verify UNKNOWN_INSUFFICIENT_CONTEXT measurement artifact integrity and corpus prevalence."""
    df_conv = load_conversations["df"]
    expected_n = len(df_conv[df_conv["root_inbound"] == True])

    with open("artifacts/taxonomy_unknown_measurement.json", "r", encoding="utf-8") as f:
        meas = json.load(f)

    assert meas["measurement_metadata"]["denominator"] == expected_n
    assert meas["measurement_metadata"]["total_unknown_count"] == 522
    assert abs(meas["measurement_metadata"]["total_unknown_pct"] - 0.65) < 0.05
    assert meas["category_breakdown"]["CATEGORY_A_OUT_OF_SCOPE_NON_SUPPORT"]["count"] == 5
    assert meas["category_breakdown"]["CATEGORY_B_GENUINE_SUPPORT_INSUFFICIENT_CONTEXT"]["total_count"] == 517


def test_human_review_sample_integrity(load_conversations):
    """Verify the 170-case deterministic human-review sample pack integrity, verbatim text, and disjointness."""
    lookup = load_conversations["lookup"]

    with open("artifacts/taxonomy_human_review_sample.json", "r", encoding="utf-8") as f:
        samp = json.load(f)

    meta = samp["metadata"]
    assert meta["random_seed"] == 42
    assert meta["total_cases"] == 170
    assert meta["taxonomy_frozen"] is False

    # Check showcase examples to ensure non-overlap
    with open("artifacts/taxonomy_v1_candidate.json", "r", encoding="utf-8") as f:
        v1 = json.load(f)
    showcase_tids = {ex["tweet_id"] for it in v1["intents"] for ex in it["representative_examples"]}

    with open("artifacts/taxonomy_confusion_matrix.json", "r", encoding="utf-8") as f:
        cm = json.load(f)
    for p in cm["confusable_pairs"]:
        showcase_tids.add(p["positive_example"]["tweet_id"])
        showcase_tids.add(p["counterexample"]["tweet_id"])

    # Part 1: 120 cases
    p1 = samp["part_1_candidate_intents"]
    assert len(p1) == 120
    by_intent = {}
    for item in p1:
        iid = item["candidate_intent"]
        by_intent.setdefault(iid, []).append(item)
    assert len(by_intent) == 15
    for iid, items in by_intent.items():
        assert len(items) == 8, f"Expected 8 cases for intent {iid}, got {len(items)}"

    # Part 2: 35 cases
    p2 = samp["part_2_boundary_cases"]
    assert len(p2) == 35
    by_pair = {}
    for item in p2:
        pid = item["tested_pair"]
        by_pair.setdefault(pid, []).append(item)
    assert len(by_pair) == 7
    for pid, items in by_pair.items():
        assert len(items) == 5, f"Expected 5 cases for pair {pid}, got {len(items)}"

    # Part 3: 15 cases
    p3 = samp["part_3_unknown_cases"]
    assert len(p3) == 15

    all_sampled_tids = set()
    for grp in [p1, p2, p3]:
        for item in grp:
            tid = item["tweet_id"]
            assert tid not in showcase_tids, f"Sampled tweet {tid} overlaps with showcase examples!"
            assert tid not in all_sampled_tids, f"Duplicate tweet {tid} in human review sample!"
            all_sampled_tids.add(tid)
            assert tid in lookup, f"Sampled tweet {tid} not in dataset!"
            assert lookup[tid] == item["text"], f"Verbatim mismatch for sampled tweet {tid}"

    assert len(all_sampled_tids) == 170

    # Ensure markdown report exists and has instructions and cases
    with open("reports/taxonomy_human_review_sample.md", "r", encoding="utf-8") as f:
        report_md = f.read()

    assert "Human Review Protocol and Annotation Instructions" in report_md
    assert "Focal Grievance / Actionable Need Rule" in report_md
    assert "The Deterministic Tie-Breaker Ladder" in report_md
    assert "SCREEN_DISPLAY_TOUCH_BIOMETRICS" in report_md
    assert "AUDIO_SOUND_SPEAKER_MIC" in report_md
    assert "Case 001" in report_md
    assert "Case 170" in report_md

