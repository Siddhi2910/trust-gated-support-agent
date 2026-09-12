# Candidate Taxonomy Human Review Sample Pack (170 Real Inquiries)

**Artifact Version:** `1.0.0-candidate`  
**Sampling Strategy:** Stratified deterministic pseudo-random sampling (`random_state=42`)  
**Source Corpus:** `data/processed/applesupport_conversations.parquet` (80,250 inbound opening inquiries)  
**Exclusion Filter:** All 79 showcase examples from `taxonomy_v1_candidate.json` and `taxonomy_confusion_matrix.json` strictly excluded  
**Taxonomy Frozen Status:** `false` (Pending human sign-off)  

---

## Human Review Protocol and Annotation Instructions

### 1. The Focal Grievance / Actionable Need Rule
Assign the customer inquiry to the intent representing the **customer’s main actionable support grievance or explicit request**.
- **Explicit Question First:** If the customer asks a direct, actionable question (e.g. *"How do I get a refund for this app?"* vs *"This app crashed and charged me"*), the requested resolution (`BILLING_CHARGE_REFUND_DISPUTE`) governs over background incident context.
- **Underlying Cause vs Symptom:** If a customer complains of battery drain after updating to iOS 11, the actionable symptom is `BATTERY_DRAIN_POWER_CONSUMPTION`, not an OS crash.
- **Security Precedence:** If account compromise or fraud is the focal grievance (*"Someone hacked my Apple ID and locked me out"*), classify as `SECURITY_PHISHING_SUSPICIOUS_CONTACT`. If routine password reset or device lock, classify as `ACCOUNT_APPLE_ID_ACCESS`.

### 2. The Deterministic Tie-Breaker Ladder (Secondary Use Only)
The 9-level priority ladder is **NOT** an automatic semantic severity override. It must **ONLY** be invoked when two candidate intents remain genuinely tied in customer emphasis:
1. `SECURITY_PHISHING_SUSPICIOUS_CONTACT`
2. `ACCOUNT_APPLE_ID_ACCESS`
3. `DEVICE_FREEZE_CRASH_REBOOT`
4. `DATA_LOSS_RECOVERY`
5. `BILLING_CHARGE_REFUND_DISPUTE`
6. `ORDER_PURCHASE_SHIPPING_STATUS`
7. `SCREEN_DISPLAY_TOUCH_BIOMETRICS`
8. `HARDWARE_CHARGING_POWER_CABLE`
9. `CONNECTIVITY_WIFI_BLUETOOTH` / `AUDIO_SOUND_SPEAKER_MIC` / `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` / `BATTERY_DRAIN_POWER_CONSUMPTION` / `PERFORMANCE_SLOWDOWN_LATENCY` / `APP_SPECIFIC_MALFUNCTION`

### 3. Special Boundary & Intent Definitions
- **`SCREEN_DISPLAY_TOUCH_BIOMETRICS`:** Encompasses all physical display glass/panel defects (lines, flicker, dead pixels, black display with audio active), touch digitizer anomalies (unresponsive touch, ghost touches), and biometric sensors (Face ID setup/failure, Touch ID sensor failure).
- **`AUDIO_SOUND_SPEAKER_MIC`:** Formally encompasses speaker distortion, receiver crackling, microphone failure, headphone jack/AirPods audio routing, volume controls, alarm/ringer volume levels, and physical volume rocker button failure.
- **`UNKNOWN_INSUFFICIENT_CONTEXT`:** Strictly reserved for:
  - **Category A (Non-Support / Commercial Promo):** Marketing retweets, spam, advertising, keynote event broadcasts.
  - **Category B (Insufficient Context):** Bare pleas for help (*"Help please"*, *"DM me"*), media/URL attachments with no textual diagnostic symptom, or symptomless emotional frustration rants (*"iOS 11 sucks fix your shit"*).
  - **Negative Constraint:** If *any* technical component, hardware symptom, error code, or specific service is named (even colloquially), DO NOT classify as UNKNOWN.

### 4. Review Decision Options
For each case below, mark your assessment:
- `[ ACCEPT ]`: Proposed candidate intent correctly captures customer focal grievance.
- `[ REJECT ]`: Proposed candidate intent is incorrect; specify the `Corrected Intent`.
- `[ UNCERTAIN ]`: Borderline ambiguity requiring committee discussion; provide notes.

---

## Part 1: Candidate Intent Cases (120 Inquiries: 8 per Intent x 15 Intents)

### Intent: `BATTERY_DRAIN_POWER_CONSUMPTION`

#### Case 001 | Tweet ID: `2193292` | Conv ID: `2193292`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "Hey @115858 while your fixing all the other bugs, can you fix my battery so it doesn’t die every 10 minutes !!!!!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 002 | Tweet ID: `2193337` | Conv ID: `2193337`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "@AppleSupport I’ve done 2 hard resets and update the software. I can’t go anywhere without an extra battery but even that can’t reboot"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 003 | Tweet ID: `1060519` | Conv ID: `1060519`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "@AppleSupport since installing iOS 11.0.3 on 5s work phone, battery has gone from 2.5 days to 1.5. Background refresh is off. Any ideas? https://t.co/5kXkYPWNK5"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 004 | Tweet ID: `40474` | Conv ID: `40474`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "@AppleSupport My battery is draining quickly on my iPhone 6s when I use 3G. I lose like 5% a minute. But it’s better when I use my WiFi."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 005 | Tweet ID: `1011847` | Conv ID: `1011847`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "Pourquoi mon iPhone 7 est si lent ?

Hey @AppleSupport why is my iPhone 7 so slow ? And battery draining quite fast."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 006 | Tweet ID: `90649` | Conv ID: `90649`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "Hey @AppleSupport @115858 can you let me know why my iPhone 6 (normally fit&amp;well, no previous issues) suddenly has battery issues, mic doesn't work, so can't make calls...I won't be upgrading if that's what you want 😂 but I've paid for the phone now so... solve this pls?😃🙌🏽"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 007 | Tweet ID: `1758996` | Conv ID: `1758996`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "I guess it’s a good thing @115858 didn’t fix that WiFi turning back on by itself problem 🙄 I love draining my battery for no reason"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 008 | Tweet ID: `436485` | Conv ID: `436485`
**Candidate Intent:** `BATTERY_DRAIN_POWER_CONSUMPTION`  
**Customer Inquiry Text:**
> "@AppleSupport  iPhone 6 freezing &amp; on  calls screen black and have to reboot &amp; real bad battery life ,"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `DEVICE_FREEZE_CRASH_REBOOT`

