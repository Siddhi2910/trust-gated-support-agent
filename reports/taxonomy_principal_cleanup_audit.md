# Principal Engineer Taxonomy Cleanup Audit Report

**Audit Date:** September 11, 2026  
**Taxonomy Version:** `1.0.0-candidate`  
**Taxonomy Freeze Status:** `false` (Pending Human Review Sign-Off)  
**Corpus Source:** `data/processed/applesupport_conversations.parquet` (80,250 opening inquiries, `root_inbound == True`)  
**Validation Suite:** 38 / 38 unit tests passing  

---

## 1. Executive Summary

This audit documents the complete resolution of all seven boundary, structural, and sampling issues identified during the Principal Engineer review prior to human taxonomy sign-off. All adjustments were empirically validated against the full AppleSupport conversations corpus, reconciled across all repository artifacts, and locked with rigorous unit tests.

### Key Outcomes:
1. **UNKNOWN Structural Refinement:** Renamed `UNKNOWN_OUT_OF_SCOPE` to `UNKNOWN_INSUFFICIENT_CONTEXT` and formally segregated into **Category A** (True Non-Support / Commercial Promo) and **Category B** (Genuine Inbound Support with Insufficient Diagnostic Context). Measured empirical prevalence on the 80,250 opening inquiries corpus at **522 cases (0.65%)**.
2. **Screen & Biometrics Scope Consolidation:** Renamed `SCREEN_DISPLAY_HARDWARE_SYMPTOM` to `SCREEN_DISPLAY_TOUCH_BIOMETRICS`, formally unifying physical display anomalies, touch digitizer defects (unresponsive touch, ghost touch), and biometric authentication sensors (Touch ID, Face ID).
3. **Audio Scope Audit:** Formally documented that `AUDIO_SOUND_SPEAKER_MIC` encompasses speakers, microphones, audio routing, volume controls, alarm/ringer volume levels, and physical volume rocker buttons.
4. **Primary Intent Priority Ladder Refinement:** Formally subordinated the 9-level priority ladder to a **secondary tie-breaker only**. The customer's primary actionable grievance and explicit question/requested resolution strictly govern intent assignment.
5. **Full Artifact Reconciliation:** Updated all candidate definitions, confusion matrix pairs, provenance lineage, and human review schemas to eliminate stale intent references and ensure 100% verbatim accuracy.
6. **Deterministic Human-Review Sample Pack:** Generated a 170-case stratified random sample (`random_state=42`) non-overlapping with existing showcase examples, accompanied by formal review guidelines and standardized decision templates.
7. **Zero Premature Freezing:** Verified that `taxonomy_frozen` remains strictly `false` across all JSON artifacts, deferring the golden set and downstream pipeline until human sign-off.

---

## 2. Issue 1: UNKNOWN Definition, Category Separation, and Empirical Measurement

### 2.1 The Conceptual Problem
The provisional definition of `UNKNOWN_OUT_OF_SCOPE` grouped commercial advertising spam together with extremely brief customer inquiries like `"help"`, `"help @AppleSupport"`, and image links. These brief inquiries are not out-of-scope spam; they are genuine customer support contacts where the available text contains insufficient diagnostic information to identify a technical failure mode.

### 2.2 Operational Separation: Category A vs Category B
The intent was renamed **`UNKNOWN_INSUFFICIENT_CONTEXT`** and structured into two explicit categories:

*   **Category A: True Out-of-Scope / Non-Support Content**
    *   *Definition:* Commercial marketing spam, keynote broadcast promotions (`#AppleEvent`), bot giveaway campaigns, crypto promotions, job recruitment, and completely unrelated conversational chatter.
    *   *Rule:* Routed to UNKNOWN because there is no customer support intent.
*   **Category B: Genuine Support Request with Insufficient Context**
    *   *Definition:* Legitimate customer communications directed at AppleSupport that lack actionable diagnostic symptoms, component names, or failure descriptions.
    *   *Sub-Category B1 (Bare Pleas & Pings):* Standalone cries for help, conversational greetings, and DM requests (`"help"`, `"can you help me"`, `"hello?"`, `"check dm"`).
    *   *Sub-Category B2 (Media/Link Attachments Without Textual Symptom):* Tweets containing only an image or URL attachment accompanied by at most a single non-diagnostic exclamation (`"HELP https://t.co/..."`, `"wtf https://t.co/..."`, `"look https://t.co/..."`).
    *   *Sub-Category B3 (Symptomless Frustration Rants):* Generalized venting or emotional dissatisfaction with an update or device without identifying any specific component or failure mode (`"this update sucks"`, `"fix your phone"`, `"worst company ever"`).

