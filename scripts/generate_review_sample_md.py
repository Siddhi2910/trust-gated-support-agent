import json

def main():
    with open('artifacts/taxonomy_human_review_sample.json', 'r', encoding='utf-8') as f:
        sample_data = json.load(f)

    md = []
    md.append('# Candidate Taxonomy Human Review Sample Pack (170 Real Inquiries)')
    md.append('')
    md.append('**Artifact Version:** `1.0.0-candidate`  ')
    md.append('**Sampling Strategy:** Stratified deterministic pseudo-random sampling (`random_state=42`)  ')
    md.append('**Source Corpus:** `data/processed/applesupport_conversations.parquet` (80,250 inbound opening inquiries)  ')
    md.append('**Exclusion Filter:** All 79 showcase examples from `taxonomy_v1_candidate.json` and `taxonomy_confusion_matrix.json` strictly excluded  ')
    md.append('**Taxonomy Frozen Status:** `false` (Pending human sign-off)  ')
    md.append('')
    md.append('---')
    md.append('')
    md.append('## Human Review Protocol and Annotation Instructions')
    md.append('')
    md.append('### 1. The Focal Grievance / Actionable Need Rule')
    md.append('Assign the customer inquiry to the intent representing the **customer’s main actionable support grievance or explicit request**.')
    md.append('- **Explicit Question First:** If the customer asks a direct, actionable question (e.g. *"How do I get a refund for this app?"* vs *"This app crashed and charged me"*), the requested resolution (`BILLING_CHARGE_REFUND_DISPUTE`) governs over background incident context.')
    md.append('- **Underlying Cause vs Symptom:** If a customer complains of battery drain after updating to iOS 11, the actionable symptom is `BATTERY_DRAIN_POWER_CONSUMPTION`, not an OS crash.')
    md.append('- **Security Precedence:** If account compromise or fraud is the focal grievance (*"Someone hacked my Apple ID and locked me out"*), classify as `SECURITY_PHISHING_SUSPICIOUS_CONTACT`. If routine password reset or device lock, classify as `ACCOUNT_APPLE_ID_ACCESS`.')
    md.append('')
    md.append('### 2. The Deterministic Tie-Breaker Ladder (Secondary Use Only)')
    md.append('The 9-level priority ladder is **NOT** an automatic semantic severity override. It must **ONLY** be invoked when two candidate intents remain genuinely tied in customer emphasis:')
    md.append('1. `SECURITY_PHISHING_SUSPICIOUS_CONTACT`')
    md.append('2. `ACCOUNT_APPLE_ID_ACCESS`')
    md.append('3. `DEVICE_FREEZE_CRASH_REBOOT`')
    md.append('4. `DATA_LOSS_RECOVERY`')
    md.append('5. `BILLING_CHARGE_REFUND_DISPUTE`')
    md.append('6. `ORDER_PURCHASE_SHIPPING_STATUS`')
    md.append('7. `SCREEN_DISPLAY_TOUCH_BIOMETRICS`')
    md.append('8. `HARDWARE_CHARGING_POWER_CABLE`')
    md.append('9. `CONNECTIVITY_WIFI_BLUETOOTH` / `AUDIO_SOUND_SPEAKER_MIC` / `KEYBOARD_TYPING_AUTOCORRECT_ISSUE` / `BATTERY_DRAIN_POWER_CONSUMPTION` / `PERFORMANCE_SLOWDOWN_LATENCY` / `APP_SPECIFIC_MALFUNCTION`')
    md.append('')
    md.append('### 3. Special Boundary & Intent Definitions')
    md.append('- **`SCREEN_DISPLAY_TOUCH_BIOMETRICS`:** Encompasses all physical display glass/panel defects (lines, flicker, dead pixels, black display with audio active), touch digitizer anomalies (unresponsive touch, ghost touches), and biometric sensors (Face ID setup/failure, Touch ID sensor failure).')
    md.append('- **`AUDIO_SOUND_SPEAKER_MIC`:** Formally encompasses speaker distortion, receiver crackling, microphone failure, headphone jack/AirPods audio routing, volume controls, alarm/ringer volume levels, and physical volume rocker button failure.')
    md.append('- **`UNKNOWN_INSUFFICIENT_CONTEXT`:** Strictly reserved for:')
    md.append('  - **Category A (Non-Support / Commercial Promo):** Marketing retweets, spam, advertising, keynote event broadcasts.')
    md.append('  - **Category B (Insufficient Context):** Bare pleas for help (*"Help please"*, *"DM me"*), media/URL attachments with no textual diagnostic symptom, or symptomless emotional frustration rants (*"iOS 11 sucks fix your shit"*).')
    md.append('  - **Negative Constraint:** If *any* technical component, hardware symptom, error code, or specific service is named (even colloquially), DO NOT classify as UNKNOWN.')
    md.append('')
    md.append('### 4. Review Decision Options')
    md.append('For each case below, mark your assessment:')
    md.append('- `[ ACCEPT ]`: Proposed candidate intent correctly captures customer focal grievance.')
    md.append('- `[ REJECT ]`: Proposed candidate intent is incorrect; specify the `Corrected Intent`.')
    md.append('- `[ UNCERTAIN ]`: Borderline ambiguity requiring committee discussion; provide notes.')
    md.append('')
    md.append('---')
    md.append('')

    # Part 1
    md.append('## Part 1: Candidate Intent Cases (120 Inquiries: 8 per Intent x 15 Intents)')
    md.append('')
    case_num = 1
    current_intent = None
    for item in sample_data['part_1_candidate_intents']:
        if item['candidate_intent'] != current_intent:
            current_intent = item['candidate_intent']
            md.append(f'### Intent: `{current_intent}`')
            md.append('')
        md.append(f'#### Case {case_num:03d} | Tweet ID: `{item["tweet_id"]}` | Conv ID: `{item["conversation_id"]}`')
        md.append(f'**Candidate Intent:** `{item["candidate_intent"]}`  ')
        md.append(f'**Customer Inquiry Text:**')
        md.append(f'> "{item["text"]}"')
        md.append('')
        md.append('- **Human Decision:** `[ ACCEPT | REJECT | UNCERTAIN ]`')
        md.append('- **Corrected Intent (if REJECT):** `[ ]`')
        md.append('- **Reviewer Notes:** `[ ]`')
        md.append('')
        case_num += 1

    md.append('---')
    md.append('')

    # Part 2
    md.append('## Part 2: Boundary & Confusion Pair Cases (35 Inquiries: 5 per Pair x 7 Pairs)')
    md.append('')
    current_pair = None
    for item in sample_data['part_2_boundary_cases']:
        if item['tested_pair'] != current_pair:
            current_pair = item['tested_pair']
            md.append(f'### Confusable Pair: `{current_pair}`')
            md.append(f'**Intent A:** `{item["intent_a"]}` | **Intent B:** `{item["intent_b"]}`  ')
            md.append(f'**Deterministic Distinguishing Rule:** {item["deterministic_rule"]}  ')
            md.append('')
        md.append(f'#### Case {case_num:03d} | Tweet ID: `{item["tweet_id"]}` | Conv ID: `{item["conversation_id"]}`')
        md.append(f'**Pair Under Test:** `{item["tested_pair"]}`  ')
        md.append(f'**Customer Inquiry Text:**')
        md.append(f'> "{item["text"]}"')
        md.append('')
        md.append(f'- **Proposed Pair:** `{item["intent_a"]}` vs `{item["intent_b"]}`')
        md.append('- **Human Decision:** `[ INTENT A | INTENT B | REJECT BOTH | UNCERTAIN ]`')
        md.append('- **Focal Grievance Identified:** `[ ]`')
        md.append('- **Reviewer Notes:** `[ ]`')
        md.append('')
        case_num += 1

    md.append('---')
    md.append('')

    # Part 3
    md.append('## Part 3: UNKNOWN / Insufficient Context Cases (15 Inquiries)')
    md.append('')
    md.append('Stratified across Category A (4 cases), Category B1 Bare Pleas (4 cases), Category B2 Media Links (4 cases), and Category B3 Symptomless Rants (3 cases).')
    md.append('')
    for item in sample_data['part_3_unknown_cases']:
        md.append(f'#### Case {case_num:03d} | Tweet ID: `{item["tweet_id"]}` | Conv ID: `{item["conversation_id"]}`')
        md.append(f'**Sampled Category:** `{item["category"]}`  ')
        md.append(f'**Non-Technical Justification:** {item["reason_not_technical"]}  ')
        md.append(f'**Customer Inquiry Text:**')
        md.append(f'> "{item["text"]}"')
        md.append('')
        md.append('- **Human Decision:** `[ ACCEPT UNKNOWN | REJECT (ASSIGN INTENT) | UNCERTAIN ]`')
        md.append('- **Corrected Intent (if REJECT):** `[ ]`')
        md.append('- **Reviewer Notes:** `[ ]`')
        md.append('')
        case_num += 1

    output_text = '\n'.join(md) + '\n'
    with open('reports/taxonomy_human_review_sample.md', 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f'Generated reports/taxonomy_human_review_sample.md successfully with {len(md)} lines.')

if __name__ == '__main__':
    main()
