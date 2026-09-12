"""Data export pipeline for Taxonomy Discovery Specialist.

Produces:
1. artifacts/taxonomy_input_sample.csv: Deterministic, seeded sample of ~400-600
   unique customer first-turn inquiries (with near-duplicate deduplication).
2. artifacts/taxonomy_input_keyword_freq.json: Top 150 unigrams and bigrams across
   all inbound customer messages with raw counts and documented stopword list.
3. artifacts/taxonomy_input_length_stats.json: Detailed char and word length distributions.
"""

import os
import re
import json
import numpy as np
import pandas as pd
from collections import Counter
from typing import Dict, Any, List, Tuple

# Comprehensive standard stopword set: NLTK English stopwords + uncontracted variants + Twitter artifacts
EXPLICIT_STOPWORDS: List[str] = sorted(list(set([
    # Standard English function words & pronouns (NLTK base)
    'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 'any', 'are',
    'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both',
    'but', 'by', 'can', 'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn',
    "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
    'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her', 'here',
    'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't",
    'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most',
    'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now', 'o', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same',
    'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such',
    't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
    'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very',
    'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which',
    'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y',
    'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves',

    # Common uncontracted colloquial spellings (when apostrophes are stripped during normalization)
    'aint', 'arent', 'cant', 'couldnt', 'didnt', 'doesnt', 'dont', 'hadnt', 'hasnt', 'havent',
    'hed', 'hell', 'heres', 'hes', 'hows', 'id', 'ill', 'im', 'isnt', 'ive', 'shed', 'shell',
    'shes', 'shouldnt', 'thats', 'theyd', 'theyll', 'theyre', 'theyve', 'theres', 'wasnt',
    'wed', 'well', 'weve', 'werent', 'whats', 'whens', 'wheres', 'whys', 'wont', 'wouldnt',
    'youd', 'youll', 'youre', 'youve',

    # Twitter, social media, and brand noise (leaving genuine technical nouns intact)
    'apple', 'applesupport', 'amp', 'co', 'dm', 'http', 'https', 'please', 'rt', 'thank', 'thanks', 'via'
])))

STOPWORDS_SET = set(EXPLICIT_STOPWORDS)


def normalize_for_deduplication(text: str) -> str:
    """Normalize text strictly for near-duplicate identification.
    
    Removes URLs, user mentions, punctuation, and extraneous whitespace.
    NOTE: The original text itself is NEVER modified in the exported dataset.
    """
    # Remove URLs
    cleaned = re.sub(r'https?://\S+', '', str(text))
    # Remove user mentions (@someone)
    cleaned = re.sub(r'@\w+', '', cleaned)
    # Lowercase
    cleaned = cleaned.lower()
    # Replace non-alphanumeric with spaces
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', cleaned)
    # Collapse whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def tokenize_for_keywords(text: str) -> List[str]:
    """Tokenize a cleaned copy of message text for keyword frequency calculation.
    
    Removes URLs, mentions, apostrophes, and extracts non-stopword alphanumeric tokens.
    """
    cleaned = re.sub(r'https?://\S+', ' ', str(text))
    cleaned = re.sub(r'@\w+', ' ', cleaned)
    cleaned = cleaned.lower()
    cleaned = re.sub(r'[\'’]', '', cleaned)
    tokens = re.findall(r'[a-z0-9]+', cleaned)
    # Filter stopwords, single-character tokens, and pure numbers
    return [
        t for t in tokens
        if t not in STOPWORDS_SET and len(t) > 1 and not t.isdigit()
    ]