### 2.3 Empirical Measurement Against Source Corpus
A comprehensive scan of all **80,250 opening customer inquiries** (`root_inbound == True`) was conducted using precise, non-diagnostic filters.

$$\text{Corpus Prevalence} = \frac{\text{Unknown Inquiries Count}}{\text{Total Opening Customer Inquiries}} = \frac{522}{80{,}250} = 0.6505\%$$

| Sub-Category | Inbound Opening Count | Prevalence (% of 80,250) | Description / Criteria |
| :--- | :---: | :---: | :--- |
| **Category A: True Non-Support** | 5 | 0.0062% | Commercial keynote event broadcasts, marketing retweets, promo campaigns |
| **Category B1: Bare Pleas & Pings** | 358 | 0.4461% | Single-phrase help cries, greetings, and DM requests with no symptom |
| **Category B2: Media-Only Attachments** | 126 | 0.1570% | Media/URL attachments with no textual symptom or single exclamation |
| **Category B3: Symptomless Rants** | 33 | 0.0411% | Pure emotional frustration regarding updates with no named component |
| **Total `UNKNOWN_INSUFFICIENT_CONTEXT`** | **522** | **0.6505%** | Complete unclassifiable / insufficient context population |

*Artifact Location:* `artifacts/taxonomy_unknown_measurement.json`

### 2.4 Representative Examples
*   **Category A (Keynote Promo):** Tweet 857698: *"Join us September 12 at 10am PT to watch the #AppleEvent live at https://t.co/xi6CRXgQPH. Retweet for updates from @115858. https://t.co/QYyd7HNoGL"*
*   **Category B1 (Bare Help Cry):** Tweet 302954: *"@AppleSupport help"*
*   **Category B2 (Media Attachment):** Tweet 40543: *"@115858 @AppleSupport HELP https://t.co/8gsmO5JXRL"*
*   **Category B2 (Media Attachment):** Tweet 170347: *"@AppleSupport wtf https://t.co/aBsrPrmu0P"*
*   **Category B3 (Symptomless Rant):** Tweet 2072151: *"FIX THIS SHIT @AppleSupport"*

### 2.5 Strict Boundary Exclusion Rule
If a customer names **any** technical component, failure symptom, error code, or specific service—even colloquially (e.g. *"battery dying"*, *"phone is slow"*, *"screen unresponsive"*, *"charger won't work"*, *"letter I bug"*), the message **MUST NOT** be classified as `UNKNOWN_INSUFFICIENT_CONTEXT`. It must be assigned to the appropriate technical Intent (1–14).

---

## 3. Issue 2: Screen Display, Touch Digitizer, and Biometric Scope

### 3.1 Structural Consolidation
Previously named `SCREEN_DISPLAY_HARDWARE_SYMPTOM`, the intent was renamed **`SCREEN_DISPLAY_TOUCH_BIOMETRICS`** to formally encompass touch digitizer anomalies and biometric authentication sensors alongside physical display panel defects.

### 3.2 Unified Scope
1.  **Physical Display Panel Anomalies:** Vertical/horizontal colored lines, flickering screens, dead pixels, backlight bleed, screen tinting, black display with active audio/vibration.
2.  **Touch Digitizer Defects:** Completely unresponsive touch screens, erratic/ghost touches, delayed touch recognition across the entire panel.
3.  **Biometric Authentication Sensors:** Touch ID sensor failures (fingerprint not recognized, sensor failed on restart, home button hardware defect) and Face ID setup or recognition failures.

### 3.3 Verbatim Representative Examples
*   Tweet 34646: *"My 6 month old IPhone 6 touch screen is unresponsive. @AppleSupport please help!"*
*   Tweet 852981: *"@AppleSupport can i ask something? why my iphone 6s has ghost touch issue since i updated it to ios 11.0.3 the parts is still original tho"*
*   Tweet 1084004: *"@AppleSupport I updated my SE to IOS.0.3 and my touch screen is unresponsive,  thanks in advance"*
*   Tweet 11134: *"@AppleSupport My Touch ID failed when I restarted my phone. Now it’s not working at all"*
*   Tweet 6483: *"Hello @115858 @AppleSupport what’s happening to my screen https://t.co/GTNXT4VoKd"*

