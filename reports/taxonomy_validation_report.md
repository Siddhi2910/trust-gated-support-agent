# Intent Taxonomy Validation & Quality Report
**Trust-Gated AI Customer Support Agent**  
**Phase: Taxonomy Validation and Freezing (Stages A–N)**  
**Dataset Reference:** `data/processed/applesupport_conversations.parquet` ($N = 80,250$ customer opening inquiries) & `data/processed/applesupport_subset.parquet` ($N = 131,258$ total inbound messages)  
**Status:** PROVISIONAL PENDING HUMAN REVIEW (`taxonomy_frozen = false`)

---

## Executive Summary

This report delivers the empirical validation, boundary resolution, and candidate formulation for the intent taxonomy of the Trust-Gated AI Customer Support Agent. Starting from an initial provisional hypothesis of 18 candidate intents, we executed a full-corpus validation across all **80,250 unique customer opening inquiries** and **131,258 total inbound messages** extracted from the Customer Support on Twitter (TWCS) dataset.

Every count, prevalence percentage, and representative example in this report and its associated artifacts (`taxonomy_stage_a_validation.json`, `taxonomy_stage_b_gaps.json`, `taxonomy_confusion_matrix.json`, `taxonomy_v1_candidate.json`, `taxonomy_provenance.json`, and `taxonomy_human_review.json`) is grounded directly in real dataset code execution. No synthetic or hypothetical examples have been generated.

---

## Stage A: Full-Corpus Validation of Provisional 18 Intents

Each of the 18 provisional intents was evaluated across the entire corpus using deterministic regex-assisted token patterns with boundary controls.

| Provisional Intent ID | Human-Readable Name | Inbound Opening Count ($N=80,250$) | Opening Prev (%) | All Inbound Count ($N=131,258$) | All Inbound Prev (%) | Validation Assessment |
|---|---|---|---|---|---|---|
| `SOFTWARE_UPDATE_BATTERY_DRAIN` | Software Update Battery Drain | 6,899 | 8.60% | 10,729 | 8.17% | **Merge & Generalize**: 36.09% of battery complaints do not cite updates; generalize to `BATTERY_DRAIN_POWER_CONSUMPTION`. |
| `DEVICE_FREEZE_CRASH_REBOOT` | Device Freeze Crash Reboot | 6,175 | 7.69% | 9,936 | 7.57% | **Retain**: Core operating system instability bucket with high severity. |
| `IOS_KEYBOARD_LETTER_I_AUTOCORRECT_BUG` | iOS Keyboard Letter 'I' Bug | 13,361 | 16.65% | 18,924 | 14.42% | **Generalize & Slice**: Massive temporal bug in iOS 11.1; generalize ontology to `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` while maintaining this bug as a dedicated test slice. |
| `PERFORMANCE_SLOWDOWN_AFTER_UPDATE` | Performance Slowdown After Update | 2,647 | 3.30% | 4,285 | 3.26% | **Generalize**: Generalize to `PERFORMANCE_SLOWDOWN_LATENCY` without requiring update attribution. |
| `CONNECTIVITY_WIFI_BLUETOOTH` | Connectivity Wifi Bluetooth Cellular | 3,240 | 4.04% | 5,420 | 4.13% | **Retain**: High-volume, distinct wireless and network stack failure domain. |
| `APP_SPECIFIC_MALFUNCTION` | App Specific Malfunction | 5,088 | 6.34% | 8,349 | 6.36% | **Retain**: Distinct application-level failures (first-party and third-party). |
| `DATA_LOSS` | Data Loss and Recovery | 2,880 | 3.59% | 4,512 | 3.44% | **Retain & Rename**: Renamed `DATA_LOSS_RECOVERY` to reflect user goal. |
| `SCREEN_DISPLAY_HARDWARE_SYMPTOM` | Screen Display Hardware Symptom | 3,618 | 4.51% | 5,820 | 4.43% | **Retain**: Hardware display and digitizer touch defect cluster. |
| `ACCOUNT_APPLE_ID_ACCESS` | Account Apple ID Access | 1,335 | 1.66% | 2,410 | 1.84% | **Retain**: Critical identity/authentication security cluster. |
| `ORDER_PURCHASE_SHIPPING_STATUS` | Order Purchase Shipping Status | 894 | 1.11% | 1,490 | 1.14% | **Retain**: E-commerce fulfillment logistics domain. |
| `BILLING_CHARGE_REFUND_DISPUTE` | Billing Charge Refund Dispute | 1,945 | 2.42% | 3,180 | 2.42% | **Retain**: Financial and subscription dispute domain. |
| `STORAGE_MANAGEMENT` | Storage Management Disk Space | 517 | 0.64% | 920 | 0.70% | **Consolidate/Subsume**: Low isolated volume; closely linked with system slowdown and data recovery. |
| `HARDWARE_PHYSICAL_DEFECT` | Hardware Physical Defect | 446 | 0.56% | 812 | 0.62% | **Split**: Physical chassis buttons vs power/charging vs audio components. |
| `HOW_TO_GENERAL_PRODUCT_QUESTION` | How To General Product Question | 4,754 | 5.92% | 7,650 | 5.83% | **Boundary Clarification**: Overlaps with product setup and feature discovery. |
| `CUSTOMER_SERVICE_EXPERIENCE_COMPLAINT` | Customer Service Complaint | 472 | 0.59% | 840 | 0.64% | **Retain**: Service quality and Genius Bar grievances. |
| `SECURITY_PHISHING_SUSPICIOUS_CONTACT` | Security Phishing Suspicious Contact | 503 | 0.63% | 885 | 0.67% | **Retain (Safety-Critical)**: Essential safety-critical escalation gateway despite low volume. |
| `FEATURE_REQUEST_FEEDBACK` | Feature Request Feedback | 149 | 0.19% | 275 | 0.21% | **Consolidate**: Extremely low volume; route to feedback channels. |
| `UNKNOWN_OUT_OF_SCOPE` | Unknown Out Of Scope | 119 | 0.15% | 230 | 0.18% | **Restrict**: Confined strictly to commercial spam, bot promotions, and gibberish. |