def export_taxonomy_sample(
    conversations_parquet_path: str,
    output_csv_path: str,
    sample_size: int = 500,
    random_seed: int = 42
) -> Dict[str, Any]:
    """Sample unique first-turn customer inquiries with near-duplicate deduplication.
    
    Returns metadata dict regarding sample properties and deduplication stats.
    """
    df = pd.read_parquet(conversations_parquet_path)

    # Filter to conversations where the conversation begins with an inbound customer message
    inbound_roots = df[df['root_inbound'] == True].sort_values('conversation_id').reset_index(drop=True)
    total_inbound_roots = len(inbound_roots)

    # Create normalized representation solely for deduplication comparison
    inbound_roots['dedup_key'] = inbound_roots['customer_inquiry_text'].apply(normalize_for_deduplication)

    # Discard trivial/empty messages (e.g., only contained a bare handle or URL)
    valid_candidates = inbound_roots[inbound_roots['dedup_key'].str.len() > 3].copy()
    valid_candidates_count = len(valid_candidates)

    # Deduplicate near-identical texts by normalized key, deterministically keeping the first
    deduped = valid_candidates.drop_duplicates(subset=['dedup_key'], keep='first').copy()
    deduped_count = len(deduped)

    # Deterministic seeded random sample
    if len(deduped) < sample_size:
        raise ValueError(f"Available unique records ({len(deduped)}) < requested sample size ({sample_size})")

    sampled_df = deduped.sample(n=sample_size, random_state=random_seed).sort_values('conversation_id').reset_index(drop=True)

    # Build final export DataFrame with exact required schema
    export_df = pd.DataFrame({
        'conversation_id': sampled_df['conversation_id'],
        'tweet_id': sampled_df['root_tweet_id'],
        'text': sampled_df['customer_inquiry_text'],  # 100% exact original raw text!
        'turn_count': sampled_df['num_turns'],
        'created_at': sampled_df['first_created_at']
    })

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    export_df.to_csv(output_csv_path, index=False, encoding='utf-8')

    return {
        'total_inbound_roots': total_inbound_roots,
        'valid_candidates_evaluated': valid_candidates_count,
        'unique_normalized_texts': deduped_count,
        'duplicate_or_trivial_texts_filtered': total_inbound_roots - deduped_count,
        'sample_size': len(export_df),
        'random_seed': random_seed,
        'unique_tweet_ids': int(export_df['tweet_id'].nunique()),
        'unique_conversation_ids': int(export_df['conversation_id'].nunique()),
        'unique_raw_texts': int(export_df['text'].nunique()),
        'output_csv': output_csv_path
    }


