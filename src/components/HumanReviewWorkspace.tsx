import React, { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  RotateCcw,
  BookOpen,
  Info,
  ShieldAlert,
  SlidersHorizontal,
  FileCheck
} from 'lucide-react';

interface ReviewCase {
  case_id: number;
  part: string;
  tweet_id: number;
  conversation_id: number;
  text: string;
  candidate_intent: string;
  alternative_intent?: string;
  tested_pair?: string;
  deterministic_rule?: string;
  category?: string;
  reason_not_technical?: string;
  human_decision: 'ACCEPT' | 'REJECT' | 'UNCERTAIN' | null;
  human_intent: string | null;
  focal_grievance: string | null;
  reviewer_notes: string | null;
  reviewed: boolean;
  reviewed_at: string | null;
}

interface ReviewMetadata {
  total_cases: number;
  reviewed_count: number;
  remaining_count: number;
  accept_count: number;
  reject_count: number;
  uncertain_count: number;
  reviewer: string;
  updated_at: string;
}

interface IntentInfo {
  intent_id: string;
  human_readable_name: string;
  definition: string;
  inclusion_criteria: string;
  exclusion_criteria: string;
  annotation_rule?: string;
}

// Safe JSON fetch helper that strictly guards against non-JSON (HTML/Vite fallback) responses
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

async function safeFetchJson<T = any>(url: string, init?: RequestInit): Promise<T> {
  const fullUrl = url.startsWith('/') ? `${API_BASE}${url}` : url;
  const res = await fetch(fullUrl, {
    ...init,
    cache: 'no-store',
    headers: {
      'Accept': 'application/json',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      ...(init?.headers || {})
    }
  });

  const contentType = res.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    const rawText = await res.text();
    const cleanSnippet = rawText.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
    throw new Error(
      `Server returned non-JSON response (${res.status} ${res.statusText || ''}). Body snippet: "${cleanSnippet || 'Empty'}"`
    );
  }

  let data: any;
  try {
    data = await res.json();
  } catch (parseErr: any) {
    throw new Error(`Invalid JSON received from ${url}: ${parseErr.message}`);
  }

  if (!res.ok) {
    throw new Error(data?.error || `Request failed with status ${res.status}`);
  }

  return data;
}

