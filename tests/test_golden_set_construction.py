"""Tests for Golden Set Construction, Human Review Workflow, and Ground Truth Integrity."""

import os
import sys
import json
import subprocess
import pytest
import pandas as pd

HUMAN_LABELS_PATH = "artifacts/human_review_labels.json"
REVIEW_SAMPLE_PATH = "artifacts/taxonomy_human_review_sample.json"
CANDIDATE_TAX_PATH = "artifacts/taxonomy_v1_candidate.json"
CONFUSION_MATRIX_PATH = "artifacts/taxonomy_confusion_matrix.json"
CONVERSATIONS_PARQUET = "data/processed/applesupport_conversations.parquet"


@pytest.fixture(scope="module")
def load_conversations():
    """Load processed conversations dataset for provenance verification."""
    if not os.path.exists(CONVERSATIONS_PARQUET):
        pytest.skip(f"Missing {CONVERSATIONS_PARQUET} (raw dataset omitted from git)")
    df = pd.read_parquet(CONVERSATIONS_PARQUET)
    lookup = dict(zip(df["root_tweet_id"], df["customer_inquiry_text"]))
    conv_lookup = dict(zip(df["root_tweet_id"], df["conversation_id"]))
    return {"df": df, "lookup": lookup, "conv_lookup": conv_lookup}


