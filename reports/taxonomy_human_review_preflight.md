# Taxonomy V1 Human Review Preflight Report

**Document Status:** PROVISIONAL — PENDING HUMAN APPROVAL  
**Taxonomy Frozen:** `false`  
**Date:** September 11, 2026  
**Artifacts Evaluated:** `artifacts/taxonomy_v1_candidate.json`, `artifacts/taxonomy_confusion_matrix.json`, `artifacts/taxonomy_provenance.json`  
**Evaluation Corpus:** `data/processed/applesupport_conversations.parquet` (80,391 conversations) & `data/processed/applesupport_subset.parquet` (106,421 tweets)

---

## 1. UNKNOWN Boundary Analysis: Out-of-Scope vs. Insufficient Information vs. Vague Complaints

### Problem Statement
The original specification for `UNKNOWN_OUT_OF_SCOPE` defined the category around marketing spam, bot advertising, cryptocurrency promotions, gibberish strings, or completely unrelated commentary. However, in the real AppleSupport dataset (where messages are directed to `@AppleSupport` and received brand responses), genuine commercial spam is nearly non-existent (<0.05%). 

Instead, the unclassifiable tail consists overwhelmingly of:
1. **Short, bare pleas for help** containing zero diagnostic context.
2. **Screenshots with no accompanying text description**.
3. **Frustrated emotional rants** that complain about an update without naming any specific hardware or software symptom.

Conflating genuine support pleas (e.g. `"@AppleSupport help"`) with commercial bot spam obscures operational reality: in production support triage, a customer crying "help" is a valid customer requiring an intake clarifying question (*"What issue are you experiencing?"*), whereas bot spam is dropped or filtered out.

### Precise Tripartite Boundary Rule

To establish operational clarity without destabilizing the candidate taxonomy structure, we establish three distinct partitions:

```
                                    INCOMING MESSAGE
                                           │
                    Is it directed at support / seeking assistance?
                                    ┌──────┴──────┐
                                   YES            NO ──> [A. TRUE OUT-OF-SCOPE / NON-SUPPORT]
                                    │
              Does it contain actionable diagnostic symptom information?
                                    ┌──────┴──────┐
                                   YES            NO ──> [B. INSUFFICIENT CONTEXT / UNKNOWN]
                                    │
                      [C. SPECIFIC INTENT / COMPLAINT]
                      (Classify to Intents 1–14 via Stage G rules)
```

#### Category A: True Out-of-Scope / Non-Support
- **Definition:** Content that does not represent a customer seeking Apple customer service. Includes marketing promotions, keynote broadcast announcements, bot retweets, non-English social commentary without technical context, and random conversational pleasantries.
- **Action:** Route to `UNKNOWN_INSUFFICIENT_CONTEXT` (Triage code: `NON_SUPPORT`).
- **Real Source Examples:**
  - **Tweet 857698:** *"Join us September 12 at 10am PT to watch the #AppleEvent live at https://t.co/xi6CRXgQPH. Retweet for updates from @115858. https://t.co/QYyd7HNoGL"* (Event marketing retweet)
  - **Tweet 188142:** *"Chateada com a @115858"* (Non-English generic venting without inquiry)
  - **Tweet 187664:** *"Quick rant"* (Preamble with no actual content)

#### Category B: Genuine Support Request with Insufficient Information
- **Definition:** The user explicitly seeks assistance from `@AppleSupport`, but provides no diagnostic symptom, hardware component, error code, or application name in the text. This includes bare help cries, unelaborated image attachments, and conversational opening greetings.
- **Action:** Route to `UNKNOWN_INSUFFICIENT_CONTEXT` (Triage code: `INSUFFICIENT_CONTEXT`). In production, triggers an automated intake clarification prompt.
- **Real Source Examples:**
  - **Tweet 302954:** *"@AppleSupport help"* (Customer opens thread with a bare plea; no symptom provided)
  - **Tweet 331384:** *"@AppleSupport I need help"* (Direct plea for help; zero symptom context)
  - **Tweet 39677:** *"@AppleSupport hello?"* (Ping to check if agent is listening)
  - **Tweet 87205:** *"@AppleSupport Please"* (Single-word plea)
  - **Tweet 40543:** *"@115858 @AppleSupport HELP https://t.co/8gsmO5JXRL"* (Cry for help pointing to an external image link with no textual explanation)