#### Case 009 | Tweet ID: `2571386` | Conv ID: `2571386`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "@AppleSupport absolutely hate the new update. I don't even want to use my iPhone. Keeps freezing and very slow to open apps. Fix ASAP plz!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 010 | Tweet ID: `543792` | Conv ID: `543792`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "@AppleSupport my iPhone keeps restarting - is there a known fix please?? Driving me crazy!!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 011 | Tweet ID: `2834853` | Conv ID: `2834853`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "WHY DO MY APPS KEEP FREEZING WITH THIS UPDATE @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 012 | Tweet ID: `2527027` | Conv ID: `2527027`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "Another update and still this display issue, @AppleSupport. Oh, and the great lagginess (sure, that’s a word) on this 6s. And still the design issues. It is like iOS 11 is trying to to get me to look at @122609. Yes. I’ve restarted. Repeatedly. https://t.co/aQrwqNlokt"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 013 | Tweet ID: `2896141` | Conv ID: `2896141`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "Hold down Command+R while starting up until you see the #Apple logo, then from the menu that appears, run Disk Utility to repair your Hard Disk.

I am here if you need additional assistance.

@AppleSupport needs to be included in this conversation.  https://t.co/ugdjZlgMWS"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 014 | Tweet ID: `1808654` | Conv ID: `1808654`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "@AppleSupport battery stuck@96% while charging after ios 11.0.3 update on 6s &amp; Shows 100% after restarting.#ios11"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 015 | Tweet ID: `1928792` | Conv ID: `1928792`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "@115858 ever since this new update my 📱 has been screwing up 😡. Not loading videos, freezing etc. I’m about 2 switch to @125607 #apple"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 016 | Tweet ID: `1886395` | Conv ID: `1886395`
**Candidate Intent:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Customer Inquiry Text:**
> "@AppleSupport An only iPhone user since 2009 first time Im planning to switch. #iOS 11.0.3 sucks beyond belief. Blackouts and crashes."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`

#### Case 017 | Tweet ID: `1458791` | Conv ID: `1458791`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "@AppleSupport why is a capital i autocorrecting to the weird A and question mark every time now?????"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 018 | Tweet ID: `1599696` | Conv ID: `1599696`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "@AppleSupport there’s an issue with y’all keyboard 👀"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 019 | Tweet ID: `1455312` | Conv ID: `1455312`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "So @AppleSupport, why does the letter I show up as a weird character? Updates have been a mess 🙄"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 020 | Tweet ID: `2014720` | Conv ID: `2014720`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "so the letter I is a box with a question mark😂 get your shit together @115858"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 021 | Tweet ID: `2179491` | Conv ID: `2179491`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "@AppleSupport there’s another glitch🙃🙃🙃whenever I try to type “it” autocorrect changes to I.t 🙃🙃🙃next glitch I want a new phone🙃🙃🙃🙃"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 022 | Tweet ID: `2014688` | Conv ID: `2014688`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "So @115858 when are you going to fix the letter “I” on our iPhone keyboard?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 023 | Tweet ID: `1773706` | Conv ID: `1773706`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "Somebody please explain to me how to fix my keyboard &amp; these letters 😫I can’t understand anyone’s texts!!! @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 024 | Tweet ID: `706134` | Conv ID: `706134`
**Candidate Intent:** `KEYBOARD_TYPING_AUTOCORRECT_ISSUE`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport your #iOS11 just screwed up my #iPhone 6Plus #NotHappy way too slow, keyboard freezes apps take time to open 😡😡😡"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `PERFORMANCE_SLOWDOWN_LATENCY`

#### Case 025 | Tweet ID: `1455370` | Conv ID: `1455370`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport also, could you help me about battery autonomy, and lag problems since iOS 11 ?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 026 | Tweet ID: `1621246` | Conv ID: `1621246`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport Hi there! My iPhone 6 has been losing battery, lagging and restarting on its own. Anything thing I can do about it?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 027 | Tweet ID: `2789816` | Conv ID: `2789816`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport my phone is moving really slow, there’s a delay in my keyboard as well....just got this phone 🤔"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 028 | Tweet ID: `1366329` | Conv ID: `1366329`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport hoping the keyboard lag on iP6 will be fixed in a coming release.  Is this the case? Gets worse everyday!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 029 | Tweet ID: `152805` | Conv ID: `152805`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "This @115858 #ios update has my phone lagging and slow AF 😠"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 030 | Tweet ID: `1713748` | Conv ID: `1713748`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport my iPhone is working terribly. Battery goes from 50 to 14 in seconds. Very slow. Freezes. On current upl"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 031 | Tweet ID: `362482` | Conv ID: `362482`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport Why has my phone become so slow after updating to 11.0.2? It feels like I am using an old android phone."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 032 | Tweet ID: `1404102` | Conv ID: `1404102`
**Candidate Intent:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Customer Inquiry Text:**
> "@AppleSupport i have updated to iOS 11.0.3, the phone is dead slow and battery drains like running nose during cold, using iPhone6"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `CONNECTIVITY_WIFI_BLUETOOTH`

#### Case 033 | Tweet ID: `1477500` | Conv ID: `1477500`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "Dear @AppleSupport in your latest update that I did last night, I now cannot turn on my wifi.  Please fix!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 034 | Tweet ID: `2341877` | Conv ID: `2341877`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "@AppleSupport i have ipad pro since updates on airplane mode keeps turn on wifi and bltooth on its own and music app freezes randomly?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 035 | Tweet ID: `2837112` | Conv ID: `2837112`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "@115858 my iPhone 7 stops playing Pandora randomly about 5 times a day, I have a mess of wires in three places for the audio Bluetooth adaptation, and nobody can hear me with the shitty mic"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 036 | Tweet ID: `2112932` | Conv ID: `2112932`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "So I finally did the new update on my phone. And I have questions. Why does my Bluetooth always turn on? What is the green button that is on above the Bluetooth? @115858 help me. https://t.co/bXWMntqFNk"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 037 | Tweet ID: `1718426` | Conv ID: `1718426`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "@AppleSupport Hi, would a cellular version of your new watch bought in the USA work with a UK network in the UK? Thanks"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 038 | Tweet ID: `2385181` | Conv ID: `2385181`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "@AppleSupport I need some help. My Apple Music says I need to confirm that I’m still a student on the next 6 days, but I’m not in Brazil I’m in Europe I’ll only have access to my Uni WiFi in 2 months... how can I confirm it?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 039 | Tweet ID: `2261758` | Conv ID: `2261758`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "Do Jabra Bluetooth headsets not work with #ios11? Since I upgraded yesterday, it can’t find device, plus battery life much worse. @115858"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 040 | Tweet ID: `447427` | Conv ID: `447427`
**Candidate Intent:** `CONNECTIVITY_WIFI_BLUETOOTH`  
**Customer Inquiry Text:**
> "@AppleSupport HOW DO I STOP MY PHONE FROM LOOKIJG FOR WIFI AND TURNING ON ITS SEARCHING ITS ALREADY WASTING MY BATTERY FAST ENLUGH STOP"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `APP_SPECIFIC_MALFUNCTION`

#### Case 041 | Tweet ID: `2071092` | Conv ID: `2071092`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "@AppleSupport this new update is terrible. Every app is crashing!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 042 | Tweet ID: `229207` | Conv ID: `229207`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "I need to submit an bug report to @115858 in regards to their iOS 11 update. I have more infor on the podcast app not working."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 043 | Tweet ID: `2555457` | Conv ID: `2555457`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "What is the point in downloading movies using the iTunes app on an iPad if the TV app won’t play them back when traveling with no WiFi? This bug has existed since iOS 10.2. How is it still a thing? The TV app is useless. @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 044 | Tweet ID: `737006` | Conv ID: `737006`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "If you haven’t updated your iPhone, I wouldn’t recommend it. My apps have been constantly crashing and my battery is drained. @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 045 | Tweet ID: `552205` | Conv ID: `552205`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "@AppleSupport ApplePay isn’t accepting my home address on certain apps, and the app creator says the bug isn’t on their end."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 046 | Tweet ID: `294912` | Conv ID: `294912`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "@AppleSupport @115858 #ios1102 Problems: draining battery like hell, Constantly Iphone and keyboard freezing, APPS crashing... etc ... HELP!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 047 | Tweet ID: `2051238` | Conv ID: `2051238`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "@115858 ever since this update my phone has been bugging apps have been crashing my iTunes music app is messing up!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 048 | Tweet ID: `1708492` | Conv ID: `1708492`
**Candidate Intent:** `APP_SPECIFIC_MALFUNCTION`  
**Customer Inquiry Text:**
> "@AppleSupport again the music app keeps crashing without any reason.
Tried restarting and no use.
See the video.
iPhone 6 plus - iOS11.0.3 https://t.co/6VpYeHL8aK"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `DATA_LOSS_RECOVERY`

#### Case 049 | Tweet ID: `1874636` | Conv ID: `1874636`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@AppleSupport any idea why my contacts have become lost from the message headers? It’s happened since last update. (iPhone 5s)"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 050 | Tweet ID: `300611` | Conv ID: `300611`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@AppleSupport there is bug after iOS 11. If you Open camera, take a picture and click  “delete”, it doesn’t work! the photo is still there!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 051 | Tweet ID: `2783276` | Conv ID: `2783276`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@AppleSupport Facing prob in my 6 &amp; spouse 5s since upgrading to iOS 11 Apart frm draining battery wrong battery %display 5scudn’t be restarted on frozen logo Tk 2 Apple store reloaded iOS all data lost. disgusting is iCloud data cud-not be retrieved. Losing faith very fast."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 052 | Tweet ID: `2001925` | Conv ID: `2001925`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@123857 iOS 11.2 not signed for iPhone X? Can’t restore data…"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 053 | Tweet ID: `122311` | Conv ID: `122311`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@AppleSupport Just noticed, my iTunes backup size grew from 10GB to 50GB while iCloud backup is still 6GB with my new phone. Does iTunes save photos from the phone in high resolution even with iCloud Photo Library enabled? Here it says it doesn’t. https://t.co/iZ6wglsK3O"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 054 | Tweet ID: `2373285` | Conv ID: `2373285`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@AppleSupport what is wrong with your customer service/support system? I lost my phone, can't sign into Find My Phone, and can't reset my password - I CAN"T GET TEXTS W/OUT A PHONE - and I can't call the support line w/out phone either.  why can't i use the chat feature?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 055 | Tweet ID: `181442` | Conv ID: `181442`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "@AppleSupport  how long is it going to take for my backup to complete on my iPhone X !? It’s been hours and my pictures still haven’t been added into my picture app yet 😰"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 056 | Tweet ID: `2856794` | Conv ID: `2856794`
**Candidate Intent:** `DATA_LOSS_RECOVERY`  
**Customer Inquiry Text:**
> "My phone deleted all my text threads and is maybe not getting texts?? Who can know! and the only fix is "replace your phone" so THANK U @115858 and lol @ everyone who suggested I replace my iPhone with another iPhone"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `SCREEN_DISPLAY_TOUCH_BIOMETRICS`

#### Case 057 | Tweet ID: `2953805` | Conv ID: `2953805`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "@115858 how do I unlock my phone if I accident razored off part of my fingerprint. Asking for a friend."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 058 | Tweet ID: `2901948` | Conv ID: `2901948`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "@AppleSupport I have bought iPhone X 256 GB.
Face recognition is very dangerous.
Set my Face ID, it opens my banks app and allow transactions."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 059 | Tweet ID: `1949792` | Conv ID: `1949792`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "@AppleSupport message app stopped working on iphone 6s plus running 11.0.3 ... when trying to open, long delay, then back to home screen"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 060 | Tweet ID: `2047848` | Conv ID: `2047848`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "@AppleSupport I’m really not happy with what’s happening with my phone. It’s freezing for 10 minutes. Restarting itself, and the screen"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 061 | Tweet ID: `1918561` | Conv ID: `1918561`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "What kind of joke is #iOS11 ??? I have an iPhone 7 and apps disappear, screen lags... @115858 @AppleSupport stop forcing people upgrade shit https://t.co/k00g2rXEyg"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 062 | Tweet ID: `2206030` | Conv ID: `2206030`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "@115858 I have 6S in Egypt and I can't repair the screen cracked as no original screens ! What can I do ?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 063 | Tweet ID: `2193450` | Conv ID: `2193450`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "@AppleSupport Ever since installing latest #iPhoneUpdate my iPhone 6+ is virtually useless. Opens apps, switches to FaceTime, places calls without prompt &amp; touch screen won't let me answer calls. Can you help me?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 064 | Tweet ID: `798832` | Conv ID: `798832`
**Candidate Intent:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS`  
**Customer Inquiry Text:**
> "so i need to know WHY i can’t read my notifications when i pull down. i don’t want my lock screen to pop up @115858 https://t.co/sv6OMetVdl"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `HARDWARE_CHARGING_POWER_CABLE`

