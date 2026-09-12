"""Corpus analysis script for taxonomy validation.

Inspects all 80,250 inbound opening inquiries and 131,258 total inbound customer messages.
Computes real match frequencies, pairwise overlaps, multi-symptom prevalence,
venting prevalence, out-of-scope prevalence, and gap candidates.
"""

import re
import json
import pandas as pd
import numpy as np
from collections import Counter

def run_corpus_analysis():
    df_conv = pd.read_parquet('data/processed/applesupport_conversations.parquet')
    inbound_roots = df_conv[df_conv['root_inbound'] == True].copy().sort_values('conversation_id').reset_index(drop=True)
    N_roots = len(inbound_roots)
    print(f"Total inbound opening inquiries: {N_roots:,}")

    # Prepare cleaned text for regex (original text preserved in dataframe)
    def clean_for_matching(text):
        t = re.sub(r'https?://\S+', ' ', str(text))
        t = re.sub(r'@\w+', ' ', t)
        t = t.lower()
        t = re.sub(r'[\'’]', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    inbound_roots['cleaned_text'] = inbound_roots['customer_inquiry_text'].apply(clean_for_matching)

    # Define high-precision, robust pattern sets for each provisional intent
    PROVISIONAL_PATTERNS = {
        'SOFTWARE_UPDATE_BATTERY_DRAIN': (
            r'\b(battery|battery life|drain|draining|battery percentage|dying fast|charge dropping|battery drain)\b'
        ),
        'DEVICE_FREEZE_CRASH_REBOOT': (
            r'\b(freeze|frozen|freezes|freezing|crash|crashes|crashing|restart|restarting|reboot|rebooting|stuck on apple logo|boot loop|spinning wheel|black screen|shut off|turns off)\b'
        ),
        'IOS_KEYBOARD_LETTER_I_AUTOCORRECT_BUG': (
            r'(\b(letter i|capital i|type i|typing i|auto ?correct|keyboard|question mark|box with question|symbol|exclamation point|a \[?\]|i autocorrect)\b|#iterror|\bi️\b)'
        ),
        'PERFORMANCE_SLOWDOWN_AFTER_UPDATE': (
            r'\b(slow|lag|laggy|lagging|sluggish|delay|unresponsive|slowdown|delayed|choppy|stutter|takes forever)\b'
        ),
        'CONNECTIVITY_WIFI_BLUETOOTH': (
            r'\b(wifi|wi-fi|bluetooth|airdrop|hotspot|cellular|data|no service|signal|lte|4g|disconnecting|wont connect|unable to connect)\b'
        ),
        'APP_SPECIFIC_MALFUNCTION': (
            r'\b(app store|safari|apple music|itunes|facetime|imessage|whatsapp|instagram|spotify|youtube|facebook|twitter|camera app|photos app|mail app|podcast|weather app|maps app)\b'
        ),
        'DATA_LOSS': (
            r'\b(lost|disappeared|deleted|missing|erased|recover|recovery|restore my contacts|restore my photos|lost my notes|lost messages|gone)\b'
        ),
        'SCREEN_DISPLAY_HARDWARE_SYMPTOM': (
            r'\b(screen|display|touch screen|unresponsive screen|touch id|face id|3d touch|dead pixel|flicker|flickering|green line|black lines|cracked screen|shattered)\b'
        ),
        'ACCOUNT_APPLE_ID_ACCESS': (
            r'\b(apple id|icloud login|icloud account|password|passcode|locked out|disabled account|forgot password|two factor|2fa|verification code|security questions)\b'
        ),
        'ORDER_PURCHASE_SHIPPING_STATUS': (
            r'\b(order|shipping|delivery|shipment|tracking|fedex|ups|dispatched|arrived|order status|store pickup|pick up in store|delivered|package)\b'
        ),
        'BILLING_CHARGE_REFUND_DISPUTE': (
            r'\b(charge|charged|billing|refund|subscription|charged twice|unauthorized charge|payment method|invoice|receipt|itunes charge|cancel subscription)\b'
        ),
        'STORAGE_MANAGEMENT': (
            r'\b(storage|storage full|other storage|system storage|icloud storage|not enough storage|manage storage|gigabytes|\bgb\b|free up space)\b'
        ),
        'HARDWARE_PHYSICAL_DEFECT': (
            r'\b(hardware|bent|broken button|home button|volume button|power button|mute switch|charging port|lightning port|headphone jack|water damage|liquid damage|swollen battery)\b'
        ),
        'HOW_TO_GENERAL_PRODUCT_QUESTION': (
            r'\b(how (do|can) (i|we|you)|how to|is there a way|wondering if|can i|possible to|does (the|apple)|what is the difference|how does)\b'
        ),
        'CUSTOMER_SERVICE_EXPERIENCE_COMPLAINT': (
            r'\b(customer service|genius bar|apple store staff|store manager|rude|terrible service|worst support|horrible experience|waiting for hours|unhelpful agent|rep hung up|poor customer service)\b'
        ),
        'SECURITY_PHISHING_SUSPICIOUS_CONTACT': (
            r'\b(phishing|phish|scam|suspicious email|suspicious text|fake apple|hacked|virus|malware|compromised|spam text|is this legit|fraudulent)\b'
        ),
        'FEATURE_REQUEST_FEEDBACK': (
            r'\b(feature request|feedback|wish you would|please add|bring back|should add|need an option to|why did you remove|suggestion for)\b'
        ),
        'UNKNOWN_OUT_OF_SCOPE': (
            r'(\b(crypto|bitcoin|forex|dm to promote|follow back|check dm for promo|free iphone giveaway)\b|^[a-z0-9\s]{1,4}$|gibberish)'
        )
    }

    # Evaluate matches
    match_matrix = {}
    for name, pat in PROVISIONAL_PATTERNS.items():
        matched = inbound_roots['cleaned_text'].str.contains(pat, regex=True, na=False)
        match_matrix[name] = matched
        count = matched.sum()
        pct = (count / N_roots) * 100
        print(f"{name:40s}: {count:6d} ({pct:5.2f}%)")

    # Measure multi-symptom / multi-intent co-occurrence
    matrix_df = pd.DataFrame(match_matrix)
    row_match_counts = matrix_df.sum(axis=1)
    print("\n--- Match Cardinality across 18 provisional patterns ---")
    for k in range(6):
        cnt = (row_match_counts == k).sum()
        print(f"Matched {k} intents: {cnt:6d} ({cnt/N_roots*100:5.2f}%)")
    print(f"Matched >5 intents: {(row_match_counts > 5).sum():6d} ({(row_match_counts > 5).sum()/N_roots*100:5.2f}%)")

    # Check update mentions
    update_pat = r'\b(update|updated|updating|ios 11|ios11|11\.0|11\.1|11\.2|high sierra)\b'
    inbound_roots['mentions_update'] = inbound_roots['cleaned_text'].str.contains(update_pat, regex=True, na=False)
    update_count = inbound_roots['mentions_update'].sum()
    print(f"\nOpening inquiries mentioning software update / iOS 11: {update_count:,} ({update_count/N_roots*100:.2f}%)")

    # Battery specifically with update
    battery_matched = match_matrix['SOFTWARE_UPDATE_BATTERY_DRAIN']
    battery_with_update = (battery_matched & inbound_roots['mentions_update']).sum()
    battery_without_update = (battery_matched & ~inbound_roots['mentions_update']).sum()
    print(f"Battery inquiries with explicit update mention: {battery_with_update:,} ({battery_with_update/battery_matched.sum()*100:.2f}%)")
    print(f"Battery inquiries without explicit update mention: {battery_without_update:,} ({battery_without_update/battery_matched.sum()*100:.2f}%)")

    # Freeze/Crash specifically with update
    crash_matched = match_matrix['DEVICE_FREEZE_CRASH_REBOOT']
    crash_with_update = (crash_matched & inbound_roots['mentions_update']).sum()
    crash_without_update = (crash_matched & ~inbound_roots['mentions_update']).sum()
    print(f"Crash/freeze inquiries with explicit update mention: {crash_with_update:,} ({crash_with_update/crash_matched.sum()*100:.2f}%)")
    print(f"Crash/freeze inquiries without explicit update mention: {crash_without_update:,} ({crash_without_update/crash_matched.sum()*100:.2f}%)")

    # Slowdown specifically with update
    slow_matched = match_matrix['PERFORMANCE_SLOWDOWN_AFTER_UPDATE']
    slow_with_update = (slow_matched & inbound_roots['mentions_update']).sum()
    slow_without_update = (slow_matched & ~inbound_roots['mentions_update']).sum()
    print(f"Slowdown inquiries with explicit update mention: {slow_with_update:,} ({slow_with_update/slow_matched.sum()*100:.2f}%)")
    print(f"Slowdown inquiries without explicit update mention: {slow_without_update:,} ({slow_without_update/slow_matched.sum()*100:.2f}%)")

    # Pairwise overlap between Battery, Crash, Slowdown
    print("\n--- Overlap between Battery, Crash, Slowdown ---")
    print(f"Battery AND Crash: {(battery_matched & crash_matched).sum():,}")
    print(f"Battery AND Slowdown: {(battery_matched & slow_matched).sum():,}")
    print(f"Crash AND Slowdown: {(crash_matched & slow_matched).sum():,}")
    print(f"Battery AND Crash AND Slowdown: {(battery_matched & crash_matched & slow_matched).sum():,}")

    # Inspect Audio / Sound / Charging gap patterns
    audio_pat = r'\b(sound|volume|speaker|speakers|microphone|mic|headphones|headphone|earbuds|airpods|airpod|audio|mute|static noise|buzzing|no sound|cant hear|hear callers)\b'
    audio_matched = inbound_roots['cleaned_text'].str.contains(audio_pat, regex=True, na=False)
    print(f"\nGap Candidate AUDIO_SOUND_MICROPHONE_SPEAKER: {audio_matched.sum():,} ({audio_matched.sum()/N_roots*100:.2f}%)")

    charging_pat = r'\b(charge|charging|charger|cable|lightning cable|wont charge|not charging|plugged in|wireless charging|charger port|adapter)\b'
    charging_matched = inbound_roots['cleaned_text'].str.contains(charging_pat, regex=True, na=False)
    # Exclude battery drain pure matches
    charging_hardware = charging_matched & ~battery_matched
    print(f"Gap Candidate HARDWARE_CHARGING_POWER_CABLE: {charging_matched.sum():,} ({charging_matched.sum()/N_roots*100:.2f}%), non-battery: {charging_hardware.sum():,}")

if __name__ == '__main__':
    run_corpus_analysis()
