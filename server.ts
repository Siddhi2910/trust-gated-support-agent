import express from 'express';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';
import { initialEvidenceBase, initialTickets, defaultConfig } from './src/mockData';
import { EvidenceSnippet, CustomerTicket, TrustGateConfig, TrustEvaluation, GateDecision } from './src/types';

const app = express();
const PORT = 3000;

app.use(express.json());

// In-memory data store
let evidenceBase: EvidenceSnippet[] = [...initialEvidenceBase];
let tickets: CustomerTicket[] = [...initialTickets];
let config: TrustGateConfig = { ...defaultConfig };

// Initialize Gemini client lazily
let aiClient: GoogleGenAI | null = null;
function getAIClient(): GoogleGenAI | null {
  if (!aiClient && process.env.GEMINI_API_KEY) {
    try {
      aiClient = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    } catch (e) {
      console.warn('[Gemini] Initialization skipped or key missing:', e);
    }
  }
  return aiClient;
}

// Helper: Semantic & Heuristic Trust Evaluation Engine
function evaluateTrustHeuristics(
  query: string,
  category: string,
  transactionAmount: number | undefined,
  companyTier: string
): { evaluation: TrustEvaluation; matchedEvidence: EvidenceSnippet[]; draft: string } {
  const queryLower = query.toLowerCase();
  
  // Find matching evidence based on keywords & tags
  const matched = evidenceBase.filter(ev => {
    const titleMatch = ev.title.toLowerCase().split(' ').some(w => w.length > 3 && queryLower.includes(w));
    const tagMatch = ev.tags.some(tag => queryLower.includes(tag.toLowerCase()));
    const contentMatch = ev.content.toLowerCase().split(' ').filter(w => w.length > 5).some(w => queryLower.includes(w));
    return (titleMatch || tagMatch || contentMatch) && (ev.category === category || tagMatch);
  }).sort((a, b) => (b.trustWeight * 20 + b.useCount) - (a.trustWeight * 20 + a.useCount));

  // Risk detection
  const riskFlags: string[] = [];
  let policySafetyScore = 95;
  let semanticCertainty = 85;

  // Security risk checks
  if (queryLower.includes('2fa') || queryLower.includes('mfa') || queryLower.includes('two-factor') || queryLower.includes('disable authentication') || queryLower.includes('bypass')) {
    if (queryLower.includes('disable') || queryLower.includes('bypass') || queryLower.includes('lost phone') || queryLower.includes('reset')) {
      riskFlags.push('HIGH RISK: Direct request to bypass Two-Factor Authentication (SOC2 Zero-Bypass)');
      policySafetyScore = Math.min(policySafetyScore, 15);
      semanticCertainty = Math.min(semanticCertainty, 40);
    }
  }

  // Financial / Refund risk checks
  if (category === 'Billing & Refunds' || queryLower.includes('refund') || queryLower.includes('credit') || queryLower.includes('billed')) {
    const amount = transactionAmount || 0;
    if (amount > config.refundLimitRequiringHuman) {
      riskFlags.push(`Financial policy flag: Requested amount ($${amount}) exceeds autonomous refund threshold ($${config.refundLimitRequiringHuman})`);
      policySafetyScore = Math.min(policySafetyScore, 55);
    }
    if (queryLower.includes('chargeback') || queryLower.includes('lawyer') || queryLower.includes('dispute') || queryLower.includes('fraud')) {
      riskFlags.push('High-severity financial escalation (chargeback/legal mention)');
      policySafetyScore = Math.min(policySafetyScore, 20);
    }
  }

  // SLA & Outage risks
  if (queryLower.includes('outage') || queryLower.includes('production down') || queryLower.includes('sev-1') || queryLower.includes('urgent')) {
    if (companyTier === 'Enterprise') {
      riskFlags.push('Enterprise Severity-1 Outage Alert: 15-minute response SLA applies');
      policySafetyScore = Math.min(policySafetyScore, 40);
    }
  }

  // Evidence match score
  let evidenceMatchScore = 20;
  if (matched.length > 0) {
    const top = matched[0];
    evidenceMatchScore = Math.min(98, 50 + top.trustWeight * 8 + Math.min(20, top.useCount));
  } else {
    riskFlags.push('Uncharted territory: No human-validated evidence directly matches this inquiry');
    semanticCertainty = Math.min(semanticCertainty, 35);
  }

  // Domain precedent score
  const domainPrecedentScore = matched.length > 0 ? 88 : 30;

  // Composite trust calculation
  const compositeScore = Math.round(
    evidenceMatchScore * 0.40 +
    policySafetyScore * 0.35 +
    semanticCertainty * 0.15 +
    domainPrecedentScore * 0.10
  );

  const trustScore = Math.max(5, Math.min(99, compositeScore));

  let gateDecision: GateDecision = 'GATE_REVIEW';
  if (trustScore >= config.autoDispatchThreshold && riskFlags.length === 0) {
    gateDecision = 'AUTO_DISPATCH';
  } else if (trustScore < config.humanTakeoverThreshold || policySafetyScore < 30) {
    gateDecision = 'HUMAN_TAKEOVER';
  } else {
    gateDecision = 'GATE_REVIEW';
  }

  let reasoning = '';
  if (gateDecision === 'AUTO_DISPATCH') {
    reasoning = `High trust score (${trustScore}%). Query precisely matches human-validated ground truth [${matched[0]?.title || 'Policy'}]. Zero policy violations or financial limits breached.`;
  } else if (gateDecision === 'GATE_REVIEW') {
    reasoning = `Moderate trust score (${trustScore}%). Holds in Trust Gate escrow for human specialist verification. ${riskFlags.join('; ')}`;
  } else {
    reasoning = `Low trust score (${trustScore}%). Critical safety boundary or missing validated evidence requires direct human specialist takeover. ${riskFlags.join('; ')}`;
  }

  // Generate grounded draft response
  let draft = '';
  if (matched.length > 0) {
    const ev = matched[0];
    draft = `Hello,\n\nThank you for reaching out to customer support regarding your inquiry.\n\nBased on our verified operational guidelines: ${ev.content}\n\n`;
    if (gateDecision === 'AUTO_DISPATCH') {
      draft += `Your request has been automatically validated against our approved policy and processed accordingly. Please let us know if you need any additional assistance!`;
    } else if (gateDecision === 'GATE_REVIEW') {
      draft += `A member of our specialized support team is currently reviewing your account details to confirm custom application of this policy. We will follow up with full confirmation shortly.`;
    } else {
      draft += `Due to strict security and compliance standards, this case has been escalated to our senior operations team for direct manual handling.`;
    }
  } else {
    draft = `Hello,\n\nThank you for contacting customer support. We have received your inquiry: "${query.slice(0, 100)}..."\n\nBecause this inquiry touches on edge-case policies without prior ground-truth validation, our AI agent has held this ticket in Trust Gate escrow for immediate review by a human specialist.`;
  }

  return {
    evaluation: {
      trustScore,
      gateDecision,
      factors: {
        evidenceMatchScore,
        policySafetyScore,
        semanticCertaintyScore: semanticCertainty,
        domainPrecedentScore
      },
      riskFlags,
      reasoning,
      evaluatedAt: new Date().toISOString()
    },
    matchedEvidence: matched.slice(0, 3),
    draft
  };
}

