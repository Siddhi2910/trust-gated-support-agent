# Final Taxonomy-Artifact Reconciliation Audit Report

**Audit Date:** 2026-09-11  
**Dataset Reference:** AppleSupport Customer Inquiries ($N = 80,391$ opening customer conversations; $N = 131,258$ full inbound tweets)  
**Taxonomy Freeze Status:** `taxonomy_frozen = false` (Provisional Candidate pending Human Review Authorization)  
**Current Intent Count:** 15 Candidate Intents  

---

## 1. Executive Summary & Objective

Prior to any formal human-review authorization to freeze the intent taxonomy for Golden Set construction, a comprehensive cross-artifact reconciliation audit was conducted across:
- `artifacts/taxonomy_v1_candidate.json`
- `artifacts/taxonomy_confusion_matrix.json`
- `artifacts/taxonomy_provenance.json`
- `reports/taxonomy_semantic_audit.md`
- `reports/taxonomy_human_review_preflight.md`
- The underlying reconstructed conversation dataset (`data/processed/applesupport_conversations.parquet`)

The primary objective was to ensure complete internal consistency across all candidate artifacts, verify that no meaningful customer support cluster was silently dropped or obscured, eliminate any stale/orphan intent references, and confirm that the primary-intent focal grievance rule is rigorously maintained.

---

## 2. Confusion-Matrix Consistency Audit

### Audit Findings
An audit of `artifacts/taxonomy_confusion_matrix.json` identified two stale intent ID references that originated during early provisional discovery drafting and were never updated when the 15-intent candidate was established:
1. `STORAGE_MANAGEMENT_DISK_SPACE` (referenced in `PAIR_04_DATA_LOSS_VS_STORAGE`)
2. `HARDWARE_PHYSICAL_DEFECT` (referenced in `PAIR_05_SCREEN_DISPLAY_VS_HARDWARE_DEFECT`)

Neither `STORAGE_MANAGEMENT_DISK_SPACE` nor `HARDWARE_PHYSICAL_DEFECT` existed as top-level candidate intents in `artifacts/taxonomy_v1_candidate.json`. Furthermore, reciprocal stale references were detected in the `exclusion_criteria` and `boundary_cases` of four candidate intents in `taxonomy_v1_candidate.json`:
- `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` (exclusion criteria referenced `HARDWARE_PHYSICAL_DEFECT`)
- `DATA_LOSS_RECOVERY` (exclusion criteria and boundary cases referenced `STORAGE_MANAGEMENT_DISK_SPACE`)
- `SCREEN_DISPLAY_HARDWARE_SYMPTOM` (boundary cases referenced `HARDWARE_PHYSICAL_DEFECT`)
- `BILLING_CHARGE_REFUND_DISPUTE` (exclusion criteria referenced `HOW_TO_GENERAL_PRODUCT_QUESTION`)

### Resolutions Implemented
1. **`artifacts/taxonomy_confusion_matrix.json` Updated:**
   - **`PAIR_04_DATA_LOSS_VS_STORAGE` Replaced with `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`:**
     - Intent A: `DATA_LOSS_RECOVERY`
     - Intent B: `ACCOUNT_APPLE_ID_ACCESS`
     - Focus: Resolves confusion between missing local user data/iCloud sync disappearance vs. Apple ID account lockout and 2FA recovery delays.
     - Positive Example: Tweet 320924 (*"All my messages are gone. @AppleSupport real cute, sis."*)
     - Counterexample: Tweet 6554 (*"@AppleSupport how long does it take usually for account recovery to get back to you? It’s been about a week now."*)
   - **`PAIR_05_SCREEN_DISPLAY_VS_HARDWARE_DEFECT` Replaced with `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`:**
     - Intent A: `SCREEN_DISPLAY_HARDWARE_SYMPTOM`
     - Intent B: `DEVICE_FREEZE_CRASH_REBOOT`
     - Focus: Resolves confusion between physical display visual/touch digitizer failures vs. whole-device operating system crash, freeze, or boot loop.
     - Positive Example: Tweet 34646 (*"My 6 month old IPhone 6 touch screen is unresponsive. @AppleSupport please help!"*)
     - Counterexample: Tweet 50615 (*"@115858 @AppleSupport y’all really bout to piss me off with this dumbass update. My phone keeps crashing and shutting off"*)
   - **Added `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`:**
     - Intent A: `APP_SPECIFIC_MALFUNCTION`
     - Intent B: `PERFORMANCE_SLOWDOWN_LATENCY`
     - Focus: Resolves single isolated app lag/crashing vs. entire device UI latency.
     - Positive Example: Tweet 520207 (*"@AppleSupport Safari keeps crashing over and over today..."*)
     - Counterexample: Tweet 481805 (*"My phone is running so slow after I updated it....@115858 wanna explain?"*)
   - **Tie-Breaker Alignment:** Every confusion pair now explicitly enforces the **Customer Focal Grievance / Actionable Need First** principle, with the priority ladder invoked strictly as a deterministic tie-breaker when co-occurring symptoms are genuinely unelaborated.

