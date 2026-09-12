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

## Decision 5: Multi-Turn Session State & Strict Context Bounding
- **Decision:** Implement multi-turn conversational session tracking with strict context bounding (capped at recent turns and total character length), where every turn is evaluated through the complete trust-gated pipeline independently.
- **Alternatives Considered:**
  1. *Unbounded Full History Concatenation*: Prepend all prior dialogue to the customer query.
  2. *Carry-Forward Decisions*: If turn 1 was AUTO_RESOLVE, automatically mark subsequent turns AUTO_RESOLVE.
  3. *Stateless Single-Turn Processing*: Ignore conversation continuity entirely.
- **Reason:** Customer inquiries evolve over time; a user might start with a benign question ("how do I update iOS?") and follow up with a critical hazard ("my battery swelled and the screen cracked"). Re-evaluating the Trust Gate on every turn prevents context poisoning and guarantees that a prior safe state cannot bypass safety, risk, or claim verification on subsequent turns. Furthermore, assistant responses are strictly treated as conversational context, NEVER as verified ground-truth historical evidence.
- **Evidence:** Rigorous multi-turn unit test suites (`tests/test_multi_turn_session.py`) confirm that new risk indicators immediately escalate active sessions, and previous decisions do not leak into future turn arbitrations.
- **Tradeoff:** Increases pipeline invocations per turn, but prevents severe safety breaches and prompt injection via conversational drift.

## Decision 6: Human Review Label Recovery and Atomic Review Persistence
- **Decision:** Recover genuine human adjudication records directly from verifiable audit logs and files (`recovered_human_labels.json`), while strictly rejecting synthetic or AI-hallucinated filler labels for the unreviewed remainder. Implement atomic read-after-write file persistence with backup snapshots for all specialist reviews.
- **Alternatives Considered:**
  1. *Synthetic Imputation*: Use an LLM or heuristic to fill the remaining 169 golden set cases with predicted labels and claim 100% completion.
  2. *Unchecked In-Place Writes*: Write directly to `artifacts/human_review_labels.json` without atomic temp-file swaps or prior backups.
- **Reason:** Research and engineering integrity demands that ground truth reflects actual human validation. Fabricating human labels creates an illusion of verified safety. Atomic writes with timestamped backups ensure that specialist reviews cannot corrupt the labels file during concurrent submissions or abrupt server restarts.
- **Evidence:** Explicitly tracking $N=1$ genuinely recovered human decisions and reporting 169 cases as unadjudicated preserves empirical honesty. Read-after-write verification prevents file truncation or partial writes.
- **Tradeoff:** Benchmark human accuracy is reported on a smaller verified human sample ($N=1$) until the remaining cases are reviewed in the Specialist Workspace, but ensures 100% methodological credibility.

## Decision 7: Ground Truth Boundaries & Strict Prohibition of Synthetic Data
- **Decision:** Ground all pipeline stages, retrieval stores, and evaluations in real AppleSupport interactions from the TWCS corpus. Strictly prohibit mock databases, synthetic customer queries, or fake support transcripts.
- **Alternatives Considered:**
  1. *Synthetic Data Augmentation*: Generate 10,000 synthetic customer issues via GPT-4 to artificially inflate test volume.
  2. *Mock In-Memory Databases*: Simulate support tickets and evidence with hardcoded dummy lists.
- **Reason:** Synthetic customer data systematically fails to capture real user behavior—including misspellings, colloquial expressions, overlapping complaints, and genuine hardware safety hazards. Real AppleSupport data provides authentic linguistic variety and realistic diagnostic challenges.
- **Evidence:** Verified 106,860 real AppleSupport tweets and 80,391 reconstructed multi-turn conversations serve as the empirical foundation for all intent definitions and evidence retrieval.
- **Tradeoff:** Requires rigorous data cleaning, provenance tracking, and leak-prevention filtering against the golden evaluation set.