#### Category C: Vague Customer Complaint with Assignable Intent
- **Definition:** A frustrated, venting, or informal customer complaint that nevertheless identifies a specific hardware component, system behavior, or failure mode. Even if phrased colloquially, aggressively, or tersely, the presence of a named diagnostic symptom assigns it to Intents 1–14.
- **Action:** Classify directly into the appropriate diagnostic intent.
- **Real Source Examples:**
  - **Tweet 1761:** *"iOS 11 is killing my battery @115858. Fix it."* → Frustrated rant, but names battery drain → `BATTERY_DRAIN_POWER_CONSUMPTION`.
  - **Tweet 50068:** *"@115858 fix this I️"* → Terse demand, but names the letter 'I' glitch → `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`.
  - **Tweet 352636:** *"@115858 my charger broke"* → Terse complaint, but names charger failure → `HARDWARE_CHARGING_POWER_CABLE`.
  - **Tweet 294357:** *"@115858 this update blows"* → Pure emotional vent with *no symptom* named → Category B (`UNKNOWN_INSUFFICIENT_CONTEXT`).

### Recommendation for Intent 15
Rename the human-readable display of Intent 15 to **`UNKNOWN_INSUFFICIENT_CONTEXT`** (Unknown, Insufficient Context, or Out of Scope), while retaining the schema ID `UNKNOWN_OUT_OF_SCOPE` or migrating to `UNKNOWN_INSUFFICIENT_CONTEXT` upon human freeze approval. Expand its formal definition to encompass both non-support content and genuine support inquiries lacking diagnostic context.

---

## 2. AUDIO Boundary Analysis: Hardware Transducers vs. Volume Controls & Settings

### Problem Statement
In `artifacts/taxonomy_v1_candidate.json`, `AUDIO_SOUND_SPEAKER_MIC` contains examples covering microphone distortion, receiver inaudibility, headphone jack mode, and earbud failures, as well as ringer and alarm volume adjustment issues (e.g. Tweets 1781 and 2682). We evaluated whether complaints about volume buttons and alarm/ringer settings should be retained in `AUDIO_SOUND_SPEAKER_MIC` or moved elsewhere.

### Corpus Findings
In the real AppleSupport dataset following the release of iOS 11:
- Apple altered the default behavior of physical volume buttons (`Settings > Sounds & Haptics > Change with Buttons`), causing customer confusion when physical buttons changed media volume instead of ringer/alert volume.
- Multiple customer inquiries specifically link physical buttons, alarm volumes, and audio output:
  - **Tweet 1781:** *"@AppleSupport why can’t I change ringer volume with the buttons? Whose dumb idea was it to change that and how do they still have a job?"*
  - **Tweet 2682:** *"@AppleSupport ios 11.0.3 on 6s. Cannot adjust alarm volume so waking up all in my house and neighbours despite ringer being set to minimum!"*
  - **Tweet 247630:** *"@AppleSupport The volume button does not control ringer volume after update on IPhone6S. Is this being looked at?"*
  - **Tweet 336591:** *"@AppleSupport So every time I try to turn down my ringer with the buttons on the side it only works for the volume and not the ringer volume"*
  - **Tweet 842455:** *"@AppleSupport iOS 11.0.3 on SE causing regular crashes and audio problems (can't adjust volume/hear incoming calls)"*

### Architectural Evaluation
1. **Diagnostic Unity:** When a customer complains that *"alarm volume is too loud"*, *"ringer volume is stuck"*, or *"I can't hear sound"*, technical support agents follow the exact same diagnostic decision tree: check the physical Silent/Ring switch, test audio playback sliders in `Settings > Sounds`, inspect the speaker mesh for physical obstruction, and verify audio routing.
2. **Avoid Fragmentation:** Creating a separate "Volume Settings" intent would introduce an artificial, low-prevalence category (<0.3% volume) that would constantly confuse annotators whenever a user says *"cannot hear incoming ringtone"*.
3. **Button Hardware vs. Audio Subsystem:** The physical volume buttons on an iPhone exist exclusively to manipulate the audio subsystem. Routing volume button complaints to audio is consistent with routing the power button to device boot/power.