#### Case 065 | Tweet ID: `740603` | Conv ID: `740603`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "My iPhone was good to me b4 this new update. Now it’s slow as shit, closes apps randomly, says I have 1% on a full charge lol I wonder why 🤔"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 066 | Tweet ID: `1588817` | Conv ID: `1588817`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "Argggh my iphone is stuck in continuous apple logo loop and as soon as power cable is disconnected, the screen goes blank instantly #help"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 067 | Tweet ID: `2728200` | Conv ID: `2728200`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "Dear @115858 please observe this screen recording. Initially my battery is showing 5% and now when I switch on my charger, it shows 5% again I disconnected and reconnected my charger it showed 13%. What is this bug of yours??  Please fix it. https://t.co/gVR0kzrfuf"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 068 | Tweet ID: `2815631` | Conv ID: `2815631`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "@AppleSupport YO does using your phone while charging i️t mess up the battery"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 069 | Tweet ID: `945501` | Conv ID: `945501`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "@AppleSupport You have been charging me bit more of US 10 per month for a suscripton to itunes I never requested. I want my money back asap"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 070 | Tweet ID: `1296825` | Conv ID: `1296825`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "@AppleSupport my Bluetooth headphones won’t pair since I updated to 11.0.3 - and my battery isn’t holding a charge!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 071 | Tweet ID: `1898008` | Conv ID: `1898008`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "@AppleSupport why after iOS 11.0.3 updates do both my iPhone5s have intermittent charging issues when using OEM wall chargers?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 072 | Tweet ID: `1828500` | Conv ID: `1828500`
**Candidate Intent:** `HARDWARE_CHARGING_POWER_CABLE`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport this has happened to my MacBook charger - can I get a replacement? https://t.co/QPE5L65TDD"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `AUDIO_SOUND_SPEAKER_MIC`

