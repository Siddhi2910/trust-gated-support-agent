import os
import json
import pytest

def test_phase1_audit_artifact_exists_and_valid():
    """Verify that artifacts/phase1_dataset_audit.json exists and satisfies strict schema."""
    audit_path = os.path.join("artifacts", "phase1_dataset_audit.json")
    assert os.path.exists(audit_path), f"Audit artifact missing at {audit_path}"
    with open(audit_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["row_counts"]["total_rows"] == 2811774
    assert data["row_counts"]["inbound_count"] == 1537843
    assert data["row_counts"]["outbound_count"] == 1273931
    assert data["row_counts"]["invalid_inbound_flags"] == 0
    assert data["integrity_checks"]["unique_tweet_ids"] == 2811774
    assert data["integrity_checks"]["duplicate_tweet_id_count"] == 0
    assert data["integrity_checks"]["exact_duplicate_row_count"] == 0
    assert data["file_info"]["sha256"] == "cd297fcfa1bf6f99938be242e8e578980bc6d1b96adc8691abec9a39175b03c0"

def test_phase1_verification_artifact_and_decision():
    """Verify that artifacts/phase1_applesupport_verification.json records a definitive GO decision."""
    verif_path = os.path.join("artifacts", "phase1_applesupport_verification.json")
    assert os.path.exists(verif_path), f"Verification artifact missing at {verif_path}"
    with open(verif_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["target_brand"] == "AppleSupport"
    assert data["brand_verification_decision"]["decision"] == "GO"
    assert data["outbound_volume"]["applesupport_outbound_tweet_count"] == 106860
    assert data["response_coverage"]["response_coverage_rate"] > 0.85
    assert data["response_coverage"]["responded_inbound_count"] > 100000
    assert data["reply_length_stats"]["mean_char_length"] > 100
    assert "disclaimer" in data["pii_heuristic_indicators"]

def test_phase1_report_exists_and_complete():
    """Verify that reports/phase1_brand_verification.md exists and contains all required metrics."""
    report_path = os.path.join("reports", "phase1_brand_verification.md")
    assert os.path.exists(report_path), f"Report missing at {report_path}"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Decision: `GO`" in content or "Decision:** `GO`" in content
    assert "AppleSupport" in content
    assert "106,860" in content
    assert "Response Coverage Rate:" in content
    assert "Mean:" in content
    assert "Heuristic PII Indicator Rate:" in content

def test_phase1_extraction_parquet_and_provenance():
    """Verify that data/processed/applesupport_subset.parquet and provenance manifest exist and are valid."""
    parquet_path = os.path.join("data", "processed", "applesupport_subset.parquet")
    manifest_path = os.path.join("artifacts", "phase1_provenance_manifest.json")

    if not os.path.exists(parquet_path):
        pytest.skip(f"Extracted parquet missing at {parquet_path} (raw dataset omitted from git)")
    assert os.path.exists(manifest_path), f"Provenance manifest missing at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["target_brand"] == "AppleSupport"
    assert manifest["raw_dataset"]["sha256_unchanged"] is True
    assert manifest["raw_dataset"]["total_rows"] == 2811774
    assert manifest["derived_dataset"]["total_rows"] == 237941
    assert manifest["derived_dataset"]["unique_conversation_ids"] == 80391
    assert manifest["provenance_integrity"]["all_derived_tweet_ids_in_raw"] is True
    assert manifest["reduction_metrics"]["reduction_ratio"] > 10.0
    assert os.path.getsize(parquet_path) == manifest["derived_dataset"]["size_bytes"]

