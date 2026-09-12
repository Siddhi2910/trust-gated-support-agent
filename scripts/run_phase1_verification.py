"""Verification runner for AppleSupport in twcs.csv.
Outputs artifacts/phase1_applesupport_verification.json and reports/phase1_brand_verification.md.
"""

import os
import json
import time
import yaml
from src.data.brand_extraction import verify_applesupport_brand

def main():
    with open("configs/base.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    raw_path = config["paths"]["raw_dataset"]
    artifacts_dir = config["paths"]["artifacts_dir"]
    reports_dir = config["paths"]["reports_dir"]
    target_brand = config["project"]["target_brand"]

    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print(f"Starting AppleSupport verification on {raw_path}...")
    t0 = time.time()
    results = verify_applesupport_brand(raw_path, target_brand=target_brand)
    elapsed = time.time() - t0

    artifact_path = os.path.join(artifacts_dir, "phase1_applesupport_verification.json")
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    report_path = os.path.join(reports_dir, "phase1_brand_verification.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Phase 1 Brand Verification Report: {target_brand}\n\n")
        f.write(f"**Verification Decision:** `{results['brand_verification_decision']['decision']}`\n\n")
        f.write(f"**Summary Justification:** {results['brand_verification_decision']['reason']}\n\n")
        f.write("## Verified Metrics\n\n")
        f.write(f"- **Outbound Brand Tweets:** {results['outbound_volume']['applesupport_outbound_tweet_count']:,}\n")
        f.write(f"- **Linked Inbound Customer Tweets:** {results['linked_conversation_volume']['total_linked_inbound_customer_tweets']:,}\n")
        f.write(f"- **Direct Inbound Questions Replied to by AppleSupport:** {results['linked_conversation_volume']['direct_parent_tweets_replied_by_apple']:,}\n")
        f.write(f"- **Responded Inbound Tweets:** {results['linked_conversation_volume']['responded_inbound_customer_tweets']:,}\n")
        f.write(f"- **Response Coverage Rate:** {results['response_coverage']['response_coverage_percentage']} ({results['response_coverage']['responded_inbound_count']:,} / {results['response_coverage']['total_linked_inbound_count']:,})\n")
        f.write(f"  - *Coverage Definition:* {results['response_coverage']['metric_definition']}\n")
        f.write(f"- **Reply Length Statistics:** Mean: {results['reply_length_stats']['mean_char_length']} chars, Median: {results['reply_length_stats']['median_char_length']} chars (Min: {results['reply_length_stats']['min_char_length']}, Max: {results['reply_length_stats']['max_char_length']})\n")
        f.write(f"- **Heuristic PII Indicator Rate:** {results['pii_heuristic_indicators']['pii_indicator_percentage']} ({results['pii_heuristic_indicators']['inbound_with_any_pii_pattern']:,} tweets with email/phone regex matches)\n")
        f.write(f"  - *Disclaimer:* {results['pii_heuristic_indicators']['disclaimer']}\n")
        f.write(f"- **Execution Time:** {elapsed:.2f} seconds wall-clock\n")

    print(f"Verification completed in {elapsed:.2f}s.")
    print(f"Artifact written to: {artifact_path}")
    print(f"Report written to: {report_path}")
    print(f"Decision: {results['brand_verification_decision']['decision']}")

if __name__ == "__main__":
    main()
