# Taxonomy Input Export Package Report

## Executive Summary

To enable a separate taxonomy-discovery specialist to inspect authentic customer support problem statements and design an evidence-based intent taxonomy without synthetic labels or unverified assumptions, this export package produces three curated data artifacts derived deterministically from `data/processed/applesupport_conversations.parquet` and `data/processed/applesupport_subset.parquet`:

1. **`artifacts/taxonomy_input_sample.csv`**: A deterministic, seeded random sample of **500 unique customer/inbound first-turn inquiries** with near-duplicate deduplication and 100% text fidelity.
2. **`artifacts/taxonomy_input_keyword_freq.json`**: Top 150 most frequent unigrams and bigrams across **all 131,258 inbound customer messages** with raw counts and fully documented stopword removal.
3. **`artifacts/taxonomy_input_length_stats.json`**: Character and word length distributions across both all inbound messages and first-turn problem statements.

No intent taxonomy has been proposed or designed in this phase. All raw texts remain strictly unmodified.

---

## 1. Sampling Methodology

### 1.1 Source Corpus and Inbound Filtering
- **Primary Source**: `data/processed/applesupport_conversations.parquet` (80,391 total conversations).
- **Candidate Subset**: Filtered strictly to conversations initiated by an inbound customer tweet (`root_inbound == True`).
- **Initial Inbound Candidates**: **80,250 opening problem statements**. (141 threads rooted by an outbound AppleSupport announcement or proactive prompt were excluded so that every sample item represents a customer-initiated technical problem).

### 1.2 Deterministic Sampling Configuration
- **Sample Size**: Exactly **500 records** (meeting the ~400–600 requirement).
- **Random Seed**: `42` (configured in `configs/base.yaml` and recorded in export metadata).
- **Sorting for Reproducibility**: Data is sorted deterministically by `conversation_id` prior to seeding and sampling.

### 1.3 Export Schema
The resulting CSV (`artifacts/taxonomy_input_sample.csv`) adheres to the requested column schema:

| Column | Type | Description |
| :--- | :--- | :--- |
| `conversation_id` | `int64` | Root tweet ID identifying the conversation thread |
| `tweet_id` | `int64` | The customer inquiry tweet ID |
| `text` | `string` | **100% exact original customer text** (unstripped, unedited) |
| `turn_count` | `int64` | Total turns in the reconstructed conversation |
| `created_at` | `string` | Original UTC timestamp string of the inquiry |

---

## 2. Near-Duplicate Deduplication Strategy

### 2.1 The Need for Deduplication
Customer support tweets on social media contain automated bot reposts, marketing promotions, repetitive spam, and identical complaints (e.g. users copy-pasting *"@AppleSupport battery is draining fast after update"*). Including identical phrasings in a 500-sample set would distort human taxonomy discovery by over-representing bot or viral repetitions.

### 2.2 Deduplication Key Normalization Algorithm
Deduplication is executed by generating a temporary normalized comparison key (`dedup_key`):
1. **Strip URLs**: `re.sub(r'https?://\S+', '', text)`
2. **Strip Mentions**: `re.sub(r'@\w+', '', text)` (e.g. `@AppleSupport`, co-tagged carriers)
3. **Case Normalization**: `.lower()`
4. **Strip Punctuation & Non-Alphanumerics**: `re.sub(r'[^a-z0-9\s]', ' ', text)`
5. **Whitespace Normalization**: `re.sub(r'\s+', ' ', text).strip()`
6. **Trivial Message Filter**: Discard messages where `len(dedup_key) <= 3` (e.g. tweets containing only a bare handle or URL).
7. **Deduplication**: Apply `drop_duplicates(subset=['dedup_key'], keep='first')` with deterministic order.

### 2.3 Strict Preservation of Original Text
> **CRITICAL DATA FIDELITY RULE**: The normalized `dedup_key` is used **solely** for grouping and duplicate detection. The exported `text` column in `taxonomy_input_sample.csv` contains the **exact, unmodified raw text** as provided in TWCS, including all original casing, emojis, exclamation marks, URLs, and `@mentions`.

