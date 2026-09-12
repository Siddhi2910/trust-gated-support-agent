"""Acceptance tests for Taxonomy Input Export Package."""

import os
import json
import pandas as pd
import pytest
from src.conversations.reconstruct import compute_file_sha256
try:
    from src.taxonomy.export_inputs import export_taxonomy_sample
except ImportError:
    from src.export_inputs import export_taxonomy_sample

RAW_TWCS_PATH = os.path.join("data", "raw", "twcs.csv")
EXPECTED_RAW_SHA256 = "cd297fcfa1bf6f99938be242e8e578980bc6d1b96adc8691abec9a39175b03c0"
CONV_PARQUET_PATH = os.path.join("data", "processed", "applesupport_conversations.parquet")
EXPECTED_CONV_SHA256 = "c63c218f149f7e7552835ee2042a5eab3a9b44e9ee8b6cf06ed41161b716e6fa"

SAMPLE_CSV_PATH = os.path.join("artifacts", "taxonomy_input_sample.csv")
KEYWORD_FREQ_PATH = os.path.join("artifacts", "taxonomy_input_keyword_freq.json")
LENGTH_STATS_PATH = os.path.join("artifacts", "taxonomy_input_length_stats.json")
REPORT_PATH = os.path.join("src", "taxonomy", "taxonomy_input_export_report.md") if os.path.exists(os.path.join("src", "taxonomy", "taxonomy_input_export_report.md")) else os.path.join("reports", "taxonomy_input_export_report.md")


def test_export_artifacts_exist_and_non_empty():
    """Verify that all 4 required export artifacts exist and have meaningful content."""
    assert os.path.exists(SAMPLE_CSV_PATH), f"Missing {SAMPLE_CSV_PATH}"
    assert os.path.exists(KEYWORD_FREQ_PATH), f"Missing {KEYWORD_FREQ_PATH}"
    assert os.path.exists(LENGTH_STATS_PATH), f"Missing {LENGTH_STATS_PATH}"
    assert os.path.exists(REPORT_PATH), f"Missing {REPORT_PATH}"

    assert os.path.getsize(SAMPLE_CSV_PATH) > 10_000, "Sample CSV unexpectedly small"
    assert os.path.getsize(KEYWORD_FREQ_PATH) > 5_000, "Keyword freq JSON unexpectedly small"
    assert os.path.getsize(LENGTH_STATS_PATH) > 1_000, "Length stats JSON unexpectedly small"
    assert os.path.getsize(REPORT_PATH) > 2_000, "Report MD unexpectedly small"


def test_sample_csv_schema_and_size():
    """Verify sample size is within ~400-600 (500) and contains exact required columns."""
    df = pd.read_csv(SAMPLE_CSV_PATH)
    assert 400 <= len(df) <= 600, f"Sample size {len(df)} outside ~400-600 range!"
    assert len(df) == 500

    expected_cols = ["conversation_id", "tweet_id", "text", "turn_count", "created_at"]
    assert list(df.columns) == expected_cols, f"Columns mismatch: {list(df.columns)}"


def test_sample_csv_no_duplicate_tweet_ids_or_conversations():
    """Verify that every tweet_id, conversation_id, and raw text in sample is unique."""
    df = pd.read_csv(SAMPLE_CSV_PATH)
    assert df["tweet_id"].nunique() == len(df), "Duplicate tweet_ids found in sample!"
    assert df["conversation_id"].nunique() == len(df), "Duplicate conversation_ids found in sample!"
    assert df["text"].nunique() == len(df), "Duplicate customer texts found in sample!"


def test_sample_csv_text_fidelity():
    """Verify that sample text matches customer_inquiry_text in conversations parquet exactly."""
    conv_df = pd.read_parquet(CONV_PARQUET_PATH)
    conv_lookup = dict(zip(conv_df["conversation_id"], conv_df["customer_inquiry_text"]))

    sample_df = pd.read_csv(SAMPLE_CSV_PATH)
    for row in sample_df.itertuples(index=False):
        cid = row.conversation_id
        assert cid in conv_lookup, f"Conversation {cid} missing from Parquet!"
        assert row.text == conv_lookup[cid], f"Text modified for conversation {cid}!"


def test_sample_seed_reproducibility(tmp_path):
    """Verify that re-running export_taxonomy_sample with seed 42 produces identical output."""
    test_csv = str(tmp_path / "test_sample.csv")
    stats = export_taxonomy_sample(
        conversations_parquet_path=CONV_PARQUET_PATH,
        output_csv_path=test_csv,
        sample_size=500,
        random_seed=42
    )
    assert stats["sample_size"] == 500

    original_hash = compute_file_sha256(SAMPLE_CSV_PATH)
    reproduced_hash = compute_file_sha256(test_csv)
    assert original_hash == reproduced_hash, "Deterministic sampling is not reproducible!"


def test_keyword_freq_structure_and_top150_counts():
    """Verify keyword frequency JSON structure, counts, and top 150 coverage."""
    with open(KEYWORD_FREQ_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadata" in data
    assert data["metadata"]["total_inbound_messages_analyzed"] == 131258
    assert data["metadata"]["stopword_count"] > 200

    assert len(data["top_150_unigrams"]) == 150
    assert len(data["top_150_bigrams"]) == 150
    assert len(data["top_150_combined"]) == 150

    # Ensure all counts are positive integers and sorted descending
    for lst_key in ["top_150_unigrams", "top_150_bigrams", "top_150_combined"]:
        items = data[lst_key]
        counts = [item["count"] for item in items]
        assert all(c > 0 for c in counts), f"Non-positive counts in {lst_key}"
        assert counts == sorted(counts, reverse=True), f"{lst_key} is not sorted descending!"


def test_length_stats_validity():
    """Verify length stats JSON contains distributions for both all and first-turn messages."""
    with open(LENGTH_STATS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for key in ["all_inbound_messages", "first_turn_customer_inquiries"]:
        assert key in data
        assert "character_length" in data[key]
        assert "word_length" in data[key]

        c_stat = data[key]["character_length"]
        w_stat = data[key]["word_length"]

        assert c_stat["count"] > 0
        assert w_stat["count"] > 0
        assert c_stat["min"] <= c_stat["mean"] <= c_stat["max"]
        assert w_stat["min"] <= w_stat["mean"] <= w_stat["max"]

        # Check quantiles monotonicity
        for stat in [c_stat, w_stat]:
            q = stat["quantiles"]
            assert q["p10"] <= q["p25"] <= q["p50_median"] <= q["p75"] <= q["p90"] <= q["p95"] <= q["p99"]


def test_immutability_of_raw_and_phase2_artifacts():
    """Verify that data/raw/twcs.csv and conversations.parquet were not modified."""
    assert compute_file_sha256(RAW_TWCS_PATH) == EXPECTED_RAW_SHA256, "Raw TWCS modified!"
    assert compute_file_sha256(CONV_PARQUET_PATH) == EXPECTED_CONV_SHA256, "Conversations Parquet modified!"