export function HumanReviewWorkspace() {
  const [cases, setCases] = useState<ReviewCase[]>([]);
  const [metadata, setMetadata] = useState<ReviewMetadata | null>(null);
  const [intents, setIntents] = useState<Record<string, IntentInfo>>({});
  const [validIntents, setValidIntents] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [filterMode, setFilterMode] = useState<'all' | 'unreviewed' | 'reviewed' | 'part1' | 'part2' | 'part3'>('all');
  const [showRules, setShowRules] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Active case editing form state
  const [decision, setDecision] = useState<'ACCEPT' | 'REJECT' | 'UNCERTAIN' | null>(null);
  const [correctedIntent, setCorrectedIntent] = useState<string>('');
  const [focalGrievance, setFocalGrievance] = useState<string>('');
  const [reviewerNotes, setReviewerNotes] = useState<string>('');

  // Fetch initial data
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await safeFetchJson<{
        cases: ReviewCase[];
        metadata: ReviewMetadata;
        intents: Record<string, IntentInfo>;
        valid_intents: string[];
      }>('/api/review/cases');

      setCases(data.cases || []);
      setMetadata(data.metadata || null);
      setIntents(data.intents || {});
      setValidIntents(data.valid_intents || []);

      // If any unreviewed, start at first unreviewed case
      const firstUnreviewedIdx = (data.cases || []).findIndex((c: ReviewCase) => !c.reviewed);
      if (firstUnreviewedIdx !== -1) {
        setCurrentIndex(firstUnreviewedIdx);
      }
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Current filtered list
  const filteredCases = cases.filter(c => {
    if (filterMode === 'unreviewed') return !c.reviewed;
    if (filterMode === 'reviewed') return c.reviewed;
    if (filterMode === 'part1') return c.part === 'PART_1_CANDIDATE_INTENTS';
    if (filterMode === 'part2') return c.part === 'PART_2_BOUNDARY_CASES';
    if (filterMode === 'part3') return c.part === 'PART_3_UNKNOWN_CASES';
    return true;
  });

  const currentCase = filteredCases[currentIndex] || cases[0];

  // Sync form state when active case changes
  useEffect(() => {
    if (currentCase) {
      setDecision(currentCase.human_decision);
      setCorrectedIntent(currentCase.human_intent && currentCase.human_decision === 'REJECT' ? currentCase.human_intent : '');
      setFocalGrievance(currentCase.focal_grievance || '');
      setReviewerNotes(currentCase.reviewer_notes || '');
      setFeedbackMsg(null);
    }
  }, [currentCase?.case_id]);

  // Handle Save
  const handleSaveDecision = async (overrideDecision?: 'ACCEPT' | 'REJECT' | 'UNCERTAIN') => {
    if (!currentCase || currentCase.case_id === undefined || currentCase.case_id === null) {
      setFeedbackMsg({ type: 'error', text: 'No active case loaded for review. Please select a case.' });
      return;
    }

    const dec = overrideDecision || decision;
    if (!dec) {
      setFeedbackMsg({ type: 'error', text: 'Please select a decision: ACCEPT, REJECT, or UNCERTAIN.' });
      return;
    }

    if (dec === 'REJECT' && !correctedIntent) {
      setFeedbackMsg({ type: 'error', text: 'Please select a corrected intent when rejecting.' });
      return;
    }

    if (dec === 'UNCERTAIN' && (!reviewerNotes || reviewerNotes.trim().length === 0)) {
      setFeedbackMsg({ type: 'error', text: 'Reviewer notes are required when marking a case UNCERTAIN.' });
      return;
    }

    try {
      setIsSaving(true);
      const result = await safeFetchJson<{
        success: boolean;
        case: ReviewCase;
        metadata: ReviewMetadata;
      }>('/api/review/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: currentCase.case_id,
          human_decision: dec,
          human_intent: dec === 'ACCEPT' ? currentCase.candidate_intent : dec === 'REJECT' ? correctedIntent : null,
          focal_grievance: focalGrievance.trim() || null,
          reviewer_notes: reviewerNotes.trim() || null
        })
      });

      // Update local state
      setCases(prev => prev.map(c => c.case_id === currentCase.case_id ? result.case : c));
      setMetadata(result.metadata);
      setFeedbackMsg({ type: 'success', text: `Saved Case #${String(currentCase.case_id).padStart(3, '0')} (${dec})` });

      // Advance intelligently
      if (filterMode === 'unreviewed') {
        const remainingCount = filteredCases.length - 1;
        if (currentIndex >= remainingCount && remainingCount > 0) {
          setCurrentIndex(remainingCount - 1);
        }
      } else {
        if (currentIndex < filteredCases.length - 1) {
          setCurrentIndex(prev => prev + 1);
        }
      }
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message });
    } finally {
      setIsSaving(false);
    }
  };

  // Quick reset
  const handleResetCase = async () => {
    if (!currentCase.reviewed) return;
    try {
      const data = await safeFetchJson<{
        success: boolean;
        metadata: ReviewMetadata;
      }>('/api/review/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: currentCase.case_id })
      });

      if (data.success) {
        setCases(prev => prev.map(c => c.case_id === currentCase.case_id ? {
          ...c,
          human_decision: null,
          human_intent: null,
          focal_grievance: null,
          reviewer_notes: null,
          reviewed: false,
          reviewed_at: null
        } : c));
        setMetadata(data.metadata);
        setDecision(null);
        setCorrectedIntent('');
        setFocalGrievance('');
        setReviewerNotes('');
        setFeedbackMsg({ type: 'success', text: `Case #${String(currentCase.case_id).padStart(3, '0')} reset to unreviewed.` });
      }
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message });
    }
  };

  // Keyboard navigation and shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts if typing inside an input or textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target as HTMLElement).tagName)) {
        if (e.key === 'Enter' && e.ctrlKey) {
          handleSaveDecision();
        }
        return;
      }

      if (e.key === 'a' || e.key === 'A') {
        e.preventDefault();
        setDecision('ACCEPT');
      } else if (e.key === 'r' || e.key === 'R') {
        e.preventDefault();
        setDecision('REJECT');
      } else if (e.key === 'u' || e.key === 'U') {
        e.preventDefault();
        setDecision('UNCERTAIN');
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        if (currentIndex < filteredCases.length - 1) setCurrentIndex(prev => prev + 1);
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        if (currentIndex > 0) setCurrentIndex(prev => prev - 1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        handleSaveDecision();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, filteredCases.length, decision, correctedIntent, focalGrievance, reviewerNotes]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-600 text-sm font-medium">Loading Human Review Pack (170 Inquiries)...</p>
        </div>
      </div>
    );
  }

  if (!currentCase) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
        <p className="text-slate-600">No cases match the selected filter.</p>
        <button
          onClick={() => setFilterMode('all')}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium"
        >
          View All Cases
        </button>
      </div>
    );
  }

  const candIntentInfo = intents[currentCase.candidate_intent] || null;
  const progressPct = metadata ? Math.round((metadata.reviewed_count / metadata.total_cases) * 100) : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-16">
      {/* Top Banner / Review Tracker */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-sm border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-indigo-400" />
              <h1 className="text-xl font-bold tracking-tight">Golden Set Human Ground-Truth Adjudication</h1>
            </div>
            <p className="text-slate-400 text-xs mt-1">
              Project Owner Human Review Pack • 170 Opening Inquiries • Single-Blind Evaluation
            </p>
          </div>

          {/* Counters */}
          {metadata && (
            <div className="flex items-center gap-4 bg-slate-800/80 px-4 py-2.5 rounded-xl border border-slate-700/60 text-xs">
              <div>
                <span className="text-slate-400 block">Reviewed</span>
                <span className="text-base font-bold text-white">
                  {metadata.reviewed_count} <span className="text-slate-400 font-normal">/ {metadata.total_cases}</span>
                </span>
              </div>
              <div className="h-7 w-px bg-slate-700" />
              <div>
                <span className="text-slate-400 block">Remaining</span>
                <span className="text-base font-bold text-amber-400">{metadata.remaining_count}</span>
              </div>
              <div className="h-7 w-px bg-slate-700" />
              <div>
                <span className="text-slate-400 block">Accepted</span>
                <span className="text-base font-bold text-emerald-400">{metadata.accept_count}</span>
              </div>
              <div className="h-7 w-px bg-slate-700" />
              <div>
                <span className="text-slate-400 block">Rejected</span>
                <span className="text-base font-bold text-rose-400">{metadata.reject_count}</span>
              </div>
              <div className="h-7 w-px bg-slate-700" />
              <div>
                <span className="text-slate-400 block">Uncertain</span>
                <span className="text-base font-bold text-sky-400">{metadata.uncertain_count}</span>
              </div>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>Overall Human Labeling Progress</span>
            <span className="font-semibold text-slate-200">{progressPct}% Complete</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Primary Intent Rules Guidance Banner */}
      <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl overflow-hidden shadow-xs">
        <button
          onClick={() => setShowRules(!showRules)}
          className="w-full px-5 py-3 flex items-center justify-between text-left text-amber-900 font-medium text-xs sm:text-sm hover:bg-amber-100/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-amber-700" />
            <span>Primary Intent Review Protocol & Decision Hierarchy</span>
          </span>
          <span className="text-xs text-amber-700 underline font-normal">
            {showRules ? 'Hide Rules' : 'Show Rules'}
          </span>
        </button>

        {showRules && (
          <div className="px-5 pb-4 pt-1 text-xs text-amber-950 space-y-1.5 border-t border-amber-200/50">
            <p className="font-semibold">Mandatory Primary Intent Rules for Annotator:</p>
            <ol className="list-decimal pl-5 space-y-1 text-slate-800">
              <li><strong>Focal Grievance:</strong> Identify the customer’s focal grievance or actionable need.</li>
              <li><strong>Explicit Question Precedence:</strong> If there is an explicit request or question, use it when it clearly identifies the intended resolution.</li>
              <li><strong>Multi-Symptom Boundary:</strong> For multi-symptom inquiries, do not automatically choose the most severe symptom. Focus on what the user wants solved.</li>
              <li><strong>Tie-Breaker Only:</strong> Use the priority ladder ONLY as a secondary tie-breaker when the focal grievance cannot distinguish between competing intents.</li>
              <li><strong>Insufficient Context:</strong> If there is genuinely insufficient context (Category A, B1, B2, B3), use <code className="bg-amber-200/60 px-1 py-0.5 rounded font-mono">UNKNOWN_INSUFFICIENT_CONTEXT</code>.</li>
              <li><strong>Rejection:</strong> If the inquiry clearly belongs to another intent in the 15-intent taxonomy, REJECT the candidate and select the correct intent.</li>
              <li><strong>Uncertainty:</strong> UNCERTAIN is valid for genuine ambiguity. Do not force an arbitrary label.</li>
            </ol>
            <p className="text-amber-800 text-[11px] pt-1 italic">
              * Note: Judge the customer inquiry itself, not whether historical AppleSupport responses were useful.
            </p>
          </div>
        )}
      </div>

      {/* Filter and Navigation Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-slate-400 font-medium mr-1 flex items-center gap-1">
            <SlidersHorizontal className="w-3.5 h-3.5" /> Filter:
          </span>
          {[
            { id: 'all', label: `All (${cases.length})` },
            { id: 'unreviewed', label: `Unreviewed (${cases.filter(c => !c.reviewed).length})` },
            { id: 'reviewed', label: `Reviewed (${cases.filter(c => c.reviewed).length})` },
            { id: 'part1', label: 'Part 1: Candidate (120)' },
            { id: 'part2', label: 'Part 2: Boundary (35)' },
            { id: 'part3', label: 'Part 3: UNKNOWN (15)' }
          ].map(f => (
            <button
              key={f.id}
              onClick={() => {
                setFilterMode(f.id as any);
                setCurrentIndex(0);
              }}
              className={`px-2.5 py-1 rounded-lg transition-colors font-medium ${
                filterMode === f.id
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Jump-to & Pagination Controls */}
        <div className="flex items-center gap-2">
          {/* Jump to Unreviewed Button */}
          {cases.some(c => !c.reviewed) && (
            <button
              onClick={() => {
                const curId = currentCase.case_id;
                // Look for the next unreviewed case after currentCase.case_id
                const nextUnreviewedAfter = cases.find(c => !c.reviewed && c.case_id > curId);
                const target = nextUnreviewedAfter || cases.find(c => !c.reviewed);
                if (!target) return;

                // Check if target is inside current filteredCases
                const targetIdx = filteredCases.findIndex(c => c.case_id === target.case_id);
                if (targetIdx !== -1) {
                  setCurrentIndex(targetIdx);
                } else {
                  // Switch to 'all' or 'unreviewed' so target is visible
                  setFilterMode('all');
                  const idxAll = cases.findIndex(c => c.case_id === target.case_id);
                  if (idxAll !== -1) setCurrentIndex(idxAll);
                }
              }}
              className="px-2.5 py-1 bg-amber-100 text-amber-900 hover:bg-amber-200 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
              title="Jump to the next unreviewed case in sequence"
            >
              <span>Next Unreviewed</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}

          {/* Jump to specific case */}
          <div className="flex items-center gap-1 text-xs">
            <span className="text-slate-500">Case:</span>
            <select
              value={currentCase.case_id}
              onChange={e => {
                const targetId = Number(e.target.value);
                const targetIdx = filteredCases.findIndex(c => c.case_id === targetId);
                if (targetIdx !== -1) {
                  setCurrentIndex(targetIdx);
                } else {
                  setFilterMode('all');
                  const idxAll = cases.findIndex(c => c.case_id === targetId);
                  if (idxAll !== -1) setCurrentIndex(idxAll);
                }
              }}
              className="border border-slate-300 rounded-md px-2 py-1 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
            >
              {cases.map(c => (
                <option key={c.case_id} value={c.case_id}>
                  #{c.case_id.toString().padStart(3, '0')} {c.reviewed ? `✓ (${c.human_decision})` : '• [Pending]'}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed"
            title="Previous Case (Left Arrow)"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs font-medium text-slate-600">
            {currentIndex + 1} of {filteredCases.length}
          </span>
          <button
            onClick={() => setCurrentIndex(prev => Math.min(filteredCases.length - 1, prev + 1))}
            disabled={currentIndex === filteredCases.length - 1}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed"
            title="Next Case (Right Arrow)"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Feedback Toast */}
      {feedbackMsg && (
        <div
          className={`p-3 rounded-xl text-xs font-medium flex items-center justify-between ${
            feedbackMsg.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border border-emerald-200'
              : 'bg-rose-50 text-rose-900 border border-rose-200'
          }`}
        >
          <span>{feedbackMsg.text}</span>
          <button onClick={() => setFeedbackMsg(null)} className="text-slate-400 hover:text-slate-600 font-bold ml-2">
            ×
          </button>
        </div>
      )}

      {/* Main Case Review Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Case Card Header */}
        <div className="bg-slate-50/90 px-6 py-3.5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <span className="px-2.5 py-1 bg-slate-900 text-white rounded-md text-xs font-mono font-bold">
              Case {currentCase.case_id.toString().padStart(3, '0')} / 170
            </span>
            <span
              className={`px-2 py-0.5 rounded text-xs font-medium ${
                currentCase.part === 'PART_1_CANDIDATE_INTENTS'
                  ? 'bg-blue-100 text-blue-800'
                  : currentCase.part === 'PART_2_BOUNDARY_CASES'
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-amber-100 text-amber-800'
              }`}
            >
              {currentCase.part === 'PART_1_CANDIDATE_INTENTS' && 'Part 1: Candidate Intent'}
              {currentCase.part === 'PART_2_BOUNDARY_CASES' && 'Part 2: Boundary Confusion Pair'}
              {currentCase.part === 'PART_3_UNKNOWN_CASES' && 'Part 3: UNKNOWN Edge Case'}
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-500 font-mono">
            <span>Tweet ID: <strong className="text-slate-700">{currentCase.tweet_id}</strong></span>
            <span>Conv ID: <strong className="text-slate-700">{currentCase.conversation_id}</strong></span>
            {currentCase.reviewed && (
              <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-sans font-medium flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Reviewed
              </span>
            )}
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Customer Inquiry Text Display */}
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
              Verbatim Customer Inquiry Text:
            </span>
            <div className="bg-slate-50 border-l-4 border-indigo-500 p-4 rounded-r-xl text-slate-900 text-base sm:text-lg leading-relaxed font-sans shadow-2xs">
              "{currentCase.text}"
            </div>
          </div>

          {/* Candidate Intent Section */}
          <div className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" />
                Provisional Candidate Intent (AI Proposal - Not Ground Truth):
              </span>
              <span className="px-2.5 py-0.5 bg-indigo-100 text-indigo-900 rounded font-mono text-xs font-semibold">
                {currentCase.candidate_intent}
              </span>
            </div>

            {candIntentInfo && (
              <div className="text-xs text-slate-700 space-y-1.5 pt-1 border-t border-indigo-100">
                <p><strong>Intent Name:</strong> {candIntentInfo.human_readable_name}</p>
                <p><strong>Definition:</strong> {candIntentInfo.definition}</p>
                <p><strong>Inclusion:</strong> {candIntentInfo.inclusion_criteria}</p>
                <p><strong>Exclusion:</strong> {candIntentInfo.exclusion_criteria}</p>
                {candIntentInfo.annotation_rule && (
                  <p className="text-indigo-900 font-medium"><strong>Annotation Rule:</strong> {candIntentInfo.annotation_rule}</p>
                )}
              </div>
            )}
          </div>

          {/* Part 2 Boundary Context if applicable */}
          {currentCase.part === 'PART_2_BOUNDARY_CASES' && (
            <div className="bg-purple-50/60 border border-purple-200/80 rounded-xl p-4 text-xs text-purple-950 space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-purple-900 uppercase tracking-wider">
                <ShieldAlert className="w-3.5 h-3.5" />
                Confusable Boundary Under Test: {currentCase.tested_pair}
              </div>
              <p><strong>Intent A:</strong> <code className="bg-purple-100/70 px-1 py-0.5 rounded font-mono">{currentCase.candidate_intent}</code></p>
              <p><strong>Intent B:</strong> <code className="bg-purple-100/70 px-1 py-0.5 rounded font-mono">{currentCase.alternative_intent}</code></p>
              <p><strong>Deterministic Rule:</strong> {currentCase.deterministic_rule}</p>
            </div>
          )}

          {/* Part 3 UNKNOWN Context if applicable */}
          {currentCase.part === 'PART_3_UNKNOWN_CASES' && (
            <div className="bg-amber-50/60 border border-amber-200/80 rounded-xl p-4 text-xs text-amber-950 space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-amber-900 uppercase tracking-wider">
                <AlertCircle className="w-3.5 h-3.5" />
                UNKNOWN Category: {currentCase.category}
              </div>
              <p><strong>Non-Technical Reason:</strong> {currentCase.reason_not_technical}</p>
            </div>
          )}

          <hr className="border-slate-200" />

          {/* Human Review Decision Section */}
          <div className="space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Human Reviewer Decision (Project Owner):
            </span>

            {/* Decision Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setDecision('ACCEPT')}
                className={`px-4 py-3 rounded-xl font-medium text-xs sm:text-sm flex items-center justify-center gap-2 border transition-all ${
                  decision === 'ACCEPT'
                    ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm ring-2 ring-emerald-400/50'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-emerald-50/50 hover:border-emerald-300'
                }`}
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>[ ACCEPT ] (Key A)</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision('REJECT')}
                className={`px-4 py-3 rounded-xl font-medium text-xs sm:text-sm flex items-center justify-center gap-2 border transition-all ${
                  decision === 'REJECT'
                    ? 'bg-rose-600 text-white border-rose-600 shadow-sm ring-2 ring-rose-400/50'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-rose-50/50 hover:border-rose-300'
                }`}
              >
                <XCircle className="w-4 h-4 text-rose-400" />
                <span>[ REJECT ] (Key R)</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision('UNCERTAIN')}
                className={`px-4 py-3 rounded-xl font-medium text-xs sm:text-sm flex items-center justify-center gap-2 border transition-all ${
                  decision === 'UNCERTAIN'
                    ? 'bg-sky-700 text-white border-sky-700 shadow-sm ring-2 ring-sky-400/50'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-sky-50/50 hover:border-sky-300'
                }`}
              >
                <HelpCircle className="w-4 h-4 text-sky-400" />
                <span>[ UNCERTAIN ] (Key U)</span>
              </button>
            </div>

            {/* If REJECT: Corrected Intent dropdown */}
            {decision === 'REJECT' && (
              <div className="bg-rose-50/50 border border-rose-200 rounded-xl p-4 space-y-2">
                <label className="text-xs font-bold text-rose-900 block">
                  Select Corrected Intent (Required on Reject):
                </label>
                <select
                  value={correctedIntent}
                  onChange={e => setCorrectedIntent(e.target.value)}
                  className="w-full border border-rose-300 rounded-lg p-2 text-xs bg-white text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-rose-500"
                >
                  <option value="">-- Choose Corrected Intent --</option>
                  {validIntents.map(iid => (
                    <option key={iid} value={iid} disabled={iid === currentCase.candidate_intent}>
                      {iid} {iid === currentCase.candidate_intent ? '(Candidate)' : ''}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Focal Grievance / Actionable Need Field */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-700 block">
                Focal Grievance / Actionable Need (short free-text note):
              </label>
              <input
                type="text"
                value={focalGrievance}
                onChange={e => setFocalGrievance(e.target.value)}
                placeholder="e.g. Battery percentage drops while plugged into charger"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              />
            </div>

            {/* Reviewer Notes Field */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-700 flex items-center justify-between">
                <span>Reviewer Notes {decision === 'UNCERTAIN' ? <strong className="text-rose-600">(REQUIRED for UNCERTAIN)</strong> : <span className="text-slate-400 font-normal">(optional)</span>}:</span>
              </label>
              <textarea
                value={reviewerNotes}
                onChange={e => setReviewerNotes(e.target.value)}
                rows={2}
                placeholder={
                  decision === 'UNCERTAIN'
                    ? 'Explain the legitimate ambiguity or reason this inquiry cannot be responsibly classified into the 15 intents...'
                    : 'Additional notes or rationale...'
                }
                className={`w-full border rounded-lg p-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 bg-white ${
                  decision === 'UNCERTAIN' && !reviewerNotes.trim()
                    ? 'border-rose-300 focus:ring-rose-500'
                    : 'border-slate-300 focus:ring-indigo-500'
                }`}
              />
            </div>

            {/* Submit & Navigation Bar */}
            <div className="flex items-center justify-between pt-3">
              <div className="flex items-center gap-2">
                {currentCase.reviewed && (
                  <button
                    type="button"
                    onClick={handleResetCase}
                    className="text-xs text-slate-500 hover:text-rose-600 flex items-center gap-1 transition-colors"
                  >
                    <RotateCcw className="w-3 h-3" /> Reset this case
                  </button>
                )}
              </div>

              <div className="flex items-center gap-3">
                <span className="text-[11px] text-slate-400 hidden sm:inline">
                  Press <kbd className="bg-slate-100 px-1 py-0.5 rounded border border-slate-300 font-mono text-[10px]">Enter</kbd> to save
                </span>
                <button
                  type="button"
                  onClick={() => handleSaveDecision()}
                  disabled={isSaving || !decision}
                  className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed shadow-xs transition-all flex items-center gap-2"
                >
                  {isSaving ? 'Saving...' : 'Save Decision & Advance'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Keyboard navigation helper */}
      <div className="bg-slate-100 border border-slate-200 rounded-xl px-4 py-2.5 text-slate-600 text-[11px] flex flex-wrap items-center justify-between gap-2">
        <span className="font-semibold text-slate-700">Keyboard Shortcuts:</span>
        <div className="flex flex-wrap items-center gap-3 font-mono">
          <span><kbd className="bg-white px-1.5 py-0.5 rounded border shadow-2xs">A</kbd> = Accept</span>
          <span><kbd className="bg-white px-1.5 py-0.5 rounded border shadow-2xs">R</kbd> = Reject</span>
          <span><kbd className="bg-white px-1.5 py-0.5 rounded border shadow-2xs">U</kbd> = Uncertain</span>
          <span><kbd className="bg-white px-1.5 py-0.5 rounded border shadow-2xs">←</kbd> / <kbd className="bg-white px-1.5 py-0.5 rounded border shadow-2xs">→</kbd> = Prev/Next</span>
          <span><kbd className="bg-white px-1.5 py-0.5 rounded border shadow-2xs">Enter</kbd> = Save</span>
        </div>
      </div>
    </div>
  );
}