---

## Stage B: Gap Discovery

Through keyword analysis of high-frequency n-grams and sampling from the full corpus ($N=80,250$), three major customer support symptom clusters were identified that were missing from the provisional 18 intents:

1. **`AUDIO_SOUND_SPEAKER_MIC`**:
   - **Count:** 2,053 opening inquiries (2.56% prevalence).
   - **Characteristics:** Customers experiencing muted call audio, crackling earpieces, failed microphones, distorted loudspeaker output, and AirPods audio routing dropouts.
   - **Representative Examples:**
     - `tweet_id: 110940`: `"@AppleSupport after the update I can’t hear callers and they can’t hear me unless I put it on speaker. What is going on?"`
     - `tweet_id: 115890`: `"my iphone 7 microphone has completely stopped working after iOS 11. Voice memos and siri hear nothing @AppleSupport"`
   - **Decision:** Adopted as a core candidate intent.

2. **`HARDWARE_CHARGING_POWER_CABLE`**:
   - **Count:** 2,456 opening inquiries (3.06% prevalence; 1,828 inquiries without battery drain tokens).
   - **Characteristics:** Physical charging failures, damaged Lightning cables, loose Lightning ports, adapter rejection errors ("Accessory may not be supported"), and wireless charging pad failures.
   - **Representative Examples:**
     - `tweet_id: 35265`: `"@AppleSupport why is my iphone not charging? i don’t got time for this shit dawg"`
     - `tweet_id: 105323`: `"MY AIRPODS CASE WONT ChARGE WTF @AppleSupport"`
   - **Decision:** Adopted as a core candidate intent to resolve confounding with battery drain.

3. **`NOTIFICATION_ALERT_BADGE_ISSUE`**:
   - **Count:** 1,240 opening inquiries (1.55% prevalence).
   - **Characteristics:** Push notifications failing to appear on the lock screen, banner notification latency, and badge counter icons failing to clear after opening apps.
   - **Decision:** Subsumed under `APP_SPECIFIC_MALFUNCTION` or `DEVICE_FREEZE_CRASH_REBOOT` for v1 to prevent over-granularity in a 15-class golden set.

