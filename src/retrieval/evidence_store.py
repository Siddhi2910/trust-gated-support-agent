"""Provenance-Aware Evidence Store for AppleSupport RAG System.

Maintains curated support evidence and troubleshooting guidelines with full audit
provenance, verification status, and promotion controls.

Evidence Sources:
1. HISTORICAL_APPLESUPPORT_REPLY: Primary support evidence from verified TWCS interactions.
2. OFFICIAL_KB: Supplementary official Apple Knowledge Base articles for technical specifications.

Evidence Lifecycle:
CANDIDATE -> REVIEW_REQUIRED -> TRUSTED -> RETIRED / REJECTED
Only TRUSTED / VERIFIED evidence can support autonomous resolution (AUTO_RESOLVE).
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Primary Historical AppleSupport Interactions from TWCS Dataset
HISTORICAL_APPLESUPPORT_EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "TWCS-EVID-BATT-11625",
        "intent": "BATTERY_DRAIN_POWER_CONSUMPTION",
        "title": "AppleSupport Historical Reply: Post-Update Battery Optimization & Diagnostics",
        "body": "We'd like to help with your battery. Following an iOS update, your device completes background indexing and updates. Check Settings > Battery to see which apps are using the most battery life. Let us know if you see any battery health recommendations.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-11625",
        "source_tweet_id": 11625,
        "source_conversation_id": 11624,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["battery", "drain", "indexing", "settings", "battery health", "ios"]
    },
    {
        "evidence_id": "TWCS-EVID-FREEZE-50616",
        "intent": "DEVICE_FREEZE_CRASH_REBOOT",
        "title": "AppleSupport Historical Reply: Force Restart for Freezing/Crashing",
        "body": "Let's work together to stop those crashes. Have you tried a force restart? Press and quickly release Volume Up, then Volume Down, and press and hold the Side power button until the Apple logo appears.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-50616",
        "source_tweet_id": 50616,
        "source_conversation_id": 50615,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["freeze", "crash", "reboot", "restart", "apple logo", "side button"]
    },
    {
        "evidence_id": "TWCS-EVID-KEYB-5836",
        "intent": "KEYBOARD_TYPING_AUTOCORRECT_ISSUE",
        "title": "AppleSupport Historical Reply: Letter 'I' Autocorrect Workaround",
        "body": "We're here to help with your keyboard. Go to Settings > General > Keyboard > Text Replacement. Tap the plus icon and enter uppercase 'I' for Phrase and lowercase 'i' for Shortcut as a workaround.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-5836",
        "source_tweet_id": 5836,
        "source_conversation_id": 5835,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["keyboard", "autocorrect", "text replacement", "typing", "letter i", "symbol"]
    },
    {
        "evidence_id": "TWCS-EVID-WIFI-90662",
        "intent": "CONNECTIVITY_WIFI_BLUETOOTH",
        "title": "AppleSupport Historical Reply: Reset Network Settings for Wi-Fi/Bluetooth Drops",
        "body": "Let's get your connection working properly. Try forgetting the network in Settings > Wi-Fi, toggle Airplane Mode for 15 seconds, and if needed reset network settings in Settings > General > Reset > Reset Network Settings.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-90662",
        "source_tweet_id": 90662,
        "source_conversation_id": 90661,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["wifi", "wi-fi", "bluetooth", "network settings", "connectivity", "reset"]
    },
    {
        "evidence_id": "TWCS-EVID-APP-520208",
        "intent": "APP_SPECIFIC_MALFUNCTION",
        "title": "AppleSupport Historical Reply: App Crashing & Force Quit Procedure",
        "body": "We'd like to get that app running smoothly. Try force closing the app from the app switcher, restart your device, and check the App Store to make sure you have installed the newest update for the app.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-520208",
        "source_tweet_id": 520208,
        "source_conversation_id": 520207,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["app crash", "crashing", "app switcher", "force close", "app store", "update"]
    },
    {
        "evidence_id": "TWCS-EVID-DATA-320925",
        "intent": "DATA_LOSS_RECOVERY",
        "title": "AppleSupport Historical Reply: Missing Messages & Photos Recovery Guidance",
        "body": "We understand how important your data is. Sign in to iCloud.com from a browser to check if your items are safely stored there, and check the Recently Deleted folder in Photos. If you have an iCloud backup, you can restore from it in Settings.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-320925",
        "source_tweet_id": 320925,
        "source_conversation_id": 320924,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["lost photos", "recovery", "recently deleted", "icloud backup", "restore", "messages"]
    },
    {
        "evidence_id": "TWCS-EVID-SCREEN-34647",
        "intent": "SCREEN_DISPLAY_TOUCH_BIOMETRICS",
        "title": "AppleSupport Historical Reply: Touch Screen Responsiveness & Screen Protector Check",
        "body": "We're happy to help with your display. Make sure the screen is clean and dry, remove any case or screen protector, and disconnect any non-certified charging cables to see if touch responds.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-34647",
        "source_tweet_id": 34647,
        "source_conversation_id": 34646,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["screen", "touch", "unresponsive", "display", "screen protector", "clean"]
    },
    {
        "evidence_id": "TWCS-EVID-CHARG-35266",
        "intent": "HARDWARE_CHARGING_POWER_CABLE",
        "title": "AppleSupport Historical Reply: Lightning Port Debris & Cable Diagnostics",
        "body": "Let's troubleshoot your charging. Check your charging port for any debris or pocket lint using a non-metal pick, inspect your cable for fraying or bent pins, and try a different wall outlet and Apple-certified cable.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-35266",
        "source_tweet_id": 35266,
        "source_conversation_id": 35265,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["charging", "cable", "port", "lightning", "mfi", "debris", "not charging"]
    },
    {
        "evidence_id": "TWCS-EVID-AUDIO-110941",
        "intent": "AUDIO_SOUND_SPEAKER_MIC",
        "title": "AppleSupport Historical Reply: Microphone and Speaker Call Audio Troubleshooting",
        "body": "We can help get your sound working. Test your microphone using Voice Memos to record a short message. Check that the microphone openings on the bottom and back of your iPhone are not blocked by a case or screen protector.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-110941",
        "source_tweet_id": 110941,
        "source_conversation_id": 110940,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["microphone", "speaker", "sound", "audio", "call", "voice memos", "hear"]
    },
    {
        "evidence_id": "TWCS-EVID-ACCT-6555",
        "intent": "ACCOUNT_APPLE_ID_ACCESS",
        "title": "AppleSupport Historical Reply: Apple ID Password Reset via iforgot.apple.com",
        "body": "For your security, we cannot reset your Apple ID password or access account details over Twitter. Please go to iforgot.apple.com to reset your password or check your account recovery status securely.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-6555",
        "source_tweet_id": 6555,
        "source_conversation_id": 6554,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["apple id", "password", "locked", "disabled", "iforgot", "security", "recovery"]
    },
    {
        "evidence_id": "TWCS-EVID-BILL-149948",
        "intent": "BILLING_CHARGE_REFUND_DISPUTE",
        "title": "AppleSupport Historical Reply: Subscription Cancellation & reportaproblem.apple.com Refund",
        "body": "We can help direct you to request a refund. Go to reportaproblem.apple.com and sign in with your Apple ID. From there, select 'Request a refund' and choose the item and reason. You can also review active subscriptions under Settings.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-149948",
        "source_tweet_id": 149948,
        "source_conversation_id": 149947,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["refund", "billing", "charge", "subscription", "report a problem", "money back"]
    },
    {
        "evidence_id": "TWCS-EVID-ORD-11646",
        "intent": "ORDER_PURCHASE_SHIPPING_STATUS",
        "title": "AppleSupport Historical Reply: Online Store Order Tracking & Shipping Confirmation",
        "body": "You can track your order status and shipment anytime at apple.com/orderstatus with your Apple ID or Web Order Number. Tracking updates appear as soon as the carrier scans the package for delivery.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-11646",
        "source_tweet_id": 11646,
        "source_conversation_id": 11645,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["order", "shipping", "tracking", "delivery", "carrier", "order status"]
    },
    {
        "evidence_id": "TWCS-EVID-SEC-92532",
        "intent": "SECURITY_PHISHING_SUSPICIOUS_CONTACT",
        "title": "AppleSupport Historical Reply: Reporting Phishing & Scam Forwarding",
        "body": "Apple will never ask for your Apple ID password or verification codes in a message. Please forward any suspicious emails or messages to reportphishing@apple.com. Never click links or provide credentials on unverified websites.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-92532",
        "source_tweet_id": 92532,
        "source_conversation_id": 92531,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["phishing", "scam", "suspicious", "security", "compromised", "fraud", "report"]
    },
    {
        "evidence_id": "TWCS-EVID-PERF-8300",
        "intent": "PERFORMANCE_SLOWDOWN_LATENCY",
        "title": "AppleSupport Historical Reply: iPhone Storage Check for Lag and Latency",
        "body": "We'd like to get your device running quickly again. Check Settings > General > iPhone Storage to make sure you have at least a few gigabytes of available storage. Also ensure your device is running the latest iOS update.",
        "source_type": "HISTORICAL_APPLESUPPORT_REPLY",
        "source_reference": "TWCS-8300",
        "source_tweet_id": 8300,
        "source_conversation_id": 8299,
        "source_author": "@AppleSupport",
        "verification_status": "TRUSTED",
        "verified_by": "historical_corpus_curator",
        "verified_at": "2026-09-11T10:00:00Z",
        "tags": ["slow", "lag", "storage", "latency", "sluggish", "performance", "speed"]
    }
]

# Supplementary Official Knowledge Base Evidence (Technical Specs / Safety Escalation Docs)
SUPPLEMENTARY_OFFICIAL_KB: List[Dict[str, Any]] = [
    {
        "evidence_id": "EVID-BATT-001",
        "intent": "BATTERY_DRAIN_POWER_CONSUMPTION",
        "title": "Official KB: Post-Update Battery Drain Diagnostic & Indexing",
        "body": "Following an iOS update, background Spotlight indexing and photo library analysis can increase battery drain for 48-72 hours. Check Settings > Battery to identify top energy-consuming apps. Ensure Low Power Mode is used during intensive periods.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201264",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["battery", "drain", "update", "ios", "low power mode"]
    },
    {
        "evidence_id": "EVID-CHARG-001",
        "intent": "HARDWARE_CHARGING_POWER_CABLE",
        "title": "Official KB: Lightning / USB-C Charging Port & Cable Diagnostics",
        "body": "Inspect the Lightning or USB-C port for pocket lint or debris using a non-conductive pick. Test with an Apple-certified MFi cable and a secondary wall adapter. If charging stops at 80%, check if Optimized Battery Charging is active.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201569",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["charging", "cable", "port", "lightning", "mfi", "debris"]
    },
    {
        "evidence_id": "EVID-FREEZE-001",
        "intent": "DEVICE_FREEZE_CRASH_REBOOT",
        "title": "Official KB: Force Restart Procedure for Unresponsive iOS Devices",
        "body": "For iPhone 8 and later: Quickly press and release Volume Up, quickly press and release Volume Down, then press and hold the Side power button until the Apple logo appears. Do not release until the screen reboots.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201412",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["freeze", "frozen", "force restart", "crash", "reboot", "apple logo"]
    },
    {
        "evidence_id": "EVID-KEYB-001",
        "intent": "KEYBOARD_TYPING_AUTOCORRECT_ISSUE",
        "title": "Official KB: iOS 11 Autocorrect & Text Replacement Workaround",
        "body": "If typing the letter 'i' generates an 'A[?]' symbol or strange character, go to Settings > General > Keyboard > Text Replacement. Tap '+' and enter uppercase 'I' for Phrase and lowercase 'i' for Shortcut, or update to the latest iOS patch.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT208240",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["keyboard", "autocorrect", "text replacement", "typing", "symbol"]
    },
    {
        "evidence_id": "EVID-SCREEN-001",
        "intent": "SCREEN_DISPLAY_TOUCH_BIOMETRICS",
        "title": "Official KB: Touch Screen Unresponsiveness and Display Cleanliness",
        "body": "Ensure the screen is clean, free of moisture, and disconnected from third-party chargers that may cause electrical grounding noise. Remove thick case protectors or poorly fitted glass protectors.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201406",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["screen", "touch", "display", "unresponsive", "protector"]
    },
    {
        "evidence_id": "EVID-WIFI-001",
        "intent": "CONNECTIVITY_WIFI_BLUETOOTH",
        "title": "Official KB: Wi-Fi & Bluetooth Network Settings Reset",
        "body": "For persistent disconnections or inability to join Wi-Fi networks: Toggle Airplane Mode for 10 seconds. If unresolved, go to Settings > General > Reset > Reset Network Settings. This removes saved Wi-Fi passwords and restores cellular configuration.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT204051",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["wifi", "wi-fi", "bluetooth", "network settings", "connectivity"]
    },
    {
        "evidence_id": "EVID-ACCT-001",
        "intent": "ACCOUNT_APPLE_ID_ACCESS",
        "title": "Official KB: Apple ID Password Reset & Account Security Access",
        "body": "To regain access to a locked or disabled Apple ID, visit iforgot.apple.com from a trusted device. Enter your Apple ID email, confirm the trusted phone number, and follow on-screen verification prompts. Apple Support advisors cannot reset passwords over social media.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201487",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["apple id", "password", "locked", "disabled", "iforgot", "access"]
    },
    {
        "evidence_id": "EVID-BILL-001",
        "intent": "BILLING_CHARGE_REFUND_DISPUTE",
        "title": "Official KB: Requesting a Refund for App Store & iTunes Purchases",
        "body": "To dispute a charge or request a refund: Sign in to reportaproblem.apple.com with your Apple ID. Select 'I'd like to' > 'Request a refund', choose the reason, and select the item. Refund decisions are typically processed within 48 hours.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT204084",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["refund", "billing", "charge", "subscription", "report a problem", "itunes"]
    },
    {
        "evidence_id": "EVID-SEC-001",
        "intent": "SECURITY_PHISHING_SUSPICIOUS_CONTACT",
        "title": "Official KB: Recognizing Phishing Emails and Suspicious Text Messages",
        "body": "Apple never asks for your Apple ID password, verification codes, or credit card PIN in an email or SMS. Forward suspicious Apple emails to reportphishing@apple.com. Do not click any links or enter credentials on third-party sites.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT204759",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["phishing", "scam", "suspicious", "security", "compromised", "fraud"]
    },
    {
        "evidence_id": "EVID-DATA-001",
        "intent": "DATA_LOSS_RECOVERY",
        "title": "Official KB: Locating Missing Photos or Restoring iCloud Backups",
        "body": "Check the 'Recently Deleted' album in the Photos app (retained for 30 days). Verify that iCloud Photos is enabled in Settings > [Your Name] > iCloud > Photos. If restoring an entire device, verify backup availability at Settings > [Your Name] > iCloud > iCloud Backup.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT205914",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["lost photos", "recovery", "recently deleted", "icloud backup", "restore"]
    },
    {
        "evidence_id": "EVID-AUDIO-001",
        "intent": "AUDIO_SOUND_SPEAKER_MIC",
        "title": "Official KB: Troubleshooting Receiver, Speaker, and Microphone Quality",
        "body": "Check Sound settings to ensure Do Not Disturb is off and Ring/Silent switch is set to ring. Clean receiver mesh gently with a soft brush. For microphone issues during calls, ensure protective film or case is not blocking the microphone openings near the camera and charging port.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT203794",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["speaker", "microphone", "audio", "volume", "sound", "crackling"]
    },
    {
        "evidence_id": "EVID-PERF-001",
        "intent": "PERFORMANCE_SLOWDOWN_LATENCY",
        "title": "Official KB: Managing iOS Storage and Background App Latency",
        "body": "Navigate to Settings > General > iPhone Storage to inspect remaining capacity. If free storage is under 1-2 GB, iOS struggles to cache operations. Offload unused apps and clear browser cache in Settings > Safari.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201656",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["slow", "lag", "storage", "latency", "sluggish", "performance"]
    },
    {
        "evidence_id": "EVID-APP-001",
        "intent": "APP_SPECIFIC_MALFUNCTION",
        "title": "Official KB: Resolving Single App Freezes and Crashing Loops",
        "body": "Force close the app by swiping up from app switcher. Check App Store > Updates to ensure the app is on the latest version compatible with your iOS. If crashing persists, delete and reinstall the app.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT201398",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["app crash", "safari", "force close", "reinstall", "app store"]
    },
    {
        "evidence_id": "EVID-ORD-001",
        "intent": "ORDER_PURCHASE_SHIPPING_STATUS",
        "title": "Official KB: Tracking Apple Online Store Order Status & Delivery",
        "body": "Track your shipment at apple.com/orderstatus using your Apple ID or Web Order Number. Carrier tracking numbers update within 24 hours of package dispatch.",
        "source_type": "OFFICIAL_KB",
        "source_reference": "HT203975",
        "verification_status": "VERIFIED",
        "verified_by": "lead_support_architect",
        "verified_at": "2026-09-10T12:00:00Z",
        "tags": ["order", "shipping", "tracking", "delivery", "dispatch"]
    }
]

# Combined canonical corpus
DEFAULT_VERIFIED_EVIDENCE: List[Dict[str, Any]] = HISTORICAL_APPLESUPPORT_EVIDENCE + SUPPLEMENTARY_OFFICIAL_KB


class EvidenceStore:
    """Manages verified support evidence with full provenance tracking."""

    # Canonical status set
    VALID_STATUSES = {"CANDIDATE", "REVIEW_REQUIRED", "TRUSTED", "VERIFIED", "RETIRED", "REJECTED"}
    TRUSTED_STATUSES = {"TRUSTED", "VERIFIED"}

    def __init__(self, persistence_path: str = "artifacts/evidence_store.json"):
        self.persistence_path = persistence_path
        self.items: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
                return
            except Exception:
                pass
        # Initialize with default verified evidence
        self.items = list(DEFAULT_VERIFIED_EVIDENCE)
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.persistence_path) or ".", exist_ok=True)
        with open(self.persistence_path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, indent=2)

    def get_all(self, only_verified: bool = True) -> List[Dict[str, Any]]:
        """Retrieve evidence items. When only_verified=True, ONLY TRUSTED/VERIFIED items are returned."""
        if only_verified:
            return [i for i in self.items if i.get("verification_status") in self.TRUSTED_STATUSES]
        return list(self.items)

    def get_by_intent(self, intent: str, only_verified: bool = True) -> List[Dict[str, Any]]:
        return [i for i in self.get_all(only_verified) if i.get("intent") == intent]

    def add_evidence(self, evidence: Dict[str, Any]) -> str:
        """Add new evidence unit (starts as CANDIDATE/REVIEW_REQUIRED; requires human approval)."""
        evidence_id = evidence.get("evidence_id") or f"EVID-CUSTOM-{len(self.items) + 1:03d}"
        evidence["evidence_id"] = evidence_id
        if "verification_status" not in evidence:
            evidence["verification_status"] = "CANDIDATE"
        self.items.append(evidence)
        self.save()
        return evidence_id
