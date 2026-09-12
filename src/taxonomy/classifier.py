"""Intent Classification Pipeline for AppleSupport Customer Inquiries.

Provides high-precision intent classification across the 15-intent canonical taxonomy:
1. BATTERY_DRAIN_POWER_CONSUMPTION
2. DEVICE_FREEZE_CRASH_REBOOT
3. KEYBOARD_TYPING_AUTOCORRECT_ISSUE
4. PERFORMANCE_SLOWDOWN_LATENCY
5. CONNECTIVITY_WIFI_BLUETOOTH
6. APP_SPECIFIC_MALFUNCTION
7. DATA_LOSS_RECOVERY
8. SCREEN_DISPLAY_TOUCH_BIOMETRICS
9. HARDWARE_CHARGING_POWER_CABLE
10. AUDIO_SOUND_SPEAKER_MIC
11. ACCOUNT_APPLE_ID_ACCESS
12. BILLING_CHARGE_REFUND_DISPUTE
13. ORDER_PURCHASE_SHIPPING_STATUS
14. SECURITY_PHISHING_SUSPICIOUS_CONTACT
15. UNKNOWN_INSUFFICIENT_CONTEXT
"""

import re
from typing import Dict, Any, List, Optional, Tuple

VALID_INTENTS = [
    "BATTERY_DRAIN_POWER_CONSUMPTION",
    "DEVICE_FREEZE_CRASH_REBOOT",
    "KEYBOARD_TYPING_AUTOCORRECT_ISSUE",
    "PERFORMANCE_SLOWDOWN_LATENCY",
    "CONNECTIVITY_WIFI_BLUETOOTH",
    "APP_SPECIFIC_MALFUNCTION",
    "DATA_LOSS_RECOVERY",
    "SCREEN_DISPLAY_TOUCH_BIOMETRICS",
    "HARDWARE_CHARGING_POWER_CABLE",
    "AUDIO_SOUND_SPEAKER_MIC",
    "ACCOUNT_APPLE_ID_ACCESS",
    "BILLING_CHARGE_REFUND_DISPUTE",
    "ORDER_PURCHASE_SHIPPING_STATUS",
    "SECURITY_PHISHING_SUSPICIOUS_CONTACT",
    "UNKNOWN_INSUFFICIENT_CONTEXT"
]

# Secondary tie-breaker priority ladder
PRIORITY_LADDER = [
    "SECURITY_PHISHING_SUSPICIOUS_CONTACT",
    "ACCOUNT_APPLE_ID_ACCESS",
    "DEVICE_FREEZE_CRASH_REBOOT",
    "DATA_LOSS_RECOVERY",
    "BILLING_CHARGE_REFUND_DISPUTE",
    "ORDER_PURCHASE_SHIPPING_STATUS",
    "SCREEN_DISPLAY_TOUCH_BIOMETRICS",
    "HARDWARE_CHARGING_POWER_CABLE",
    "CONNECTIVITY_WIFI_BLUETOOTH",
    "AUDIO_SOUND_SPEAKER_MIC",
    "KEYBOARD_TYPING_AUTOCORRECT_ISSUE",
    "BATTERY_DRAIN_POWER_CONSUMPTION",
    "PERFORMANCE_SLOWDOWN_LATENCY",
    "APP_SPECIFIC_MALFUNCTION",
    "UNKNOWN_INSUFFICIENT_CONTEXT"
]