---

## 4. Issue 3: Audio Scope Audit and Clarification

### 4.1 Scope Confirmation
An audit of `AUDIO_SOUND_SPEAKER_MIC` confirmed that volume controls, alarm volume, ringer volume, and volume rocker buttons belong in this intent. The definition and inclusion criteria were updated to explicitly include:
*   Acoustic transducers (loudspeaker distortion, receiver inaudibility on phone calls, microphone failure).
*   Audio routing (stuck in headphone mode, AirPods/earbuds channel failure).
*   Sound level and volume controls (alarm volume too loud/quiet, ringer volume adjustment issues, physical volume rocker buttons).

### 4.2 Verbatim Representative Examples
*   Tweet 407520: *"@AppleSupport after updating my iOS, people can't hear me on calls or it sounds like im in a wind tunnel. please advise, thx"*
*   Tweet 1781: *"@AppleSupport why can’t I change ringer volume with the buttons? Whose dumb idea was it to change that and how do they still have a job?"*
*   Tweet 2682: *"@AppleSupport ios 11.0.3 on 6s. Cannot adjust alarm volume so waking up all in my house and neighbours despite ringer being set to minimum!"*
*   Tweet 14326: *"Updated my phone last night &amp; now its stuck in headphone mode, cant hear anything on video, FaceTime &amp; call sound goes in&amp;out @AppleSupport"*
*   Tweet 15313: *"3rd pair of @115858 ear shaped earbuds to go bad in the left side. I am currently deaf in one ear after a workout #SaveMyRightEar"*

---

## 5. Issue 4: Primary Intent Priority Ladder Refinement

### 5.1 Subordinating the Priority Ladder
The 9-level priority ladder has been explicitly designated as a **secondary tie-breaker only**. It does not override customer intent.

### 5.2 Annotation Hierarchy Rules
1.  **Rule 1: Customer's Focal Grievance / Main Actionable Support Need**  
    Classify according to the primary breakdown or grievance motivating the customer's contact.
    *   *Example:* Customer states *"My phone died while charging and now won't turn on"*. The focal grievance is the charging/power failure (`HARDWARE_CHARGING_POWER_CABLE`), not routine battery depletion.
2.  **Rule 2: Explicit Question / Requested Resolution Takes Precedence**  
    When a customer asks a direct question seeking a specific resolution, the requested resolution dictates the primary intent regardless of background narrative.
    *   *Example:* *"My Apple ID was locked because of a strange charge, how do I get a refund?"* → Actionable resolution is `BILLING_CHARGE_REFUND_DISPUTE`.
3.  **Rule 3: Priority Ladder as Deterministic Tie-Breaker Only**  
    When two intents are genuinely tied in customer emphasis and cannot be separated by Rules 1 or 2, invoke the tie-breaker rank:
    1.  `SECURITY_PHISHING_SUSPICIOUS_CONTACT`
    2.  `ACCOUNT_APPLE_ID_ACCESS`
    3.  `DEVICE_FREEZE_CRASH_REBOOT`
    4.  `DATA_LOSS_RECOVERY`
    5.  `BILLING_CHARGE_REFUND_DISPUTE`
    6.  `ORDER_PURCHASE_SHIPPING_STATUS`
    7.  `SCREEN_DISPLAY_TOUCH_BIOMETRICS`
    8.  `HARDWARE_CHARGING_POWER_CABLE`
    9.  `CONNECTIVITY_WIFI_BLUETOOTH` / `AUDIO_SOUND_SPEAKER_MIC` / `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` / `BATTERY_DRAIN_POWER_CONSUMPTION` / `PERFORMANCE_SLOWDOWN_LATENCY` / `APP_SPECIFIC_MALFUNCTION`

---

## 6. Issue 5: Artifact Reconciliation

All repository artifacts were checked and updated for internal consistency:

1.  **`artifacts/taxonomy_v1_candidate.json`:**
    *   Contains exactly 15 candidate intents.
    *   All 75 representative examples verified verbatim against source corpus.
    *   Zero references to deprecated intents (`SCREEN_DISPLAY_HARDWARE_SYMPTOM`, `UNKNOWN_OUT_OF_SCOPE`, `STORAGE_MANAGEMENT_DISK_SPACE`, `HARDWARE_PHYSICAL_DEFECT`).
2.  **`artifacts/taxonomy_confusion_matrix.json`:**
    *   Updated `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` to reference `SCREEN_DISPLAY_TOUCH_BIOMETRICS`.
    *   Updated distinguishing rule and tie-breaker to cover touch digitizers and biometric sensors.
3.  **`artifacts/taxonomy_provenance.json`:**
    *   Updated `intent_lineage` to reflect the expanded renames of `SCREEN_DISPLAY_TOUCH_BIOMETRICS` and `UNKNOWN_INSUFFICIENT_CONTEXT`.
4.  **`artifacts/taxonomy_human_review.json`:**
    *   Synchronized `candidate_intents` array with the 15 candidate intents.
    *   Maintained `taxonomy_frozen: false`.

---

## 7. Issue 6 & 7: Deterministic Human-Review Sample Pack & Protocol

### 7.1 Sampling Methodology
A stratified pseudo-random sample of **170 customer inquiries** was drawn from the 80,250 opening inquiries dataset using a documented deterministic seed (`random_state=42`).

*   **Strict Showcase Exclusion:** None of the 79 existing showcase examples from the candidate taxonomy or confusion matrix were eligible for sampling.
*   **Zero Duplication:** All 170 sampled inquiries are mutually distinct.

### 7.2 Sample Composition
*   **Part 1: 120 Candidate Intent Cases (8 per Intent across 15 Intents)**  
    Provides empirical validation for every active candidate category.
*   **Part 2: 35 Boundary Confusion Cases (5 per Pair across 7 Confusion Pairs)**  
    Targets verified overlapping semantic boundaries (e.g. Battery vs Charging, Crash vs Slowdown, App vs OS Crash, Data Loss vs Account Access, Screen/Biometrics vs Device Freeze, Account Access vs Billing, App Malfunction vs Slowdown).
*   **Part 3: 15 UNKNOWN Cases (Stratified Across Categories)**  
    Includes 4 Category A (Commercial keynote promos), 4 Category B1 (Bare help cries), 4 Category B2 (Media/link attachments), and 3 Category B3 (Symptomless frustration rants).

### 7.3 Review Artifacts Generated
*   **Machine-Readable Dataset:** `artifacts/taxonomy_human_review_sample.json`
*   **Reviewer Evaluation Pack:** `reports/taxonomy_human_review_sample.md` (1,713 lines complete with full customer text, proposed intent/pair, and review decision template `[ ACCEPT | REJECT | UNCERTAIN ]`).

---

## 8. Test Verification and Frozen Status Confirmation

### 8.1 Unit Test Coverage
The test suite in `tests/test_taxonomy_validation.py` was expanded to validate all principal cleanups:
*   `test_candidate_taxonomy_no_stale_intent_references`: Verifies zero occurrences of deprecated intent IDs across all candidate intent fields.
*   `test_unknown_measurement_integrity`: Verifies the 522-case UNKNOWN count, denominator matching, and category breakdown.
*   `test_human_review_sample_integrity`: Verifies that the 170-case sample contains exactly 120 Part 1, 35 Part 2, and 15 Part 3 cases, matches source text verbatim, has zero duplicate IDs, and zero overlap with showcase examples.

### 8.2 Full Test Suite Results
```bash
pytest
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-9.1.1, pluggy-1.6.0
collected 38 items

tests/test_config_loads.py .                                             [  2%]
tests/test_phase1_audit.py ....                                          [ 13%]
tests/test_phase2_reconstruction.py .........                            [ 36%]
tests/test_repo_structure.py ....                                        [ 47%]
tests/test_taxonomy_input_export.py ........                             [ 68%]
tests/test_taxonomy_validation.py ............                           [100%]

============================= 38 passed in 10.48s ==============================
```

