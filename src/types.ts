export type TicketCategory =
  | 'Billing & Refunds'
  | 'Technical Integration'
  | 'Security & Compliance'
  | 'Account & Access'
  | 'Product & Subscriptions';

export type TicketStatus =
  | 'pending_eval'
  | 'autonomous_dispatched'
  | 'gated_review'
  | 'human_resolved'
  | 'escalated';

export type GateDecision = 'AUTO_DISPATCH' | 'GATE_REVIEW' | 'HUMAN_TAKEOVER';

export interface EvidenceSnippet {
  id: string;
  title: string;
  content: string;
  category: TicketCategory;
  validationStatus: 'human_validated' | 'ai_proposed';
  validator: string;
  validatedAt: string;
  trustWeight: number; // 1 to 5
  useCount: number;
  tags: string[];
  isGroundTruth: boolean;
}

export interface TrustFactors {
  evidenceMatchScore: number;    // 0 - 100
  policySafetyScore: number;      // 0 - 100
  semanticCertaintyScore: number; // 0 - 100
  domainPrecedentScore: number;   // 0 - 100
}

export interface TrustEvaluation {
  trustScore: number; // 0 - 100
  gateDecision: GateDecision;
  factors: TrustFactors;
  riskFlags: string[];
  reasoning: string;
  evaluatedAt: string;
}

export interface HumanReviewLog {
  reviewer: string;
  action: 'approved' | 'edited_and_learned' | 'overridden';
  feedbackNotes?: string;
  reviewedAt: string;
  newEvidenceExtracted?: string;
  evidenceTitle?: string;
}

export interface CustomerTicket {
  id: string;
  customerName: string;
  customerEmail: string;
  companyName: string;
  tier: 'Starter' | 'Professional' | 'Enterprise';
  query: string;
  category: TicketCategory;
  status: TicketStatus;
  createdAt: string;
  aiDraft: string;
  finalResponse?: string;
  trustEvaluation: TrustEvaluation;
  matchedEvidence: EvidenceSnippet[];
  humanReview?: HumanReviewLog;
  transactionAmount?: number;
}

export interface TrustGateConfig {
  autoDispatchThreshold: number; // Default: 80
  humanTakeoverThreshold: number; // Default: 50
  refundLimitRequiringHuman: number; // e.g., $150
  strictSecurityCheck: boolean;
  activeLearningEnabled: boolean;
}

export interface SystemMetrics {
  totalTickets: number;
  autonomousDispatchedCount: number;
  gatedReviewedCount: number;
  escalatedCount: number;
  evidenceCount: number;
  avgTrustScore: number;
  humanLearnedCount: number;
}