### Decision
**Volume controls, alarm/ringer volume levels, and physical volume rocker button issues are intentionally and formally included in `AUDIO_SOUND_SPEAKER_MIC`.**

### Formal Definition & Criteria Expansion
- **Definition:** Customer reports physical speaker distortion, receiver inaudibility on calls, microphone transducer failure, headphone jack/mode anomalies, earbud hardware defects, or volume control/settings anomalies (alarm volume, ringer volume, physical volume buttons).
- **Inclusion Criteria:** Mentions speaker, receiver, microphone, mic, sound, AirPods audio, distorted audio, caller cannot hear me, ringer volume, alarm volume, volume buttons, or sound too quiet/loud.
- **Exclusion Criteria:** Bluetooth radio failing to pair or connect generally (classify as `CONNECTIVITY_WIFI_BLUETOOTH`); system-wide iOS freezing during media playback (classify as `DEVICE_FREEZE_CRASH_REBOOT`).

---

## 3. APP_SPECIFIC vs. PERFORMANCE vs. DEVICE_FREEZE Boundary Analysis

### Tripartite Boundary Architecture

To eliminate ambiguity between localized application defects, system-wide performance degradation, and catastrophic operating system crashes, we formulate a strict three-tier boundary rule:

```
                                  SYMPTOM SCOPE
                                        │
           Is the issue confined to ONE single named application?
                                 ┌──────┴──────┐
                                YES            NO
                                 │              │
                    [APP_SPECIFIC_MALFUNCTION]  │
                                                ▼
                                    SEVERITY OF SYSTEM IMPACT
                                                │
                 Does the device suffer total lockup, crash, or reboot?
                                 ┌──────┴──────┐
                                YES            NO
                                 │              │
                   [DEVICE_FREEZE_CRASH_REBOOT] [PERFORMANCE_SLOWDOWN_LATENCY]
```

### Boundary Definitions & Verbatim Source Evidence

#### 1. APP_SPECIFIC_MALFUNCTION
- **Rule:** A named application (Safari, App Store, Spotify, Mail, YouTube, Camera, WhatsApp) is crashing, failing to launch, refusing to download assets, or exhibiting broken internal features, **while the rest of the iOS operating system and other applications continue to function normally**.
- **Real Verbatim Source Examples:**
  - **Tweet 520207:** *"@AppleSupport Safari keeps crashing over and over today. I deleted ~/Library/Safari to start anew, but the problem persists -  sigh"* (Safari app repeatedly crashing; OS remains running)
  - **Tweet 546608:** *"@AppleSupport Help needed Safari keeps crashing on my MacBook ? It’s annoying ! Any help appreciated"* (Isolated application crash on Safari)
  - **Tweet 400396:** *"Anybody else having issues with iPhone ios11.0.2? App Store won't download &amp; won’t update any apps! @115858 @118936 @AppleSupport #appstore"* (App Store application failure to update/download)

#### 2. PERFORMANCE_SLOWDOWN_LATENCY
- **Rule:** The entire device, home screen, navigation, or general multitasking feels sluggish, unresponsive, or delayed. Frame rates drop, animations stutter, apps take longer to open, and typing exhibits latency, **but the device does not freeze solid, black-screen, or restart**.
- **Real Verbatim Source Examples:**
  - **Tweet 481805:** *"My phone is running so slow after I updated it....@115858 wanna explain?"* (General device slowdown following update)
  - **Tweet 157814:** *"@115858 my phone is so slow after updating wtf!? Unbearable to use 😩😩😩😩"* (General sluggishness rendering phone frustrating to use)
  - **Tweet 253468:** *"@AppleSupport hi, ever since i installed the new software and my phone is so slow and laggy. Please advise"* (System-wide lag and latency)