// API Routes FIRST

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString(), aiAvailable: !!process.env.GEMINI_API_KEY });
});

// ==========================================
// HUMAN REVIEW GOLDEN SET ENDPOINTS
// ==========================================
const HUMAN_LABELS_FILE = path.join(process.cwd(), 'artifacts/human_review_labels.json');
const CANDIDATE_TAX_FILE = path.join(process.cwd(), 'artifacts/taxonomy_v1_candidate.json');
const BACKUP_DIR = path.join(process.cwd(), 'artifacts/backups');

const VALID_INTENTS_15 = [
  'BATTERY_DRAIN_POWER_CONSUMPTION',
  'DEVICE_FREEZE_CRASH_REBOOT',
  'KEYBOARD_TYPING_AUTOCORRECT_ISSUE',
  'PERFORMANCE_SLOWDOWN_LATENCY',
  'CONNECTIVITY_WIFI_BLUETOOTH',
  'APP_SPECIFIC_MALFUNCTION',
  'DATA_LOSS_RECOVERY',
  'SCREEN_DISPLAY_TOUCH_BIOMETRICS',
  'HARDWARE_CHARGING_POWER_CABLE',
  'AUDIO_SOUND_SPEAKER_MIC',
  'ACCOUNT_APPLE_ID_ACCESS',
  'BILLING_CHARGE_REFUND_DISPUTE',
  'ORDER_PURCHASE_SHIPPING_STATUS',
  'SECURITY_PHISHING_SUSPICIOUS_CONTACT',
  'UNKNOWN_INSUFFICIENT_CONTEXT'
];

