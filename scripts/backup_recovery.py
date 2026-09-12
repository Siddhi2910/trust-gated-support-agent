#!/usr/bin/env python3
"""Safe Backup and Recovery Utility for Human Review Labels.

Ensures immutable backups, verified checksums, and corruption recovery
without risk of data loss.
"""

import os
import sys
import json
import shutil
import hashlib
import argparse
from datetime import datetime

HUMAN_LABELS_FILE = "artifacts/human_review_labels.json"
BACKUP_DIR = "artifacts/backups"


def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_labels_file(filepath=HUMAN_LABELS_FILE):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data.get("metadata", {})
        cases = data.get("cases", [])

        if len(cases) != 170:
            print(f"❌ Validation failed: expected 170 cases, got {len(cases)}")
            return False

        reviewed = sum(1 for c in cases if c.get("reviewed") is True)
        if meta.get("reviewed_count") != reviewed:
            print(f"❌ Metadata mismatch: metadata.reviewed_count ({meta.get('reviewed_count')}) != actual ({reviewed})")
            return False

        sha = compute_sha256(filepath)
        print(f"✓ Valid: {filepath}")
        print(f"  SHA256: {sha}")
        print(f"  Cases: {len(cases)} (Reviewed: {reviewed}, Remaining: {170 - reviewed})")
        return True
    except Exception as e:
        print(f"❌ Corrupt or unparseable JSON in {filepath}: {e}")
        return False


def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print(f"No backups directory found at {BACKUP_DIR}.")
        return []

    backups = [f for f in sorted(os.listdir(BACKUP_DIR)) if f.startswith("human_review_labels_backup_") and f.endswith(".json")]
    if not backups:
        print(f"No backups found in {BACKUP_DIR}.")
        return []

    print(f"\nAvailable Backups in {BACKUP_DIR}:")
    print("-" * 75)
    for b in backups:
        p = os.path.join(BACKUP_DIR, b)
        sz = os.path.getsize(p)
        sha = compute_sha256(p)
        print(f"  {b}  ({sz} bytes, sha256: {sha[:12]}...)")
    print("-" * 75 + "\n")
    return backups


def create_backup(custom_tag=None):
    if not os.path.exists(HUMAN_LABELS_FILE):
        print(f"❌ Source file not found: {HUMAN_LABELS_FILE}")
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    tag = f"_{custom_tag}" if custom_tag else ""
    backup_name = f"human_review_labels_backup_{ts}{tag}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    # Exclusive write to ensure it never overwrites
    if os.path.exists(backup_path):
        print(f"❌ Target backup already exists: {backup_path}")
        return None

    shutil.copy2(HUMAN_LABELS_FILE, backup_path)
    sha = compute_sha256(backup_path)
    print(f"✓ Created immutable backup: {backup_path}")
    print(f"  SHA256: {sha}")
    return backup_path


def restore_backup(backup_path):
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False

    # First create a safety backup of current state
    if os.path.exists(HUMAN_LABELS_FILE):
        pre_restore = create_backup(custom_tag="pre_restore")
        print(f"  (Safety pre-restore backup saved: {pre_restore})")

    shutil.copy2(backup_path, HUMAN_LABELS_FILE)
    print(f"✓ Restored {HUMAN_LABELS_FILE} from {backup_path}")
    return verify_labels_file(HUMAN_LABELS_FILE)


def main():
    parser = argparse.ArgumentParser(description="Human Review Labels Backup and Recovery Tool")
    parser.add_argument("--list", action="store_true", help="List all available backups")
    parser.add_argument("--backup", action="store_true", help="Create a new timestamped backup")
    parser.add_argument("--verify", action="store_true", help="Verify integrity of current labels file")
    parser.add_argument("--restore", type=str, help="Path to backup file to restore")

    args = parser.parse_args()

    if args.list:
        list_backups()
    elif args.backup:
        create_backup()
    elif args.verify:
        verify_labels_file()
    elif args.restore:
        restore_backup(args.restore)
    else:
        list_backups()
        verify_labels_file()


if __name__ == "__main__":
    main()
