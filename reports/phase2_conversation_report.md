# Phase 2: Conversation Reconstruction Report

## Executive Summary

Phase 2 implements a deterministic, leakage-safe conversation reconstruction layer over the verified `data/processed/applesupport_subset.parquet` dataset. The reconstruction groups individual tweets into topologically coherent, multi-turn customer support conversation trees, preserving exact textual content, role assignments, parent/child relationships, chronological ordering, and graph linkage provenance.

The reconstruction produces:
- **Primary Derived Parquet**: `data/processed/applesupport_conversations.parquet` (80,391 conversations, 58.54 MB, Snappy-compressed).
- **Quality & Metrics Artifact**: `artifacts/phase2_conversation_stats.json`.
- **Raw TWCS Immutability**: `data/raw/twcs.csv` SHA-256 confirmed identical before and after reconstruction (`cd297fcfa1bf6f99938be242e8e578980bc6d1b96adc8691abec9a39175b03c0`).

---

## 1. How Conversation IDs Are Constructed

Each conversation thread originates at a specific root tweet (the opening customer inquiry or initial brand prompt). The reconstruction identifies roots deterministically:
1. Every tweet's ancestral path is traced upward using `in_response_to_tweet_id`.
2. The tree terminates at the node with no parent (`in_response_to_tweet_id` is null). This terminal node ID is designated as the `conversation_id`.
3. In `applesupport_subset.parquet`, exactly **80,391 unique roots** were resolved. In 100% of these conversations, the root tweet ID equals `conversation_id`.
4. 80,250 conversations (99.82%) are rooted by an inbound customer tweet; 141 conversations (0.18%) are rooted by an outbound AppleSupport announcement or proactive inquiry that initiated customer exchanges.

---

## 2. How Parent/Child Relationships Are Resolved

Conversations in Twitter customer service are **directed rooted trees** rather than simple linear chains:
1. **Parent Linkage**: For every turn, `in_response_to_tweet_id` is resolved against the subset's tweet index. If found, an explicit directed edge `parent_tweet_id -> child_tweet_id` is recorded in the child's metadata, and the child's ID is appended to the parent's `child_tweet_ids` array.
2. **Branching Support**: 4,912 conversations (6.11%) exhibit branching topology where a single parent tweet receives multiple child responses (e.g. multi-part diagnostic instructions or follow-ups). The tree structure accurately preserves all branches.
3. **Topological Ordering**: Turns are ordered primarily by their parsed UTC timestamp (`created_at`). In rare edge cases where timestamps coincide, a secondary sort key uses topological depth from root (ensuring parents strictly precede children), followed by deterministic `tweet_id` tie-breaking.
4. **Referential Consistency**: 100% of internal parent-child relationships are bidirectionally consistent (if $B$ lists $A$ as parent, $A$ contains $B$ in `child_tweet_ids`).

---

## 3. How Missing References Are Handled

Twitter data collection in TWCS contains inherent graph boundaries where tweets outside the collection period or deleted tweets are referenced:
1. **Missing Parents**: Exactly **0** conversations in the derived subset have missing parent links among internal turns. Every non-root turn points to a parent present in the conversation.
2. **Missing Children**: **6,432 conversations (8.00%)** contain at least one tweet citing a `response_tweet_id` that is not present in the AppleSupport subset (totaling **13,332 missing child references**).
   - These missing child references represent external mentions, replies by unrelated third-party users, or tweets outside the TWCS crawl window.
   - **Handling Rule**: The reconstruction explicitly records these absent references in `missing_child_ids` and flags `has_missing_children: true`, rather than fabricating records or dropping the conversation. Downstream phases can inspect this flag to know whether thread continuation was truncated.

---

## 4. Multi-Turn Conversation Representation

Each reconstructed conversation is represented both at the conversation level and at the turn level in `applesupport_conversations.parquet`:

| Field | Type | Description |
| :--- | :--- | :--- |
| `conversation_id` | `int64` | Root tweet ID identifying the thread |
| `root_tweet_id` | `int64` | The root tweet ID |
| `root_author_id` | `string` | Anonymized user ID or 'AppleSupport' |
| `root_inbound` | `bool` | True if root is customer inquiry |
| `customer_author_id` | `string` | Primary customer author ID |
| `num_turns` | `int32` | Total number of tweets in the conversation |
| `num_customer_turns` | `int32` | Customer / inbound turn count |
| `num_brand_turns` | `int32` | AppleSupport outbound turn count |
| `num_other_turns` | `int32` | Other participant turn count (e.g. cross-tagged carriers) |
| `first_created_at` | `string` | Timestamp string of first turn |
| `last_created_at` | `string` | Timestamp string of final turn |
| `duration_seconds` | `int64` | Elapsed duration from first to last turn |
| `is_multi_turn` | `bool` | True if `num_turns >= 2` (100.0% in subset) |
| `has_customer_and_brand`| `bool` | True if thread contains both customer & agent |
| `has_missing_parent` | `bool` | Flag for unresolved parent references |
| `has_missing_children` | `bool` | Flag for unresolved child references |
| `missing_child_count` | `int32` | Count of absent referenced child tweets |
| `is_branching` | `bool` | True if any turn has multiple children |
| `customer_inquiry_text` | `string` | Opening customer inquiry text (unmodified) |
| `first_brand_response_text` | `string` | Initial AppleSupport response text |
| `conversation_text` | `string` | Formatted multi-turn dialogue transcript |
| `turns_json` | `string` | Lossless JSON array of turn objects |