// Helper to write JSON files atomically using a temporary file and rename
function atomicWriteJsonSync(filePath: string, data: any): void {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  const tmpPath = `${filePath}.${Date.now()}.${Math.random().toString(36).slice(2)}.tmp`;
  fs.writeFileSync(tmpPath, JSON.stringify(data, null, 2), 'utf-8');
  fs.renameSync(tmpPath, filePath);
}

// Helper to create an immutable timestamped backup of human_review_labels.json
function ensureSafeReviewBackup(): string | null {
  try {
    if (!fs.existsSync(HUMAN_LABELS_FILE)) return null;
    if (!fs.existsSync(BACKUP_DIR)) {
      fs.mkdirSync(BACKUP_DIR, { recursive: true });
    }
    const existing = fs.readdirSync(BACKUP_DIR).filter(f => f.startsWith('human_review_labels_backup_') && f.endsWith('.json'));
    // On first real human submission (when no backup exists yet), create the baseline backup
    if (existing.length === 0) {
      const ts = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = path.join(BACKUP_DIR, `human_review_labels_backup_${ts}.json`);
      fs.copyFileSync(HUMAN_LABELS_FILE, backupPath, fs.constants.COPYFILE_EXCL);
      console.log(`[Review Backup] Created initial immutable backup at ${backupPath}`);
      return backupPath;
    }
    return null;
  } catch (err) {
    console.warn('[Review Backup] Non-fatal warning during backup check:', err);
    return null;
  }
}

// GET all 170 review cases with metadata and taxonomy definitions
app.get(['/api/review/cases', '/api/review/cases/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');

    if (!fs.existsSync(HUMAN_LABELS_FILE)) {
      return res.status(404).json({ error: 'human_review_labels.json not found' });
    }
    const labelsData = JSON.parse(fs.readFileSync(HUMAN_LABELS_FILE, 'utf-8'));
    let taxonomyData: { intents?: any[] } = { intents: [] };
    if (fs.existsSync(CANDIDATE_TAX_FILE)) {
      taxonomyData = JSON.parse(fs.readFileSync(CANDIDATE_TAX_FILE, 'utf-8'));
    }

    const intentMap: Record<string, any> = {};
    for (const it of taxonomyData.intents || []) {
      intentMap[it.intent_id] = {
        intent_id: it.intent_id,
        human_readable_name: it.human_readable_name,
        definition: it.definition,
        inclusion_criteria: it.inclusion_criteria,
        exclusion_criteria: it.exclusion_criteria,
        annotation_rule: it.annotation_rule
      };
    }

    res.json({
      metadata: labelsData.metadata,
      cases: labelsData.cases,
      intents: intentMap,
      valid_intents: VALID_INTENTS_15
    });
  } catch (err: any) {
    console.error('Error fetching review cases:', err);
    res.status(500).json({ error: err.message });
  }
});