#### 3. DEVICE_FREEZE_CRASH_REBOOT
- **Rule:** The device undergoes a catastrophic or binary failure: the entire operating system locks up completely (touch and hardware buttons stop responding), the screen turns black with a spinning gear, the phone reboots spontaneously, or it gets stuck in an Apple logo boot loop. **Even if an application initially triggered the freeze, if the entire operating system crashes or requires a forced hard reboot, classify as `DEVICE_FREEZE_CRASH_REBOOT`.**
- **Real Verbatim Source Examples:**
  - **Tweet 50615:** *"@115858 @AppleSupport y’all really bout to piss me off with this dumbass update. My phone keeps crashing and shutting off"* (System-wide crashing and spontaneous power-off)
  - **Tweet 188591:** *"@AppleSupport iOS 11.0.1 constantly freezes my phone, home screen and several apps. It’s a terrible terrible version!"* (Total system freeze locking the home screen and device)
  - **Tweet 336214:** *"Ugh @AppleSupport !  iOS 11 is horrible and forces me to shut down my phone every 5 min because it freezes my phone!"* (System freeze forcing repeated manual shutdowns)

---

## 4. SCREEN / BIOMETRIC Boundary Analysis

### Problem Statement
The definition of `SCREEN_DISPLAY_HARDWARE_SYMPTOM` in candidate v1 currently includes Touch ID and Face ID, whereas the intent title focuses strictly on "Screen Display and Touch Sensor". We analyzed whether grouping biometric sensors with display/touch is semantically coherent or whether they should be separated.

### Corpus Prevalence Analysis
Running queries across all 80,391 AppleSupport conversations:
- **Touch ID mentions:** 203 inquiries (0.25% of corpus)
- **Face ID mentions:** 158 inquiries (0.20% of corpus)
- **Combined Biometrics Total:** 361 inquiries (**0.45%** of corpus)

### Semantic & Technical Evaluation
1. **Front-Panel Sensor Architecture:** In Apple hardware, Touch ID was integrated directly into the capacitive glass surface of the Home button (iPhone 5s–8/8 Plus), and Face ID relies on the TrueDepth infrared sensor array located within the screen display notch (iPhone X). Both represent the physical biometric authentication sensors embedded in the front display assembly.
2. **Alternative Options Considered:**
   - *Option A: Broaden to include Biometrics in Title and Definition (`SCREEN_DISPLAY_TOUCH_BIOMETRICS`).* Maintains operational cohesion, gives biometric sensor failures a clear home, and requires zero artificial intent proliferation.
   - *Option B: Remove Biometrics from the Intent.* If removed, Touch ID / Face ID hardware failures would have no home. Placing them in `ACCOUNT_APPLE_ID_ACCESS` would be technically invalid (Apple ID is cloud identity, passwords, and 2FA; Touch ID sensor failure is a local hardware sensor defect). Placing them in `UNKNOWN` would misclassify genuine hardware defects as out-of-scope.
   - *Option C: Create a dedicated `BIOMETRIC_FACE_TOUCH_ID` Intent.* Violates the minimum empirical volume threshold (0.45% < 1.0%), creating an underpopulated bucket that harms classifier stability.

### Decision
**Option A is selected:** Broaden the intent name, definition, and inclusion criteria to formally encompass front-panel biometric sensors alongside screen display and touch digitizers.