#### Case 073 | Tweet ID: `2238187` | Conv ID: `2238187`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "@AppleSupport I really hate how Apple Music works with having a family. Anytime more than one person in a family wants to listen it kicks the other off, why?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 074 | Tweet ID: `246527` | Conv ID: `246527`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "@AppleSupport why my iPhone do some weirds “beeps” when someone send me a text? I mean not the normal sound, do two doble beeps!?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 075 | Tweet ID: `2863567` | Conv ID: `2863567`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "I wanted to say the #iPhoneX is awesome but I can’t. It sucks; no one can hear me &amp; it does not play voicemails. Stores won’t take it back. @AppleSupport @115858 @115714"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 076 | Tweet ID: `1766076` | Conv ID: `1766076`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "@AppleSupport after I updated my os yo 11.03 last night my music doesn’t play through car audio system! It charges alright, phone works too!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 077 | Tweet ID: `798827` | Conv ID: `798827`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "Wow @115858, your own app won’t open due to “security.” An audio file created on the iPhone in the Voice Recorder app playing in Quicktime. https://t.co/K30YM5tMSk"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 078 | Tweet ID: `2750445` | Conv ID: `2750445`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "Hey @AppleSupport what is going on here? That was a browser window playing a video. I can still hear it, so the computer hasn't crashed bit it's non responsive. #help! https://t.co/4u4kYEvLcr"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 079 | Tweet ID: `174975` | Conv ID: `174975`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "Hey @AppleSupport what’s with this volume thing and the @115888 app when I switch apps on iPhone X? https://t.co/oXvO3qqNcs"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 080 | Tweet ID: `947768` | Conv ID: `947768`
**Candidate Intent:** `AUDIO_SOUND_SPEAKER_MIC`  
**Customer Inquiry Text:**
> "@AppleSupport hey guys i play my apple music from my imac to my stereo. is there a way to control the browser volume separate from music??"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `ACCOUNT_APPLE_ID_ACCESS`

#### Case 081 | Tweet ID: `1106641` | Conv ID: `1106641`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "@AppleSupport why is ios11 so bad on my phone and why does iCloud corrupt all my photos? Seriously I can barely use @128065 anymore."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 082 | Tweet ID: `154443` | Conv ID: `154443`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "@applesupport nothing but woes since installing 10.13.1: network not recognized, Gmail doesn't load sometimes, network disconnect, re-entering password repeatedly, etc. How can you lunch since a bugged up OS?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 083 | Tweet ID: `1886647` | Conv ID: `1886647`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "I'm locked out of my fuck ass iphone please help @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 084 | Tweet ID: `2039858` | Conv ID: `2039858`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "@116333 why is iCloud Drive so slow to sync? I’ve had to drive from work to home today, then later from home to work to copy to usb 👎🏻"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 085 | Tweet ID: `897704` | Conv ID: `897704`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "Hey @AppleSupport I have been having issues with the WiFi connection it requires me over and over the password, and the email is really slow"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 086 | Tweet ID: `820686` | Conv ID: `820686`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "If my Apple ID signs me out one more time I’ll hit the roof @AppleSupport #ios11update"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 087 | Tweet ID: `2311842` | Conv ID: `2311842`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "@AppleSupport don’t fucking give me thousands of notifications to put in my password and when i do this happens, i fucking hate y’all https://t.co/K2AFHC8RI1"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 088 | Tweet ID: `1003753` | Conv ID: `1003753`
**Candidate Intent:** `ACCOUNT_APPLE_ID_ACCESS`  
**Customer Inquiry Text:**
> "@AppleSupport I’m getting the following error when trying to access my Apple ID - iPhone 6s plus (11.0.3).  HELP!! https://t.co/qPPhunkwEs"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `BILLING_CHARGE_REFUND_DISPUTE`

#### Case 089 | Tweet ID: `1765110` | Conv ID: `1765110`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@115858 2017 MacBook Pro won’t charge, iPad won’t update, falsely says not connected to internet, desktop &gt; hour to update. No work possible"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 090 | Tweet ID: `1834108` | Conv ID: `1834108`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport since updating to 11.0.3 I have needed to charge my phone twice a day. Is this related ? Any help or options to fix?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 091 | Tweet ID: `154425` | Conv ID: `154425`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "It’s just 8am and after a full overnight charge, my @115858 iPhone is at 25% battery. 
Do yourself a favor and don’t buy an iPhone. https://t.co/OBMoOJDLPP"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 092 | Tweet ID: `2063439` | Conv ID: `2063439`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@AppleSupport hi why does my iPhone keep doing this when using it, it won't hold charge and the back camera keeps heating up https://t.co/0eFAp8ZS9a"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 093 | Tweet ID: `589565` | Conv ID: `589565`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@115858 you charge a small fortune for an iphone and can’t make it type the letter “I️ “ properly. Figure your shit out already!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 094 | Tweet ID: `2922669` | Conv ID: `2922669`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@AppleSupport the battery with iOS 11 FUCKING SUCKS. I shouldn’t have to charge 3 times a day. I have a brand new phone"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 095 | Tweet ID: `756536` | Conv ID: `756536`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@AppleSupport @115858 I'm charged ₹60 for free subscription on iTunes. Please provide me details why I'm charged when it's free. https://t.co/DORPM0mBla"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 096 | Tweet ID: `1864165` | Conv ID: `1864165`
**Candidate Intent:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Customer Inquiry Text:**
> "@applesupport my phone won't hold a charge since update 11.0.3. Affecting my ability to conduct business. #iphone7 #batterydrain #apple"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `ORDER_PURCHASE_SHIPPING_STATUS`