## Decision 8: Honest Metrics Reporting vs. Vanity Headlines
- **Decision:** Enforce transparent, mathematically sound evaluation reporting that explicitly critiques misleading vanity headlines and highlights edge cases.
- **Alternatives Considered:**
  1. *Promotional / Marketing Reporting*: Publish headlines like "100% Autonomous Resolution" or "Zero Hallucination Guaranteed".
  2. *Standard Accuracy Reporting*: Report aggregate accuracy without partitioning into clean, boundary, and out-of-scope sets.
- **Reason:** Aggressive automation metrics often hide catastrophic vulnerabilities. For instance, a naive keyword baseline achieves 100% "resolution" simply by replying to every message blindly—including battery fires and account takeovers. Honest reporting separates safe automation from unsafe auto-replies and documents test set limitations.
- **Evidence:** Benchmark reporting clearly dissects Part 1 (120 candidate intents), Part 2 (35 boundary cases), and Part 3 (15 unknown cases), exposing why naive baselines fail catastrophically in production despite high superficial agreement.
- **Tradeoff:** The system's headline automation rate (47.1%) appears lower than naive bots (100%), but delivers 0.0% unsafe auto-replies and complete safety containment.

## Decision 9: Secondary Qualitative Role for LLM-as-a-Judge
- **Decision:** Position LLM-as-a-Judge strictly as a secondary, advisory qualitative evaluation layer that never replaces, modifies, or overrides deterministic rules, lexical claim verification, or human annotations.
- **Alternatives Considered:**
  1. *Primary Authority*: Use an LLM judge to determine ground truth labels and grade pipeline decisions automatically.
  2. *Fabricated Fallback*: Pre-populate judge scores with mock numbers if no API key is present.
  3. *No LLM Judge*: Rely solely on deterministic metrics.
- **Reason:** While an LLM judge provides valuable qualitative insight into tone, empathy, and perceived groundedness, LLMs are themselves susceptible to bias, inconsistency, and hallucination. When credentials are missing, the judge must report `UNAVAILABLE` rather than synthesizing fake metrics.
- **Evidence:** `src/evaluation/judge.py` defines a versioned prompt (`v1.0.0-trust-gated-eval`) and records model metadata, outputting qualitative scores only when valid live credentials are provided.
- **Tradeoff:** Qualitative evaluations require external API calls, but deterministic safety gates and human golden benchmarks retain absolute final authority.

## Decision 10: Safe Automation Coverage vs. Unsafe Auto Rate Formulation
- **Decision:** Formalize evaluation around two complementary operational metrics: Safe Automation Coverage (percentage of total traffic safely resolved without risk, ambiguity, or claim gaps) and Unsafe Auto Rate (percentage of traffic auto-replied to despite safety hazards, boundary conflicts, or ungrounded claims).
- **Alternatives Considered:**
  1. *Raw Automation Rate*: Total auto-resolved cases divided by total cases.
  2. *Standard Precision/Recall*: Treats all misclassifications with equal weight regardless of safety implications.
- **Reason:** In customer support AI, a false negative (unnecessary human escalation) costs operational labor, but a false positive (auto-resolving a lithium battery fire or hacked account with canned text) causes catastrophic brand, safety, and legal liability. Unsafe Auto Rate must be driven to 0.0%.
- **Evidence:** Under this formulation, Baseline 1 exhibits a 52.9% Unsafe Auto Rate, Baseline 2 exhibits unmonitored risk, and the Trust-Gated Dual-Track system achieves 0.0% Unsafe Auto Rate with 47.1% Safe Automation Coverage.
- **Tradeoff:** Restricts autonomous resolution volume to cases where evidence and safety are definitively verified.

## Decision 11: Immutability & Preservation of Frozen Taxonomy and Golden Set
- **Decision:** Treat `taxonomy_v1_frozen.json` and `artifacts/golden_set.json` as strictly immutable ground-truth artifacts. All code enhancements, bug fixes, and feature additions must adapt to the frozen standards without modifying or weakening them.
- **Alternatives Considered:**
  1. *Retrospective Label Modification*: Change golden set labels or taxonomy definitions whenever the model makes an error to inflate benchmark accuracy.
  2. *Dynamic Taxonomy Mutation*: Allow runtime endpoints to alter core intent schemas on the fly.
