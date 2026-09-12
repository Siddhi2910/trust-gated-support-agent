"""Risk and Safety Escalation Gate for Customer Support.

Screens inquiries for high-risk vectors (battery swelling/smoke/burns,
compromised accounts, fraud, legal threats) that strictly require immediate
human specialist escalation.
"""

import re
from typing import Dict, Any, List

SAFETY_HAZARD_PATTERNS = [
    r"\b(?:smoke|smoking|spark(?:s|ing)?|fire|exploded?|exploding|swollen|swelling|bulging|burn(?:ed|t|ing)?|electric\s*shock|overheated\s+and\s+burned)\b"
]

SECURITY_BREACH_PATTERNS = [
    r"\b(?:hacked|compromised|unauthorized\s+access|stolen\s+identity|someone\s+logged\s+into\s+my|ransomware|extortion)\b"
]

FINANCIAL_FRAUD_PATTERNS = [
    r"\b(?:unauthorized\s+charges?|fraudulent|stolen\s+card|bank\s+fraud|thousands?\s+of\s+dollars|identity\s+theft)\b"
]

LEGAL_REGULATORY_PATTERNS = [
    r"\b(?:lawyer|attorney|lawsuit|sue\s+you|legal\s+action|better\s+business\s+bureau|bbb|consumer\s+protection|ftc)\b"
]


class RiskGate:
    """Evaluates inquiry risk and enforces mandatory human escalation."""

    @classmethod
    def evaluate(cls, text: str, predicted_intent: str = "") -> Dict[str, Any]:
        cleaned = (text or "").lower()

        # 1. Critical Physical Safety / Hazard
        for pat in SAFETY_HAZARD_PATTERNS:
            if re.search(pat, cleaned):
                return {
                    "risk_level": "CRITICAL",
                    "requires_immediate_escalation": True,
                    "risk_category": "HARDWARE_SAFETY_HAZARD",
                    "escalation_queue": "SAFETY_INCIDENT_TEAM",
                    "reason": "Inquiry mentions smoke, fire, battery swelling, or physical burn hazard."
                }

        # 2. High Risk: Legal / Regulatory Threats
        for pat in LEGAL_REGULATORY_PATTERNS:
            if re.search(pat, cleaned):
                return {
                    "risk_level": "HIGH",
                    "requires_immediate_escalation": True,
                    "risk_category": "LEGAL_REGULATORY_DISPUTE",
                    "escalation_queue": "EXECUTIVE_RELATIONS",
                    "reason": "Customer threatens litigation, attorney involvement, or regulatory complaint."
                }

        # 3. High Risk: Account Takeover & Active Compromise
        for pat in SECURITY_BREACH_PATTERNS:
            if re.search(pat, cleaned):
                return {
                    "risk_level": "HIGH",
                    "requires_immediate_escalation": True,
                    "risk_category": "ACCOUNT_SECURITY_COMPROMISE",
                    "escalation_queue": "SECURITY_SPECIALIST",
                    "reason": "Customer reports active account compromise, hacking, or unauthorized identity takeover."
                }

        # 4. High Risk: Large-Scale Financial Fraud
        for pat in FINANCIAL_FRAUD_PATTERNS:
            if re.search(pat, cleaned):
                return {
                    "risk_level": "HIGH",
                    "requires_immediate_escalation": True,
                    "risk_category": "FINANCIAL_FRAUD",
                    "escalation_queue": "BILLING_SPECIALIST_TIER2",
                    "reason": "Customer reports fraudulent or high-value unauthorized transactions."
                }

        # 5. Medium Risk: Intent-based security or billing disputes
        if predicted_intent in ["SECURITY_PHISHING_SUSPICIOUS_CONTACT", "ACCOUNT_APPLE_ID_ACCESS"]:
            return {
                "risk_level": "MEDIUM",
                "requires_immediate_escalation": False,
                "risk_category": "SECURITY_SENSITIVE",
                "escalation_queue": "ACCOUNT_SECURITY",
                "reason": "Inquiry involves account access or credentials; automated steps must adhere to strict verification."
            }

        return {
            "risk_level": "LOW",
            "requires_immediate_escalation": False,
            "risk_category": "STANDARD_OPERATIONAL",
            "escalation_queue": "TIER1_SUPPORT",
            "reason": "No high-risk safety, legal, or severe financial vectors identified."
        }
