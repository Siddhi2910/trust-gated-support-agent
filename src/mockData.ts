import { EvidenceSnippet, CustomerTicket, TrustGateConfig } from './types';

export const initialEvidenceBase: EvidenceSnippet[] = [
  {
    id: 'ev-101',
    title: 'Self-Serve Refund Eligibility (14-Day Window)',
    content: 'Full refunds are permitted within 14 calendar days of transaction for Starter and Pro plans if usage does not exceed 25% of the monthly quota. Invoices below $150 can be approved autonomously when this criterion is satisfied. Invoices exceeding $150 or older than 14 days require mandatory Tier-2 manual sign-off.',
    category: 'Billing & Refunds',
    validationStatus: 'human_validated',
    validator: 'Sarah Chen (Lead Billing Ops)',
    validatedAt: '2026-08-15T10:30:00Z',
    trustWeight: 5,
    useCount: 142,
    tags: ['refund', '14-days', 'invoice', 'quota', 'billing'],
    isGroundTruth: true
  },
  {
    id: 'ev-102',
    title: 'Enterprise Tier Response SLA & Escalations',
    content: 'Enterprise contracts include a contractual 15-minute initial response guarantee for Severity-1 outages and 1 hour for Severity-2 issues. If an Enterprise customer reports service degradation affecting their live production API, the ticket must immediately trigger an urgent alert to the On-Call Engineering rota.',
    category: 'Technical Integration',
    validationStatus: 'human_validated',
    validator: 'Marcus Brody (Director of CX)',
    validatedAt: '2026-08-20T14:15:00Z',
    trustWeight: 5,
    useCount: 88,
    tags: ['sla', 'enterprise', 'sev-1', 'escalation', 'outage'],
    isGroundTruth: true
  },
  {
    id: 'ev-103',
    title: 'Two-Factor Authentication (2FA) Lockout Protocol',
    content: 'For security compliance (SOC2 Type II), support agents and automated models are strictly forbidden from disabling 2FA or resetting credentials over chat. The user must provide a notarized identity check or have their primary organization owner submit an authorization ticket from the verified admin email.',
    category: 'Security & Compliance',
    validationStatus: 'human_validated',
    validator: 'Elena Rostova (Chief Information Security Officer)',
    validatedAt: '2026-08-25T09:00:00Z',
    trustWeight: 5,
    useCount: 64,
    tags: ['2fa', 'security', 'lockout', 'soc2', 'mfa', 'identity'],
    isGroundTruth: true
  },
  {
    id: 'ev-104',
    title: 'Webhook Signature Verification & Retries',
    content: 'All outgoing webhooks are signed using HMAC-SHA256 with the secret key found in Settings > Webhooks. Retries occur on 5xx errors with exponential backoff: 30s, 2m, 10m, 1h, and 6h before permanent delivery failure. Headers include X-Webhook-Signature and X-Delivery-Attempt.',
    category: 'Technical Integration',
    validationStatus: 'human_validated',
    validator: 'Devon Vance (Staff DevRel)',
    validatedAt: '2026-08-28T16:45:00Z',
    trustWeight: 4,
    useCount: 53,
    tags: ['webhook', 'hmac', 'signature', 'retry', 'integration', 'api'],
    isGroundTruth: true
  },
  {
    id: 'ev-105',
    title: 'GDPR Right to Be Forgotten & Workspace Data Purge',
    content: 'Article 17 requests must be processed within 30 calendar days. Initiating a workspace deletion purges customer personal data from active stores within 72 hours and cold backups within 30 days. Financial audit logs (invoices, tax identifiers) are retained for 7 years per statutory tax obligations.',
    category: 'Security & Compliance',
    validationStatus: 'human_validated',
    validator: 'Alistair Finch (Legal Counsel)',
    validatedAt: '2026-09-01T11:20:00Z',
    trustWeight: 5,
    useCount: 31,
    tags: ['gdpr', 'data-purge', 'compliance', 'privacy', 'legal'],
    isGroundTruth: true
  },
  {
    id: 'ev-106',
    title: 'Seat Allocation & Prorated Mid-Cycle Adjustments',
    content: 'When adding or removing team seats mid-billing cycle, prorated adjustments are credited or debited to the upcoming monthly invoice. Unassigned seats do not automatically decrease invoice amounts unless explicitly cancelled in the Organization Members panel before the renewal date.',
    category: 'Product & Subscriptions',
    validationStatus: 'human_validated',
    validator: 'Sarah Chen (Lead Billing Ops)',
    validatedAt: '2026-09-03T13:10:00Z',
    trustWeight: 4,
    useCount: 76,
    tags: ['seats', 'proration', 'billing-cycle', 'downgrade', 'organization'],
    isGroundTruth: true
  }
];