#### Case 097 | Tweet ID: `2014830` | Conv ID: `2014830`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "@AppleSupport charged for the fight that never actually downloaded. We couldn’t get passed the order page??? https://t.co/e4XUiGC2OX"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 098 | Tweet ID: `553544` | Conv ID: `553544`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "Seriously, @115858? I have to manually disable notifications for all apps, with the phone resetting every 4 seconds, in order to get my phone working again? It's like a really annoying game of race the clock. iOS 11 broke my iPhone X overnight. What a pain! https://t.co/dwtZImORJr"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 099 | Tweet ID: `2029687` | Conv ID: `2029687`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "@AppleSupport why are my messages being sent, but in my screen shows it's still trying to send and shows no delivery? And then deletes?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 100 | Tweet ID: `1912997` | Conv ID: `1912997`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "@AppleSupport if i order an iphone from https://t.co/hIJbdY3Djh it will be delivered to my house or p o box ?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 101 | Tweet ID: `2012480` | Conv ID: `2012480`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "Say hello to the future. Order iPhone X."

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 102 | Tweet ID: `1148813` | Conv ID: `1148813`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "How does the iPhone pre-order work? Is it for online orders only? @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 103 | Tweet ID: `2302112` | Conv ID: `2302112`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "@AppleSupport Hello teamApple, order number W421888395, I need to talk urgently about delivering this order nearby, ur phone is not dialin"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 104 | Tweet ID: `247610` | Conv ID: `247610`
**Candidate Intent:** `ORDER_PURCHASE_SHIPPING_STATUS`  
**Customer Inquiry Text:**
> "@AppleSupport 
I ordered iPhone two days ago and didn't receive confirmation email until now. Is that normal?"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `SECURITY_PHISHING_SUSPICIOUS_CONTACT`

#### Case 105 | Tweet ID: `2298077` | Conv ID: `2298077`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport check this fraud!! https://t.co/XKaEFph2PF"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 106 | Tweet ID: `2311579` | Conv ID: `2311579`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "@AppleSupport Wanted to let you guys know about a scam going down in your name. https://t.co/3ey3GlZGs4"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 107 | Tweet ID: `2782073` | Conv ID: `2782073`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "@AppleSupport, wanted to share the email I received to help warn others. I assume it’s a scam? https://t.co/Fwha1bbUu5"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 108 | Tweet ID: `505101` | Conv ID: `505101`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "@AppleSupport Hey, I think you've a scammer out there have gotten several calls from  a Lexington Park number saying your going to delete my iCloud account!!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 109 | Tweet ID: `1133153` | Conv ID: `1133153`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "@AppleSupport is this a scam or really Apple? See pic below that came up on my phone https://t.co/fT7cCDTgWF"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 110 | Tweet ID: `328552` | Conv ID: `328552`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "Absolutely love getting scam emails from @115858. NOT. @AppleSupport"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 111 | Tweet ID: `633902` | Conv ID: `633902`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "Lol @115858 wtf? I just got a call from “Scam Likely”!"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 112 | Tweet ID: `689325` | Conv ID: `689325`
**Candidate Intent:** `SECURITY_PHISHING_SUSPICIOUS_CONTACT`  
**Customer Inquiry Text:**
> "im convinced somebody hacked my phone because this shit has been doing all kinds of fuckery that i just cant explain &amp; honestly im a little shook..... but mostly annoyed. @115858"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

### Intent: `UNKNOWN_INSUFFICIENT_CONTEXT`

#### Case 113 | Tweet ID: `1807484` | Conv ID: `1807484`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "@AppleSupport @115858 https://t.co/v0KDFxlDBT"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 114 | Tweet ID: `2860047` | Conv ID: `2860047`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "@AppleSupport @115948 ☹️☹️ https://t.co/byLnUWjYaI"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 115 | Tweet ID: `2378883` | Conv ID: `2378883`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "@AppleSupport quick question"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 116 | Tweet ID: `1405494` | Conv ID: `1405494`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport help me!!! https://t.co/UKY0ebnVBG"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 117 | Tweet ID: `2866195` | Conv ID: `2866195`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "@AppleSupport help https://t.co/8HUS3cmIKl"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 118 | Tweet ID: `1168545` | Conv ID: `1168545`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "Wtf? @AppleSupport #ios11  @115858 #iossucks https://t.co/9EG4FD427f"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 119 | Tweet ID: `1580440` | Conv ID: `1580440`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "What is this @115858 @AppleSupport https://t.co/r9c5OzODxz"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 120 | Tweet ID: `2940408` | Conv ID: `2940408`
**Candidate Intent:** `UNKNOWN_INSUFFICIENT_CONTEXT`  
**Customer Inquiry Text:**
> "#Etisalat #Apple #Applecare #AppleSupport #dubaided #Dubai_consumers #TRA #BBC_DUBAI #GULF_NEWS #KHALEEJ_TIMES @115858 @AppleSupport @39782 @36393 @112852 @34651 @112853 #no_support_for_customers #etisalat_apple_playing_games #urgent_assistence https://t.co/8Bb0bWYO2d"

- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

---

## Part 2: Boundary & Confusion Pair Cases (35 Inquiries: 5 per Pair x 7 Pairs)

### Confusable Pair: `PAIR_01_BATTERY_VS_CHARGING`
**Intent A:** `BATTERY_DRAIN_POWER_CONSUMPTION` | **Intent B:** `HARDWARE_CHARGING_POWER_CABLE`  
**Deterministic Distinguishing Rule:** Rapid energy discharge / percentage drop / heat under load belongs to BATTERY_DRAIN_POWER_CONSUMPTION. Inability to charge, loose/frayed cable, or defective lightning port belongs to HARDWARE_CHARGING_POWER_CABLE. If both occur, customer focal grievance decides.  

#### Case 121 | Tweet ID: `2634938` | Conv ID: `2634938`
**Pair Under Test:** `PAIR_01_BATTERY_VS_CHARGING`  
**Customer Inquiry Text:**
> "@AppleSupport is there a fix for the iOS 11.1.1 battery issue yet? My battery drains while plugged in."

- **Proposed Pair:** `BATTERY_DRAIN_POWER_CONSUMPTION` vs `HARDWARE_CHARGING_POWER_CABLE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 122 | Tweet ID: `1762817` | Conv ID: `1762817`
**Pair Under Test:** `PAIR_01_BATTERY_VS_CHARGING`  
**Customer Inquiry Text:**
> "OKAY @115858 MY PHONE SAYS ITS CHARGING BUT MY BATTERY WENT DOWN TWO PERCENTAGES"

- **Proposed Pair:** `BATTERY_DRAIN_POWER_CONSUMPTION` vs `HARDWARE_CHARGING_POWER_CABLE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 123 | Tweet ID: `2448342` | Conv ID: `2448342`
**Pair Under Test:** `PAIR_01_BATTERY_VS_CHARGING`  
**Customer Inquiry Text:**
> "Interesting how my #iPhone went from 10% battery to 33% after being plugged in for 2m &amp; now it’s at 28% writing this tweet. Still haven’t figured that out @115858? #fail"