Each turn in `turns_json` preserves:
- `turn_index` (0-based chronological index)
- `tweet_id` (original TWCS ID)
- `author_id` (original author ID)
- `inbound` (boolean)
- `role` ("customer", "agent", or "other_brand")
- `created_at` & `created_at_epoch`
- `text` (100% exact original text, unstripped and unmodified)
- `in_response_to_tweet_id` & `response_tweet_id` (original strings)
- `parent_tweet_id` (resolved int or null)
- `child_tweet_ids` (resolved list of ints)
- `missing_child_ids` (list of missing child ints)

---

## 5. Actual Conversation Statistics

| Metric | Measured Value |
| :--- | :--- |
| **Total Reconstructed Conversations** | **80,391** |
| **Total Tweets / Turns** | **237,941** |
| **Inbound / Customer Turns** | **131,258 (55.16%)** |
| **Outbound Turns** | **106,683 (44.84%)** |
| AppleSupport Outbound Turns | 106,401 |
| Other Brand Outbound Turns (carriers, etc.) | 282 |
| **Single-Turn Conversations** | **0 (0.00%)** |
| **Multi-Turn Conversations ($\ge$ 2 turns)** | **80,391 (100.00%)** |
| **Conversations with $\ge$ 3 turns** | **27,987 (34.81%)** |
| **Conversations with Customer + AppleSupport** | **80,391 (100.00%)** |
| **Branching Conversations** | **4,912 (6.11%)** |
| **Mean Turns per Conversation** | **2.9598** |
| **Median Turns per Conversation** | **2.0** |
| **Standard Deviation of Length** | **2.6549** |
| **Min Turns / Max Turns** | **2 / 282** |
| **Conversations with Missing Parent Links** | **0 (0.00%)** |
| **Conversations with Missing Child Links** | **6,432 (8.00%)** |
| **Total Missing Child References** | **13,332** |
| **Chronological Ordering Anomalies** | **0 (0.00%)** |
| **Graph Cycles / Invalid Loops** | **0 (0.00%)** |
| **Median Conversation Duration** | **8,143 seconds (~2.26 hours)** |
| **Mean Conversation Duration** | **46,616 seconds (~12.95 hours)** |

### Conversation Length Distribution

| Turns | Count | Percentage |
| :--- | :--- | :--- |
| 2 | 52,404 | 65.19% |
| 3 | 7,951 | 9.89% |
| 4 | 10,509 | 13.07% |
| 5 | 2,963 | 3.69% |
| 6 | 3,050 | 3.80% |
| 7 | 1,169 | 1.45% |
| 8 | 1,014 | 1.26% |
| 9 | 411 | 0.51% |
| 10 | 351 | 0.44% |
| 11+ | 569 | 0.71% |

---

## 6. Data-Quality Limitations

1. **Missing Follow-ups Outside TWCS**: 8.00% of conversations (6,432 threads) have outbound or customer tweets whose cited response IDs (`response_tweet_id`) are missing from the crawled TWCS corpus. These represent interactions that continued beyond the collection boundary or were deleted on Twitter.
2. **Channel Redirection to DM**: Consistent with standard Apple Support operational protocol, many 2-turn conversations conclude with instructions like *"DM us your device model and iOS version so we can look into this"*. The private DM exchange occurred off-platform, explaining why 65.19% of conversations are exactly 2 turns long.
3. **Cross-Brand Inquiries**: 282 turns involve third-party brands (e.g. mobile carriers like Sprint, T-Mobile, Verizon) when customers tagged both their carrier and `@AppleSupport` regarding cellular or activation issues. These are explicitly tagged with `role: other_brand`.

---

## 7. Measured Runtime Performance

- **Reconstruction Loop**: **15.10 seconds** (processing all 80,391 conversations and 237,941 turns).
- **Total Runner Execution**: **15.33 seconds** (including Parquet I/O, raw file SHA-256 verification, and JSON writing).
- **Memory Footprint**: Lightweight streaming and dict-based indexing; runs within standard container limits.

---

## 8. Tests Performed

The reconstruction logic is verified by test suites covering:
1. **Referential Integrity**: Every reconstructed `tweet_id` exists in the verified Phase 1 subset and TWCS raw source.
2. **Text Fidelity**: Zero characters of tweet text are altered or stripped.
3. **Determinism**: Running the reconstruction process twice produces identical, bitwise-matching Parquet files (`ee70052e7be482e78be57cde9960a1981ba6b817fed8818abf0833bee6a5bd9b`).
4. **No Duplicate Tweet IDs**: Every tweet ID appears in exactly one conversation and one turn.
5. **Parent/Child Graph Consistency**: Directed tree edges are acyclic and consistent.
6. **Raw Immutability**: `data/raw/twcs.csv` SHA-256 remains unmodified.
7. **No Unrelated Merges**: Only tweets with valid relational paths to the root are assigned to a conversation.

---

## 9. Design Tradeoffs

1. **Storage Format (Hybrid Flat + JSON vs Normalized Relational Tables)**:
   - *Decision*: Store conversation-level attributes directly in columns (with `customer_inquiry_text`, `first_brand_response_text`, and `conversation_text` readily accessible for indexing and retrieval) while storing complete turn lists in `turns_json`.
   - *Tradeoff*: Slight duplication between summary fields and turn objects (~58 MB Parquet size) in exchange for fast, single-table analytical queries without multi-table joins.
2. **Graph Scope (AppleSupport Subgraph vs Complete 2.8M TWCS)**:
   - *Decision*: Reconstruct strictly on the verified AppleSupport subgraph.
   - *Tradeoff*: Does not reconstruct irrelevant brands (e.g. British Airways or Delta), achieving sub-20s runtimes while capturing 100% of target brand support interactions.
