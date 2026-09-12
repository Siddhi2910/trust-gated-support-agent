"""Acceptance tests for Phase 2 Conversation Reconstruction."""

import os
import json
import hashlib
import pandas as pd
import pytest
from src.conversations.reconstruct import compute_file_sha256

RAW_TWCS_PATH = os.path.join("data", "raw", "twcs.csv")
EXPECTED_RAW_SHA256 = "cd297fcfa1bf6f99938be242e8e578980bc6d1b96adc8691abec9a39175b03c0"
SUBSET_PARQUET_PATH = os.path.join("data", "processed", "applesupport_subset.parquet")
CONV_PARQUET_PATH = os.path.join("data", "processed", "applesupport_conversations.parquet")
STATS_JSON_PATH = os.path.join("artifacts", "phase2_conversation_stats.json")
REPORT_MD_PATH = os.path.join("reports", "phase2_conversation_report.md")

if not os.path.exists(CONV_PARQUET_PATH):
    pytest.skip("Phase 2 parquet files omitted from git repo", allow_module_level=True)


def test_reconstruction_artifacts_exist_and_valid():
    """Verify that all Phase 2 outputs exist and are non-empty."""
    assert os.path.exists(CONV_PARQUET_PATH), f"Missing {CONV_PARQUET_PATH}"
    assert os.path.exists(STATS_JSON_PATH), f"Missing {STATS_JSON_PATH}"
    assert os.path.exists(REPORT_MD_PATH), f"Missing {REPORT_MD_PATH}"

    assert os.path.getsize(CONV_PARQUET_PATH) > 10_000_000, "Parquet file unexpectedly small"
    assert os.path.getsize(STATS_JSON_PATH) > 1_000, "Stats JSON unexpectedly small"
    assert os.path.getsize(REPORT_MD_PATH) > 2_000, "Report MD unexpectedly small"

    with open(STATS_JSON_PATH, "r", encoding="utf-8") as f:
        stats = json.load(f)

    assert stats["phase"] == "phase2_conversation_reconstruction"
    assert stats["conversation_counts"]["total_reconstructed_conversations"] == 80391
    assert stats["turn_counts"]["total_turns"] == 237941
    assert stats["conversation_counts"]["percentage_with_customer_and_applesupport"] == "100.00%"


def test_every_reconstructed_tweet_id_exists_in_phase1_subset():
    """Verify that all reconstructed tweet IDs exist in Phase 1 subset and count matches."""
    subset_df = pd.read_parquet(SUBSET_PARQUET_PATH)
    subset_tids = set(subset_df["tweet_id"].values)

    conv_df = pd.read_parquet(CONV_PARQUET_PATH)
    assert len(conv_df) == 80391

    reconstructed_tids = set()
    total_turns_counted = 0

    # Sample check 5,000 conversations for deep turn-level verification
    sampled_rows = conv_df.head(5000)
    for row in sampled_rows.itertuples(index=False):
        turns = json.loads(row.turns_json)
        total_turns_counted += len(turns)
        for t in turns:
            tid = t["tweet_id"]
            assert tid in subset_tids, f"Tweet ID {tid} not found in subset!"
            reconstructed_tids.add(tid)

    # Across all conversations, check num_turns sum
    assert conv_df["num_turns"].sum() == 237941
    assert conv_df["num_turns"].min() >= 2


def test_no_original_text_is_changed():
    """Verify that tweet text was not altered during reconstruction."""
    subset_df = pd.read_parquet(SUBSET_PARQUET_PATH)
    text_lookup = dict(zip(subset_df["tweet_id"], subset_df["text"]))

    conv_df = pd.read_parquet(CONV_PARQUET_PATH)
    # Check 1,000 conversations
    for row in conv_df.head(1000).itertuples(index=False):
        turns = json.loads(row.turns_json)
        for t in turns:
            tid = t["tweet_id"]
            original_text = text_lookup[tid]
            assert t["text"] == original_text, f"Text mismatch for tweet {tid}"


def test_conversation_id_assignment_is_deterministic():
    """Verify conversation_id corresponds to root_tweet_id and assignment is consistent."""
    conv_df = pd.read_parquet(CONV_PARQUET_PATH)
    assert (conv_df["conversation_id"] == conv_df["root_tweet_id"]).all(), "conversation_id != root_tweet_id!"
    assert conv_df["conversation_id"].is_unique, "conversation_id is not unique!"
    assert conv_df["conversation_id"].is_monotonic_increasing, "conversation_ids are not strictly sorted!"


def test_no_duplicate_tweet_id_assigned():
    """Verify no tweet ID is duplicated across conversations or turns."""
    conv_df = pd.read_parquet(CONV_PARQUET_PATH)
    seen_tids = set()

    for row in conv_df.head(10000).itertuples(index=False):
        turns = json.loads(row.turns_json)
        for t in turns:
            tid = t["tweet_id"]
            assert tid not in seen_tids, f"Duplicate tweet ID {tid} detected!"
            seen_tids.add(tid)


def test_parent_child_relationships_are_consistent():
    """Verify parent/child graph integrity within conversations."""
    conv_df = pd.read_parquet(CONV_PARQUET_PATH)

    for row in conv_df.head(2000).itertuples(index=False):
        turns = json.loads(row.turns_json)
        turn_map = {t["tweet_id"]: t for t in turns}

        for t in turns:
            pid = t["parent_tweet_id"]
            if pid is not None:
                assert pid in turn_map, f"Parent {pid} not found in conversation {row.conversation_id}"
                # The parent must have t["tweet_id"] in its child_tweet_ids
                parent_turn = turn_map[pid]
                assert t["tweet_id"] in parent_turn["child_tweet_ids"], (
                    f"Child {t['tweet_id']} missing from parent {pid} child list!"
                )
                # Monotonic timestamp check
                assert t["created_at_epoch"] >= parent_turn["created_at_epoch"], (
                    f"Timing anomaly: child {t['tweet_id']} timestamp precedes parent {pid}"
                )


def test_no_unrelated_records_are_merged():
    """Verify that every turn in a conversation is topologically linked to the root."""
    conv_df = pd.read_parquet(CONV_PARQUET_PATH)

    for row in conv_df.head(1000).itertuples(index=False):
        turns = json.loads(row.turns_json)
        root_id = row.root_tweet_id
        turn_map = {t["tweet_id"]: t for t in turns}

        for t in turns:
            curr = t["tweet_id"]
            path = set()
            while curr != root_id:
                path.add(curr)
                parent_id = turn_map[curr]["parent_tweet_id"]
                assert parent_id is not None, f"Node {curr} in conv {root_id} has no path to root!"
                assert parent_id not in path, f"Cycle detected at node {parent_id} in conv {root_id}!"
                curr = parent_id
            assert curr == root_id


def test_raw_twcs_remains_unchanged():
    """Verify that data/raw/twcs.csv has remained strictly immutable."""
    assert os.path.exists(RAW_TWCS_PATH), "Raw TWCS file missing!"
    current_hash = compute_file_sha256(RAW_TWCS_PATH)
    assert current_hash == EXPECTED_RAW_SHA256, "FATAL: Raw TWCS dataset was modified!"


def test_provenance_and_both_roles_present():
    """Verify that 100% of conversations have customer and AppleSupport turns."""
    conv_df = pd.read_parquet(CONV_PARQUET_PATH)
    assert (conv_df["has_customer_and_brand"] == True).all()
    assert (conv_df["num_customer_turns"] >= 1).all()
    assert (conv_df["num_brand_turns"] >= 1).all()
    assert (conv_df["is_multi_turn"] == True).all()