2. **`artifacts/taxonomy_v1_candidate.json` Updated:**
   - All stale references in exclusion criteria and boundary cases were replaced with valid, existing intent IDs (`UNKNOWN_OUT_OF_SCOPE`, `PERFORMANCE_SLOWDOWN_LATENCY`, and updated pair identifiers).
   - Zero orphan or nonexistent intent IDs remain across any artifact.

---

## 3. Dropped-Intent Audit & Empirical Corpus Evidence

Each previously considered provisional category was audited against the complete conversation dataset ($N = 80,391$ conversations) using deterministic pattern matching and sample inspection:

| Evaluated Category | Observed Count ($N=80,391$) | % of Corpus | Final Status | Destination Intent | Empirical & Operational Justification | Hiding a Support Cluster? |
|:---|:---:|:---:|:---:|:---|:---|:---:|
| **`STORAGE_MANAGEMENT_DISK_SPACE`** | 69 | 0.09% | Absorbed / Distributed | `PERFORMANCE_SLOWDOWN_LATENCY` (if UI lag); `APP_SPECIFIC_MALFUNCTION` (if update/install blocked); `DATA_LOSS_RECOVERY` (if files deleted); `UNKNOWN_INSUFFICIENT_CONTEXT` (if bare vent) | Extremely low prevalence (0.09%, <1 in 1,100 conversations). Does not meet the $\ge 1.0\%$ volume threshold. In practice, storage issues are symptoms that prompt outreach only when they cause device sluggishness, block app downloads, or trigger accidental deletion. | **No.** Inquiries naturally distribute to the operational failure mode. |
| **`HARDWARE_PHYSICAL_DEFECT`** | 25 (residual) | 0.03% (residual) | Split & Retained | `HARDWARE_CHARGING_POWER_CABLE` (3.06%), `AUDIO_SOUND_SPEAKER_MIC` (2.56%), `SCREEN_DISPLAY_HARDWARE_SYMPTOM` (2.65%) | The broad provisional category was split in Stage B into three distinct component intents ($>8.2\%$ combined). The residual non-screen, non-cable, non-audio physical defects (cracked back glass, water submersion, bent casing) total only 25 conversations (0.03%) and do not warrant a standalone top-level bucket. | **No.** Over 99% of physical hardware inquiries are explicitly captured in the three dedicated component intents. |
| **`HOW_TO_GENERAL_PRODUCT_QUESTION`** | 2,835 | 3.53% | Routed by Substantive Fault | Respective technical intents (e.g., `BATTERY_DRAIN_POWER_CONSUMPTION`, `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`, `DATA_LOSS_RECOVERY`) | "How to" is an interrogative syntactic structure, not a semantic domain. Users asking *"how do I fix my battery?"* (Tweet 31915) or *"how do I stop 'I' changing?"* (Tweet 1759) have diagnostic hardware/software failures. Creating a generic "How-To" intent would dismantle diagnostic clustering and cross-cut all 14 intents. Pure non-diagnostic navigation questions belong in `UNKNOWN_INSUFFICIENT_CONTEXT`. | **No.** Eliminates orthogonal cross-cutting ambiguity. |
| **`CUSTOMER_SERVICE_EXPERIENCE_COMPLAINT`** | 455 | 0.57% | Routed by Underlying Fault / Fallback | Technical intent if mentioned; `UNKNOWN_INSUFFICIENT_CONTEXT` if pure service vent | Most customer service complaints accompany an underlying technical blocker (e.g., Tweet 8437: unable to book Genius Bar due to locked Apple ID $\rightarrow$ `ACCOUNT_APPLE_ID_ACCESS`). Pure complaints about hold times or rude agents without technical context (e.g., Tweet 35971) are non-diagnostic vents routed to the fallback class. | **No.** Real technical needs receive technical triage; meta-support vents are handled via fallback de-escalation. |
| **`FEATURE_REQUEST_FEEDBACK`** | 73 | 0.09% | Absorbed by Fallback | `UNKNOWN_INSUFFICIENT_CONTEXT` (Category A: Non-Support / Product Feedback) | Volume is negligible (0.09%). Feature requests and product suggestions have no troubleshooting playbooks or diagnostic resolution workflows. | **No.** Explicitly classified under Category A of the fallback definition. |
| **`NOTIFICATION_ALERT_BADGE_ISSUE`** | 64 | 0.08% | Absorbed by App / Fallback | `APP_SPECIFIC_MALFUNCTION` (if third-party app); `PERFORMANCE_SLOWDOWN_LATENCY` or `UNKNOWN_INSUFFICIENT_CONTEXT` (if general) | Volume is negligible (0.08%). The vast majority of notification glitches pertain to specific apps (e.g., WhatsApp, Mail) and are properly handled as app malfunctions. | **No.** Volume is far below threshold. |