// GET review status counts
app.get(['/api/review/status', '/api/review/status/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');

    if (!fs.existsSync(HUMAN_LABELS_FILE)) {
      return res.status(404).json({ error: 'human_review_labels.json not found' });
    }
    const labelsData = JSON.parse(fs.readFileSync(HUMAN_LABELS_FILE, 'utf-8'));
    res.json(labelsData.metadata);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Core human review submit handler supporting safe atomic write and read-after-write verification
function processReviewSubmit(filePath: string, body: any, isTestStore: boolean = false) {
  const { case_id, human_decision, human_intent, focal_grievance, reviewer_notes } = body;

  // 1. Validate case ID
  if (case_id === undefined || case_id === null) {
    throw { status: 400, message: 'case_id is required' };
  }
  const numericId = Number(case_id);
  if (isNaN(numericId)) {
    throw { status: 400, message: 'case_id must be a valid number' };
  }

  // 2. Validate decision type
  if (!human_decision || !['ACCEPT', 'REJECT', 'UNCERTAIN'].includes(human_decision)) {
    throw { status: 400, message: 'human_decision must be ACCEPT, REJECT, or UNCERTAIN' };
  }

  if (!fs.existsSync(filePath)) {
    throw { status: 404, message: `Labels file not found: ${path.basename(filePath)}` };
  }

  const labelsData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  const targetCase = labelsData.cases.find((c: any) => Number(c.case_id) === numericId);
  if (!targetCase) {
    throw { status: 404, message: `Case ${case_id} not found in review dataset` };
  }

  // 3. Validate intent belongs to CURRENT 15-intent taxonomy
  if (human_decision === 'ACCEPT') {
    if (targetCase.candidate_intent && !VALID_INTENTS_15.includes(targetCase.candidate_intent)) {
      throw { status: 400, message: `Candidate intent ${targetCase.candidate_intent} is not in current 15-intent taxonomy` };
    }
    targetCase.human_decision = 'ACCEPT';
    targetCase.human_intent = targetCase.candidate_intent;
  } else if (human_decision === 'REJECT') {
    if (!human_intent) {
      throw { status: 400, message: 'Corrected human_intent is required when decision is REJECT' };
    }
    if (!VALID_INTENTS_15.includes(human_intent)) {
      throw {
        status: 400,
        message: `Invalid intent: ${human_intent}. Intent must belong to the CURRENT 15-intent taxonomy. Stale taxonomy IDs are strictly rejected.`
      };
    }
    targetCase.human_decision = 'REJECT';
    targetCase.human_intent = human_intent;
  } else if (human_decision === 'UNCERTAIN') {
    if (!reviewer_notes || String(reviewer_notes).trim().length === 0) {
      throw { status: 400, message: 'Reviewer notes are strictly required when decision is UNCERTAIN' };
    }
    targetCase.human_decision = 'UNCERTAIN';
    targetCase.human_intent = null;
  }

  // 4. Validate exact case provenance
  if (!isTestStore && (!targetCase.tweet_id || !targetCase.conversation_id)) {
    throw { status: 400, message: `Case provenance violation: missing tweet_id or conversation_id for case ${case_id}` };
  }

  targetCase.focal_grievance = focal_grievance ? String(focal_grievance).trim() : null;
  targetCase.reviewer_notes = reviewer_notes ? String(reviewer_notes).trim() : null;
  targetCase.reviewed = true;
  targetCase.reviewed_at = new Date().toISOString();

  // Recompute summary metadata
  const cases = labelsData.cases;
  const total = cases.length;
  const reviewed = cases.filter((c: any) => c.reviewed === true).length;
  const accepts = cases.filter((c: any) => c.human_decision === 'ACCEPT').length;
  const rejects = cases.filter((c: any) => c.human_decision === 'REJECT').length;
  const uncertains = cases.filter((c: any) => c.human_decision === 'UNCERTAIN').length;

  labelsData.metadata.total_cases = total;
  labelsData.metadata.reviewed_count = reviewed;
  labelsData.metadata.remaining_count = total - reviewed;
  labelsData.metadata.accept_count = accepts;
  labelsData.metadata.reject_count = rejects;
  labelsData.metadata.uncertain_count = uncertains;
  labelsData.metadata.updated_at = new Date().toISOString();

  // Ensure safe immutable backup exists prior to writing changes (only for real store)
  if (!isTestStore) {
    ensureSafeReviewBackup();
  }

  // 5. Write atomically
  atomicWriteJsonSync(filePath, labelsData);

  // 6. Confirm write & 7. Reload saved record from disk
  const reloadedData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  const reloadedCase = reloadedData.cases.find((c: any) => Number(c.case_id) === numericId);

  // 8. Verify that the saved value equals the submitted value
  if (!reloadedCase) {
    throw { status: 500, message: `Persistence verification error: Case ${case_id} could not be reloaded from disk` };
  }
  if (reloadedCase.human_decision !== human_decision) {
    throw {
      status: 500,
      message: `Persistence verification error: on-disk decision (${reloadedCase.human_decision}) does not match submitted (${human_decision})`
    };
  }
  if (human_decision === 'REJECT' && reloadedCase.human_intent !== human_intent) {
    throw {
      status: 500,
      message: `Persistence verification error: on-disk intent (${reloadedCase.human_intent}) does not match submitted (${human_intent})`
    };
  }

  // 9. Return verified success
  return {
    success: true,
    case: reloadedCase,
    metadata: reloadedData.metadata
  };
}

// POST submit a human review decision for a case
app.post(['/api/review/submit', '/api/review/submit/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const result = processReviewSubmit(HUMAN_LABELS_FILE, req.body, false);
    res.json(result);
  } catch (err: any) {
    const statusCode = err.status || 500;
    const msg = err.message || err.error || 'Failed to submit human review decision';
    console.error('Error submitting review:', msg);
    res.status(statusCode).json({ error: msg });
  }
});

