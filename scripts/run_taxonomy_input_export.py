"""Executable runner for Taxonomy Input Export Package.

Produces:
1. artifacts/taxonomy_input_sample.csv
2. artifacts/taxonomy_input_keyword_freq.json
3. artifacts/taxonomy_input_length_stats.json
"""

import os
import sys
import time
import yaml

sys.path.insert(0, os.path.abspath("."))
from src.taxonomy.export_inputs import (
    export_taxonomy_sample,
    compute_keyword_frequencies,
    compute_length_statistics
)


def main():
    with open("configs/base.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    conversations_parquet = config["paths"]["applesupport_conversations"]
    subset_parquet = config["paths"]["applesupport_subset"]
    artifacts_dir = config["paths"]["artifacts_dir"]
    random_seed = config["project"]["random_seed"]

    sample_csv_path = os.path.join(artifacts_dir, "taxonomy_input_sample.csv")
    keyword_freq_path = os.path.join(artifacts_dir, "taxonomy_input_keyword_freq.json")
    length_stats_path = os.path.join(artifacts_dir, "taxonomy_input_length_stats.json")

    print("Starting Taxonomy Input Export Package generation...")
    t0 = time.time()

    # 1. Deterministic seeded sample (N=500, seed=42)
    print(f"\n1. Exporting deterministic sampled first-turn inquiries (N=500, seed={random_seed})...")
    sample_stats = export_taxonomy_sample(
        conversations_parquet_path=conversations_parquet,
        output_csv_path=sample_csv_path,
        sample_size=500,
        random_seed=random_seed
    )
    print(f"   Saved {sample_stats['sample_size']} rows to: {sample_csv_path}")
    print(f"   Evaluated: {sample_stats['total_inbound_roots']:,} inbound roots")
    print(f"   Unique normalized texts: {sample_stats['unique_normalized_texts']:,}")
    print(f"   Sample unique tweet_ids: {sample_stats['unique_tweet_ids']}")
    print(f"   Sample unique raw texts: {sample_stats['unique_raw_texts']}")

    # 2. Keyword frequencies (top 150 unigrams / bigrams)
    print(f"\n2. Computing top 150 unigrams/bigrams across all inbound messages...")
    kw_stats = compute_keyword_frequencies(
        subset_parquet_path=subset_parquet,
        output_json_path=keyword_freq_path,
        top_k=150
    )
    print(f"   Saved keyword frequencies to: {keyword_freq_path}")
    print(f"   Analyzed messages: {kw_stats['metadata']['total_inbound_messages_analyzed']:,}")
    print(f"   Stopword list count: {kw_stats['metadata']['stopword_count']}")
    print(f"   Top 5 unigrams: {[x['term'] + ' (' + str(x['count']) + ')' for x in kw_stats['top_150_unigrams'][:5]]}")
    print(f"   Top 5 bigrams: {[x['term'] + ' (' + str(x['count']) + ')' for x in kw_stats['top_150_bigrams'][:5]]}")

    # 3. Message length statistics
    print(f"\n3. Computing message length distributions...")
    len_stats = compute_length_statistics(
        subset_parquet_path=subset_parquet,
        conversations_parquet_path=conversations_parquet,
        output_json_path=length_stats_path
    )
    print(f"   Saved length distributions to: {length_stats_path}")
    all_in = len_stats['all_inbound_messages']
    first_in = len_stats['first_turn_customer_inquiries']
    print(f"   All inbound (N={all_in['total_messages']:,}): chars mean={all_in['character_length']['mean']}, median={all_in['character_length']['median']}; words mean={all_in['word_length']['mean']}, median={all_in['word_length']['median']}")
    print(f"   First-turn (N={first_in['total_messages']:,}): chars mean={first_in['character_length']['mean']}, median={first_in['character_length']['median']}; words mean={first_in['word_length']['mean']}, median={first_in['word_length']['median']}")

    elapsed = time.time() - t0
    print(f"\nAll 3 data export artifacts successfully created in {elapsed:.2f}s.")


if __name__ == "__main__":
    main()