- **Proposed Pair:** `BATTERY_DRAIN_POWER_CONSUMPTION` vs `HARDWARE_CHARGING_POWER_CABLE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 124 | Tweet ID: `254686` | Conv ID: `254686`
**Pair Under Test:** `PAIR_01_BATTERY_VS_CHARGING`  
**Customer Inquiry Text:**
> "@AppleSupport Updated to latest IOS and my phone battery is dying. Turned off location/background refresh. Refuses charge with Apple charger"

- **Proposed Pair:** `BATTERY_DRAIN_POWER_CONSUMPTION` vs `HARDWARE_CHARGING_POWER_CABLE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 125 | Tweet ID: `146710` | Conv ID: `146710`
**Pair Under Test:** `PAIR_01_BATTERY_VS_CHARGING`  
**Customer Inquiry Text:**
> "Dear @115858 @AppleSupport - this is NOT a full battery. Phone died, put on the charger and went from 1% to 100% in 2 minutes...SORT IT OUT(I have done all the battery optimisation stuff already AND a full restore) 11.1.2 is SHITE... https://t.co/7kVeLAKAQR"

- **Proposed Pair:** `BATTERY_DRAIN_POWER_CONSUMPTION` vs `HARDWARE_CHARGING_POWER_CABLE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

### Confusable Pair: `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`
**Intent A:** `DEVICE_FREEZE_CRASH_REBOOT` | **Intent B:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Deterministic Distinguishing Rule:** Complete unresponsive system lockup requiring hard reset, kernel panic, or sudden restart belongs to DEVICE_FREEZE_CRASH_REBOOT. Operable system with UI frame drops, typing latency, or sluggish navigation belongs to PERFORMANCE_SLOWDOWN_LATENCY.  

#### Case 126 | Tweet ID: `2020080` | Conv ID: `2020080`
**Pair Under Test:** `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "Ever since my phone automatically updated itself, its been shit, crashes, lags, have to restart it most days... thanks @AppleSupport @115858"

- **Proposed Pair:** `DEVICE_FREEZE_CRASH_REBOOT` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 127 | Tweet ID: `371467` | Conv ID: `371467`
**Pair Under Test:** `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> ".@115858 my phone is running mighty slow and experience about 4-5 crashes a day after this “update” tf Bruh?"

- **Proposed Pair:** `DEVICE_FREEZE_CRASH_REBOOT` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 128 | Tweet ID: `2082034` | Conv ID: `2082034`
**Pair Under Test:** `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@AppleSupport My iPhone has been extremely slow ever since I updated my phone. It will constantly freeze &amp; turn off on its own. Why is this?"

- **Proposed Pair:** `DEVICE_FREEZE_CRASH_REBOOT` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 129 | Tweet ID: `1000235` | Conv ID: `1000235`
**Pair Under Test:** `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@AppleSupport updated my phone the other day and it keeps freezing so I have to restart it. Then it’s really slow. Sort it out."

- **Proposed Pair:** `DEVICE_FREEZE_CRASH_REBOOT` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 130 | Tweet ID: `1265821` | Conv ID: `1265821`
**Pair Under Test:** `PAIR_02_CRASH_FREEZE_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@116333 the the most recent update is so bad I sold my @115858 stock. Slow/ glitch/ freezing. Please stop running company into ground!!!!!"

- **Proposed Pair:** `DEVICE_FREEZE_CRASH_REBOOT` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

### Confusable Pair: `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`
**Intent A:** `APP_SPECIFIC_MALFUNCTION` | **Intent B:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Deterministic Distinguishing Rule:** Failure isolated to a single application belongs to APP_SPECIFIC_MALFUNCTION. Operating system crash, black screen, or forced restart affecting the entire device belongs to DEVICE_FREEZE_CRASH_REBOOT.  

#### Case 131 | Tweet ID: `388043` | Conv ID: `388043`
**Pair Under Test:** `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`  
**Customer Inquiry Text:**
> "@AppleSupport - Is there an iOS 11.0.3 out soon or something? My Mail app crashes and needs a phone reboot twice daily at the moment. PITA."

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 132 | Tweet ID: `324534` | Conv ID: `324534`
**Pair Under Test:** `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`  
**Customer Inquiry Text:**
> "@AppleSupport updated my 7plus to 11.0.2 - cannot run more than one non-system app at a time. Apps crash, phone becomes unresponsive 😐"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 133 | Tweet ID: `1967961` | Conv ID: `1967961`
**Pair Under Test:** `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport my new iPhone 8 is giving me no end of grief. Whenever the camera is on (photo or snapchat)it either freezes or restart"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 134 | Tweet ID: `804109` | Conv ID: `804109`
**Pair Under Test:** `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport I can’t believe how my iphone works since iOS 11.0.2. Every app crash my phone. What the hell?! FIX IT!!!! 😠😠 #iOSCrash"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 135 | Tweet ID: `2925629` | Conv ID: `2925629`
**Pair Under Test:** `PAIR_03_APP_MALFUNCTION_VS_OS_CRASH`  
**Customer Inquiry Text:**
> "@115858 needs to update their shit my phone keeps freezing and safari is slower than dirt it’s ridiculous"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

### Confusable Pair: `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`
**Intent A:** `DATA_LOSS_RECOVERY` | **Intent B:** `ACCOUNT_APPLE_ID_ACCESS`  
**Deterministic Distinguishing Rule:** Missing user-generated content (photos, contacts, notes, message history) belongs to DATA_LOSS_RECOVERY. Credential authentication, 2FA verification codes, password reset, or account lockout belongs to ACCOUNT_APPLE_ID_ACCESS.  

#### Case 136 | Tweet ID: `2790678` | Conv ID: `2790678`
**Pair Under Test:** `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`  
**Customer Inquiry Text:**
> "@AppleSupport since my contacts are on iCloud shouldn’t they automatically sync. Suppose I delete on the phone it should go from iPad too?"

- **Proposed Pair:** `DATA_LOSS_RECOVERY` vs `ACCOUNT_APPLE_ID_ACCESS`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 137 | Tweet ID: `2082705` | Conv ID: `2082705`
**Pair Under Test:** `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`  
**Customer Inquiry Text:**
> "Hello @AppleSupport , I can't login to my iCloud account [with right password], I also can't backup my contacts and I've lost them."

- **Proposed Pair:** `DATA_LOSS_RECOVERY` vs `ACCOUNT_APPLE_ID_ACCESS`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 138 | Tweet ID: `2732870` | Conv ID: `2732870`
**Pair Under Test:** `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`  
**Customer Inquiry Text:**
> "@AppleSupport please help forgot iPhone backup password. Many iphones crashed . All my data has gone"

- **Proposed Pair:** `DATA_LOSS_RECOVERY` vs `ACCOUNT_APPLE_ID_ACCESS`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 139 | Tweet ID: `1948006` | Conv ID: `1948006`
**Pair Under Test:** `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`  
**Customer Inquiry Text:**
> "@AppleSupport Since downloading IOS11.03 most of my photos have gone from my photo roll and won't re download from icloud. please help."

- **Proposed Pair:** `DATA_LOSS_RECOVERY` vs `ACCOUNT_APPLE_ID_ACCESS`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 140 | Tweet ID: `2271745` | Conv ID: `2271745`
**Pair Under Test:** `PAIR_04_DATA_LOSS_VS_ACCOUNT_ACCESS`  
**Customer Inquiry Text:**
> "@115858 I recently updated to 11.1.2, backed up BEFORE the update, and now I’m missing 3 years worth of photos from my iPhone.  I see that I can’t restore from previous backup (iOS 10).  What is my fix for this issue?"

