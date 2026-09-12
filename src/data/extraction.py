"""AppleSupport subset extraction and lineage tracking module.

Extracts AppleSupport conversation threads from twcs.csv into data/processed/applesupport_subset.parquet.
Computes conversation_id (root tweet of the thread) and outputs a comprehensive
provenance manifest documenting dataset reduction, hash verification, and id mapping.
"""

import os
import csv
import json
import time
import hashlib
from typing import Dict, Any, Set, List, Tuple
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def compute_file_sha256(filepath: str, buffer_size: int = 1048576) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def extract_applesupport_subset(
    raw_csv_path: str,
    output_parquet_path: str,
    target_brand: str = "AppleSupport",
    include_full_context: bool = True
) -> Dict[str, Any]:
    """Extract AppleSupport conversations and write to Parquet with provenance metadata."""
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Raw dataset not found at {raw_csv_path}")

    start_wall_time = time.time()
    raw_size_bytes = os.path.getsize(raw_csv_path)
    print("Computing raw dataset initial SHA-256...", flush=True)
    raw_sha256_initial = compute_file_sha256(raw_csv_path)

    # Pass 1: Build conversation graph index
    apple_out_ids: Set[int] = set()
    parent_map: Dict[int, int] = {}
    child_map: Dict[int, List[int]] = {}
    raw_tweet_ids: Set[int] = set()

    print("Pass 1: indexing conversation graph from raw CSV...", flush=True)

    with open(raw_csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) < 7:
                continue
            try:
                tid = int(row[0].strip())
            except ValueError:
                continue

            raw_tweet_ids.add(tid)
            author = row[1].strip()
            inbound = (row[2].strip() == "True")

            if author == target_brand and not inbound:
                apple_out_ids.add(tid)

            in_resp = row[6].strip()
            if in_resp:
                try:
                    p_id = int(float(in_resp))
                    parent_map[tid] = p_id
                except ValueError:
                    pass

            resp_str = row[5].strip()
            if resp_str:
                parts = [p.strip() for p in resp_str.split(",") if p.strip()]
                for p in parts:
                    try:
                        c_id = int(float(p))
                        if tid not in child_map:
                            child_map[tid] = []
                        child_map[tid].append(c_id)
                    except ValueError:
                        pass

    # Find roots for all AppleSupport tweets
    memo_root: Dict[int, int] = {}
    def find_root(t: int) -> int:
        curr = t
        path = []
        while curr in parent_map:
            if curr in memo_root:
                curr = memo_root[curr]
                break
            path.append(curr)
            nxt = parent_map[curr]
            if nxt in path or nxt == curr:
                break
            curr = nxt
        for p in path:
            memo_root[p] = curr
        return curr

    apple_roots: Set[int] = set()
    for tid in apple_out_ids:
        apple_roots.add(find_root(tid))

    # Collect all reachable tweets from apple_roots that exist in raw_tweet_ids
    extracted_tweet_ids: Set[int] = set()
    tweet_to_conversation_id: Dict[int, int] = {}

    for r in apple_roots:
        frontier = [r]
        while frontier:
            curr = frontier.pop()
            if curr in raw_tweet_ids and curr not in extracted_tweet_ids:
                extracted_tweet_ids.add(curr)
                tweet_to_conversation_id[curr] = r
                if curr in child_map:
                    for child in child_map[curr]:
                        frontier.append(child)

    # Pass 2: Stream through twcs.csv and collect matching records
    print(f"Found {len(apple_roots)} conversation roots and {len(extracted_tweet_ids)} matching tweets.", flush=True)
    print("Pass 2: streaming through raw CSV to extract matching records...", flush=True)
    extracted_records = []
    with open(raw_csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) < 7:
                continue
            try:
                tid = int(row[0].strip())
            except ValueError:
                continue

            if tid in extracted_tweet_ids:
                conv_id = tweet_to_conversation_id.get(tid, tid)
                inbound_val = (row[2].strip() == "True")
                in_resp_val = row[6].strip()
                resp_val = row[5].strip()

                extracted_records.append({
                    "tweet_id": tid,
                    "author_id": row[1].strip(),
                    "inbound": inbound_val,
                    "created_at": row[3].strip(),
                    "text": row[4],
                    "response_tweet_id": resp_val if resp_val else None,
                    "in_response_to_tweet_id": in_resp_val if in_resp_val else None,
                    "conversation_id": conv_id,
                })

    # Convert to DataFrame and write to Parquet
    print(f"Extracted {len(extracted_records)} records. Converting to Parquet...", flush=True)
    df = pd.DataFrame(extracted_records)
    # Sort for deterministic layout: by conversation_id, then tweet_id
    df.sort_values(by=["conversation_id", "tweet_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_parquet_path, compression="snappy")

    derived_file_size = os.path.getsize(output_parquet_path)
    derived_sha256 = compute_file_sha256(output_parquet_path)

    # Post-check: ensure raw dataset hash is strictly unchanged
    raw_sha256_final = compute_file_sha256(raw_csv_path)
    assert raw_sha256_initial == raw_sha256_final, "FATAL: Raw dataset was modified during extraction!"

    # Verification: every extracted tweet_id exists in raw dataset
    all_exist_in_raw = extracted_tweet_ids.issubset(raw_tweet_ids)
    assert all_exist_in_raw, "FATAL: Some derived tweet_ids do not exist in raw dataset!"

    elapsed_wall_seconds = time.time() - start_wall_time
    total_raw_rows = len(raw_tweet_ids)
    total_derived_rows = len(df)
    unique_conversations = df["conversation_id"].nunique()
    reduction_ratio = round(total_raw_rows / total_derived_rows, 4) if total_derived_rows > 0 else 0.0

    manifest = {
        "manifest_version": "1.0.0",
        "target_brand": target_brand,
        "include_full_context": include_full_context,
        "raw_dataset": {
            "path": raw_csv_path,
            "sha256": raw_sha256_final,
            "sha256_unchanged": (raw_sha256_initial == raw_sha256_final),
            "size_bytes": raw_size_bytes,
            "total_rows": total_raw_rows,
        },
        "derived_dataset": {
            "path": output_parquet_path,
            "sha256": derived_sha256,
            "size_bytes": derived_file_size,
            "size_mb": round(derived_file_size / (1024 * 1024), 2),
            "total_rows": total_derived_rows,
            "unique_conversation_ids": unique_conversations,
            "columns": list(df.columns),
            "compression": "snappy",
        },
        "reduction_metrics": {
            "raw_total_rows": total_raw_rows,
            "derived_total_rows": total_derived_rows,
            "reduction_ratio": reduction_ratio,
            "retention_percentage": f"{(total_derived_rows / total_raw_rows) * 100:.2f}%",
        },
        "provenance_integrity": {
            "all_derived_tweet_ids_in_raw": all_exist_in_raw,
            "verified_tweet_count": len(extracted_tweet_ids),
            "raw_dataset_immutable": True,
        },
        "execution_metadata": {
            "elapsed_wall_seconds": round(elapsed_wall_seconds, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        },
    }

    return manifest