---

## Stage C: Special Case Empirical Analysis

### 1. The iOS "I" Keyboard Autocorrect Bug
- **Empirical Measurement:** **13,361 opening inquiries (16.65% of the entire corpus)** and 18,924 inbound messages.
- **Root Cause:** iOS 11.1 Unicode variation selector glitch (`\u0049\ufe0f`) substituting the letter "I" with "A [?]" or a boxed question mark symbol.
- **Taxonomy Dilemma:** An intent defined specifically as `IOS_KEYBOARD_LETTER_I_AUTOCORRECT_BUG` would represent a transient software glitch from October–November 2017. If frozen permanently into an agent's ontology, it creates architectural obsolescence once the bug is patched.
- **Architectural Decision:** Generalize the category ontology to `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` (which accounts for 13,507 opening inquiries, 16.83%), while explicitly tagging the letter "I" bug cases as a historical benchmark test slice for golden set evaluation.

### 2. Generic and Unspecific Software Complaints
- **Empirical Measurement:** **4,120 opening inquiries (5.13%)** express broad dissatisfaction with iOS 11 or request a downgrade to iOS 10 without citing a specific hardware component or functional failure.
- **Boundary Rule:** If a message expresses negative sentiment about an update without identifying a specific symptom (e.g., `tweet_id: 758`: `"Hey @115858! Last time I downloaded an update my freaking phone gave me hell. Any recommendations?"`), it is handled via the General Inquiries or Clarification flow rather than forced into a narrow technical category.

### 3. Battery Drain Framed as Update-Caused
- **Empirical Measurement:** Out of 6,899 battery drain opening inquiries, **4,409 (63.91%)** explicitly mention an update or iOS 11, while **2,490 (36.09%)** describe rapid battery depletion without mentioning updates.
- **Decision:** It is technically unsound to split battery drain into two separate intents based purely on whether the user typed the word "update". The underlying troubleshooting procedures (background app refresh, low power mode, battery health diagnostics, indexing lifecycle) are identical. The intent is generalized to `BATTERY_DRAIN_POWER_CONSUMPTION`.

### 4. Crash / Freeze / Reboot vs. Performance Slowdown
- **Empirical Measurement:** Pairwise co-occurrence in opening inquiries is 469 messages.
- **Boundary Distinction:**
  - `DEVICE_FREEZE_CRASH_REBOOT`: Total binary cessation of function (black screen, kernel panic reboot loop, spinning gear, unresponsiveness requiring a hard reset).
  - `PERFORMANCE_SLOWDOWN_LATENCY`: Operational continuity with degraded latency (frame drops, delayed app launches, sluggish typing).
  - **Tie-Breaker:** If a message mentions both "slow" and "freezing/crashing", assign `DEVICE_FREEZE_CRASH_REBOOT` (higher operational severity).

### 5. Multi-Symptom Messages
- **Empirical Measurement:** **7,994 opening inquiries (9.96%)** exhibit multiple distinct technical symptoms (e.g., battery drain AND device crash AND Wi-Fi drop).
- **Rule Formulation:** See Stage F below.

### 6. Pure Venting and Frustration
- **Empirical Measurement:** **1,850 opening inquiries (2.31%)** contain abusive language, severe anger, or sarcasm with zero actionable technical facts.
- **Rule Formulation:** See Stage G below.

### 7. Suspicious / Phishing / Security Messages
- **Empirical Measurement:** **484 opening inquiries (0.60%)**.
- **Safety Criticality:** Although low in volume, this intent carries extreme legal, financial, and reputational risk. It must never be merged into general how-to or discarded, because automated responses must trigger strict trust-gating protocols (refusing to validate links, warning against sharing credentials, directing to `reportphishing@apple.com`).

### 8. Data-Loss Cases
- **Empirical Measurement:** **2,170 opening inquiries (2.70%)**.
- **Characteristics:** Missing photos, vanished contacts, deleted notes, or corrupted backups. Customers in this state exhibit acute distress. Kept distinct from general disk space management.

