# Architecture Decision Log

## Decision 0: Preservation of Existing React/TypeScript UI Scaffolding Without Scope Creep
- **Decision:** Preserve the pre-existing React/TypeScript frontend scaffolding located in `/src` (components, pages, types) completely intact, but strictly isolate it from backend data processing during Phase 0 and Phase 1.
- **Alternatives Considered:**
  1. Delete all existing React/TypeScript UI files and start a purely Python/Streamlit repo from scratch.
  2. Attempt to wire the existing UI immediately to live TWCS data and pipeline logic in Phase 0/1.
- **Reason:** Per the master architecture specification and user guidance, Python owns the data processing, retrieval, trust gate, and evaluation core. Prematurely wiring the UI before data extraction, intent taxonomy, retrieval, and trust gates exist leads to artificial shortcuts and ungrounded mock states. Conversely, deleting the UI would discard useful UI layout structures that can be adapted for the review queue and trust receipt visualization in later phases (Phase 13).
- **Evidence:** Clean separation of concerns allows Phase 0 and Phase 1 to focus purely on verifiable, deterministic data engineering and audit without frontend distraction.
- **Tradeoff:** The repository temporarily hosts both the existing React frontend files and the new Python pipeline skeleton side-by-side until the UI integration phase.

## Decision 1: AppleSupport Brand Selection (Phase 1 GO Decision)
- **Decision:** Select `AppleSupport` as the single target brand for the trust-gated customer support agent.
- **Alternatives Considered:**
  1. Multi-brand cross-domain agent (Delta, AmazonHelp, AppleSupport, Uber_Support simultaneously).
  2. Telecom provider (e.g. `sprintcare`, `TMobileHelp`).
  3. Single brand: `AppleSupport`.
- **Reason:** AppleSupport represents the highest-quality technical support domain in the TWCS corpus with the highest volume of structured troubleshooting and high diagnostic density. Multi-brand agents introduce erratic domain shifts, whereas AppleSupport offers deep technical specificity (iOS updates, battery diagnostics, Apple ID account recovery, iCloud synchronization, hardware reset procedures) required for rigorous retrieval-augmented generation and deterministic safety gating.
- **Evidence from Phase 1 Audit:**
  - 106,860 verified outbound brand replies (far exceeding the 10,000 threshold).
  - 88.93% response coverage across 119,895 linked inbound customer tweets (exceeding the 50% threshold).
  - High diagnostic response length (mean: 136.61 chars, median: 129 chars), indicative of structured instructions rather than simple deflection.
  - Heuristic PII indicator rate of 0.22% (258 phone pattern matches, 0 raw email patterns), confirming high cleanliness and manageable safety boundary containment.
- **Tradeoff:** Focuses the trust gate and taxonomy specifically on technical hardware and software support rather than airline ticketing or shipping logistics.

## Decision 2: Conversation-Level Reconstruction vs. Isolated Tweet Processing
- **Decision:** Perform data modeling, lineage tracking, and retrieval indexing at the reconstructed conversation thread level rather than on isolated single tweets.
- **Alternatives Considered:**
  1. *Isolated Tweet-Level Processing*: Treat each tweet as an independent query-response pair or individual text document.
  2. *Windowed Context Buffer*: Slide a fixed $k$-turn window over adjacent tweets without reconstructing the true tree graph.
  3. *Full Conversation Tree Reconstruction*: Reconstruct the exact rooted conversation tree graph, linking all customer questions, diagnostic clarifications, and brand resolutions chronologically and topologically.
- **Reason:** Customer support interactions are inherently contextual and multi-turn. In technical troubleshooting, an isolated tweet such as *"Yes, I restarted it and updated to 11.0.3 already"* or *"DM sent with screenshot"* is completely uninterpretable and unanswerable without the preceding customer symptom and diagnostic questions. Later phases (intent discovery, semantic retrieval, risk classification, and claim verification) require complete historical dialogues to understand problem symptoms, troubleshooting steps attempted, and the final resolution provided.
- **Evidence from Phase 2 Reconstruction:**
  - 100.0% of reconstructed conversations in the AppleSupport dataset are multi-turn ($\ge 2$ turns), totaling 80,391 conversations and 237,941 turns.
  - 34.81% of conversations (27,987 threads) extend beyond 2 turns (up to 282 turns), exhibiting rich diagnostic back-and-forth.
  - 6.11% of conversations (4,912 threads) exhibit branching topology, where customers or agents provide multi-part responses that an isolated linear model would truncate or misattribute.
  - 100.0% of conversations contain both customer and AppleSupport turns, guaranteeing that every indexed conversation captures genuine support interaction.
