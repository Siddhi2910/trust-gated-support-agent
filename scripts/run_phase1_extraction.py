"""Executable runner for Phase 1 AppleSupport extraction.
Outputs data/processed/applesupport_subset.parquet and artifacts/phase1_provenance_manifest.json.
"""

import os
import sys
import json
import time
import yaml

sys.path.insert(0, os.path.abspath("."))
from src.data.extraction import extract_applesupport_subset

def main():
    with open("configs/base.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    raw_path = config["paths"]["raw_dataset"]
    output_parquet = config["paths"]["applesupport_subset"]
    artifacts_dir = config["paths"]["artifacts_dir"]
    target_brand = config["project"]["target_brand"]
    include_full_context = config.get("extraction", {}).get("include_full_context", True)

    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)

    print(f"Starting Phase 1 AppleSupport extraction from {raw_path} to {output_parquet}...")
    t0 = time.time()
    manifest = extract_applesupport_subset(
        raw_csv_path=raw_path,
        output_parquet_path=output_parquet,
        target_brand=target_brand,
        include_full_context=include_full_context,
    )
    wall_clock = time.time() - t0

    manifest_path = os.path.join(artifacts_dir, "phase1_provenance_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Also keep a standard artifacts/provenance_manifest.json pointer
    std_manifest_path = os.path.join(artifacts_dir, "provenance_manifest.json")
    with open(std_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Extraction completed in {wall_clock:.2f}s.")
    print(f"Parquet written to: {output_parquet} ({manifest['derived_dataset']['size_mb']} MB)")
    print(f"Provenance manifest written to: {manifest_path}")
    print(f"Summary:")
    print(f"  Raw rows: {manifest['reduction_metrics']['raw_total_rows']:,}")
    print(f"  Derived rows: {manifest['reduction_metrics']['derived_total_rows']:,}")
    print(f"  Unique conversations: {manifest['derived_dataset']['unique_conversation_ids']:,}")
    print(f"  Reduction ratio: {manifest['reduction_metrics']['reduction_ratio']}x ({manifest['reduction_metrics']['retention_percentage']})")
    print(f"  Integrity: all derived tweet IDs verified in raw = {manifest['provenance_integrity']['all_derived_tweet_ids_in_raw']}")

if __name__ == "__main__":
    main()