### 2.4 Deduplication Pipeline Numbers
- Total inbound roots evaluated: **80,250**
- Candidate non-trivial roots: **79,869**
- Unique normalized problem statements: **78,763**
- Near-identical duplicates removed: **1,487**
- Drawn sample size: **500**
- Sample unique conversation IDs: **500** (100.0%)
- Sample unique tweet IDs: **500** (100.0%)
- Sample unique raw texts: **500** (100.0%)
- Sample unique normalized texts: **500** (100.0%)

---

## 3. Keyword Frequency Extraction Methodology

### 3.1 Corpus Scope
Keyword frequency analysis was performed across **all 131,258 inbound customer messages** in `data/processed/applesupport_subset.parquet`.

### 3.2 Text Preparation & Tokenization
To compute authentic unigram and bigram frequencies without corrupting source data:
1. Operates on a temporary cleaned copy of the text.
2. Removes URLs (`https?://\S+`) and `@mentions` (`@\w+`).
3. Lowercases text and normalizes apostrophes/curly single quotes (`['’]`).
4. Extracts alphanumeric tokens using regex `[a-z0-9]+`.
5. Filters out tokens with `len <= 1`, pure digits, and tokens matching the explicit stopword list.
6. Bigrams are formed by pairing adjacent non-stopword tokens within each message.

### 3.3 Explicit Stopword List (236 Words)
To guarantee complete auditability, the exact stopword list contains standard English function words, colloquial contraction variants, and Twitter platform noise:

```
a, about, above, after, again, against, ain, aint, all, am, amp, an, and, any,
apple, applesupport, are, aren, aren't, arent, as, at, be, because, been, before,
being, below, between, both, but, by, can, cant, co, couldn, couldn't, couldnt,
d, did, didn, didn't, didnt, dm, do, does, doesn, doesn't, doesnt, doing, don,
don't, dont, down, during, each, few, for, from, further, had, hadn, hadn't,
hadnt, has, hasn, hasn't, hasnt, have, haven, haven't, havent, having, he,
hed, hell, her, here, heres, hers, herself, hes, him, himself, his, how, hows,
http, https, i, id, if, ill, im, in, into, is, isn, isn't, isnt, it, it's, its,
itself, ive, just, ll, m, ma, me, mightn, mightn't, more, most, mustn, mustn't,
my, myself, needn, needn't, no, nor, not, now, o, of, off, on, once, only, or,
other, our, ours, ourselves, out, over, own, please, re, rt, s, same, shan,
shan't, she, she's, shed, shell, shes, should, should've, shouldn, shouldn't,
shouldnt, so, some, such, t, than, thank, thanks, that, that'll, thats, the,
their, theirs, them, themselves, then, there, theres, these, they, theyd, theyll,
theyre, theyve, this, those, through, to, too, under, until, up, ve, very, via,
was, wasn, wasn't, wasnt, we, wed, well, were, weren, weren't, werent, weve,
what, whats, when, whens, where, wheres, which, while, who, whom, why, whys,
will, with, won, won't, wont, wouldn, wouldn't, wouldnt, y, you, you'd, you'll,
you're, you've, youd, youll, your, youre, yours, yourself, yourselves, youve
```

### 3.4 Key Domain Findings (Top Unigrams & Bigrams)