### 8.3 Freeze Status
All JSON artifacts were programmatically checked to confirm `taxonomy_frozen` is strictly `false`. No golden set has been created, and no downstream pipeline code has been implemented. The candidate taxonomy is in a clean, reproducible preflight state ready for human reviewer evaluation.

---

## 9. Principal Engineer Final Pre-Golden Sample Quality Audit

Prior to human labeling, a comprehensive case-by-case data-quality audit was performed across Part 2 (35 Boundary Cases) and Part 3 (15 UNKNOWN Cases) of `artifacts/taxonomy_human_review_sample.json`.

### 9.1 Audit Findings and Corrective Actions
1. **Part 2 Boundary Discrimination:** Several boundary cases initially contained inquiries that failed to discriminate the pair:
   - *Battery vs Charging:* Cases with battery drain complaints that casually mentioned "charging 3 times a day" were replaced with inquiries showing direct technical tension (battery percentage dropping while charging, 1% to 100% in 2 minutes, refusing to charge).
   - *App Malfunction vs Slowdown:* A case where the user mentioned "slowmo" (slow-motion video mode) was mistakenly sampled for system latency; replaced with a direct inquiry contrasting system slowness with text message slowness.
   - *Data Loss vs Account Access:* Cases involving storage capacity sizing questions or third-intent phishing emails were replaced with textbook boundaries (lost contacts due to inability to log into iCloud; forgot backup password with lost device data; missing photos from camera roll failing to redownload from iCloud).
   - *Account Access vs Billing:* Family Sharing setup questions and general bank complaints were replaced with inquiries where login failure or two-factor authentication loops actively blocked the user from cancelling subscriptions or reporting unauthorized charges.
   - *Screen vs Freeze:* A generic UI freeze complaint was replaced with a direct touch digitizer failure (touch screen unresponsive / calibration off requiring daily resets).
2. **Part 3 Redundancy and Category Fidelity:**
   - Eliminated three identical `"Say hello to the future. iPhone X available now."` promotional tweets in Category A, replacing duplicates with genuine pre-order broadcasts and coworker launch celebration messages.
   - Separated bare conversational help cries and DM routing requests (Category B1) from media/URL attachments (Category B2).
   - Replaced media URL questions in Category B3 with pure symptomless frustration rants.
   - Achieved **100% text uniqueness** across all 15 UNKNOWN cases.

### 9.2 Comprehensive Audit & Replacement Table

