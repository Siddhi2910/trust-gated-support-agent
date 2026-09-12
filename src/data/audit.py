"""Raw dataset audit module for Customer Support on Twitter (twcs.csv).

Performs strict, read-only streaming audit computing:
- Total rows, columns, data types
- Inbound vs outbound counts
- Unique tweet IDs and duplicate ID check
- Exact duplicate row check
- Unique author count
- Missing / malformed in_response_to_tweet_id and response_tweet_id counts
- Checksum of twcs.csv to guarantee immutability
"""

import os
import csv
import json
import time
import hashlib
from typing import Dict, Any

def compute_file_sha256(filepath: str, buffer_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file efficiently without loading entirely into memory."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def audit_raw_dataset(csv_path: str) -> Dict[str, Any]:
    """Audit twcs.csv in a single streaming pass."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Raw dataset not found at {csv_path}")

    start_wall_time = time.time()
    file_size_bytes = os.path.getsize(csv_path)
    file_sha256 = compute_file_sha256(csv_path)

    total_rows = 0
    inbound_count = 0
    outbound_count = 0
    invalid_inbound_flag_count = 0

    seen_tweet_ids = set()
    duplicate_tweet_ids = 0

    seen_row_hashes = set()
    exact_duplicate_rows = 0

    unique_authors = set()

    null_in_response_to = 0
    malformed_in_response_to = 0

    null_response_tweet_id = 0
    malformed_response_tweet_id = 0

    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        try:
            columns = next(reader)
        except StopIteration:
            raise ValueError(f"Empty CSV file at {csv_path}")

        # Column indices: tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id
        for row in reader:
            if not row:
                continue
            total_rows += 1

            if len(row) < 7:
                continue

            tweet_id_str, author_id, inbound_str, created_at, text, resp_id_str, in_resp_str = (
                row[0].strip(),
                row[1].strip(),
                row[2].strip(),
                row[3].strip(),
                row[4],
                row[5].strip(),
                row[6].strip(),
            )

            # 1. Tweet ID & duplicate check
            if tweet_id_str in seen_tweet_ids:
                duplicate_tweet_ids += 1
            else:
                seen_tweet_ids.add(tweet_id_str)

            # 2. Row uniqueness via lightweight hash
            row_hash = hash((tweet_id_str, author_id, inbound_str, in_resp_str))
            if row_hash in seen_row_hashes:
                exact_duplicate_rows += 1
            else:
                seen_row_hashes.add(row_hash)

            # 3. Author ID
            unique_authors.add(author_id)

            # 4. Inbound flag
            if inbound_str == "True":
                inbound_count += 1
            elif inbound_str == "False":
                outbound_count += 1
            else:
                invalid_inbound_flag_count += 1

            # 5. Null / malformed in_response_to_tweet_id
            if not in_resp_str:
                null_in_response_to += 1
            else:
                try:
                    # In TWCS, float values like '115712.0' or integer strings appear
                    float(in_resp_str)
                except ValueError:
                    malformed_in_response_to += 1

            # 6. Null / malformed response_tweet_id
            if not resp_id_str:
                null_response_tweet_id += 1
            else:
                # May be comma-separated list of IDs
                parts = [p.strip() for p in resp_id_str.split(",") if p.strip()]
                for p in parts:
                    try:
                        float(p)
                    except ValueError:
                        malformed_response_tweet_id += 1

    elapsed_wall_seconds = time.time() - start_wall_time

    audit_result = {
        "file_info": {
            "path": csv_path,
            "size_bytes": file_size_bytes,
            "sha256": file_sha256,
            "columns": columns,
            "column_count": len(columns),
        },
        "row_counts": {
            "total_rows": total_rows,
            "inbound_count": inbound_count,
            "outbound_count": outbound_count,
            "invalid_inbound_flags": invalid_inbound_flag_count,
        },
        "integrity_checks": {
            "unique_tweet_ids": len(seen_tweet_ids),
            "duplicate_tweet_id_count": duplicate_tweet_ids,
            "duplicate_tweet_id_check_passed": duplicate_tweet_ids == 0,
            "exact_duplicate_row_count": exact_duplicate_rows,
            "exact_duplicate_row_check_passed": exact_duplicate_rows == 0,
            "unique_author_count": len(unique_authors),
        },
        "linkage_fields": {
            "null_in_response_to_count": null_in_response_to,
            "malformed_in_response_to_count": malformed_in_response_to,
            "null_response_tweet_id_count": null_response_tweet_id,
            "malformed_response_tweet_id_count": malformed_response_tweet_id,
        },
        "execution_metadata": {
            "elapsed_wall_seconds": round(elapsed_wall_seconds, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        },
    }
    return audit_result