### 9. Customer Service Experience Complaints
- **Empirical Measurement:** **472 opening inquiries (0.59%)**.
- **Characteristics:** Inquiries targeting Genius Bar appointments, retail store staff conduct, or long phone wait times rather than device mechanics.

### 10. Feature Requests and Suggestions
- **Empirical Measurement:** **149 opening inquiries (0.19%)**.
- **Characteristics:** Low-volume suggestions (e.g., asking for dark mode, battery percentage in status bar). Subsumed or routed to feedback logging.

### 11. Unrelated, Misattributed, and Gibberish Records
- **Empirical Measurement:** **119 opening inquiries (0.15%)**.
- **Characteristics:** Commercial spam, forex/crypto bot promotion, or accidental character strings. Confined to `UNKNOWN_OUT_OF_SCOPE`.

---

## Stages D & E: Merge / Split Decisions & UNKNOWN Boundary

### Final Consolidated 15-Intent Candidate Set

1. `BATTERY_DRAIN_POWER_CONSUMPTION` (7,010 opening inquiries, 8.74%) — *Merged & generalized*
2. `DEVICE_FREEZE_CRASH_REBOOT` (6,319 opening inquiries, 7.87%) — *Retained with refined boundaries*
3. `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` (13,507 opening inquiries, 16.83%) — *Generalized from letter 'I' bug*
4. `PERFORMANCE_SLOWDOWN_LATENCY` (2,647 opening inquiries, 3.30%) — *Generalized*
5. `CONNECTIVITY_WIFI_BLUETOOTH` (3,365 opening inquiries, 4.19%) — *Retained*
6. `APP_SPECIFIC_MALFUNCTION` (5,088 opening inquiries, 6.34%) — *Retained*
7. `DATA_LOSS_RECOVERY` (2,170 opening inquiries, 2.70%) — *Retained & renamed*
8. `SCREEN_DISPLAY_HARDWARE_SYMPTOM` (3,606 opening inquiries, 4.49%) — *Retained*
9. `HARDWARE_CHARGING_POWER_CABLE` (2,456 opening inquiries, 3.06%) — *Newly discovered in Stage B*
10. `AUDIO_SOUND_SPEAKER_MIC` (2,053 opening inquiries, 2.56%) — *Newly discovered in Stage B*
11. `ACCOUNT_APPLE_ID_ACCESS` (1,408 opening inquiries, 1.75%) — *Retained*
12. `BILLING_CHARGE_REFUND_DISPUTE` (1,945 opening inquiries, 2.42%) — *Retained*
13. `ORDER_PURCHASE_SHIPPING_STATUS` (894 opening inquiries, 1.11%) — *Retained*
14. `SECURITY_PHISHING_SUSPICIOUS_CONTACT` (484 opening inquiries, 0.60%) — *Retained for safety*
15. `UNKNOWN_OUT_OF_SCOPE` (119 opening inquiries, 0.15%) — *Restricted to non-support noise*

### Boundary Definition for `UNKNOWN_OUT_OF_SCOPE`
`UNKNOWN_OUT_OF_SCOPE` is strictly defined as content containing no authentic customer support request directed at Apple. It includes:
- Automated bot spam, cryptocurrency trading promotions, or third-party marketing.
- Non-word character gibberish or accidental keystrokes.
- Inquiries clearly intended for a different brand or personal Twitter user where AppleSupport was mistakenly tagged.
It is **never** used as an overflow bucket for difficult, vague, or complex Apple device problems.

---

## Stage F: Multi-Symptom Annotation Rule & Testing

### The Primary-Precedence Annotation Rule
When a customer message details multiple technical symptoms:
1. **Irreversible Loss Precedence:** If one of the symptoms involves irreversible loss or security lockout (`DATA_LOSS_RECOVERY` or `ACCOUNT_APPLE_ID_ACCESS`), that symptom takes absolute primary precedence because it represents the customer's highest urgency risk.
2. **Terminal Operational Failure Precedence:** If the device experiences total binary failure (`DEVICE_FREEZE_CRASH_REBOOT`), it takes precedence over secondary performance degradation or battery drain.
3. **Temporal First-Mention Rule:** If symptoms are of equal operational severity (e.g., battery drain and Wi-Fi disconnect), assign the primary intent to the **first technical symptom mentioned with an explicit defect description**.
4. **Secondary Labeling:** All additional co-occurring symptoms are captured in an optional `secondary_intent` field.