- **Proposed Intent Name:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` (Human Readable: *Screen Display, Touch Digitizer, and Biometrics*).
- **Expanded Definition:** Customer reports physical or graphical screen anomalies (dead pixels, vertical colored lines, screen flickering, black screen), touch digitizer unresponsiveness (ghost touch, unresponsive glass), or front-panel biometric sensor malfunctions (Touch ID failure, Face ID failure).
- **Real Verbatim Source Examples:**
  - **Tweet 34646:** *"My 6 month old IPhone 6 touch screen is unresponsive. @AppleSupport please help!"* (Touch digitizer)
  - **Tweet 852981:** *"@AppleSupport can i ask something? why my iphone 6s has ghost touch issue since i updated it to ios 11.0.3 the parts is still original tho"* (Ghost touch digitizer)
  - **Tweet 11134:** *"@AppleSupport My Touch ID failed when I restarted my phone. Now it’s not working at all"* (Touch ID biometric failure)
  - **Tweet 84161:** *"I just took a shower and my Face ID stopped working, wtf @115858"* (Face ID biometric failure)
  - **Tweet 6483:** *"Hello @115858 @AppleSupport what’s happening to my screen https://t.co/GTNXT4VoKd"* (Display panel graphical glitch)

---

## 5. Multi-Symptom Annotation Policy: Focal Grievance First with Priority Ladder as Tie-Breaker

### Problem Statement & Guiding Principle
In social customer support, users frequently express frustration by listing multiple concurrent issues or symptoms in a single post (e.g. Tweet 37652: *"Thanks @115858 for making my iPhone 6+ slow, sluggish non stop crashing, unresponsive &amp; battery life shot to pieces since new iPhone &amp; update"*).

To guarantee high inter-annotator agreement and consistent benchmark evaluation while respecting genuine user intent, the Golden Set requires an unambiguous, deterministic **Single-Label Primary-Intent Rule**.

**Core Mandate:**
> **Primary intent is determined by customer focal grievance / actionable need first; the priority ladder is a deterministic tie-breaker only.**

The priority ladder is **not** an absolute semantic severity override that replaces customer intent. A customer's primary intent must be determined through a structured 3-step evaluation protocol:

1. **Main Actionable Need / Focal Grievance:** Identify the primary symptom, failure mode, or grievance that drove the customer to reach out.
2. **Explicit Question or Requested Resolution:** If the customer explicitly asks a question or demands a specific action (e.g., *"How do I get a refund?"*, *"How do I recover my contacts?"*, *"Can you fix my charging port?"*), that explicit request defines the primary intent, regardless of secondary symptoms mentioned in passing.
3. **Deterministic Tie-Breaker Only:** Only when two or more intents remain genuinely tied in prominence, severity, or explicit demand (such as in undifferentiated compound laundry-list vents), apply the deterministic **Priority Ladder with UNKNOWN as fallback** to break the tie.

---

### Priority Ladder with UNKNOWN as Fallback (Deterministic Tie-Breaker)

This ladder is invoked strictly as a tie-breaker when Step 1 and Step 2 do not yield a single dominant focal grievance:

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: CRITICAL SECURITY & ACCOUNT COMPROMISE                             │
│   • SECURITY_PHISHING_SUSPICIOUS_CONTACT (Phishing, scam SMS, malware)      │
│   • ACCOUNT_APPLE_ID_ACCESS (Account locked out, 2FA code blocked)          │
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 2: FINANCIAL & TRANSACTIONAL BLOCKERS                                │
│   • BILLING_CHARGE_REFUND_DISPUTE (Unauthorized charge, refund dispute)     │
│   • ORDER_PURCHASE_SHIPPING_STATUS (Order delivery delay, cancellation)    │
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 3: CATASTROPHIC DEVICE INOPERABILITY (DEVICE DOWN)                   │
│   • DEVICE_FREEZE_CRASH_REBOOT (Stuck on boot loop, black screen, rebooting)│
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 4: PHYSICAL INTERFACE & POWER HARDWARE BLOCKERS                      │
│   • SCREEN_DISPLAY_TOUCH_BIOMETRICS (Unresponsive touch screen, Face ID)    │
│   • HARDWARE_CHARGING_POWER_CABLE (Phone won't charge, broken port/cable)   │
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 5: PERMANENT DATA LOSS                                               │
│   • DATA_LOSS_RECOVERY (Deleted contacts, missing photos, lost notes)       │
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 6: CORE COMMUNICATION SUBSYSTEM FAILURE                              │
│   • CONNECTIVITY_WIFI_BLUETOOTH (No service, Wi-Fi greyed out, AirDrop)    │
│   • AUDIO_SOUND_SPEAKER_MIC (Caller cannot hear me, microphone dead)       │
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 7: LOCALIZED APP & INPUT ANOMALIES                                   │
│   • APP_SPECIFIC_MALFUNCTION (Specific app crashing/failing)               │
│   • KEYBOARD_TYPING_AUTOCORRECT_ISSUE (Letter 'I' glitch, typing lag)       │
├────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 8: PERFORMANCE & POWER DEGRADATION (NON-BLOCKING)                    │
│   • BATTERY_DRAIN_POWER_CONSUMPTION (Battery drains fast but phone works)   │
│   • PERFORMANCE_SLOWDOWN_LATENCY (Device is sluggish/laggy)                 │
├────────────────────────────────────────────────────────────────────────────┤
│ FALLBACK: INSUFFICIENT CONTEXT / UNKNOWN                                   │
│   • UNKNOWN_INSUFFICIENT_CONTEXT (Bare help, rants without symptom)         │
└────────────────────────────────────────────────────────────────────────────┘
```