- **Proposed Pair:** `DATA_LOSS_RECOVERY` vs `ACCOUNT_APPLE_ID_ACCESS`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

### Confusable Pair: `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`
**Intent A:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` | **Intent B:** `DEVICE_FREEZE_CRASH_REBOOT`  
**Deterministic Distinguishing Rule:** Physical display panel anomalies (lines, flicker, dead pixels), touch digitizer unresponsiveness/ghost touch, and biometric sensor defects (Touch ID, Face ID) belong to SCREEN_DISPLAY_TOUCH_BIOMETRICS. System freeze with black screen and boot loop belongs to DEVICE_FREEZE_CRASH_REBOOT.  

#### Case 141 | Tweet ID: `1631296` | Conv ID: `1631296`
**Pair Under Test:** `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`  
**Customer Inquiry Text:**
> "Hey @115858, iOS 11 is a piece of SHIT. Black screen, pressing home or power does nothing &amp; have to hard reset to get back into my iPhone 6s."

- **Proposed Pair:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 142 | Tweet ID: `643243` | Conv ID: `643243`
**Pair Under Test:** `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`  
**Customer Inquiry Text:**
> "@AppleSupport I have the new iPhone 8+ and sometimes when accessing the camera from the lock screen, I get a black screen with the spinner."

- **Proposed Pair:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 143 | Tweet ID: `234621` | Conv ID: `234621`
**Pair Under Test:** `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`  
**Customer Inquiry Text:**
> ".@AppleSupport since the update to #iOS11 my #iPhone 6s’ touch screen has been becoming unresponsive at times. Other times it seems as if the calibration is off. Happens 3-4 times per day and requires a reset to temp. fix it each time. @115858"

- **Proposed Pair:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 144 | Tweet ID: `545151` | Conv ID: `545151`
**Pair Under Test:** `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`  
**Customer Inquiry Text:**
> "Dear @AppleSupport please fix the 'black screen-spinning wheel' problem ASAP.
The whole world got affected. #iPhone"

- **Proposed Pair:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 145 | Tweet ID: `1733796` | Conv ID: `1733796`
**Pair Under Test:** `PAIR_05_SCREEN_DISPLAY_VS_DEVICE_FREEZE`  
**Customer Inquiry Text:**
> "@AppleSupport I’m stuck with my iPhone the white screen with logo won’t go, I did a hard restart already and iTunes restore, nothing works"

- **Proposed Pair:** `SCREEN_DISPLAY_TOUCH_BIOMETRICS` vs `DEVICE_FREEZE_CRASH_REBOOT`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

### Confusable Pair: `PAIR_06_ACCOUNT_ACCESS_VS_BILLING`
**Intent A:** `ACCOUNT_APPLE_ID_ACCESS` | **Intent B:** `BILLING_CHARGE_REFUND_DISPUTE`  
**Deterministic Distinguishing Rule:** Account sign-in, password, or verification code issues belong to ACCOUNT_APPLE_ID_ACCESS. Unexpected credit card charges, App Store refund requests, or subscription disputes belong to BILLING_CHARGE_REFUND_DISPUTE.  

#### Case 146 | Tweet ID: `1481887` | Conv ID: `1481887`
**Pair Under Test:** `PAIR_06_ACCOUNT_ACCESS_VS_BILLING`  
**Customer Inquiry Text:**
> "@115858 I'm being charged $1.50 /mth for extra iCloud storage but my account still shows only 5gb so phone won't backup. Help!"

- **Proposed Pair:** `ACCOUNT_APPLE_ID_ACCESS` vs `BILLING_CHARGE_REFUND_DISPUTE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 147 | Tweet ID: `2949572` | Conv ID: `2949572`
**Pair Under Test:** `PAIR_06_ACCOUNT_ACCESS_VS_BILLING`  
**Customer Inquiry Text:**
> "@115858 keeps charging me $1 a month for icloud storage but my iphone still hasn’t backed up in 92 weeks... what’s going on here 🤔"

- **Proposed Pair:** `ACCOUNT_APPLE_ID_ACCESS` vs `BILLING_CHARGE_REFUND_DISPUTE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 148 | Tweet ID: `619390` | Conv ID: `619390`
**Pair Under Test:** `PAIR_06_ACCOUNT_ACCESS_VS_BILLING`  
**Customer Inquiry Text:**
> "@AppleSupport won't let me log in I want to cancel subscriptions. The verifications codes I keep being sent aren't working"

- **Proposed Pair:** `ACCOUNT_APPLE_ID_ACCESS` vs `BILLING_CHARGE_REFUND_DISPUTE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 149 | Tweet ID: `397476` | Conv ID: `397476`
**Pair Under Test:** `PAIR_06_ACCOUNT_ACCESS_VS_BILLING`  
**Customer Inquiry Text:**
> "@AppleSupport I need to cancel a subscription but when I tap my Apple ID, this happens! Can you help? https://t.co/MsBiiOaPlJ"

- **Proposed Pair:** `ACCOUNT_APPLE_ID_ACCESS` vs `BILLING_CHARGE_REFUND_DISPUTE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 150 | Tweet ID: `846969` | Conv ID: `846969`
**Pair Under Test:** `PAIR_06_ACCOUNT_ACCESS_VS_BILLING`  
**Customer Inquiry Text:**
> "@AppleSupport got double charged for something but when I try to log in to report a problem it just keeps bringing up the login screen"

- **Proposed Pair:** `ACCOUNT_APPLE_ID_ACCESS` vs `BILLING_CHARGE_REFUND_DISPUTE`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

### Confusable Pair: `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`
**Intent A:** `APP_SPECIFIC_MALFUNCTION` | **Intent B:** `PERFORMANCE_SLOWDOWN_LATENCY`  
**Deterministic Distinguishing Rule:** Latency or loading hang localized to a single app belongs to APP_SPECIFIC_MALFUNCTION. System-wide navigation stutter, home screen lag, or device-wide sluggishness belongs to PERFORMANCE_SLOWDOWN_LATENCY.  

#### Case 151 | Tweet ID: `1153873` | Conv ID: `1153873`
**Pair Under Test:** `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@AppleSupport my phone is so slow so the new iOS update? Only on text messages though? Why is this?"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 152 | Tweet ID: `32416` | Conv ID: `32416`
**Pair Under Test:** `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@AppleSupport iOS 11 is so slow on my iPhone 5S. For example the camera app takes 5-10 seconds before it can take a photo. What gives?🤦‍♂️"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 153 | Tweet ID: `713785` | Conv ID: `713785`
**Pair Under Test:** `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@AppleSupport  app store downloads have been impossibly slow for the last week since iOS11 &amp; I mean impossible"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 154 | Tweet ID: `613149` | Conv ID: `613149`
**Pair Under Test:** `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "@115858 @AppleSupport my iPhone 5s has many problems, the camera stopped working, and with each software update is slow, should give me a new one"

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 155 | Tweet ID: `255793` | Conv ID: `255793`
**Pair Under Test:** `PAIR_07_APP_MALFUNCTION_VS_SLOWDOWN`  
**Customer Inquiry Text:**
> "Hi @AppleSupport, are there issues with the App Store? App Updates are EXTREMELY slow..."

- **Proposed Pair:** `APP_SPECIFIC_MALFUNCTION` vs `PERFORMANCE_SLOWDOWN_LATENCY`
- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`
- **Focal Grievance Identified:** `[ ]`
- **Reviewer Notes:** `[ ]`