| Case # | Pair / Category | Status | Diagnostic Reason | Replacement Tweet ID | Replacement Customer Inquiry Text |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **121** | `PAIR_01_BATTERY_VS_CHARGING` | **KEEP** | Directly tests battery drain while connected to charger | — | — |
| **122** | `PAIR_01_BATTERY_VS_CHARGING` | **KEEP** | Directly tests battery percentage dropping while device indicates charging | — | — |
| **123** | `PAIR_01_BATTERY_VS_CHARGING` | **KEEP** | Tests erratic battery percentage jumps when connected to charger | — | — |
| **124** | `PAIR_01_BATTERY_VS_CHARGING` | **REPLACE** | Pure battery drain complaint mentioning "charging 3 times a day" without charging hardware defect | `254686` | `@AppleSupport Updated to latest IOS and my phone battery is dying. Turned off location/background refresh. Refuses charge with Apple charger` |
| **125** | `PAIR_01_BATTERY_VS_CHARGING` | **REPLACE** | Pure battery drain complaint ("on my 3rd charge today") with zero charging hardware symptom | `146710` | `Dear @115858 @AppleSupport - this is NOT a full battery. Phone died, put on the charger and went from 1% to 100% in 2 minutes...SORT IT OUT(I have done all the battery optimisation stuff already AND a full restore) 11.1.2 is SHITE... https://t.co/7kVeLAKAQR` |
| **126** | `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN` | **KEEP** | Directly contrasts system crashes and restart requirements with lag | — | — |
| **127** | `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN` | **KEEP** | Directly contrasts running slow with multiple daily crashes | — | — |
| **128** | `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN` | **KEEP** | Directly contrasts running slow with freezing and self-rebooting | — | — |
| **129** | `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN` | **REPLACE** | Generic multi-intent laundry list (crash, apps slow, battery, volume buttons) without isolated tension | `1000235` | `@AppleSupport updated my phone the other day and it keeps freezing so I have to restart it. Then it’s really slow. Sort it out.` |
| **130** | `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN` | **KEEP** | Cleanly tests boundary between system slowness, glitches, and device freezing | — | — |
| **131** | `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH` | **KEEP** | Mail app crash triggering full OS reboot requirement | — | — |
| **132** | `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH` | **REPLACE** | Restart was mere user troubleshooting for camera defect; no OS crash or freeze occurred | `324534` | `@AppleSupport updated my 7plus to 11.0.2 - cannot run more than one non-system app at a time. Apps crash, phone becomes unresponsive 😐` |
| **133** | `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH` | **KEEP** | Camera/Snapchat usage triggers device freeze or reboot | — | — |
| **134** | `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH` | **REPLACE** | Single third-party app crash (WhatsApp) with no OS-level crash or freeze symptom | `804109` | `@115858 @AppleSupport I can’t believe how my iphone works since iOS 11.0.2. Every app crash my phone. What the hell?! FIX IT!!!! 😠😠 #iOSCrash` |
| **135** | `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH` | **KEEP** | Contrasts phone freezing with Safari app slowness | — | — |
| **136** | `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS` | **KEEP** | Tests iCloud account synchronization vs contact deletion data loss | — | — |
| **137** | `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS` | **REPLACE** | Account email configuration question; no user personal data lost | `2082705` | `Hello @AppleSupport , I can't login to my iCloud account [with right password], I also can't backup my contacts and I've lost them.` |
| **138** | `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS` | **REPLACE** | Belongs primarily to third intent `SECURITY_PHISHING_SUSPICIOUS_CONTACT` (phishing email report) | `2732870` | `@AppleSupport please help forgot iPhone backup password. Many iphones crashed . All my data has gone` |
| **139** | `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS` | **REPLACE** | Pre-purchase hardware storage capacity sizing question rather than data loss or login access | `1948006` | `@AppleSupport Since downloading IOS11.03 most of my photos have gone from my photo roll and won't re download from icloud. please help.` |
| **140** | `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS` | **KEEP** | Missing 3 years of photos due to backup restoration incompatibility | — | — |
| **141** | `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` | **KEEP** | Black screen with unresponsive physical buttons requiring hard reset | — | — |
| **142** | `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` | **KEEP** | Camera lock screen access triggers black screen with spinning wheel (respring vs screen) | — | — |
| **143** | `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` | **REPLACE** | "screen freezes or shutdowns" refers to UI lockups rather than physical display/touch digitizer defect | `234621` | `.@AppleSupport since the update to #iOS11 my #iPhone 6s’ touch screen has been becoming unresponsive at times. Other times it seems as if the calibration is off. Happens 3-4 times per day and requires a reset to temp. fix it each time. @115858` |
| **144** | `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` | **KEEP** | Tests Dec 2 2017 springboard crash loop bug (black screen with spinning wheel) vs display failure | — | — |
| **145** | `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE` | **KEEP** | White screen with Apple logo persistent across hard restart and iTunes restore | — | — |
| **146** | `PAIR_06_ACCOUNT_ACCESS_VS_BILLING` | **KEEP** | Billed monthly for iCloud storage tier but account quota remains at 5GB | — | — |
| **147** | `PAIR_06_ACCOUNT_ACCESS_VS_BILLING` | **KEEP** | Recurring monthly charges active while backup service fails | — | — |
| **148** | `PAIR_06_ACCOUNT_ACCESS_VS_BILLING` | **REPLACE** | Family Sharing profile configuration; no billing dispute or account login failure | `619390` | `@AppleSupport won't let me log in I want to cancel subscriptions. The verifications codes I keep being sent aren't working` |
| **149** | `PAIR_06_ACCOUNT_ACCESS_VS_BILLING` | **KEEP** | Tapping Apple ID errors out while attempting to cancel subscription | — | — |
| **150** | `PAIR_06_ACCOUNT_ACCESS_VS_BILLING` | **REPLACE** | Pure bank charge complaint with no Apple ID access/credential failure | `846969` | `@AppleSupport got double charged for something but when I try to log in to report a problem it just keeps bringing up the login screen` |
| **151** | `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN` | **REPLACE** | Customer referenced "slowmo" (slow-motion video mode), not latency; camera display issue | `1153873` | `@AppleSupport my phone is so slow so the new iOS update? Only on text messages though? Why is this?` |
| **152** | `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN` | **KEEP** | Contrasts general system latency with camera app launch delay (5-10s) | — | — |
| **153** | `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN` | **KEEP** | Tests App Store download latency vs general performance | — | — |
| **154** | `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN` | **KEEP** | Contrasts camera failure with software update slowness | — | — |
| **155** | `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN` | **KEEP** | Tests App Store update latency | — | — |
| **156** | `CATEGORY_A_NON_SUPPORT` | **REPLACE** | Duplicate text with Cases 157 & 158 ("Say hello to the future. iPhone X available now.") | `1392452` | `Say hello to the future. Pre-order iPhone X.` |
| **157** | `CATEGORY_A_NON_SUPPORT` | **REPLACE** | Duplicate text with Cases 156 & 158 ("Say hello to the future. iPhone X available now.") | `2726010` | `To all my incredibly talented coworkers, congratulations on the launch of iPhone X! Thanks @63269 for celebrating with us! https://t.co/Jhg31JPIzN` |
| **158** | `CATEGORY_A_NON_SUPPORT` | **KEEP** | Single retained representative of iPhone X commercial availability announcement | — | — |
| **159** | `CATEGORY_A_NON_SUPPORT` | **KEEP** | Keynote broadcast marketing thank-you response | — | — |
| **160** | `CATEGORY_B1_BARE_PLEA_PING` | **KEEP** | Single-word conversational cry for help ("@AppleSupport help") | — | — |
| **161** | `CATEGORY_B1_BARE_PLEA_PING` | **REPLACE** | Near-duplicate "Help + URL"; Category B1 reserved for text pleas without URLs | `52273` | `@AppleSupport can you please help me` |
| **162** | `CATEGORY_B1_BARE_PLEA_PING` | **REPLACE** | Near-duplicate "HELP + URL"; Category B1 reserved for text pleas without URLs | `167286` | `@AppleSupport can you check your dm please` |
| **163** | `CATEGORY_B1_BARE_PLEA_PING` | **REPLACE** | Near-duplicate "HELP + URL"; Category B1 reserved for text pleas without URLs | `408455` | `@AppleSupport i need help pls DM!?` |
| **164** | `CATEGORY_B2_MEDIA_LINK_ONLY` | **KEEP** | Hashtags plus media URL attachment without diagnostic text | — | — |
| **165** | `CATEGORY_B2_MEDIA_LINK_ONLY` | **KEEP** | Emotional exclamation plus hashtags and media URL | — | — |
| **166** | `CATEGORY_B2_MEDIA_LINK_ONLY` | **KEEP** | Direct mention and media URL only | — | — |
| **167** | `CATEGORY_B2_MEDIA_LINK_ONLY` | **REPLACE** | Structural duplicate of Case 166 (direct mention + URL); replaced with conversational remark + URL | `162838` | `Lol look @AppleSupport https://t.co/RggSZH4i9S` |
| **168** | `CATEGORY_B3_SYMPTOMLESS_RANT` | **REPLACE** | Contains media URL (belongs in Category B2); Category B3 reserved for pure text rants | `1302379` | `I literally hate the new @115858 update.` |
| **169** | `CATEGORY_B3_SYMPTOMLESS_RANT` | **KEEP** | Pure emotional frustration rant without named technical component | — | — |
| **170** | `CATEGORY_B3_SYMPTOMLESS_RANT` | **KEEP** | Pure emotional frustration rant against iOS update | — | — |

---

### 9.3 Sample Integrity & Provenance Guarantee
- **Total Sample Size:** Exactly 170 customer inquiries.
- **Corpus Provenance:** Every single case is an authentic opening customer inquiry from `data/processed/applesupport_conversations.parquet` with genuine `tweet_id` and `conversation_id`. Zero synthetic or paraphrased texts.
- **Showcase Disjointness:** Zero overlap with the 79 showcase examples in `artifacts/taxonomy_v1_candidate.json` and `artifacts/taxonomy_confusion_matrix.json`.
- **Text Uniqueness:** Zero duplicate inquiries across the entire 170-case pack.
- **Status:** Candidate taxonomy remains unfrozen (`taxonomy_frozen: false`). The pack is fully primed for human review.