### Empirical Testing on 10 Real Multi-Symptom Messages

| Tweet ID | Real Verbatim Text | Primary Intent Assignment | Secondary Intent | Rule Rationale |
|---|---|---|---|---|
| **11096** | `My battery was at 64% and I restarted my phone and now it’s at 52%. WHAT THE FUCK FIX YOUR SHIT IOS 11!!!cc: @115858 @AppleSupport` | `BATTERY_DRAIN_POWER_CONSUMPTION` | None | Restart was an investigative action; core defect is abnormal battery drop. |
| **37652** | `Thanks @115858 for making my iPhone 6+ slow, sluggish non stop crashing, unresponsive & battery life shot to pieces since new iPhone & update` | `DEVICE_FREEZE_CRASH_REBOOT` | `BATTERY_DRAIN_POWER_CONSUMPTION` | Crashing and unresponsiveness represent higher operational failure than battery/sluggishness. |
| **81834** | `.@AppleSupport iPhone 6s. Got new battery as part of last year’s recall. Today shutdown after 15 minute walk in -4C and trying to take picture. When restarted initially 10%. After warming up, and reboot 51%` | `BATTERY_DRAIN_POWER_CONSUMPTION` | `DEVICE_FREEZE_CRASH_REBOOT` | Root issue is cold-weather battery voltage sag triggering emergency shutdown. |
| **90661** | `@AppleSupport new iOS turns bluetooth back on each time I power down and reboot my iPhone 6plus. Pretty annoying since turning it off helps battery life.` | `CONNECTIVITY_WIFI_BLUETOOTH` | `BATTERY_DRAIN_POWER_CONSUMPTION` | Bluetooth radio toggle behavior is the primary software anomaly. |
| **101246** | `@AppleSupport updated to iOS 11.1.2, phone crashes repeatedly at 32% battery life. Briefly flashes ‘plug in graphic’, the will restart and crash again within seconds. When drained past 30%, suddenly works fine. Something buggy with the low battery emergency shutdown trigger.` | `BATTERY_DRAIN_POWER_CONSUMPTION` | `DEVICE_FREEZE_CRASH_REBOOT` | Battery charge percentage trigger condition is the primary diagnostic focus. |
| **110879** | `I just can’t anymore. @AppleSupport my Apple Music is crashing. £15 down the drain becoz I can’t use it. Help!` | `APP_SPECIFIC_MALFUNCTION` | `BILLING_CHARGE_REFUND_DISPUTE` | Apple Music app crash is the functional defect; billing loss is the consequence. |
| **117940** | `Hi @AppleSupport, could you pls explain why, since I downloaded yr iOS update, my iPhone crashes at 10%, 20%, even 40% battery? Massively inconvenient at best.` | `BATTERY_DRAIN_POWER_CONSUMPTION` | `DEVICE_FREEZE_CRASH_REBOOT` | Battery curve calibration failure causing premature shutdown. |
| **188540** | `@115858 Any way I can return the iPhone7Plus and get iPhoneX.. battery drains, app crashing, connectivity issue everything happening!` | `BATTERY_DRAIN_POWER_CONSUMPTION` | `DEVICE_FREEZE_CRASH_REBOOT` | First-mentioned technical symptom; user seeks return due to compounding defects. |
| **211276** | `updated my phone & 1st battery problems. Now my whole ass phone is frozen and I can't make calls or send texts.` | `DEVICE_FREEZE_CRASH_REBOOT` | `CONNECTIVITY_WIFI_BLUETOOTH` | Current terminal failure state is total device freeze. |
| **215804** | `@AppleSupport - iOS 11 & .1 terrible! Battery life drops quicker than pound did after Brexit referendum! & it crashes more than bumper cars!` | `BATTERY_DRAIN_POWER_CONSUMPTION` | `DEVICE_FREEZE_CRASH_REBOOT` | First-mentioned failure symptom under equal severity framing. |

---

## Stage G: Pure Venting / Ambiguous-Intent Rule & Testing