#### Top 20 Unigrams
| Rank | Term | Raw Count | Domain Interpretation |
| :--- | :--- | :--- | :--- |
| 1 | `phone` | 24,806 | Hardware device inquiries |
| 2 | `iphone` | 22,624 | Primary device model |
| 3 | `ios` | 18,174 | Operating system issues |
| 4 | `update` | 17,764 | Software update regressions |
| 5 | `fix` | 15,659 | Problem resolution requests |
| 6 | `new` | 10,261 | New device or new update setup |
| 7 | `battery` | 9,303 | Battery degradation / drain |
| 8 | `help` | 7,896 | Assistance requests |
| 9 | `get` | 7,438 | Retrieval / functional access |
| 10 | `since` | 6,617 | Temporal onset of issues |
| 11 | `still` | 6,038 | Persistent unresolving symptoms |
| 12 | `app` | 5,933 | Application crashes / behaviors |
| 13 | `time` | 5,864 | Timing / frequency of failure |
| 14 | `updated` | 5,363 | Post-update condition |
| 15 | `screen` | 5,164 | Display, touch, black screen issues |
| 16 | `work` | 4,980 | Non-functional features |
| 17 | `issue` | 4,929 | Reported anomaly |
| 18 | `ios11` | 4,817 | Specific OS release version |
| 19 | `apps` | 4,759 | Multi-app compatibility |
| 20 | `problem` | 4,628 | Problem statement |

#### Top 20 Bigrams
| Rank | Term | Raw Count | Domain Interpretation |
| :--- | :--- | :--- | :--- |
| 1 | `ios update` | 2,387 | OS update problems |
| 2 | `new update` | 2,025 | Latest patch feedback |
| 3 | `battery life` | 1,915 | Rapid battery discharge |
| 4 | `iphone 6s` | 1,781 | Specific hardware model |
| 5 | `every time` | 1,734 | Intermittent/recurrent failures |
| 6 | `question mark` | 1,679 | iOS 11 letter 'I' glitch |
| 7 | `new ios` | 1,496 | Upgraded OS release |
| 8 | `iphone plus` | 1,430 | Plus form-factor models |
| 9 | `new iphone` | 1,382 | New device migration |
| 10 | `ever since` | 1,319 | Causal onset ("ever since update") |
| 11 | `updated phone` | 1,207 | Post-upgrade troubleshooting |
| 12 | `update phone` | 1,089 | Upgrade instructions |
| 13 | `new phone` | 1,005 | Setup and data transfer |
| 14 | `high sierra` | 978 | macOS desktop operating system |
| 15 | `since updated` | 975 | Regression onset |
| 16 | `updated ios` | 862 | OS version troubleshooting |
| 17 | `latest update` | 774 | Current patch issues |
| 18 | `phone keeps` | 744 | Looping reboots or crashes |
| 19 | `type letter` | 743 | iOS 11 autocorrect bug |
| 20 | `question marks`| 726 | iOS 11 keyboard rendering bug |

---

## 4. Message Length Distributions

The export package records empirical message lengths in `artifacts/taxonomy_input_length_stats.json` across two distinct scopes:
1. **All Inbound Customer Messages** ($N=131,258$, including both opening inquiries and ongoing replies).
2. **First-Turn Customer Inquiries** ($N=80,250$, opening problem statements).

### 4.1 Comparative Summary
| Metric | All Inbound Messages | First-Turn Inquiries | Delta / Pattern |
| :--- | :--- | :--- | :--- |
| **Total Count** | 131,258 | 80,250 | — |
| **Mean Character Length** | 106.54 chars | **115.10 chars** | +8.56 chars |
| **Median Character Length** | 105.0 chars | **114.0 chars** | +9.0 chars |
| **Std Dev Character Length** | 53.60 chars | 50.84 chars | More focused |
| **Mean Word Count** | 18.32 words | **19.92 words** | +1.60 words |
| **Median Word Count** | 18.0 words | **19.0 words** | +1.0 words |
| **Min / Max Chars** | 1 / 362 chars | 1 / 328 chars | Full range |
| **Min / Max Words** | 1 / 94 words | 1 / 70 words | Full range |

### 4.2 Character Quantiles
| Quantile | All Inbound Messages | First-Turn Inquiries |
| :--- | :--- | :--- |
| **p10** | 40.0 chars | 58.0 chars |
| **p25** | 67.0 chars | 81.0 chars |
| **p50 (Median)** | 105.0 chars | 114.0 chars |
| **p75** | 138.0 chars | 138.0 chars |
| **p90** | 163.0 chars | 165.0 chars |
| **p95** | 206.0 chars | 211.0 chars |
| **p99** | 277.0 chars | 276.0 chars |

