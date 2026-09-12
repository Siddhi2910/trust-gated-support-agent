"""Executable runner for Phase 2 Conversation Reconstruction.

Loads verified AppleSupport Parquet subset, reconstructs multi-turn conversational
trees, and outputs:
- data/processed/applesupport_conversations.parquet
- artifacts/phase2_conversation_stats.json
"""

import os
import sys
import json
import time
import yaml

sys.path.insert(0, os.path.abspath("."))
from src.conversations.reconstruct import reconstruct_conversations


def main():
    with open("configs/base.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    input_parquet = config["paths"]["applesupport_subset"]
    output_parquet = config["paths"]["applesupport_conversations"]
    raw_csv = config["paths"]["raw_dataset"]
    artifacts_dir = config["paths"]["artifacts_dir"]
    target_brand = config["project"]["target_brand"]

    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)

    print(f"Starting Phase 2 Conversation Reconstruction...")
    print(f"  Input: {input_parquet}")
    print(f"  Output: {output_parquet}")
    print(f"  Target Brand: {target_brand}")

    t0 = time.time()
    stats = reconstruct_conversations(
        input_parquet_path=input_parquet,
        output_parquet_path=output_parquet,
        target_brand=target_brand,
        raw_csv_path=raw_csv,
    )
    wall_clock = time.time() - t0

    stats_path = os.path.join(artifacts_dir, "phase2_conversation_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"\nReconstruction completed in {wall_clock:.2f}s (reconstruction loop: {stats['execution_metadata']['elapsed_wall_seconds']}s).")
    print(f"Conversations Parquet: {output_parquet} ({stats['output_dataset']['size_mb']} MB)")
    print(f"Stats written to: {stats_path}")
    print(f"\n--- Conversation Quality & Integrity Summary ---")
    print(f"  Total conversations: {stats['conversation_counts']['total_reconstructed_conversations']:,}")
    print(f"  Total turns: {stats['turn_counts']['total_turns']:,}")
    print(f"  Turns breakdown: {stats['turn_counts']['customer_turns']:,} customer ({stats['turn_counts']['inbound_turns']:,} inbound), {stats['turn_counts']['applesupport_turns']:,} AppleSupport, {stats['turn_counts']['other_brand_turns']:,} other brands")
    print(f"  Multi-turn conversations (>=2 turns): {stats['conversation_counts']['multi_turn_conversations']:,} (100.00%)")
    print(f"  Single-turn conversations: {stats['conversation_counts']['single_turn_conversations']:,} (0.00%)")
    print(f"  Conversations with both Customer & AppleSupport: {stats['conversation_counts']['conversations_with_customer_and_applesupport']:,} ({stats['conversation_counts']['percentage_with_customer_and_applesupport']})")
    print(f"  Turns per conversation: Mean={stats['length_statistics']['quantiles']['mean']}, Median={stats['length_statistics']['quantiles']['p50_median']}, Max={stats['length_statistics']['quantiles']['max']}")
    print(f"  Branching conversations: {stats['conversation_counts']['branching_conversations']:,} ({stats['conversation_counts']['percentage_branching']})")
    print(f"  Cycles detected: {stats['graph_integrity_and_anomalies']['cycles_detected']}")
    print(f"  Chronological anomalies: {stats['graph_integrity_and_anomalies']['chronological_ordering_anomalies']}")
    print(f"  Missing parent links: {stats['graph_integrity_and_anomalies']['conversations_with_missing_linked_parents']}")
    print(f"  Missing child links: {stats['graph_integrity_and_anomalies']['conversations_with_missing_linked_children']:,} conversations ({stats['graph_integrity_and_anomalies']['total_missing_child_references']:,} missing references)")
    print(f"  Parquet SHA-256: {stats['output_dataset']['sha256']}")


if __name__ == "__main__":
    main()