### Case Studies: Focal Grievance vs. Tie-Breaker Ladder

| Customer Inquiry Text | Evaluation Step 1: Focal Grievance / Actionable Need | Evaluation Step 2: Explicit Resolution / Question | Evaluation Step 3: Ladder Invoked? | Assigned Primary Intent |
|:---|:---|:---|:---:|:---|
| *"My Apple ID is locked and I can't log in"* | Focal issue is standard account lockout. | None; statement of account access lockout. | No | `ACCOUNT_APPLE_ID_ACCESS` |
| *"Someone compromised my Apple ID and I cannot log in"* | Focal issue is unauthorized security breach / fraudulent takeover. | Security compromise is the focal grievance. | No | `SECURITY_PHISHING_SUSPICIOUS_CONTACT` |
| *"I was charged twice and want a refund"* | Financial billing error and refund demand. | Explicit demand: *"want a refund"*. | No | `BILLING_CHARGE_REFUND_DISPUTE` |
| *"My phone won't charge"* | Direct physical power intake failure. | Statement of charging hardware failure. | No | `HARDWARE_CHARGING_POWER_CABLE` |
| *"My phone won't charge and I lost all my photos, please tell me how to get my pictures back"* | Two symptoms mentioned, but customer explicitly requests data recovery: *"please tell me how to get my pictures back"*. | Explicit resolution demanded: photo recovery. | No | `DATA_LOSS_RECOVERY` |
| *"My phone won't charge and I lost all my photos"* (neither symptom elaborated or requested) | Customer lists two unelaborated hardware and data issues without an explicit focal question. | None; equal co-occurring grievances. | **Yes** (Tied: Level 4 Hardware Charging vs Level 5 Data Loss) | `HARDWARE_CHARGING_POWER_CABLE` (Level 4 > Level 5) |
| *"battery dying, phone freezing, and screen unresponsive"* (Tweet 37652) | Equal laundry list of 3 post-update symptoms in a general vent. | None; undifferentiated list. | **Yes** (Tied: Level 3 Freeze vs Level 4 Screen vs Level 8 Battery) | `DEVICE_FREEZE_CRASH_REBOOT` (Level 3 > Level 4 > Level 8) |
| *"Battery is worse than ever, touch is slow/not responsive"* (Tweet 362478) | Equal pair of unelaborated symptoms. | None. | **Yes** (Tied: Level 4 Touch vs Level 8 Battery) | `SCREEN_DISPLAY_TOUCH_BIOMETRICS` (Level 4 > Level 8) |
| *"My phone is running so slow and battery dies in 2 hours"* | Degraded user experience (both Level 8). | None. | **Yes** (Intra-Level 8 Tie-Breaker: Battery Drain > Latency) | `BATTERY_DRAIN_POWER_CONSUMPTION` |

### Multi-Label Annotation Recommendation
While the benchmark evaluation metric for the Golden Set will evaluate **Single-Label Primary Accuracy** against this deterministic ladder, we recommend that the annotation schema support an optional secondary field:
- `primary_intent` (Mandatory, string): Exactly one intent selected via the Priority Ladder.
- `secondary_intents` (Optional, array of strings): Any additional distinct symptoms explicitly mentioned in the text.