# Core diagnostic patterns for each intent
INTENT_PATTERNS = {
    "SECURITY_PHISHING_SUSPICIOUS_CONTACT": [
        r"\b(?:phish|phishing|scam|scammer|hacked|hackers?|compromised|suspicious\s+(?:email|text|message|call)|unauthorized\s+access|fraud)\b"
    ],
    "ACCOUNT_APPLE_ID_ACCESS": [
        r"\b(?:apple\s*id|icloud\s+account|itunes\s+account|two\s*factor|2fa|verification\s+code|locked\s+out|account\s+disabled|reset\s+(?:my\s+)?password|forgot\s+(?:my\s+)?password|security\s+questions?)\b"
    ],
    "BILLING_CHARGE_REFUND_DISPUTE": [
        r"\b(?:refund|charged|double\s+charge|unauthorized\s+charge|overcharged|subscription|bill|billing|receipt|invoice|itunes\s+purchase|credit\s+card|money\s+back|cancel\s+(?:my\s+)?subscription)\b"
    ],
    "ORDER_PURCHASE_SHIPPING_STATUS": [
        r"\b(?:shipping|delivery|track(?:ing)?\s+number|order\s+status|order\s+number|carrier|dispatched|courier|ups|fedex|shipment|store\s+pickup|when\s+will\s+it\s+arrive)\b"
    ],
    "DATA_LOSS_RECOVERY": [
        r"\b(?:lost\s+all\s+(?:my\s+)?(?:photos|contacts|data|notes|messages)|photos\s+disappeared|recover\s+(?:my\s+)?(?:data|photos|deleted)|how\s+do\s+i\s+recover|restore\s+backup|backup\s+recovery)\b"
    ],
    "HARDWARE_CHARGING_POWER_CABLE": [
        r"\b(?:won'?t\s+charge|not\s+charging|stops?\s+charging|charging\s+port|charger|lightning\s+cable|cable\s+frayed|wireless\s+charger|magsafe|plugged\s+in\s+but\s+not)\b"
    ],
    "BATTERY_DRAIN_POWER_CONSUMPTION": [
        r"\b(?:battery(?:\s+\w+){0,2}\s+(?:drain|draining|drained|dies|dying|dead|low|percentage|capacity|consumption|dropping|issue|problem)|overheating|phone\s+gets\s+hot|battery\s+health)\b"
    ],
    "KEYBOARD_TYPING_AUTOCORRECT_ISSUE": [
        r"\b(?:keyboard|autocorrect|auto\s*correct|typing|predictive\s+text|symbol\s+appears|letter\s+i\b|capital\s+a\b|\ba\s*\[\?\]|\bi\s*\[\?\]|dictation)\b"
    ],
    "SCREEN_DISPLAY_TOUCH_BIOMETRICS": [
        r"\b(?:screen|display|touch\s*id|face\s*id|touch\s+screen|digitizer|dead\s+pixels?|black\s+screen|lines?\s+on\s+screen|ghost\s+touch|unresponsive\s+touch|screen\s+flicker)\b"
    ],
    "AUDIO_SOUND_SPEAKER_MIC": [
        r"\b(?:speaker|microphone|mic\b|volume|sound|audio|earpiece|crackling|distorted\s+sound|no\s+sound|ringer|alarm\s+too\s+quiet|can'?t\s+hear\s+call)\b"
    ],
    "CONNECTIVITY_WIFI_BLUETOOTH": [
        r"\b(?:wi-?fi|wifi|bluetooth|airdrop|cellular|no\s+service|searching\.\.\.|lte|hotspot|personal\s+hotspot|network\s+settings|disconnects?\s+from\s+wi-?fi)\b"
    ],
    "DEVICE_FREEZE_CRASH_REBOOT": [
        r"\b(?:freezes?|frozen|crashing|reboot(?:s|ing)?|boot\s*loop|stuck\s+on\s+apple\s+logo|randomly\s+restarts?|bricked|black\s+screen\s+of\s+death|spinning\s+wheel)\b"
    ],
    "PERFORMANCE_SLOWDOWN_LATENCY": [
        r"\b(?:lag|lagging|laggy|slow|sluggish|latency|delayed|unresponsive\s+phone|takes\s+forever\s+to\s+open|stutters?)\b"
    ],
    "APP_SPECIFIC_MALFUNCTION": [
        r"\b(?:safari|itunes|app\s+store|apple\s+music|maps|podcasts|imessage|facetime|whatsapp|spotify|twitter|instagram|youtube|camera\s+app)\b.*?\b(?:crashes?|not\s+working|won'?t\s+open|glitch)\b"
    ]
}

# UNKNOWN indicators
UNKNOWN_PROMO_PATTERNS = [
    r"https?://t\.co/\w+",
    r"\b(?:retweet|rt\b|giveaway|promo|stream|listen\s+live|check\s+out\s+my)\b"
]