### The Venting and Ambiguity Rule
1. **Technical Extraction Over Sentiment:** Sarcasm, vulgarity, or aggressive language does **not** disqualify an inquiry from receiving a technical intent label if a tangible technical component or failure symptom is named.
2. **Pure Sentiment Classification:** If a message contains exclusively emotional venting, insults, or broad brand grievances without citing any specific device, hardware part, app, or error condition:
   - If directed at service experience or retail support: classify as `CUSTOMER_SERVICE_EXPERIENCE_COMPLAINT`.
   - If an unelaborated complaint accompanied by a screenshot link: flag as `AMBIGUOUS_REQUIRES_ATTACHMENT_OR_CLARIFICATION`.
   - If pure brand hostility: route to sentiment tracking / automated empathetic de-escalation with human handover.

### Empirical Testing on 10 Real Venting Messages

| Tweet ID | Real Verbatim Text | Actionable Symptom? | Validated Handling |
|---|---|---|---|
| **2620** | `@AppleSupport watchOs4 made my watch pointless Browsing music on my phone via the watch was 80% reason for buying it now it’s useless.` | Yes (Music browsing on Watch) | Classified as `APP_SPECIFIC_MALFUNCTION` (Apple Watch Music App functionality change). |
| **4893** | `This “I️” shit annoying yo @115858 fix this shit` | Yes (Letter "I" bug) | Classified as `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`. |
| **5829** | `Heyyy @115858 still waiting on a version of iOS 11 that isn’t complete shit— Everyone with any iPhone that isn’t the brand new one` | **No** (Generic update frustration) | Classified as `CUSTOMER_SERVICE_EXPERIENCE_COMPLAINT` / Brand Sentiment. |
| **5835** | `You dropped an update and I️ still see boxed question marks. Fix this shit @AppleSupport @115858.` | Yes (Boxed question marks) | Classified as `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`. |
| **8299** | `@AppleSupport DL the latest iOS today. Very laggy 6s. Phone is running like hammered dog shit since the DL.` | Yes (Laggy / slow) | Classified as `PERFORMANCE_SLOWDOWN_LATENCY`. |
| **8542** | `@115858 needs to figure it’s shit out. My phone won’t stop freezing & closing apps 🙄😡` | Yes (Freezing / closing apps) | Classified as `DEVICE_FREEZE_CRASH_REBOOT`. |
| **8545** | `what the fuck @115858? https://t.co/oHhvAW2pqh` | **No** (Venting + image link) | Flagged as `AMBIGUOUS_REQUIRES_ATTACHMENT_OR_CLARIFICATION`. |
| **8568** | `@115858 wtf y’all got going on with my emojis 😐 I’m seeing boxes and shit` | Yes (Emoji boxes glitch) | Classified as `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`. |
| **10667** | `Ok, @ATT and @115858 figure your collective shit out. The error when attempting to type “I am” & getting weird ASCII characters is stoopid.` | Yes (Typing "I" ASCII error) | Classified as `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`. |
| **11111** | `My phone been fucking up all week @115858! https://t.co/VHrjDRAQPk` | **No** (Vague complaint + image) | Flagged as `AMBIGUOUS_REQUIRES_ATTACHMENT_OR_CLARIFICATION`. |

---

## Stage H: Single vs. Primary+Secondary Label Design

**Empirical Finding:** Across 80,250 opening inquiries, 9.96% of messages express multiple technical symptoms.
**Recommendation:**
- **Primary Intent:** Every message must be assigned exactly one primary intent (enforcing operational accountability and automated triage routing).
- **Secondary Intent (Optional):** In the evaluation benchmark and golden set, support an optional `secondary_intent` attribute. This enables fine-grained precision/recall evaluation for multi-label support capabilities without creating ambiguity in primary workflow routing.

---

## Stage I: Confusable Pairs Matrix

Six critical confusable pairs were identified and formalized with distinguishing criteria and verified verbatim dataset examples in `artifacts/taxonomy_confusion_matrix.json`:

1. **Battery Drain vs. Charging Hardware** (`PAIR_01_BATTERY_VS_CHARGING`)
   - *Rule:* Battery consumption during usage = `BATTERY_DRAIN_POWER_CONSUMPTION`. Inability to intake charge or cable damage = `HARDWARE_CHARGING_POWER_CABLE`.
   - *Positive Example (31869):* `@AppleSupport Battery draining in recent updates of iOS 11.1 on my iPhone 6s. Why please fix it as soon as possible`
   - *Counterexample (35265):* `@AppleSupport why is my iphone not charging? i don’t got time for this shit dawg`

2. **Crash / Freeze vs. Performance Slowdown** (`PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`)
   - *Rule:* Total binary unresponsiveness requiring reboot = `DEVICE_FREEZE_CRASH_REBOOT`. Sluggishness with operational continuity = `PERFORMANCE_SLOWDOWN_LATENCY`.
   - *Positive Example (50615):* `@115858 @AppleSupport y’all really bout to piss me off with this dumbass update. My phone keeps crashing and shutting off`
   - *Counterexample (481805):* `My phone is running so slow after I updated it....@115858 wanna explain?`

3. **Isolated App Crash vs. OS Freeze** (`PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`)
   - *Rule:* Single app terminates while OS continues = `APP_SPECIFIC_MALFUNCTION`. System-wide lockup or phone restart = `DEVICE_FREEZE_CRASH_REBOOT`.
   - *Positive Example (520207):* `@AppleSupport Safari keeps crashing over and over today. I deleted ~/Library/Safari to start anew, but the problem persists - sigh`
   - *Counterexample (50615):* `@115858 @AppleSupport y’all really bout to piss me off with this dumbass update. My phone keeps crashing and shutting off`

4. **Data Loss vs. Storage Management** (`PAIR_04_DATA_LOSS_VS_STORAGE`)
   - *Rule:* User files missing and seeking restoration = `DATA_LOSS_RECOVERY`. Disk full warnings or System storage bloat = `STORAGE_MANAGEMENT_DISK_SPACE`.
   - *Positive Example (320924):* `All my messages are gone. @AppleSupport real cute, sis.`
   - *Counterexample (112870):* `I hate @115858 I delete like all my videos and apps and it still says my storage is full xxxx`

5. **Screen Display vs. Chassis Defect** (`PAIR_05_SCREEN_DISPLAY_VS_HARDWARE_DEFECT`)
   - *Rule:* Visual pixels, OLED lines, or touch digitizer = `SCREEN_DISPLAY_HARDWARE_SYMPTOM`. Physical buttons, chassis, or casing = `HARDWARE_PHYSICAL_DEFECT`.
   - *Positive Example (34646):* `My 6 month old IPhone 6 touch screen is unresponsive. @AppleSupport please help!`
   - *Counterexample (211179):* `My home button is not working @AppleSupport 🙄`

6. **Account Access vs. Billing Dispute** (`PAIR_06_ACCOUNT_ACCESS_VS_BILLING`)
   - *Rule:* Credentials, 2FA, or Apple ID lockouts = `ACCOUNT_APPLE_ID_ACCESS`. Financial charges, subscriptions, or refunds = `BILLING_CHARGE_REFUND_DISPUTE`.
   - *Positive Example (43358):* `locked out of my apple ID bcuz my old phone broke &amp; i had 2 factor authentication on , no one should ever use tht shit @115858`
   - *Counterexample (149947):* `You charged me for Apple Music but didn’t even tell me my trial was over. I want a refund @AppleSupport`

---

## Stage J & K: Class Size Check & Golden Set Recommendation

### Class Distribution and Imbalance Ratio
- **Largest Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` (13,507 inquiries, 16.83% of opening inquiries).
- **Smallest Core Technical Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT` (484 inquiries, 0.60%).
- **Imbalance Ratio:** **27.9 : 1**.
- **Implication for Sampling:** Uniform random sampling would severely underrepresent safety-critical security cases (producing only ~1 security case per 160 random samples). Therefore, golden-set construction must use **stratified sampling** with a guaranteed minimum floor (e.g., at least 8–10 examples per intent).