def compute_keyword_frequencies(
    subset_parquet_path: str,
    output_json_path: str,
    top_k: int = 150
) -> Dict[str, Any]:
    """Extract top 150 unigrams and bigrams across all inbound customer messages."""
    df = pd.read_parquet(subset_parquet_path)
    inbound_df = df[df['inbound'] == True]
    total_inbound_messages = len(inbound_df)

    unigram_counts = Counter()
    bigram_counts = Counter()

    for text in inbound_df['text']:
        tokens = tokenize_for_keywords(text)
        unigram_counts.update(tokens)
        if len(tokens) >= 2:
            bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
            bigram_counts.update(bigrams)

    top_unigrams = [{'term': w, 'count': int(c), 'type': 'unigram'} for w, c in unigram_counts.most_common(top_k)]
    top_bigrams = [{'term': b, 'count': int(c), 'type': 'bigram'} for b, c in bigram_counts.most_common(top_k)]

    # Compute top combined list
    combined = []
    for w, c in unigram_counts.items():
        combined.append({'term': w, 'count': int(c), 'type': 'unigram'})
    for b, c in bigram_counts.items():
        combined.append({'term': b, 'count': int(c), 'type': 'bigram'})
    combined.sort(key=lambda x: x['count'], reverse=True)
    top_combined = combined[:top_k]

    result = {
        'description': 'Top frequent unigrams and bigrams across all inbound AppleSupport customer messages',
        'metadata': {
            'total_inbound_messages_analyzed': total_inbound_messages,
            'unique_unigrams_extracted': len(unigram_counts),
            'unique_bigrams_extracted': len(bigram_counts),
            'stopword_count': len(EXPLICIT_STOPWORDS),
            'stopwords_list': EXPLICIT_STOPWORDS,
            'tokenization_method': (
                "Cleaned copy only: URLs and @mentions removed, lowercase, apostrophes stripped, "
                "regex [a-z0-9]+ matching non-stopword tokens of length > 1, excluding pure digits."
            )
        },
        'top_150_combined': top_combined,
        'top_150_unigrams': top_unigrams,
        'top_150_bigrams': top_bigrams
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    return result


def _compute_distribution(series: pd.Series, bins: List[Tuple[int, int, str]]) -> Dict[str, Any]:
    """Helper to compute comprehensive distribution stats for a numeric series."""
    quantiles = {
        'p10': round(float(series.quantile(0.10)), 2),
        'p25': round(float(series.quantile(0.25)), 2),
        'p50_median': round(float(series.quantile(0.50)), 2),
        'p75': round(float(series.quantile(0.75)), 2),
        'p90': round(float(series.quantile(0.90)), 2),
        'p95': round(float(series.quantile(0.95)), 2),
        'p99': round(float(series.quantile(0.99)), 2),
    }

    buckets = []
    total = len(series)
    for low, high, label in bins:
        if high is None:
            count = int((series >= low).sum())
        else:
            count = int(((series >= low) & (series <= high)).sum())
        pct = round((count / total) * 100, 2) if total > 0 else 0.0
        buckets.append({
            'range': label,
            'count': count,
            'percentage': f"{pct:.2f}%"
        })

    return {
        'count': int(len(series)),
        'min': int(series.min()) if len(series) > 0 else 0,
        'max': int(series.max()) if len(series) > 0 else 0,
        'mean': round(float(series.mean()), 2) if len(series) > 0 else 0.0,
        'median': round(float(series.median()), 2) if len(series) > 0 else 0.0,
        'std': round(float(series.std()), 2) if len(series) > 0 else 0.0,
        'quantiles': quantiles,
        'distribution_buckets': buckets
    }


def compute_length_statistics(
    subset_parquet_path: str,
    conversations_parquet_path: str,
    output_json_path: str
) -> Dict[str, Any]:
    """Compute character and word length distributions for customer messages."""
    subset_df = pd.read_parquet(subset_parquet_path)
    all_inbound = subset_df[subset_df['inbound'] == True]['text'].dropna()

    conv_df = pd.read_parquet(conversations_parquet_path)
    first_turn_inbound = conv_df[conv_df['root_inbound'] == True]['customer_inquiry_text'].dropna()

    char_bins = [
        (0, 30, "0-30 chars"),
        (31, 60, "31-60 chars"),
        (61, 90, "61-90 chars"),
        (91, 120, "91-120 chars"),
        (121, 140, "121-140 chars (legacy limit)"),
        (141, 200, "141-200 chars"),
        (201, 240, "201-240 chars"),
        (241, 280, "241-280 chars (extended limit)"),
        (281, None, "281+ chars (multi-tweet / links)")
    ]

    word_bins = [
        (1, 5, "1-5 words"),
        (6, 10, "6-10 words"),
        (11, 15, "11-15 words"),
        (16, 20, "16-20 words"),
        (21, 25, "21-25 words"),
        (26, 30, "26-30 words"),
        (31, 40, "31-40 words"),
        (41, 50, "41-50 words"),
        (51, None, "51+ words")
    ]

    # Metrics for all inbound customer messages (131,258)
    all_chars = all_inbound.str.len()
    all_words = all_inbound.str.split().str.len()

    # Metrics for first-turn opening customer inquiries (80,250)
    first_chars = first_turn_inbound.str.len()
    first_words = first_turn_inbound.str.split().str.len()

    result = {
        'description': 'Character and word length distribution for inbound customer support messages',
        'all_inbound_messages': {
            'total_messages': len(all_inbound),
            'character_length': _compute_distribution(all_chars, char_bins),
            'word_length': _compute_distribution(all_words, word_bins)
        },
        'first_turn_customer_inquiries': {
            'total_messages': len(first_turn_inbound),
            'character_length': _compute_distribution(first_chars, char_bins),
            'word_length': _compute_distribution(first_words, word_bins)
        }
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    return result