export const initialTickets: CustomerTicket[] = [
  {
    id: 'TCK-8921',
    customerName: 'Alexander Hayes',
    customerEmail: 'a.hayes@nexusdynamics.io',
    companyName: 'Nexus Dynamics',
    tier: 'Professional',
    query: 'Hi team, we were billed $49 on September 2nd for our Starter-to-Pro upgrade, but our developer decided to stick with the Starter tier. It has only been 8 days and we used under 5% of the quota. Can we get a refund back to our Visa card?',
    category: 'Billing & Refunds',
    status: 'autonomous_dispatched',
    createdAt: '2026-09-10T11:15:00Z',
    transactionAmount: 49,
    aiDraft: 'Hello Alexander,\n\nThank you for reaching out! Since your upgrade transaction occurred 8 days ago (within our 14-day refund window) and your usage is below 25% of the quota, your request satisfies our verified refund eligibility criteria.\n\nI have automatically initiated a full refund of $49.00 to your Visa card ending in the original billing method. You should see the credit reflected within 3-5 business days. Your workspace has been safely adjusted back to the Starter plan.\n\nPlease let us know if you need anything else!',
    finalResponse: 'Hello Alexander,\n\nThank you for reaching out! Since your upgrade transaction occurred 8 days ago (within our 14-day refund window) and your usage is below 25% of the quota, your request satisfies our verified refund eligibility criteria.\n\nI have automatically initiated a full refund of $49.00 to your Visa card ending in the original billing method. You should see the credit reflected within 3-5 business days. Your workspace has been safely adjusted back to the Starter plan.\n\nPlease let us know if you need anything else!',
    trustEvaluation: {
      trustScore: 92,
      gateDecision: 'AUTO_DISPATCH',
      factors: {
        evidenceMatchScore: 96,
        policySafetyScore: 94,
        semanticCertaintyScore: 90,
        domainPrecedentScore: 88
      },
      riskFlags: [],
      reasoning: 'Matches human-validated evidence ev-101 (14-day refund eligibility). Transaction amount ($49) is well below the $150 automated threshold. Quota usage condition is verified.',
      evaluatedAt: '2026-09-10T11:15:04Z'
    },
    matchedEvidence: [initialEvidenceBase[0]]
  },
  {
    id: 'TCK-8922',
    customerName: 'Claire Beaumont',
    customerEmail: 'claire@zenithlogistics.com',
    companyName: 'Zenith Logistics',
    tier: 'Professional',
    query: 'Our accounting department needs to transfer 5 unused Pro seats from our EU branch to our US entity without double-paying for the current quarter. Is there an automated voucher or prorated credit mechanism for inter-subsidiary seat migration?',
    category: 'Product & Subscriptions',
    status: 'gated_review',
    createdAt: '2026-09-10T13:40:00Z',
    transactionAmount: 375,
    aiDraft: 'Hi Claire,\n\nThanks for contacting customer support. Standard mid-cycle seat adjustments apply prorated credits to the upcoming monthly invoice within the same organization account.\n\nHowever, for cross-subsidiary transfers between separate legal billing entities (such as EU and US branches), manual invoicing realignment is typically required to avoid international tax discrepancies. A member of our billing operations team is reviewing your account structure to facilitate the seat credit transfer smoothly.',
    trustEvaluation: {
      trustScore: 66,
      gateDecision: 'GATE_REVIEW',
      factors: {
        evidenceMatchScore: 62,
        policySafetyScore: 70,
        semanticCertaintyScore: 68,
        domainPrecedentScore: 64
      },
      riskFlags: [
        'Inter-subsidiary cross-entity billing lacks explicit ground-truth precedent',
        'Amount exceeds standard automated adjustment cap ($375 > $150)',
        'Potential international VAT/tax compliance distinction'
      ],
      reasoning: 'General seat proration evidence (ev-106) matched partially, but inter-subsidiary transfer policies have not yet been validated by human specialists.',
      evaluatedAt: '2026-09-10T13:40:06Z'
    },
    matchedEvidence: [initialEvidenceBase[5]]
  },
  {
    id: 'TCK-8923',
    customerName: 'Dmitri Volkov',
    customerEmail: 'dmitri@hypervector.tech',
    companyName: 'HyperVector Tech',
    tier: 'Enterprise',
    query: 'URGENT: Our lead engineer lost their phone and cannot log into our primary admin console because 2FA is prompting. We have a major deployment in 30 minutes! Please disable 2FA for dmitri@hypervector.tech immediately so we can ship the release.',
    category: 'Security & Compliance',
    status: 'escalated',
    createdAt: '2026-09-10T14:10:00Z',
    aiDraft: 'Hello Dmitri,\n\nWe understand the urgency regarding your deployment timeline. However, in accordance with our SOC2 security policy, 2FA cannot be bypassed or disabled directly over chat or by automated support.\n\nTo safely resolve this without compromising your organization, your primary account owner must verify identity through our out-of-band security procedure. I have escalated this ticket directly to our Security Operations team for expedited review.',
    trustEvaluation: {
      trustScore: 34,
      gateDecision: 'HUMAN_TAKEOVER',
      factors: {
        evidenceMatchScore: 82,
        policySafetyScore: 12,
        semanticCertaintyScore: 40,
        domainPrecedentScore: 30
      },
      riskFlags: [
        'HIGH RISK: Direct request to bypass Two-Factor Authentication',
        'Security compliance strict policy trigger (SOC2 Zero-Bypass)',
        'Urgency pressure tactic detected ("deployment in 30 minutes")'
      ],
      reasoning: 'Critical security boundary. While ev-103 states 2FA bypass is forbidden, automated communication on active account lockouts during production emergencies requires direct human operator handling and verified identity authentication.',
      evaluatedAt: '2026-09-10T14:10:05Z'
    },
    matchedEvidence: [initialEvidenceBase[2]]
  }
];

export const defaultConfig: TrustGateConfig = {
  autoDispatchThreshold: 80,
  humanTakeoverThreshold: 50,
  refundLimitRequiringHuman: 150,
  strictSecurityCheck: true,
  activeLearningEnabled: true
};