- **Tradeoff:** Increases data modeling complexity (directed tree construction, depth-first cycle verification, topological timestamp sorting) and produces a larger derived table (~58.5 MB Parquet) compared to flat tweets, but delivers pristine semantic grounding and eliminates context fragmentation for all downstream retrieval and evaluation.

## Decision 3: Taxonomy V1 Candidate Architecture and Distinguishability Rules
- **Decision:** Establish a provisional 15-intent taxonomy (`artifacts/taxonomy_v1_candidate.json`) derived directly from real AppleSupport conversation analysis, with explicit pairwise distinguishability boundaries (`artifacts/taxonomy_confusion_matrix.json`) and provenance lineage (`artifacts/taxonomy_provenance.json`), while strictly keeping `taxonomy_frozen: false`.
- **Alternatives Considered:**
  1. *Premature Freeze*: Mark `taxonomy_frozen: true` immediately upon passing structural schema tests.
  2. *Coarse Taxonomy (3-5 broad buckets)*: Collapse all technical issues into "Hardware", "Software", "Billing".
  3. *Overly Granular Taxonomy (50+ intents)*: Separate by exact device model or minor error code.
  4. *Balanced 15-Intent Taxonomy with Provisional Status*: Maintain actionable operational granularity (battery, charging, freezing, audio, display, keyboard, connectivity, apps, accounts, billing, orders, phishing, storage, data loss, out-of-scope) with strict pairwise tie-breakers.
- **Reason:** Real customer support workflows require fine-grained diagnostic differentiation (e.g. battery chemical degradation vs. hardware lightning port failure; whole OS crash/freeze vs. single app crash). Broad buckets fail to guide specific retrieval playbooks, while hyper-granular buckets introduce severe label noise. Maintaining provisional status ensures human oversight before downstream indexing and evaluation pipelines freeze.
- **Evidence:** Rigorous Stage A-N discovery identified high diagnostic concentration around iOS 11 update symptoms (battery, keyboard 'I' bug, Wi-Fi greyed out, touch digitizer unresponsiveness), accounting for over 70% of inbound volume.
- **Tradeoff:** Requires comprehensive manual and automated boundary testing to ensure annotator agreement and prevent boundary drift between adjacent intents.

## Decision 4: Rigorous Semantic Audit and Example Correction Prior to Human Freeze
- **Decision:** Mandate a full semantic audit of representative examples in `artifacts/taxonomy_v1_candidate.json` and replace any examples captured via naive keyword matching or cross-intent duplication with 100% verified, inbound, opening customer inquiries, while retaining `taxonomy_frozen: false`.
- **Alternatives Considered:**
  1. *Rely Solely on Syntactic / Automated Tests*: Treat passing automated tests as sufficient for taxonomy freeze.
  2. *Structural Re-architecture*: Modify the number and names of the 15 intents.
  3. *Semantic Audit and Verbatim Exemplar Refinement*: Preserve the well-grounded 15-intent structure while replacing all semantically compromised or duplicated examples with pristine verbatim records.
- **Reason:** Automated test suites verified that example tweet IDs existed and had matching text, but could not detect semantic mismatches caused by lexical ambiguity. In particular, the word "charge" appeared in credit card billing, battery drain, and cable power; "lost" appeared in colloquial idioms ("Has Youtube lost it?") rather than data loss; and "lock screen" appeared for media player controls rather than display hardware. Allowing contaminated exemplars into the frozen taxonomy would permanently corrupt downstream few-shot prompting, embedding evaluation, and golden set generation.
- **Evidence from Semantic Audit:**
  - Audit revealed 11 problematic tweets across multiple intents (e.g., Tweet 2628 duplicated across battery, charging, and billing; Tweet 749 in data loss; Tweet 4906 in connectivity despite explicit disclaimer; Tweet 8579 in charging instead of billing).
  - 29 examples across 10 intents were audited and replaced with unique, verified, inbound, opening customer inquiries directly illustrating the intent definitions.
  - Zero duplicate tweet IDs now exist across the 75 candidate slots.
  - Automated test suite was strengthened to enforce example uniqueness, inbound customer authorship, and explicit absence of previously misclassified tweets.
- **Freeze Status:** `taxonomy_frozen: false`. The candidate taxonomy is structurally and semantically refined, but must await human review and sign-off before being marked frozen.

