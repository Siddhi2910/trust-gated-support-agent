"""Deterministic conversation reconstruction module for AppleSupport customer support interactions.

Reconstructs multi-turn conversational threads from the verified Phase 1 AppleSupport
subset (data/processed/applesupport_subset.parquet). Preserves exact tweet texts,
original tweet IDs, parent/child topological relationships, chronological ordering,
role designations (customer vs agent), and missing-link provenance.
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def compute_file_sha256(filepath: str, buffer_size: int = 65536) -> str:
    """Compute SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def parse_twitter_timestamp(ts_str: str) -> Tuple[datetime, int]:
    """Parse Twitter timestamp string (e.g. 'Tue Oct 31 22:27:49 +0000 2017') into UTC datetime and epoch seconds."""
    dt = datetime.strptime(ts_str, "%a %b %d %H:%M:%S %z %Y")
    epoch_sec = int(dt.timestamp())
    return dt, epoch_sec


def reconstruct_conversations(
    input_parquet_path: str,
    output_parquet_path: str,
    target_brand: str = "AppleSupport",
    raw_csv_path: Optional[str] = "data/raw/twcs.csv",
) -> Dict[str, Any]:
    """Reconstruct conversational threads deterministically from the AppleSupport Parquet subset.

    Args:
        input_parquet_path: Path to applesupport_subset.parquet.
        output_parquet_path: Output path for applesupport_conversations.parquet.
        target_brand: Target support handle ('AppleSupport').
        raw_csv_path: Optional path to raw twcs.csv for immutability check.

    Returns:
        A comprehensive metrics dictionary detailing reconstruction statistics.
    """
    if not os.path.exists(input_parquet_path):
        raise FileNotFoundError(f"Input parquet missing at {input_parquet_path}")

    start_wall_time = time.time()

    # Pre-check raw CSV immutability if provided
    raw_sha256_before = None
    if raw_csv_path and os.path.exists(raw_csv_path):
        raw_sha256_before = compute_file_sha256(raw_csv_path)

    # 1. Load the Phase 1 verified subset
    subset_df = pd.read_parquet(input_parquet_path)
    total_input_rows = len(subset_df)
    subset_tweet_ids = set(subset_df["tweet_id"].values)

    # 2. Index all tweets by conversation_id
    # We use itertuples for rapid, memory-safe traversal
    tweets_by_conv: Dict[int, List[Any]] = defaultdict(list)
    for row in subset_df.itertuples(index=False):
        tweets_by_conv[row.conversation_id].append(row)

    sorted_conv_ids = sorted(tweets_by_conv.keys())
    total_conversations = len(sorted_conv_ids)

    # Metric tracking accumulators
    total_turns_reconstructed = 0
    inbound_turn_count = 0
    outbound_turn_count = 0
    customer_turn_count = 0
    applesupport_turn_count = 0
    other_brand_turn_count = 0

    conv_length_counts: Dict[int, int] = defaultdict(int)
    conv_lengths: List[int] = []
    duration_seconds_list: List[int] = []

    missing_parent_convs = 0
    missing_children_convs = 0
    total_missing_child_refs = 0
    branching_convs = 0
    cycle_anomalies = 0
    timing_anomalies = 0
    both_roles_count = 0

    reconstructed_records: List[Dict[str, Any]] = []

    # 3. Process each conversation deterministically
    for conv_id in sorted_conv_ids:
        raw_rows = tweets_by_conv[conv_id]
        n_turns = len(raw_rows)
        conv_lengths.append(n_turns)
        conv_length_counts[n_turns] += 1
        total_turns_reconstructed += n_turns

        # Build local adjacency and node maps
        node_map: Dict[int, Any] = {}
        parent_map: Dict[int, int] = {}
        children_map: Dict[int, List[int]] = defaultdict(list)
        missing_children_map: Dict[int, List[int]] = defaultdict(list)
        missing_parent_map: Dict[int, int] = {}
        timestamp_map: Dict[int, Tuple[datetime, int]] = {}

        has_branching = False
        has_conv_missing_parent = False
        has_conv_missing_children = False
        local_missing_child_count = 0

        for r in raw_rows:
            tid = r.tweet_id
            node_map[tid] = r
            dt, epoch = parse_twitter_timestamp(r.created_at)
            timestamp_map[tid] = (dt, epoch)

            # Role tracking
            if r.inbound:
                inbound_turn_count += 1
                customer_turn_count += 1
            else:
                outbound_turn_count += 1
                if r.author_id == target_brand:
                    applesupport_turn_count += 1
                else:
                    other_brand_turn_count += 1

            # Parent linkage
            in_resp = r.in_response_to_tweet_id
            if in_resp:
                try:
                    pid = int(float(in_resp))
                    if pid in subset_tweet_ids:
                        parent_map[tid] = pid
                        children_map[pid].append(tid)
                    else:
                        missing_parent_map[tid] = pid
                        has_conv_missing_parent = True
                except (ValueError, TypeError):
                    pass

            # Child linkage
            resp_str = r.response_tweet_id
            if resp_str:
                for p in str(resp_str).split(","):
                    p = p.strip()
                    if p:
                        try:
                            chid = int(float(p))
                            if chid not in subset_tweet_ids:
                                missing_children_map[tid].append(chid)
                                has_conv_missing_children = True
                                local_missing_child_count += 1
                        except (ValueError, TypeError):
                            pass

        if has_conv_missing_parent:
            missing_parent_convs += 1
        if has_conv_missing_children:
            missing_children_convs += 1
            total_missing_child_refs += local_missing_child_count

        # Check for branching
        for pid, chs in children_map.items():
            if len(chs) > 1:
                has_branching = True
                break
        if has_branching:
            branching_convs += 1

        # Cycle detection and topological depth
        visited_cycle = set()
        for start_id in node_map:
            curr = start_id
            path = set()
            while curr in parent_map:
                path.add(curr)
                parent = parent_map[curr]
                if parent in path:
                    cycle_anomalies += 1
                    break
                curr = parent

        # Calculate depth from root
        def get_depth(node_id: int) -> int:
            depth = 0
            curr = node_id
            visited = set()
            while curr in parent_map and curr not in visited:
                visited.add(curr)
                curr = parent_map[curr]
                depth += 1
            return depth

        depth_map = {nid: get_depth(nid) for nid in node_map}

        # Chronological anomaly check: child created_at < parent created_at
        for child_id, parent_id in parent_map.items():
            if parent_id in timestamp_map:
                if timestamp_map[child_id][1] < timestamp_map[parent_id][1]:
                    timing_anomalies += 1

        # Sort turns: Primary: timestamp; Secondary: topological depth; Tertiary: tweet_id
        sorted_nodes = sorted(
            node_map.keys(),
            key=lambda nid: (timestamp_map[nid][1], depth_map[nid], nid),
        )

        # Build structured turns
        ordered_turns: List[Dict[str, Any]] = []
        customer_author_id: Optional[str] = None
        customer_inquiry_text = ""
        first_brand_response_text = ""
        transcript_lines = []

        has_customer = False
        has_apple = False

        for idx, nid in enumerate(sorted_nodes):
            row = node_map[nid]
            role = "customer" if row.inbound else ("agent" if row.author_id == target_brand else "other_brand")

            if row.inbound:
                has_customer = True
                if not customer_author_id:
                    customer_author_id = row.author_id
                if not customer_inquiry_text:
                    customer_inquiry_text = row.text
            elif row.author_id == target_brand:
                has_apple = True
                if not first_brand_response_text:
                    first_brand_response_text = row.text

            turn_obj = {
                "turn_index": idx,
                "tweet_id": nid,
                "author_id": row.author_id,
                "inbound": row.inbound,
                "role": role,
                "created_at": row.created_at,
                "created_at_epoch": timestamp_map[nid][1],
                "text": row.text,
                "in_response_to_tweet_id": row.in_response_to_tweet_id,
                "response_tweet_id": row.response_tweet_id,
                "parent_tweet_id": parent_map.get(nid),
                "child_tweet_ids": sorted(children_map.get(nid, [])),
                "missing_parent_id": missing_parent_map.get(nid),
                "missing_child_ids": sorted(missing_children_map.get(nid, [])),
            }
            ordered_turns.append(turn_obj)

            speaker_label = f"Customer ({row.author_id})" if row.inbound else f"{row.author_id}"
            transcript_lines.append(f"[Turn {idx}] {speaker_label}: {row.text}")

        if has_customer and has_apple:
            both_roles_count += 1

        first_turn = ordered_turns[0]
        last_turn = ordered_turns[-1]
        duration_sec = last_turn["created_at_epoch"] - first_turn["created_at_epoch"]
        duration_seconds_list.append(duration_sec)

        root_tweet_id = conv_id
        root_node = node_map.get(root_tweet_id, ordered_turns[0])
        root_author = root_node.author_id if hasattr(root_node, "author_id") else root_node["author_id"]
        root_inbound = root_node.inbound if hasattr(root_node, "inbound") else root_node["inbound"]

        num_cust_turns = sum(1 for t in ordered_turns if t["role"] == "customer")
        num_brand_turns = sum(1 for t in ordered_turns if t["role"] == "agent")
        num_other_turns = n_turns - num_cust_turns - num_brand_turns

        conversation_record = {
            "conversation_id": conv_id,
            "root_tweet_id": root_tweet_id,
            "root_author_id": root_author,
            "root_inbound": root_inbound,
            "customer_author_id": customer_author_id or "unknown",
            "num_turns": n_turns,
            "num_customer_turns": num_cust_turns,
            "num_brand_turns": num_brand_turns,
            "num_other_turns": num_other_turns,
            "first_created_at": first_turn["created_at"],
            "last_created_at": last_turn["created_at"],
            "duration_seconds": duration_sec,
            "is_multi_turn": (n_turns >= 2),
            "has_customer_and_brand": (has_customer and has_apple),
            "has_missing_parent": has_conv_missing_parent,
            "has_missing_children": has_conv_missing_children,
            "missing_child_count": local_missing_child_count,
            "is_branching": has_branching,
            "customer_inquiry_text": customer_inquiry_text,
            "first_brand_response_text": first_brand_response_text,
            "conversation_text": "\n".join(transcript_lines),
            "turns_json": json.dumps(ordered_turns, ensure_ascii=False),
        }
        reconstructed_records.append(conversation_record)

    # 4. Write reconstructed conversations to Parquet
    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)
    out_table = pa.Table.from_pylist(reconstructed_records)
    pq.write_table(out_table, output_parquet_path, compression="snappy")

    derived_file_size = os.path.getsize(output_parquet_path)
    derived_sha256 = compute_file_sha256(output_parquet_path)

    # 5. Post-check raw immutability
    if raw_sha256_before:
        raw_sha256_after = compute_file_sha256(raw_csv_path)
        assert raw_sha256_before == raw_sha256_after, "FATAL: Raw dataset was modified during reconstruction!"

    wall_seconds = time.time() - start_wall_time

    # 6. Calculate statistics
    conv_lengths_arr = np.array(conv_lengths)
    durations_arr = np.array(duration_seconds_list)

    length_quantiles = {
        "min": int(np.min(conv_lengths_arr)),
        "p10": float(np.percentile(conv_lengths_arr, 10)),
        "p25": float(np.percentile(conv_lengths_arr, 25)),
        "p50_median": float(np.median(conv_lengths_arr)),
        "p75": float(np.percentile(conv_lengths_arr, 75)),
        "p90": float(np.percentile(conv_lengths_arr, 90)),
        "p95": float(np.percentile(conv_lengths_arr, 95)),
        "p99": float(np.percentile(conv_lengths_arr, 99)),
        "max": int(np.max(conv_lengths_arr)),
        "mean": round(float(np.mean(conv_lengths_arr)), 4),
        "std": round(float(np.std(conv_lengths_arr)), 4),
    }

    duration_quantiles = {
        "min": int(np.min(durations_arr)),
        "p25": float(np.percentile(durations_arr, 25)),
        "p50_median": float(np.median(durations_arr)),
        "p75": float(np.percentile(durations_arr, 75)),
        "p90": float(np.percentile(durations_arr, 90)),
        "max": int(np.max(durations_arr)),
        "mean": round(float(np.mean(durations_arr)), 2),
    }

    # Sort length distribution
    length_distribution = {str(k): conv_length_counts[k] for k in sorted(conv_length_counts.keys())}

    stats = {
        "manifest_version": "2.0.0",
        "phase": "phase2_conversation_reconstruction",
        "target_brand": target_brand,
        "input_dataset": {
            "path": input_parquet_path,
            "total_rows": total_input_rows,
            "sha256": compute_file_sha256(input_parquet_path),
        },
        "output_dataset": {
            "path": output_parquet_path,
            "total_conversations": total_conversations,
            "total_turns_reconstructed": total_turns_reconstructed,
            "size_bytes": derived_file_size,
            "size_mb": round(derived_file_size / (1024 * 1024), 2),
            "sha256": derived_sha256,
            "compression": "snappy",
            "columns": list(out_table.column_names),
        },
        "conversation_counts": {
            "total_reconstructed_conversations": total_conversations,
            "single_turn_conversations": sum(1 for l in conv_lengths if l == 1),
            "multi_turn_conversations": sum(1 for l in conv_lengths if l >= 2),
            "conversations_with_customer_and_applesupport": both_roles_count,
            "percentage_with_customer_and_applesupport": f"{(both_roles_count / total_conversations) * 100:.2f}%",
            "branching_conversations": branching_convs,
            "percentage_branching": f"{(branching_convs / total_conversations) * 100:.2f}%",
        },
        "turn_counts": {
            "total_turns": total_turns_reconstructed,
            "inbound_turns": inbound_turn_count,
            "outbound_turns": outbound_turn_count,
            "customer_turns": customer_turn_count,
            "applesupport_turns": applesupport_turn_count,
            "other_brand_turns": other_brand_turn_count,
        },
        "length_statistics": {
            "quantiles": length_quantiles,
            "distribution_top10": {str(k): conv_length_counts[k] for k in sorted(conv_length_counts.keys())[:10]},
            "full_distribution": length_distribution,
        },
        "duration_statistics_seconds": duration_quantiles,
        "graph_integrity_and_anomalies": {
            "conversations_with_missing_linked_parents": missing_parent_convs,
            "conversations_with_missing_linked_children": missing_children_convs,
            "percentage_conversations_with_missing_children": f"{(missing_children_convs / total_conversations) * 100:.2f}%",
            "total_missing_child_references": total_missing_child_refs,
            "conversations_with_unresolved_graph_references": missing_children_convs + missing_parent_convs,
            "conversations_with_unusual_cycles_or_invalid_relationships": cycle_anomalies,
            "chronological_ordering_anomalies": timing_anomalies,
            "parent_child_monotonic_timing_verified": (timing_anomalies == 0),
            "cycles_detected": cycle_anomalies,
        },
        "data_integrity_verification": {
            "all_turns_in_phase1_subset": (total_turns_reconstructed == total_input_rows),
            "raw_dataset_immutable": True if raw_sha256_before else None,
            "deterministic_ordering": True,
        },
        "execution_metadata": {
            "elapsed_wall_seconds": round(wall_seconds, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        },
    }

    return stats