This approach delivers a crisp, reproducible single-label ground truth for trust gating while retaining rich diagnostic metadata for multi-intent evaluation.

---

## 6. Taxonomy-Level Changes Proposed for Human Approval

The following four targeted modifications are prepared for human approval:

1. **Intent 8 Name & Scope Broadening:**
   - Current ID: `SCREEN_DISPLAY_HARDWARE_SYMPTOM`
   - Proposed ID: `SCREEN_DISPLAY_TOUCH_BIOMETRICS`
   - Human Readable Name: *Screen Display, Touch Digitizer, and Biometrics*
   - Explicitly covers LCD/OLED anomalies, digitizer failure, Touch ID, and Face ID.
2. **Intent 10 Definition & Inclusion Expansion:**
   - Retain ID: `AUDIO_SOUND_SPEAKER_MIC`
   - Formally expand definition and inclusion criteria to include physical volume buttons, alarm volume adjustment, and ringer volume decoupling.
3. **Intent 15 Redefinition & Renaming:**
   - Current ID: `UNKNOWN_OUT_OF_SCOPE`
   - Proposed ID: `UNKNOWN_INSUFFICIENT_CONTEXT`
   - Human Readable Name: *Unknown, Insufficient Context, or Out of Scope*
   - Redefined to cover non-support content (Category A) and genuine support requests lacking diagnostic context (Category B).
4. **Formalization of the Focal Grievance First Rule with Priority Ladder as Tie-Breaker:**
   - Documented as the authoritative annotation protocol for the Golden Set.

---

## 7. Real Source Examples Supporting Decisions

Every tweet cited in this report is verified against `data/processed/applesupport_conversations.parquet` and `data/processed/applesupport_subset.parquet`:

| Tweet ID | Conversation ID | Inbound | Author ID | Verbatim Source Text |
|:---:|:---:|:---:|:---:|:---|
| **1781** | 1781 | True | 116104 | *"@AppleSupport why can’t I change ringer volume with the buttons? Whose dumb idea was it to change that and how do they still have a job?"* |
| **2682** | 2682 | True | 116351 | *"@AppleSupport ios 11.0.3 on 6s. Cannot adjust alarm volume so waking up all in my house and neighbours despite ringer being set to minimum!"* |
| **6483** | 6483 | True | 117151 | *"Hello @115858 @AppleSupport what’s happening to my screen https://t.co/GTNXT4VoKd"* |
| **11134** | 11134 | True | 118105 | *"@AppleSupport My Touch ID failed when I restarted my phone. Now it’s not working at all"* |
| **34646** | 34646 | True | 123511 | *"My 6 month old IPhone 6 touch screen is unresponsive. @AppleSupport please help!"* |
| **37652** | 37652 | True | 124237 | *"Thanks @115858 for making my iPhone 6+ slow, sluggish non stop crashing, unresponsive &amp; battery life shot to pieces since new iPhone &amp; update"* |
| **39677** | 39677 | True | 124696 | *"@AppleSupport hello?"* |
| **40543** | 40543 | True | 124898 | *"@115858 @AppleSupport HELP https://t.co/8gsmO5JXRL"* |
| **50615** | 50615 | True | 127357 | *"@115858 @AppleSupport y’all really bout to piss me off with this dumbass update. My phone keeps crashing and shutting off"* |
| **84161** | 84161 | True | 134677 | *"I just took a shower and my Face ID stopped working, wtf @115858"* |
| **87205** | 87205 | True | 135314 | *"@AppleSupport Please"* |
| **157814** | 157814 | True | 152179 | *"@115858 my phone is so slow after updating wtf!? Unbearable to use 😩😩😩😩"* |
| **188591** | 188591 | True | 160088 | *"@AppleSupport iOS 11.0.1 constantly freezes my phone, home screen and several apps. It’s a terrible terrible version!"* |
| **253468** | 253468 | True | 176162 | *"@AppleSupport hi, ever since i installed the new software and my phone is so slow and laggy. Please advise"* |
| **302954** | 302954 | True | 188303 | *"@AppleSupport help"* |
| **331384** | 331384 | True | 194723 | *"@AppleSupport I need help"* |
| **336214** | 336214 | True | 195726 | *"Ugh @AppleSupport !  iOS 11 is horrible and forces me to shut down my phone every 5 min because it freezes my phone!"* |
| **362478** | 362478 | True | 202111 | *"@AppleSupport IOS11 has completely messed up my iPhone 7. Battery is worse than ever, touch is slow/not responsive. Sort it out ffs"* |
| **400396** | 400396 | True | 210683 | *"Anybody else having issues with iPhone ios11.0.2? App Store won't download &amp; won’t update any apps! @115858 @118936 @AppleSupport #appstore"* |
| **436485** | 436485 | True | 219077 | *"@AppleSupport  iPhone 6 freezing &amp; on  calls screen black and have to reboot &amp; real bad battery life ,"* |
| **481805** | 481805 | True | 229519 | *"My phone is running so slow after I updated it....@115858 wanna explain?"* |
| **520207** | 520207 | True | 240062 | *"@AppleSupport Safari keeps crashing over and over today. I deleted ~/Library/Safari to start anew, but the problem persists -  sigh"* |
| **546608** | 546608 | True | 247108 | *"@AppleSupport Help needed Safari keeps crashing on my MacBook ? It’s annoying ! Any help appreciated"* |
| **627932** | 627932 | True | 269096 | *"@applesupport  ios 11.1.1 issues—battery life drastically reduced, apps freeze, touch id no longer works.  Where’s the fix?  You’ve turned into Microsoft."* |
| **852981** | 852981 | True | 322625 | *"@AppleSupport can i ask something? why my iphone 6s has ghost touch issue since i updated it to ios 11.0.3 the parts is still original tho"* |
| **857698** | 857698 | True | 323719 | *"Join us September 12 at 10am PT to watch the #AppleEvent live at https://t.co/xi6CRXgQPH. Retweet for updates from @115858. https://t.co/QYyd7HNoGL"* |