// POST test-submit endpoint for ISOLATED persistence testing (Phase 5 compliance)
app.post(['/api/review/test-submit', '/api/review/test-submit/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const testFile = path.join(process.cwd(), 'artifacts/test_human_review_persistence.json');
    const result = processReviewSubmit(testFile, req.body, true);
    res.json(result);
  } catch (err: any) {
    const statusCode = err.status || 500;
    const msg = err.message || err.error || 'Failed to execute test persistence';
    res.status(statusCode).json({ error: msg });
  }
});

// GET list of existing immutable backups
app.get(['/api/review/backups', '/api/review/backups/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    if (!fs.existsSync(BACKUP_DIR)) {
      return res.json({ backups: [] });
    }
    const files = fs.readdirSync(BACKUP_DIR)
      .filter(f => f.startsWith('human_review_labels_backup_') && f.endsWith('.json'))
      .map(f => {
        const stats = fs.statSync(path.join(BACKUP_DIR, f));
        return {
          filename: f,
          size_bytes: stats.size,
          created_at: stats.birthtime.toISOString()
        };
      });
    res.json({ backups: files });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// POST reset case review
app.post(['/api/review/reset', '/api/review/reset/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const { case_id, all } = req.body;
    const labelsData = JSON.parse(fs.readFileSync(HUMAN_LABELS_FILE, 'utf-8'));

    if (all) {
      for (const c of labelsData.cases) {
        c.human_decision = null;
        c.human_intent = null;
        c.focal_grievance = null;
        c.reviewer_notes = null;
        c.reviewed = false;
        c.reviewed_at = null;
      }
    } else if (case_id !== undefined && case_id !== null) {
      const target = labelsData.cases.find((c: any) => Number(c.case_id) === Number(case_id));
      if (target) {
        target.human_decision = null;
        target.human_intent = null;
        target.focal_grievance = null;
        target.reviewer_notes = null;
        target.reviewed = false;
        target.reviewed_at = null;
      }
    }

    const cases = labelsData.cases;
    const total = cases.length;
    const reviewed = cases.filter((c: any) => c.reviewed === true).length;
    const accepts = cases.filter((c: any) => c.human_decision === 'ACCEPT').length;
    const rejects = cases.filter((c: any) => c.human_decision === 'REJECT').length;
    const uncertains = cases.filter((c: any) => c.human_decision === 'UNCERTAIN').length;

    labelsData.metadata.total_cases = total;
    labelsData.metadata.reviewed_count = reviewed;
    labelsData.metadata.remaining_count = total - reviewed;
    labelsData.metadata.accept_count = accepts;
    labelsData.metadata.reject_count = rejects;
    labelsData.metadata.uncertain_count = uncertains;
    labelsData.metadata.updated_at = new Date().toISOString();

    fs.writeFileSync(HUMAN_LABELS_FILE, JSON.stringify(labelsData, null, 2), 'utf-8');
    res.json({ success: true, metadata: labelsData.metadata });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GET all tickets
app.get('/api/tickets', (req, res) => {
  res.json({ tickets });
});

// POST new customer ticket
app.post('/api/tickets', async (req, res) => {
  try {
    const { customerName, customerEmail, companyName, tier, query, category, transactionAmount } = req.body;

    if (!customerName || !query || !category) {
      return res.status(400).json({ error: 'Missing required ticket fields' });
    }

    const newTicketId = `TCK-${Math.floor(1000 + Math.random() * 9000)}`;

    // Run Trust Evaluation
    let { evaluation, matchedEvidence, draft } = evaluateTrustHeuristics(
      query,
      category,
      transactionAmount ? Number(transactionAmount) : undefined,
      tier || 'Starter'
    );

    // If Gemini is available, attempt to enrich draft and evaluation
    const ai = getAIClient();
    if (ai) {
      try {
        const evidenceContext = matchedEvidence.map(e => `[${e.id}] ${e.title}: ${e.content}`).join('\n');
        const prompt = `You are the core intelligence of a Trust-Gated Customer Support Agent.
User query: "${query}"
Category: "${category}"
Customer Tier: "${tier || 'Starter'}"
Matched Ground-Truth Evidence from Human Validators:
${evidenceContext || 'No matching ground-truth evidence available.'}

Trust Gate Decision from Policy Engine: ${evaluation.gateDecision} (Score: ${evaluation.trustScore})
Risk Flags: ${evaluation.riskFlags.join(', ') || 'None'}

Generate a professional, polite, and grounded support response that strictly adheres to the human-validated evidence. If gated or escalated, reassure the customer while explaining human review. Do not hallucinate policies outside the evidence. Output only the message body.`;

        const response = await ai.models.generateContent({
          model: 'gemini-2.5-flash',
          contents: prompt
        });

        if (response.text) {
          draft = response.text.trim();
        }
      } catch (geminiErr) {
        console.warn('[Gemini Call Failed, using heuristic draft]:', geminiErr);
      }
    }

    // Determine initial ticket status based on Trust Gate decision
    let status: CustomerTicket['status'] = 'gated_review';
    let finalResponse: string | undefined = undefined;

    if (evaluation.gateDecision === 'AUTO_DISPATCH') {
      status = 'autonomous_dispatched';
      finalResponse = draft;
      // Update use counts for matched evidence
      matchedEvidence.forEach(m => {
        const found = evidenceBase.find(e => e.id === m.id);
        if (found) found.useCount += 1;
      });
    } else if (evaluation.gateDecision === 'HUMAN_TAKEOVER') {
      status = 'escalated';
    } else {
      status = 'gated_review';
    }

    const ticket: CustomerTicket = {
      id: newTicketId,
      customerName,
      customerEmail: customerEmail || 'customer@example.com',
      companyName: companyName || 'Independent Client',
      tier: tier || 'Starter',
      query,
      category,
      status,
      createdAt: new Date().toISOString(),
      transactionAmount: transactionAmount ? Number(transactionAmount) : undefined,
      aiDraft: draft,
      finalResponse,
      trustEvaluation: evaluation,
      matchedEvidence
    };

    tickets.unshift(ticket);
    res.status(201).json({ ticket });
  } catch (err: any) {
    console.error('Error creating ticket:', err);
    res.status(500).json({ error: err.message || 'Internal server error' });
  }
});

// POST Review & Evidence Learning for a Ticket
app.post('/api/tickets/:id/review', (req, res) => {
  const { id } = req.params;
  const { reviewer, action, finalResponse, feedbackNotes, newEvidenceSnippet } = req.body;

  const ticketIndex = tickets.findIndex(t => t.id === id);
  if (ticketIndex === -1) {
    return res.status(404).json({ error: 'Ticket not found' });
  }

  const ticket = tickets[ticketIndex];
  ticket.finalResponse = finalResponse || ticket.aiDraft;
  ticket.status = 'human_resolved';
  ticket.humanReview = {
    reviewer: reviewer || 'Support Specialist',
    action: action || 'approved',
    feedbackNotes,
    reviewedAt: new Date().toISOString(),
    newEvidenceExtracted: newEvidenceSnippet ? newEvidenceSnippet.content : undefined,
    evidenceTitle: newEvidenceSnippet ? newEvidenceSnippet.title : undefined
  };

  // If the human created or extracted new evidence, learn it into the knowledge base!
  if (newEvidenceSnippet && newEvidenceSnippet.content && newEvidenceSnippet.title) {
    const newEvidence: EvidenceSnippet = {
      id: `ev-${Math.floor(200 + Math.random() * 800)}`,
      title: newEvidenceSnippet.title,
      content: newEvidenceSnippet.content,
      category: ticket.category,
      validationStatus: 'human_validated',
      validator: reviewer || 'Human CX Specialist',
      validatedAt: new Date().toISOString(),
      trustWeight: 5,
      useCount: 1,
      tags: newEvidenceSnippet.tags || [ticket.category.toLowerCase().split(' ')[0], 'human-learned'],
      isGroundTruth: true
    };
    evidenceBase.unshift(newEvidence);
    ticket.matchedEvidence.push(newEvidence);
  }

  tickets[ticketIndex] = ticket;
  res.json({ ticket, evidenceBase });
});

// GET all evidence
app.get('/api/evidence', (req, res) => {
  res.json({ evidence: evidenceBase });
});

// POST add evidence directly
app.post('/api/evidence', (req, res) => {
  const { title, content, category, validator, tags, trustWeight } = req.body;
  if (!title || !content || !category) {
    return res.status(400).json({ error: 'Missing title, content, or category' });
  }

  const newSnippet: EvidenceSnippet = {
    id: `ev-${Math.floor(200 + Math.random() * 800)}`,
    title,
    content,
    category,
    validationStatus: 'human_validated',
    validator: validator || 'Lead CX Specialist',
    validatedAt: new Date().toISOString(),
    trustWeight: trustWeight ? Number(trustWeight) : 5,
    useCount: 0,
    tags: Array.isArray(tags) ? tags : (tags ? tags.split(',').map((t: string) => t.trim()) : ['policy']),
    isGroundTruth: true
  };

  evidenceBase.unshift(newSnippet);
  res.status(201).json({ evidence: newSnippet, allEvidence: evidenceBase });
});

// DELETE evidence snippet
app.delete('/api/evidence/:id', (req, res) => {
  const { id } = req.params;
  evidenceBase = evidenceBase.filter(e => e.id !== id);
  res.json({ success: true, allEvidence: evidenceBase });
});

// GET configuration and metrics
app.get('/api/config', (req, res) => {
  const total = tickets.length;
  const auto = tickets.filter(t => t.status === 'autonomous_dispatched').length;
  const gated = tickets.filter(t => t.status === 'gated_review').length;
  const escalated = tickets.filter(t => t.status === 'escalated').length;
  const learned = tickets.filter(t => t.humanReview?.newEvidenceExtracted).length;
  const avgTrust = total > 0 ? Math.round(tickets.reduce((acc, t) => acc + t.trustEvaluation.trustScore, 0) / total) : 0;

  res.json({
    config,
    metrics: {
      totalTickets: total,
      autonomousDispatchedCount: auto,
      gatedReviewedCount: gated,
      escalatedCount: escalated,
      evidenceCount: evidenceBase.length,
      avgTrustScore: avgTrust,
      humanLearnedCount: learned
    }
  });
});

// POST update configuration
app.post('/api/config', (req, res) => {
  config = { ...config, ...req.body };
  res.json({ config });
});

// Helper to execute customer inquiries through real Python Trust-Gated Pipeline
function executePythonPipeline(payload: {
  text: string;
  conversation_id?: number | string;
  tweet_id?: number | string;
  in_response_to_tweet_id?: number | string;
}): Promise<any> {
  return new Promise((resolve, reject) => {
    const py = spawn('python3', ['scripts/run_pipeline_cli.py']);
    let stdout = '';
    let stderr = '';

    py.stdout.on('data', d => stdout += d.toString());
    py.stderr.on('data', d => stderr += d.toString());

    py.on('close', code => {
      if (code !== 0) {
        return reject(new Error(stderr || `Pipeline exited with code ${code}`));
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (e: any) {
        reject(new Error(`Failed to parse pipeline output: ${stdout}`));
      }
    });

    py.stdin.write(JSON.stringify(payload));
    py.stdin.end();
  });
}

// POST Simulate Query (Sandbox) - Connected to Real Python Trust-Gated Pipeline
app.post('/api/simulate-query', async (req, res) => {
  try {
    const { query, category, transactionAmount, companyTier } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query is required for simulation' });
    }

    const pipelineResult = await executePythonPipeline({ text: query });

    const isAuto = pipelineResult.decision?.can_auto_resolve ?? false;
    const gateDecision = isAuto
      ? 'Auto-Dispatch'
      : (pipelineResult.risk?.requires_immediate_escalation ? 'Hard-Gated Escrow' : 'Hold for Review');
    const trustScore = Math.round((pipelineResult.decision?.confidence_score ?? 0.5) * 100);

    const riskFlags: string[] = [];
    if (pipelineResult.risk?.requires_immediate_escalation) {
      riskFlags.push(`${pipelineResult.risk?.risk_category || 'RISK'}: ${pipelineResult.risk?.reason || 'Immediate escalation required'}`);
    }
    if (pipelineResult.intent?.ambiguity_flag) {
      riskFlags.push('Ambiguous Multi-Intent');
    }
    if (!pipelineResult.gates?.answerability?.answerable) {
      riskFlags.push('Insufficient Grounding Evidence');
    }
    if (pipelineResult.claims?.hallucination_detected) {
      riskFlags.push('Unverified Claim Detected');
    }

    const matchedEvidence = (pipelineResult.generation?.evidence_used || []).map((e: any) => ({
      id: e.evidence_id,
      title: e.title,
      content: e.body || `[${e.source_type || 'SOURCE'}] ${e.source_reference || ''}`,
      category: pipelineResult.intent?.intent,
      trustWeight: 5
    }));

    const result = {
      evaluation: {
        trustScore,
        riskLevel: (pipelineResult.risk?.risk_level || 'low').toLowerCase(),
        riskFlags,
        matchedRules: matchedEvidence.map((e: any) => e.id),
        gateDecision,
        breakdown: {
          intentClarity: Math.round((pipelineResult.intent?.confidence ?? 0.8) * 100),
          evidenceGrounding: Math.round((pipelineResult.claims?.groundedness_score ?? 1.0) * 100),
          policyCompliance: pipelineResult.risk?.requires_immediate_escalation ? 10 : 95,
          hallucinationRisk: pipelineResult.claims?.hallucination_detected ? 90 : 5
        }
      },
      matchedEvidence,
      draft: pipelineResult.generation?.response_text,
      pipelineResult
    };

    res.json(result);
  } catch (err: any) {
    console.error('Simulation error:', err);
    res.status(500).json({ error: err.message });
  }
});

// POST Reset Demo
app.post('/api/reset-demo', (req, res) => {
  evidenceBase = [...initialEvidenceBase];
  tickets = [...initialTickets];
  config = { ...defaultConfig };
  res.json({ success: true, tickets, evidence: evidenceBase, config });
});

// GET recovery status & honest label counts
app.get(['/api/recovery/status', '/api/recovery/status/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const recPath = path.join(process.cwd(), 'artifacts', 'recovered_human_labels.json');
    if (!fs.existsSync(recPath)) {
      return res.status(404).json({ error: 'recovered_human_labels.json not found' });
    }
    const data = JSON.parse(fs.readFileSync(recPath, 'utf-8'));
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GET automated evaluation benchmark summary
app.get(['/api/benchmark/summary', '/api/benchmark/summary/'], (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const bPath = path.join(process.cwd(), 'artifacts', 'evaluation_benchmark_results.json');
    if (!fs.existsSync(bPath)) {
      return res.status(404).json({ error: 'evaluation_benchmark_results.json not found' });
    }
    const data = JSON.parse(fs.readFileSync(bPath, 'utf-8'));
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// POST process customer inquiry through Trust-Gated Dual-Track Pipeline
app.post(['/api/pipeline/process', '/api/pipeline/process/'], async (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const { text, conversation_id, tweet_id, in_response_to_tweet_id } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'text is required' });
    }

    const result = await executePythonPipeline({ text, conversation_id, tweet_id, in_response_to_tweet_id });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/conversations/:id - retrieve stored conversation session state
app.get('/api/conversations/:id', (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const cid = req.params.id;
    const sessionPath = path.join(__dirname, 'artifacts', 'conversation_sessions.json');
    if (!fs.existsSync(sessionPath)) {
      return res.status(404).json({ error: 'No active sessions found' });
    }
    const data = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
    const session = data.sessions ? data.sessions[cid] : null;
    if (!session) {
      return res.status(404).json({ error: `Conversation ${cid} not found` });
    }
    res.json(session);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/conversations/:id - clear a conversation session state
app.delete('/api/conversations/:id', (req, res) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    const cid = req.params.id;
    const sessionPath = path.join(__dirname, 'artifacts', 'conversation_sessions.json');
    if (fs.existsSync(sessionPath)) {
      const data = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
      if (data.sessions && data.sessions[cid]) {
        delete data.sessions[cid];
        data.active_sessions_count = Object.keys(data.sessions).length;
        fs.writeFileSync(sessionPath, JSON.stringify(data, null, 2), 'utf-8');
        return res.json({ status: 'cleared', conversation_id: cid });
      }
    }
    res.json({ status: 'not_found', conversation_id: cid });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Explicit restriction: GET /api/golden-set is blocked to prevent exposing frozen evaluation set
app.all(['/api/golden-set', '/api/golden-set/*'], (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.status(403).json({
    error: 'Access to the frozen golden set is restricted to prevent evaluation leakage.',
    status: 403
  });
});

// Explicit API 404 handler: guarantees that any unhandled /api/* request returns JSON, NEVER HTML
app.all('/api/*', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.status(404).json({
    error: `API route not found: ${req.method} ${req.originalUrl || req.url}`,
    status: 404
  });
});

// Explicit error handler for API routes to always return JSON errors, NEVER HTML
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  if (req.originalUrl?.startsWith('/api') || req.path?.startsWith('/api') || req.headers.accept?.includes('application/json')) {
    console.error('[API Error]', err);
    res.setHeader('Content-Type', 'application/json');
    const status = typeof err.status === 'number' ? err.status : (typeof err.statusCode === 'number' ? err.statusCode : 500);
    return res.status(status).json({
      error: err.message || 'Internal Server Error',
      status
    });
  }
  next(err);
});

// Vite Middleware & SPA serving
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true, allowedHosts: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Trust-Gated Support Agent server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