---

## 4. UNKNOWN / Fallback Class Integrity Audit

`UNKNOWN_OUT_OF_SCOPE` (recommended for renaming to `UNKNOWN_INSUFFICIENT_CONTEXT` upon human freeze) was audited to verify that it functions strictly as a bounded fallback class rather than a generic dumping ground:
1. **True Out-of-Scope (Category A):**
   - Promotional spam, cryptocurrency bots, competitor brand mentions, social chatter, and feature suggestions (e.g., Tweet 1177: *"Win an iPhone 8 by clicking this link"*).
2. **Genuinely Insufficient Context (Category B):**
   - Inbound support requests where the customer expresses frustration or asks for help but provides zero diagnostic context (e.g., Tweet 4827: *"@AppleSupport please DM me I need help"*, Tweet 32549: *"@AppleSupport your update broke my phone fix it"*).
3. **Guard Against Vague but Classifiable Inquiries:**
   - Any message providing a discernible symptom (e.g., *"my phone died and won't turn on"* $\rightarrow$ `HARDWARE_CHARGING_POWER_CABLE`; *"my phone is so slow"* $\rightarrow$ `PERFORMANCE_SLOWDOWN_LATENCY`) is strictly barred from the fallback class.

---

## 5. Current Taxonomy Completeness (15 Candidate Intents)

All 15 intents in `artifacts/taxonomy_v1_candidate.json` were programmatically audited:
- **Unique Intent IDs:** Verified (15 unique IDs).
- **Required Fields:** All intents possess `human_readable_name`, `definition`, `inclusion_criteria`, `exclusion_criteria`, `boundary_cases`, `representative_examples`, `prevalence_and_count`, `annotation_rule`, and `known_ambiguity`.
- **Verbatim Real Examples:** All 75 representative examples (5 per intent) match source tweets in `applesupport_conversations.parquet` with 100% character-level fidelity.
- **Zero Duplicate Examples:** No tweet ID is reused across multiple intents.
- **Inbound Customer Status:** All 75 examples are verified inbound customer inquiries (`root_inbound == True`, `root_author_id != 'AppleSupport'`).
- **Zero Orphan References:** All boundary references match valid, current intent IDs.

---

## 6. Confusion-Pair Quality & Status

All 7 confusable pairs in `artifacts/taxonomy_confusion_matrix.json` are verified:

| Pair ID | Intent A | Intent B | Intent A Verbatim Example | Intent B Verbatim Example | Status |
|:---|:---|:---|:---|:---|:---:|
| `PAIR_01_BATTERY_VS_CHARGING` | `BATTERY_DRAIN_POWER_CONSUMPTION` | `HARDWARE_CHARGING_POWER_CABLE` | Tweet 31869 (Battery draining iOS 11.1) | Tweet 35265 (iPhone not charging) | **Valid** |
| `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN` | `DEVICE_FREEZE_CRASH_REBOOT` | `PERFORMANCE_SLOWDOWN_LATENCY` | Tweet 50615 (Phone keeps crashing/shutting off) | Tweet 481805 (Phone running so slow) | **Valid** |
| `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH` | `APP_SPECIFIC_MALFUNCTION` | `DEVICE_FREEZE_CRASH_REBOOT` | Tweet 520207 (Safari keeps crashing) | Tweet 50615 (Phone keeps crashing/shutting off) | **Valid** |
| `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS` | `DATA_LOSS_RECOVERY` | `ACCOUNT_APPLE_ID_ACCESS` | Tweet 320924 (All my messages are gone) | Tweet 6554 (Account recovery taking a week) | **Valid** |
| `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` | `SCREEN_DISPLAY_HARDWARE_SYMPTOM` | `DEVICE_FREEZE_CRASH_REBOOT` | Tweet 34646 (Touch screen unresponsive) | Tweet 50615 (Phone keeps crashing/shutting off) | **Valid** |
| `PAIR_06_ACCOUNT_ACCESS_VS_BILLING` | `ACCOUNT_APPLE_ID_ACCESS` | `BILLING_CHARGE_REFUND_DISPUTE` | Tweet 43358 (Locked out of Apple ID with 2FA) | Tweet 149947 (Charged for Apple Music, want refund) | **Valid** |
| `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN` | `APP_SPECIFIC_MALFUNCTION` | `PERFORMANCE_SLOWDOWN_LATENCY` | Tweet 520207 (Safari keeps crashing) | Tweet 481805 (Phone running so slow) | **Valid** |

---

## 7. Multi-Symptom Rule Adherence

The operational rule governing multi-symptom customer inquiries remains strictly preserved:
1. **Focal Grievance / Main Actionable Need First:** Determine the primary symptom, failure mode, or grievance that drove the contact.
2. **Explicit Question / Requested Resolution:** If the customer explicitly demands a remedy or asks a direct diagnostic question (e.g., *"want a refund"*, *"tell me how to get my pictures back"*), that explicit request defines the primary intent.
3. **Priority Ladder as Tie-Breaker Only:** Only when multiple competing symptoms remain genuinely unelaborated and tied in prominence without an explicit focal demand, the **Priority Ladder with UNKNOWN as fallback** is invoked to deterministically break the tie. The priority ladder never overrides customer intent.

---

## 8. Automated Test Suite Results

The comprehensive test suite was executed via `pytest -v`:
- **Total Tests Executed:** 36 tests
- **Tests Passed:** 36 passed (100%)
- **Execution Time:** 10.69 seconds
- **New Deterministic Verifications Added:**
  - `test_confusion_matrix_verbatim_examples`: Verifies every `intent_a` and `intent_b` in the confusion matrix exists in `taxonomy_v1_candidate.json` and all examples are verbatim.
  - `test_candidate_taxonomy_no_stale_intent_references`: Verifies that no exclusion criteria or boundary cases reference deprecated or nonexistent intents (`STORAGE_MANAGEMENT_DISK_SPACE`, `HARDWARE_PHYSICAL_DEFECT`, `HOW_TO_GENERAL_PRODUCT_QUESTION`, `NOTIFICATION_ALERT_BADGE_ISSUE`).
  - `test_human_review_taxonomy_not_frozen`: Validates `taxonomy_frozen == false` across both `artifacts/taxonomy_human_review.json` and `artifacts/taxonomy_v1_candidate.json`.

---

## 9. Artifact Modification Log

1. **`artifacts/taxonomy_confusion_matrix.json`:**
   - Replaced stale pairs with valid, candidate-aligned confusable pairs (`PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`, `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`, `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`).
   - Aligned all tie-breaker descriptions with the focal-grievance-first policy.
2. **`artifacts/taxonomy_v1_candidate.json`:**
   - Corrected 4 exclusion criteria / boundary references that contained stale provisional intent IDs.
   - Preserved `taxonomy_frozen = false`.
3. **`tests/test_taxonomy_validation.py`:**
   - Added automated tests enforcing confusion matrix intent validity, stale intent exclusion, and freeze status.
4. **`reports/taxonomy_reconciliation_audit.md`:**
   - Generated this complete, evidence-grounded reconciliation audit report.

---

## 10. Unresolved Ambiguity & Review Status

- **Unresolved Ambiguities:** None. All 15 intents have mutually exclusive definitions, clear inclusion/exclusion boundaries, and verified confusion matrix tie-breakers.
- **Formal Review Status:** **The candidate taxonomy remains strictly UNFROZEN (`taxonomy_frozen = false`).** Golden Set construction, retrieval implementation, and downstream pipelines remain paused pending explicit human sign-off.