### 4.3 Word Quantiles
| Quantile | All Inbound Messages | First-Turn Inquiries |
| :--- | :--- | :--- |
| **p10** | 6.0 words | 9.0 words |
| **p25** | 11.0 words | 14.0 words |
| **p50 (Median)** | 18.0 words | 19.0 words |
| **p75** | 24.0 words | 24.0 words |
| **p90** | 29.0 words | 30.0 words |
| **p95** | 37.0 words | 37.0 words |
| **p99** | 50.0 words | 50.0 words |

### 4.4 Character Length Histogram (First-Turn Inquiries)
- **0–30 chars**: 2,829 (3.53%) — brief greetings or mentions without symptom detail
- **31–60 chars**: 7,725 (9.63%) — short direct questions (e.g. *"When is iOS 11.1 coming out?"*)
- **61–90 chars**: 15,317 (19.09%) — concise bug reports
- **91–120 chars**: 21,570 (26.88%) — standard single-sentence symptom descriptions
- **121–140 chars**: 17,994 (22.42%) — tweets maxing out Twitter's legacy 140-character limit
- **141–200 chars**: 7,651 (9.53%) — multi-sentence symptoms enabled by Twitter's 280-char expansion
- **201–240 chars**: 3,745 (4.67%) — detailed troubleshooting steps already attempted
- **241–280 chars**: 3,365 (4.19%) — long, complex inquiries with specs and conditions
- **281+ chars**: 54 (0.07%) — multi-tweet threads / expanded URL citations

---

## 5. Artifact Limitations & Specialist Guidance

1. **Original Text Integrity**:
   - The `text` field in `taxonomy_input_sample.csv` contains verbatim original tweets.
   - It includes `@mentions` (e.g., `@AppleSupport`), shortened URLs (`https://t.co/...`), and Unicode emoji symbols.
   - Downstream taxonomy specialists should be aware that customer problem statements often cite image attachments (screenshots of error screens) via t.co URLs that cannot be resolved offline.
2. **Character Limit Truncation**:
   - 22.42% of first-turn tweets fall into the 121–140 character range, reflecting constraints from Twitter's legacy 140-character limit. Customers frequently abbreviated words, used shorthand, or omitted punctuation to fit their message.
3. **Channel Deflection**:
   - In 65.19% of conversations, detailed symptom resolution (such as IMEI numbers, Apple ID credentials, or billing receipts) was redirected to private direct messages, leaving the public Twitter first turn as the primary symptom signal.
4. **No Synthesized Taxonomy Labels**:
   - This export contains purely descriptive, empirical data. No taxonomy categories, clusters, or labels have been pre-assigned.

---

## 6. Verification and Acceptance Suite

A dedicated acceptance test suite (`tests/test_taxonomy_input_export.py`) validates:
1. **Sample Size**: Exactly 500 rows.
2. **Schema Compliance**: All required columns present (`conversation_id`, `tweet_id`, `text`, `turn_count`, `created_at`).
3. **Tweet ID Uniqueness**: 500 unique tweet IDs and 500 unique conversation IDs.
4. **No Text Alteration**: The exported text exactly matches `customer_inquiry_text` in `applesupport_conversations.parquet`.
5. **Seed Reproducibility**: Re-running `export_taxonomy_sample` with seed `42` produces a bitwise identical CSV.
6. **Artifact Non-Emptiness**: `taxonomy_input_keyword_freq.json` contains 150 items for unigrams, bigrams, and combined.
7. **Length Stats Validity**: Quantile ordering is monotonic and covers all inbound messages.
8. **Immutability of Prior Phases**: `applesupport_conversations.parquet`, `applesupport_subset.parquet`, and `twcs.csv` remain unmodified.
