"""Executable runner for Phase 1A dataset audit.
Computes and outputs artifacts/phase1_dataset_audit.json with wall-clock timing.
"""

import os
import json
import time
import yaml
from src.data.audit import audit_raw_dataset

def main():
    with open("configs/base.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    raw_dataset_path = config["paths"]["raw_dataset"]
    artifacts_dir = config["paths"]["artifacts_dir"]
    os.makedirs(artifacts_dir, exist_ok=True)

    print(f"Starting Phase 1A raw dataset audit on {raw_dataset_path}...")
    t0 = time.time()
    audit_results = audit_raw_dataset(raw_dataset_path)
    wall_clock_time = time.time() - t0

    output_path = os.path.join(artifacts_dir, "phase1_dataset_audit.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print(f"Audit completed in {wall_clock_time:.2f}s.")
    print(f"Artifact written to: {output_path}")
    print("Summary:")
    print(f"  Total rows: {audit_results['row_counts']['total_rows']:,}")
    print(f"  Inbound: {audit_results['row_counts']['inbound_count']:,} | Outbound: {audit_results['row_counts']['outbound_count']:,}")
    print(f"  Unique tweet IDs: {audit_results['integrity_checks']['unique_tweet_ids']:,}")
    print(f"  Duplicate tweet IDs: {audit_results['integrity_checks']['duplicate_tweet_id_count']}")
    print(f"  Unique authors: {audit_results['integrity_checks']['unique_author_count']:,}")

if __name__ == "__main__":
    main()