---

## 8. Remaining Ambiguities for Human Sign-Off

1. **System Autocorrect in Third-Party vs. First-Party Apps:**
   - In iOS 11, the famous letter 'I' predictive text / autocorrect glitch manifested when typing inside any app (Mail, Messages, Twitter, Notes).
   - *Rule:* The priority hierarchy treats this as an OS-level keyboard defect (`KEYBOARD_TYPING_AUTOCORRECT_ISSUE`), even if the user names the app (e.g. *"Mail app changes I to A"*). Human reviewer must confirm this override.
2. **First-Party App Crashes Triggered by Cloud Sync vs. App Bug:**
   - E.g., Apple Music failing to load tracks because of an expired trial or subscription issue.
   - *Rule:* If the core complaint is being prompted to purchase or billing renewal, classify as `BILLING_CHARGE_REFUND_DISPUTE`. If the app crashes or throws a technical error code, classify as `APP_SPECIFIC_MALFUNCTION`.
3. **Formal Freeze Confirmation:**
   - `artifacts/taxonomy_v1_candidate.json` and `artifacts/taxonomy_human_review.json` maintain `taxonomy_frozen: false`.
   - Freezing requires explicit human sign-off on the proposed ID adjustments (`SCREEN_DISPLAY_TOUCH_BIOMETRICS` and `UNKNOWN_INSUFFICIENT_CONTEXT`).

---

## 9. Automated Verification Test Suite

All 35 existing automated tests in the repository pass with zero errors:
```
tests/test_config_loads.py .                                             [  2%]
tests/test_phase1_audit.py ....                                          [ 14%]
tests/test_phase2_reconstruction.py .........                            [ 40%]
tests/test_repo_structure.py ....                                        [ 51%]
tests/test_taxonomy_input_export.py ........                             [ 74%]
tests/test_taxonomy_validation.py .........                              [100%]
============================= 35 passed in 10.38s ==============================
```