class IntentClassifier:
    """Deterministic, explainable rule-and-focal-grievance intent classifier."""

    def __init__(self, valid_intents: Optional[List[str]] = None):
        self.valid_intents = valid_intents or VALID_INTENTS
        self.priority_ladder = PRIORITY_LADDER

    def classify(self, text: str) -> Dict[str, Any]:
        """Classify customer text into canonical intent with confidence score and reasoning."""
        if not text or not text.strip():
            return {
                "intent": "UNKNOWN_INSUFFICIENT_CONTEXT",
                "confidence": 0.99,
                "focal_grievance": "Empty or missing inquiry text",
                "matched_intents": [],
                "decision_rule": "EMPTY_TEXT_FALLBACK",
                "ambiguity_flag": False
            }

        # Normalize unicode quotes and dashes
        cleaned = text.strip().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        lower = cleaned.lower()

        # Check for Category B UNKNOWN: Bare plea or symptomless rant
        words = re.findall(r"\b\w+\b", lower)
        has_question_or_diagnostic = any(
            w in lower for w in ["why", "how", "fix", "help", "broken", "issue", "problem", "error", "won't", "can't"]
        )
        
        # Check specific intent pattern matches
        matched: List[Tuple[str, int]] = []
        for intent, patterns in INTENT_PATTERNS.items():
            match_score = 0
            for pat in patterns:
                finds = re.findall(pat, lower, re.IGNORECASE)
                if finds:
                    match_score += len(finds) * 2
            if match_score > 0:
                matched.append((intent, match_score))

        # Sort matched intents by score descending
        matched.sort(key=lambda x: x[1], reverse=True)

        # Multi-symptom resolution: Critical Boundaries
        # 1. Battery vs Charging
        if any(m[0] == "BATTERY_DRAIN_POWER_CONSUMPTION" for m in matched) and any(m[0] == "HARDWARE_CHARGING_POWER_CABLE" for m in matched):
            if re.search(r"\b(?:won'?t\s+charge|cable|charger|port)\b", lower):
                # Actionable need is replenishment
                primary = "HARDWARE_CHARGING_POWER_CABLE"
            else:
                primary = "BATTERY_DRAIN_POWER_CONSUMPTION"
            matched = [(primary, 5)] + [m for m in matched if m[0] != primary]

        # 2. Crash vs Performance
        if any(m[0] == "DEVICE_FREEZE_CRASH_REBOOT" for m in matched) and any(m[0] == "PERFORMANCE_SLOWDOWN_LATENCY" for m in matched):
            if re.search(r"\b(?:freeze|frozen|reboot|restart|crash)\b", lower):
                primary = "DEVICE_FREEZE_CRASH_REBOOT"
            else:
                primary = "PERFORMANCE_SLOWDOWN_LATENCY"
            matched = [(primary, 5)] + [m for m in matched if m[0] != primary]

        # 3. Data Loss vs Others
        if any(m[0] == "DATA_LOSS_RECOVERY" for m in matched):
            if re.search(r"\b(?:recover|lost\s+all|disappeared|how\s+can\s+i\s+get\s+back)\b", lower):
                matched = [("DATA_LOSS_RECOVERY", 6)] + [m for m in matched if m[0] != "DATA_LOSS_RECOVERY"]

        # If no patterns matched: determine if UNKNOWN
        if not matched:
            return {
                "intent": "UNKNOWN_INSUFFICIENT_CONTEXT",
                "confidence": 0.85,
                "focal_grievance": "Inquiry lacks actionable technical symptom or named product defect",
                "matched_intents": [],
                "decision_rule": "NO_SUPPORTED_INTENT_PATTERN_MATCH",
                "ambiguity_flag": False
            }

        # Select top intent
        top_intent, top_score = matched[0]
        
        # Tie breaking via Priority Ladder if top scores are equal
        ambiguity = False
        if len(matched) > 1 and matched[1][1] == top_score:
            ambiguity = True
            # Find which has higher priority on ladder
            top_intent = min([matched[0][0], matched[1][0]], key=lambda x: self.priority_ladder.index(x))

        # Confidence calculation
        if len(matched) == 1:
            confidence = 0.92
        elif matched[0][1] >= matched[1][1] * 2:
            confidence = 0.88
        else:
            confidence = 0.65

        # Short focal grievance
        grievance_map = {
            "BATTERY_DRAIN_POWER_CONSUMPTION": "Unusually rapid battery discharge or power loss",
            "DEVICE_FREEZE_CRASH_REBOOT": "Device freezing, unexpected restart, or boot crash",
            "KEYBOARD_TYPING_AUTOCORRECT_ISSUE": "Typing, autocorrect, or keyboard rendering glitch",
            "PERFORMANCE_SLOWDOWN_LATENCY": "System lag, interface latency, or slow responsiveness",
            "CONNECTIVITY_WIFI_BLUETOOTH": "Wireless, Wi-Fi, or Bluetooth connectivity failure",
            "APP_SPECIFIC_MALFUNCTION": "Specific application crash or operational defect",
            "DATA_LOSS_RECOVERY": "Missing data recovery or deleted content retrieval",
            "SCREEN_DISPLAY_TOUCH_BIOMETRICS": "Display panel, touch digitizer, or biometric sensor anomaly",
            "HARDWARE_CHARGING_POWER_CABLE": "Inability to charge device, cable, or port defect",
            "AUDIO_SOUND_SPEAKER_MIC": "Speaker distortion, microphone, or audio routing issue",
            "ACCOUNT_APPLE_ID_ACCESS": "Apple ID login, password, or account lockout access issue",
            "BILLING_CHARGE_REFUND_DISPUTE": "Disputed purchase, refund request, or billing inquiry",
            "ORDER_PURCHASE_SHIPPING_STATUS": "Online order tracking, dispatch, or delivery status",
            "SECURITY_PHISHING_SUSPICIOUS_CONTACT": "Suspected phishing, security breach, or scam attempt",
            "UNKNOWN_INSUFFICIENT_CONTEXT": "Inquiry lacks sufficient context for technical routing"
        }

        return {
            "intent": top_intent,
            "confidence": round(confidence, 2),
            "focal_grievance": grievance_map.get(top_intent, "Customer support inquiry"),
            "matched_intents": [m[0] for m in matched],
            "decision_rule": "FOCAL_GRIEVANCE_PRIMARY_MATCH" if not ambiguity else "PRIORITY_LADDER_TIE_BREAKER",
            "ambiguity_flag": ambiguity
        }