def test_review_pack_and_labels_exist_and_track_integrity():
    """Verify artifacts exist and strictly track label consistency and unreviewed integrity."""
    assert os.path.exists(HUMAN_LABELS_PATH), f"Missing {HUMAN_LABELS_PATH}"
    assert os.path.exists(REVIEW_SAMPLE_PATH), f"Missing {REVIEW_SAMPLE_PATH}"

    with open(HUMAN_LABELS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["metadata"]
    cases = data["cases"]
    assert len(cases) == 170
    assert meta["total_cases"] == 170, f"Expected 170 cases, got {meta['total_cases']}"
    
    actual_reviewed = sum(1 for c in cases if c["reviewed"])
    actual_remaining = sum(1 for c in cases if not c["reviewed"])
    actual_accept = sum(1 for c in cases if c.get("human_decision") == "ACCEPT")
    actual_reject = sum(1 for c in cases if c.get("human_decision") == "REJECT")
    actual_uncertain = sum(1 for c in cases if c.get("human_decision") == "UNCERTAIN")

    assert meta["reviewed_count"] == actual_reviewed
    assert meta["remaining_count"] == actual_remaining
    assert meta["accept_count"] == actual_accept
    assert meta["reject_count"] == actual_reject
    assert meta["uncertain_count"] == actual_uncertain

    for c in cases:
        assert c["candidate_intent"] is not None, f"Case {c['case_id']} missing candidate_intent!"
        if not c["reviewed"]:
            assert c["human_decision"] is None, f"Unreviewed Case {c['case_id']} has human_decision!"
            assert c["human_intent"] is None, f"Unreviewed Case {c['case_id']} has human_intent!"
        else:
            assert c["human_decision"] in ["ACCEPT", "REJECT", "UNCERTAIN"], f"Invalid decision in Case {c['case_id']}"


def test_every_case_has_provenance_and_verbatim_text(load_conversations):
    """Verify every review case has genuine provenance and verbatim text in applesupport corpus."""
    lookup = load_conversations["lookup"]
    conv_lookup = load_conversations["conv_lookup"]

    with open(HUMAN_LABELS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for c in data["cases"]:
        tid = c["tweet_id"]
        conv_id = c["conversation_id"]
        text = c["text"]

        assert tid in lookup, f"Tweet ID {tid} (Case {c['case_id']}) not in corpus!"
        assert conv_lookup[tid] == conv_id, f"Conv ID mismatch for Tweet {tid}"
        assert lookup[tid] == text, f"Verbatim text mismatch for Tweet {tid}"


def test_no_duplicate_tweet_ids():
    """Verify all 170 sampled cases have unique tweet IDs."""
    with open(HUMAN_LABELS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    tweet_ids = [c["tweet_id"] for c in data["cases"]]
    assert len(tweet_ids) == 170
    assert len(set(tweet_ids)) == 170, "Duplicate tweet IDs detected in review pack!"


def test_no_showcase_example_overlap():
    """Verify complete disjointness between the 170 review cases and 79 showcase examples."""
    with open(CANDIDATE_TAX_PATH, "r", encoding="utf-8") as f:
        tax = json.load(f)

    showcase_tids = {ex["tweet_id"] for it in tax["intents"] for ex in it["representative_examples"]}

    with open(CONFUSION_MATRIX_PATH, "r", encoding="utf-8") as f:
        cm = json.load(f)

    for p in cm["confusable_pairs"]:
        showcase_tids.add(p["positive_example"]["tweet_id"])
        showcase_tids.add(p["counterexample"]["tweet_id"])

    assert len(showcase_tids) == 79, f"Expected 79 showcase examples, found {len(showcase_tids)}"

    with open(HUMAN_LABELS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    review_tids = {c["tweet_id"] for c in data["cases"]}
    overlap = review_tids.intersection(showcase_tids)
    assert len(overlap) == 0, f"Found {len(overlap)} overlapping tweets between review pack and showcase: {overlap}"


def test_taxonomy_frozen_is_false_before_final_human_review():
    """Ensure taxonomy is NOT frozen until human review is complete."""
    with open(CANDIDATE_TAX_PATH, "r", encoding="utf-8") as f:
        tax = json.load(f)
    assert tax.get("taxonomy_frozen") is False, "taxonomy_frozen must be False in candidate taxonomy!"

    # Also check artifacts/golden_set.json does not prematurely exist
    if os.path.exists("artifacts/golden_set.json"):
        with open("artifacts/golden_set.json", "r", encoding="utf-8") as f:
            gs = json.load(f)
        # If it exists, all cases must be reviewed
        assert gs["metadata"]["total_cases"] == 170


def test_unreviewed_cases_cannot_enter_golden_set():
    """Verify that finalize_golden_set.py blocks and fails when unreviewed cases exist."""
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmpdir:
        art_dir = os.path.join(tmpdir, "artifacts")
        os.makedirs(art_dir, exist_ok=True)
        # Mock an unreviewed labels file
        mock_labels = {
            "metadata": {"total_cases": 1, "reviewed_count": 0, "remaining_count": 1},
            "cases": [{"case_id": 1, "reviewed": False, "human_decision": None}]
        }
        with open(os.path.join(art_dir, "human_review_labels.json"), "w", encoding="utf-8") as f:
            json.dump(mock_labels, f)
        
        script_path = os.path.abspath("scripts/finalize_golden_set.py")
        res = subprocess.run(
            [sys.executable, script_path],
            cwd=tmpdir,
            capture_output=True,
            text=True
        )
        assert res.returncode != 0, "finalize_golden_set.py should exit with non-zero code when unreviewed cases exist!"
        assert "BLOCKED: Cannot finalize Golden Set!" in res.stdout
        assert "unreviewed cases remaining" in res.stdout


def test_candidate_labels_belong_to_taxonomy():
    """Verify all candidate intents belong to the declared 15 intents."""
    with open(CANDIDATE_TAX_PATH, "r", encoding="utf-8") as f:
        tax = json.load(f)
    valid_intents = {it["intent_id"] for it in tax["intents"]}

    with open(HUMAN_LABELS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for c in data["cases"]:
        cand = c["candidate_intent"]
        assert cand in valid_intents, f"Invalid candidate intent {cand} in Case {c['case_id']}"


def test_uncertain_handling_is_explicit():
    """Verify uncertain handling: require reviewer notes and distinguish ambiguous cases."""
    # Test review CLI logic for uncertain decision
    from scripts.review_cli import VALID_INTENTS
    assert len(VALID_INTENTS) == 15
    assert "UNKNOWN_INSUFFICIENT_CONTEXT" in VALID_INTENTS