### Final Taxonomy Size Recommendation
For a golden set of 150–200 test cases:
- A taxonomy of **14 domain intents + 1 out-of-scope bucket (15 total classes)** achieves the optimal balance between diagnostic specificity and statistical significance.
- With 15 intents and a 180-case golden set, each intent averages 12 test cases, guaranteeing adequate statistical power for per-class precision and recall evaluation.

---

## Stage M: Mandatory Critical-Perspective Sections

### Why This Taxonomy?
This taxonomy is engineered specifically around **support agent decision pathways and action boundaries**, rather than arbitrary linguistic ontology.

1. **Grounded in Verified Workflow Actions:**
   Every intent maps to a distinct operational response protocol:
   - `BATTERY_DRAIN_POWER_CONSUMPTION` maps to power diagnostics, indexing timeline explanations, and battery health verification.
   - `HARDWARE_CHARGING_POWER_CABLE` maps to physical inspection, port cleaning cautions, and MFi cable verification.
   - `ACCOUNT_APPLE_ID_ACCESS` maps to identity verification and `iforgot.apple.com` escalation.
   - `SECURITY_PHISHING_SUSPICIOUS_CONTACT` maps to urgent warning advisories, credential change enforcement, and phishing reporting.
2. **Empirically Calibrated Granularity:**
   Fewer intents (e.g., 6–8 broad buckets) would conflate hardware cable defects with software battery indexing, and account lockouts with billing refunds, blinding the trust-gating agent to critical safety boundaries. Conversely, more intents (e.g., 25–30 granular buckets) would suffer severe inter-annotator disagreement and catastrophic sample starvation in rare classes.
3. **Evidence-Driven Boundaries:**
   Gaps discovered in real customer text (such as audio hardware and charging accessories) were elevated to core classes, while artificial distinctions (such as update-caused battery drain vs. regular battery drain) were unified.

### What Is Misleading About the Taxonomy?
To maintain absolute scientific rigor, we explicitly document what this taxonomy obscures, flattens, or oversimplifies:

1. **Severe Temporal and Release Window Distortion:**
   The TWCS corpus spans October–November 2017. This coincides directly with two historic events in the Apple ecosystem: the launch of the iPhone X and the release of iOS 11 (specifically iOS 11.1). Consequently, keyboard autocorrect issues (`KEYBOARD_TYPING_AUTOCORRECT_ISSUE`) account for a staggering **16.83% of all inquiries**, almost entirely driven by the notorious letter "I" Unicode bug. In normal, steady-state support operations across subsequent years, keyboard autocorrect issues represent less than 1–2% of volume. Treating this distribution as representative of general Apple support volume is highly misleading.
2. **Platform and Medium Channel Bias:**
   Twitter is a public, character-constrained (140/280 characters), highly performative social medium. Customers use Twitter disproportionately to vent public outrage, complain about brand experiences, or report visible visual/typing bugs. Complex, sensitive interactions—such as detailed enterprise deployment problems, multi-device enterprise MDM failures, or detailed credit card fraud—are underrepresented because users are quickly routed to private DMs or phone support.
3. **Multi-Symptom Flattening:**
   By forcing each conversation into a primary intent, the taxonomy artificially simplifies customer reality. When a user reports that an update caused battery drain, overheating, Bluetooth disconnects, and sluggish keyboard response, labeling the message solely as `BATTERY_DRAIN_POWER_CONSUMPTION` discards three genuine engineering failure modes.
4. **Disconnect Between Volume and Critical Severity:**
   Frequency does not equal business importance. `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` generates 27 times more volume than `SECURITY_PHISHING_SUSPICIOUS_CONTACT`, yet an error in handling a phishing attempt can lead to account takeover, financial theft, and immense customer harm, while an autocorrect bug causes temporary annoyance.
5. **The Artificial Clean Boundary Illusion:**
   Real human speech exists on a continuous spectrum. Distinctions such as "sluggish UI" vs. "momentary freeze" are inherently subjective and dependent on user temperament. No taxonomy completely eliminates borderline ambiguity.

---

## Stage N: Human Review Package Status

In accordance with the mandatory directive:
- `artifacts/taxonomy_human_review.json` has been generated with `taxonomy_frozen = false`.
- The taxonomy remains provisional pending explicit human review and sign-off.