---

## Part 3: UNKNOWN / Insufficient Context Cases (15 Inquiries)

Stratified across Category A (4 cases), Category B1 Bare Pleas (4 cases), Category B2 Media Links (4 cases), and Category B3 Symptomless Rants (3 cases).

#### Case 156 | Tweet ID: `1392452` | Conv ID: `1392452`
**Sampled Category:** `CATEGORY_A_NON_SUPPORT`  
**Non-Technical Justification:** Commercial product pre-order announcement broadcast; contains no customer support inquiry.  
**Customer Inquiry Text:**
> "Say hello to the future. Pre-order iPhone X."

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 157 | Tweet ID: `2726010` | Conv ID: `2726010`
**Sampled Category:** `CATEGORY_A_NON_SUPPORT`  
**Non-Technical Justification:** Launch celebration coworker tweet / non-support social commentary.  
**Customer Inquiry Text:**
> "To all my incredibly talented coworkers, congratulations on the launch of iPhone X! Thanks @63269 for celebrating with us! https://t.co/Jhg31JPIzN"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 158 | Tweet ID: `996645` | Conv ID: `996645`
**Sampled Category:** `CATEGORY_A_NON_SUPPORT`  
**Non-Technical Justification:** Commercial keynote broadcast marketing retweet / promotional campaign; contains no genuine customer support inquiry.  
**Customer Inquiry Text:**
> "Say hello to the future. iPhone X available now."

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 159 | Tweet ID: `1990611` | Conv ID: `1990611`
**Sampled Category:** `CATEGORY_A_NON_SUPPORT`  
**Non-Technical Justification:** Commercial keynote broadcast marketing retweet / promotional campaign; contains no genuine customer support inquiry.  
**Customer Inquiry Text:**
> "@278601 Thanks for joining the #AppleEvent. Say hello to the future. iPhone X.
https://t.co/qtR0VeO3eI"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 160 | Tweet ID: `1713710` | Conv ID: `1713710`
**Sampled Category:** `CATEGORY_B1_BARE_PLEA_PING`  
**Non-Technical Justification:** Bare conversational plea, greeting, or DM request directed to AppleSupport with zero diagnostic symptom, hardware component, or actionable issue named.  
**Customer Inquiry Text:**
> "@AppleSupport help"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 161 | Tweet ID: `52273` | Conv ID: `52273`
**Sampled Category:** `CATEGORY_B1_BARE_PLEA_PING`  
**Non-Technical Justification:** Bare conversational plea directed to AppleSupport with zero diagnostic symptom or component named.  
**Customer Inquiry Text:**
> "@AppleSupport can you please help me"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 162 | Tweet ID: `167286` | Conv ID: `167286`
**Sampled Category:** `CATEGORY_B1_BARE_PLEA_PING`  
**Non-Technical Justification:** Bare conversational DM request directed to AppleSupport with zero diagnostic symptom or component named.  
**Customer Inquiry Text:**
> "@AppleSupport can you check your dm please"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 163 | Tweet ID: `408455` | Conv ID: `408455`
**Sampled Category:** `CATEGORY_B1_BARE_PLEA_PING`  
**Non-Technical Justification:** Bare conversational cry for help and DM request with zero diagnostic symptom named.  
**Customer Inquiry Text:**
> "@AppleSupport i need help pls DM!?"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 164 | Tweet ID: `1196063` | Conv ID: `1196063`
**Sampled Category:** `CATEGORY_B2_MEDIA_LINK_ONLY`  
**Non-Technical Justification:** Media/URL link attachment with no textual diagnostic symptom or only a single-word exclamation (e.g. help/wtf); text alone provides insufficient context.  
**Customer Inquiry Text:**
> "@AppleSupport #iphone #ios #iosupdate https://t.co/chXShYks5b"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 165 | Tweet ID: `2485671` | Conv ID: `2485671`
**Sampled Category:** `CATEGORY_B2_MEDIA_LINK_ONLY`  
**Non-Technical Justification:** Media/URL link attachment with no textual diagnostic symptom or only a single-word exclamation (e.g. help/wtf); text alone provides insufficient context.  
**Customer Inquiry Text:**
> "@115858 wtf?? #HighSierra #MoreLikeSierraIsHigh https://t.co/JiPVNHp8UU"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 166 | Tweet ID: `543643` | Conv ID: `543643`
**Sampled Category:** `CATEGORY_B2_MEDIA_LINK_ONLY`  
**Non-Technical Justification:** Media/URL link attachment with no textual diagnostic symptom or only a single-word exclamation (e.g. help/wtf); text alone provides insufficient context.  
**Customer Inquiry Text:**
> "@AppleSupport https://t.co/8nlHMnzgx0"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 167 | Tweet ID: `162838` | Conv ID: `162838`
**Sampled Category:** `CATEGORY_B2_MEDIA_LINK_ONLY`  
**Non-Technical Justification:** Media/URL attachment with conversational remark "Lol look" and zero textual symptom; text alone provides insufficient context.  
**Customer Inquiry Text:**
> "Lol look @AppleSupport https://t.co/RggSZH4i9S"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 168 | Tweet ID: `1302379` | Conv ID: `1302379`
**Sampled Category:** `CATEGORY_B3_SYMPTOMLESS_RANT`  
**Non-Technical Justification:** Pure emotional frustration rant against update with zero diagnostic symptom or component identified.  
**Customer Inquiry Text:**
> "I literally hate the new @115858 update."

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 169 | Tweet ID: `2072151` | Conv ID: `2072151`
**Sampled Category:** `CATEGORY_B3_SYMPTOMLESS_RANT`  
**Non-Technical Justification:** Emotional frustration rant against iOS update with zero diagnostic symptom or component identified.  
**Customer Inquiry Text:**
> "FIX THIS SHIT @AppleSupport"

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

#### Case 170 | Tweet ID: `863983` | Conv ID: `863983`
**Sampled Category:** `CATEGORY_B3_SYMPTOMLESS_RANT`  
**Non-Technical Justification:** Emotional frustration rant against iOS update with zero diagnostic symptom or component identified.  
**Customer Inquiry Text:**
> "I️ hate this update."

- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`
- **Corrected Intent (if REJECT):** `[ ]`
- **Reviewer Notes:** `[ ]`