- **Reason:** Modifying the benchmark or evaluation set to fit model predictions violates scientific integrity and introduces evaluation leakage. Benchmark stability is mandatory for reliable regression testing.
- **Evidence:** Automated tests (`test_golden_set_leakage.py`, `test_frozen_taxonomy_integrity.py`) strictly enforce cryptographic SHA-256 and structural invariance of these files.
- **Tradeoff:** Requires iterative refinement of pipeline heuristics, tie-breaker ladders, and evidence retrieval rather than taking easy shortcuts by editing labels.

## Decision 12: Lexical & Semantic Claim Groundedness Limits (No "Hallucination-Free" Claims)
- **Decision:** Accurately describe claim verification as a lexical-semantic constraint based on token and n-gram overlap against historical TWCS evidence, explicitly acknowledging that 0 detected unsupported claims does not constitute a mathematical guarantee against all possible hallucinations.
- **Alternatives Considered:**
  1. *Absolute Guarantee Claim*: Market the system as "100% guaranteed hallucination-free".
  2. *Unchecked Generation*: Let LLMs generate answers without sentence-level claim extraction or evidence grounding.
- **Reason:** Verification systems operate on empirical heuristics. While decomposing responses into atomic claims and checking each against retrieved evidence prevents unsupported assertions from reaching customers, language models in unconstrained settings can produce subtle logical or temporal inaccuracies. Claiming absolute perfection is scientifically inaccurate.
- **Evidence:** The ClaimVerifier (`src/trust/claim_verifier.py`) enforces a 0.55 grounding threshold, flagging ungrounded claims for human escalation while reporting its methodological limitations in all evaluation reports.
- **Tradeoff:** Transparently communicates system capabilities and boundaries to stakeholders without overselling.

## Decision 13: Production API Contracts (`/health` and `/api/support/handle`)
- **Decision:** Implement standardized production HTTP API endpoints: `GET /health` (returning system status, version, timestamp, and AI availability) and `POST /api/support/handle` (accepting customer messages and session parameters, returning structured resolution decisions, confidence, risk levels, groundedness scores, and audit receipts).
- **Alternatives Considered:**
  1. *Internal-Only CLI*: Restrict pipeline execution to python command-line scripts.
  2. *Monolithic UI-Coupled Endpoints*: Route all requests through UI-specific demo endpoints like `/api/tickets`.
- **Reason:** Production deployment requires robust, framework-agnostic interfaces suitable for ingress routing, load balancing, external webhooks (e.g. Twitter/X or Zendesk connectors), and automated uptime monitoring.
- **Evidence:** Both endpoints return clean JSON payloads with standard HTTP status codes (200, 400, 500), validate input boundaries, and execute the genuine Trust-Gated Dual-Track pipeline without mock shortcuts.
- **Tradeoff:** Requires maintenance of both high-level production API contracts and specialized human review workspace endpoints.

## Decision 14: Stateless Production Configuration & Secrets Isolation
- **Decision:** Eliminate all hardcoded localhost URLs and secrets. Load environment variables dynamically via standard environment variables (`GEMINI_API_KEY`, `LLM_JUDGE_MODEL`, `VITE_API_BASE_URL`), and document them in `.env.example`.
- **Alternatives Considered:**
  1. *Hardcoded Fallbacks*: Embed fallback API keys or `http://localhost:3000` strings directly in source code.
  2. *Frontend Secret Injection*: Expose server-side LLM credentials to the client browser.
- **Reason:** Hardcoded credentials and localhost URLs break containerized cloud deployments (Cloud Run, Kubernetes) and introduce critical security vulnerabilities. Client-side code must use relative URLs or `VITE_API_BASE_URL` to route requests securely through the Express backend proxy.
- **Evidence:** Frontend components (`App.tsx`, `HumanReviewWorkspace.tsx`) use `apiFetch` and `safeFetchJson` with `API_BASE` resolution. Server-side code isolates `GEMINI_API_KEY` exclusively to backend handlers.
- **Tradeoff:** Requires proper environment configuration in container environments, but ensures cloud-readiness and enterprise security.


