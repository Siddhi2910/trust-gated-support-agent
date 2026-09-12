import React, { useState } from 'react';
import {
  Layers,
  CheckCircle2,
  AlertTriangle,
  Send,
  Sparkles,
  BookPlus,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  UserCheck,
  Tag,
  MessageSquare,
  Building,
  DollarSign
} from 'lucide-react';
import { CustomerTicket, EvidenceSnippet } from '../types';
import { TrustScoreBadge } from './TrustScoreBadge';

interface SpecialistQueueProps {
  tickets: CustomerTicket[];
  selectedTicketId?: string;
  onSelectTicket: (id: string) => void;
  onReviewTicket: (reviewData: {
    ticketId: string;
    reviewer: string;
    action: 'approved' | 'edited_and_learned' | 'overridden';
    finalResponse: string;
    feedbackNotes?: string;
    newEvidenceSnippet?: {
      title: string;
      content: string;
      tags: string[];
    };
  }) => Promise<void>;
  isLoading: boolean;
}

export const SpecialistQueue: React.FC<SpecialistQueueProps> = ({
  tickets,
  selectedTicketId,
  onSelectTicket,
  onReviewTicket,
  isLoading
}) => {
  const [filterStatus, setFilterStatus] = useState<'all' | 'gated' | 'escalated' | 'resolved'>('gated');
  const [reviewerName, setReviewerName] = useState('Sarah Chen (Lead Billing & CX Ops)');
  
  // Active review form state
  const activeTicket = tickets.find(t => t.id === selectedTicketId) || tickets.find(t => t.status === 'gated_review') || tickets[0];
  
  const [editedResponse, setEditedResponse] = useState(activeTicket ? (activeTicket.finalResponse || activeTicket.aiDraft) : '');
  const [feedbackNotes, setFeedbackNotes] = useState('');
  
  // Evidence Learning toggle & fields
  const [learnAsEvidence, setLearnAsEvidence] = useState(true);
  const [evidenceTitle, setEvidenceTitle] = useState('');
  const [evidenceSnippetContent, setEvidenceSnippetContent] = useState('');
  const [evidenceTags, setEvidenceTags] = useState('billing, proration, transfer');
  const [learningSuccessBanner, setLearningSuccessBanner] = useState<string | null>(null);

  // Sync edited response when active ticket changes
  React.useEffect(() => {
    if (activeTicket) {
      setEditedResponse(activeTicket.finalResponse || activeTicket.aiDraft);
      setEvidenceTitle(`Verified Policy: ${activeTicket.category} Precedent`);
      setEvidenceSnippetContent(activeTicket.aiDraft.slice(0, 200));
      setLearningSuccessBanner(null);
    }
  }, [activeTicket?.id]);

  const filteredTickets = tickets.filter(t => {
    if (filterStatus === 'all') return true;
    if (filterStatus === 'gated') return t.status === 'gated_review';
    if (filterStatus === 'escalated') return t.status === 'escalated';
    if (filterStatus === 'resolved') return t.status === 'human_resolved' || t.status === 'autonomous_dispatched';
    return true;
  });

  const handleApprove = async () => {
    if (!activeTicket) return;
    await onReviewTicket({
      ticketId: activeTicket.id,
      reviewer: reviewerName,
      action: 'approved',
      finalResponse: activeTicket.aiDraft,
      feedbackNotes: 'Approved verbatim without modifications'
    });
    setLearningSuccessBanner(`Ticket ${activeTicket.id} approved and dispatched!`);
  };

  const handleEditAndLearn = async () => {
    if (!activeTicket) return;

    const payload: any = {
      ticketId: activeTicket.id,
      reviewer: reviewerName,
      action: 'edited_and_learned',
      finalResponse: editedResponse,
      feedbackNotes
    };

    if (learnAsEvidence && evidenceTitle && evidenceSnippetContent) {
      payload.newEvidenceSnippet = {
        title: evidenceTitle,
        content: evidenceSnippetContent,
        tags: evidenceTags.split(',').map(s => s.trim())
      };
    }

    await onReviewTicket(payload);
    setLearningSuccessBanner(
      learnAsEvidence
        ? `Successfully resolved! New Ground Truth evidence "${evidenceTitle}" has been learned into the AI Trust Graph.`
        : `Ticket ${activeTicket.id} resolved with custom specialist response.`
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header & Specialist Identity */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Layers className="w-4 h-4" />
            <span>Human-in-the-Loop Triage Station</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">
            Trust Gate Escrow & Evidence Validation
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Review held drafts, audit confidence risks, and convert human decisions into permanent ground-truth evidence.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-950 px-3.5 py-2 rounded-xl border border-slate-800">
          <UserCheck className="w-4 h-4 text-emerald-400" />
          <div>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Active Specialist:</span>
            <input
              type="text"
              id="reviewer-name-input"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              className="text-xs font-semibold text-slate-200 bg-transparent border-none p-0 focus:outline-none focus:ring-0 w-48 sm:w-60"
            />
          </div>
        </div>
      </div>

      {learningSuccessBanner && (
        <div className="p-4 rounded-xl bg-emerald-950/80 border border-emerald-500/50 text-emerald-200 text-xs sm:text-sm flex items-center gap-2.5 animate-fadeIn">
          <Sparkles className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{learningSuccessBanner}</span>
        </div>
      )}

      {/* Main Layout: Queue List & Inspection Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Ticket Queue */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Review Queue ({filteredTickets.length})
              </h3>
              <div className="flex items-center gap-1 text-[11px]">
                <button
                  type="button"
                  id="filter-gated-btn"
                  onClick={() => setFilterStatus('gated')}
                  className={`px-2 py-1 rounded ${filterStatus === 'gated' ? 'bg-amber-500/20 text-amber-300 font-semibold' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Gated
                </button>
                <button
                  type="button"
                  id="filter-escalated-btn"
                  onClick={() => setFilterStatus('escalated')}
                  className={`px-2 py-1 rounded ${filterStatus === 'escalated' ? 'bg-rose-500/20 text-rose-300 font-semibold' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Escalated
                </button>
                <button
                  type="button"
                  id="filter-all-btn"
                  onClick={() => setFilterStatus('all')}
                  className={`px-2 py-1 rounded ${filterStatus === 'all' ? 'bg-slate-800 text-slate-200 font-semibold' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  All
                </button>
              </div>
            </div>

            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {filteredTickets.map((t) => {
                const isSelected = activeTicket?.id === t.id;
                return (
                  <div
                    key={t.id}
                    id={`ticket-item-${t.id}`}
                    onClick={() => onSelectTicket(t.id)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-slate-800/90 border-cyan-500/50 shadow-md ring-1 ring-cyan-500/20'
                        : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-850 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="font-mono font-bold text-cyan-400">{t.id}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                        t.tier === 'Enterprise' ? 'bg-purple-950 text-purple-300 border border-purple-800' :
                        t.tier === 'Professional' ? 'bg-blue-950 text-blue-300 border border-blue-800' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {t.tier}
                      </span>
                    </div>

                    <h4 className="text-xs font-semibold text-slate-200 truncate">
                      {t.customerName} ({t.companyName})
                    </h4>
                    <p className="text-[11px] text-slate-400 truncate mt-1">
                      {t.query}
                    </p>

                    <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between">
                      <span className="text-[10px] text-slate-500">
                        {new Date(t.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <TrustScoreBadge evaluation={t.trustEvaluation} size="sm" />
                    </div>
                  </div>
                );
              })}

              {filteredTickets.length === 0 && (
                <div className="p-8 text-center text-xs text-slate-500">
                  No tickets found matching this filter.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Ticket Inspection & Review Workspace */}
        <div className="lg:col-span-8 space-y-5">
          {activeTicket ? (
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
              {/* Ticket Topbar */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-800 gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-cyan-400">
                      {activeTicket.id}
                    </span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-200 border border-slate-700">
                      {activeTicket.category}
                    </span>
                    {activeTicket.transactionAmount && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-medium">
                        ${activeTicket.transactionAmount} Amount
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-bold text-slate-100 mt-1">
                    {activeTicket.customerName} — {activeTicket.companyName}
                  </h3>
                  <span className="text-xs text-slate-400">{activeTicket.customerEmail}</span>
                </div>

                <div className="text-right">
                  <span className="text-[11px] text-slate-400 block">Submitted At</span>
                  <span className="text-xs text-slate-200 font-mono">
                    {new Date(activeTicket.createdAt).toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Customer Prompt Box */}
              <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 space-y-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Customer Message</span>
                </span>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
                  {activeTicket.query}
                </p>
              </div>

              {/* Full Trust Gate Evaluation Breakdown */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Trust Gate Diagnostic Audit
                </span>
                <TrustScoreBadge
                  evaluation={activeTicket.trustEvaluation}
                  showBreakdown={true}
                  size="lg"
                />
              </div>

              {/* Response Workspace */}
              <div className="space-y-4 pt-2 border-t border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                    Specialist Response Formulation
                  </span>
                  {activeTicket.humanReview && (
                    <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Reviewed by {activeTicket.humanReview.reviewer}</span>
                    </span>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Customer-Facing Final Message:
                  </label>
                  <textarea
                    id="specialist-response-textarea"
                    rows={6}
                    value={editedResponse}
                    onChange={(e) => setEditedResponse(e.target.value)}
                    className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-700 text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed font-sans"
                    placeholder="Enter or modify the final response to customer..."
                  />
                </div>

                {/* Evidence Learning Promotion Section */}
                <div className="bg-gradient-to-br from-emerald-950/40 to-slate-950 p-4 rounded-xl border border-emerald-800/40 space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        id="learn-as-evidence-toggle"
                        checked={learnAsEvidence}
                        onChange={(e) => setLearnAsEvidence(e.target.checked)}
                        className="w-4 h-4 rounded text-emerald-500 focus:ring-emerald-400 bg-slate-900 border-slate-700"
                      />
                      <span className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                        <BookPlus className="w-4 h-4" />
                        <span>Promote Decision to Human-Validated Evidence (Learn)</span>
                      </span>
                    </label>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700/50">
                      Active Learning
                    </span>
                  </div>

                  {learnAsEvidence && (
                    <div className="space-y-3 pt-2 text-xs">
                      <p className="text-[11px] text-slate-300">
                        This extracts your decision as permanent Ground Truth. Similar queries in the future will automatically match this evidence and receive higher trust scores!
                      </p>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">Evidence Title</label>
                          <input
                            type="text"
                            id="new-evidence-title"
                            value={evidenceTitle}
                            onChange={(e) => setEvidenceTitle(e.target.value)}
                            placeholder="e.g. Inter-Subsidiary Seat Credit Protocol"
                            className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1">Index Tags (comma separated)</label>
                          <input
                            type="text"
                            id="new-evidence-tags"
                            value={evidenceTags}
                            onChange={(e) => setEvidenceTags(e.target.value)}
                            placeholder="seat, transfer, subsidiary"
                            className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-[11px] text-slate-400 mb-1">Evidence Rule / Policy Content</label>
                        <textarea
                          rows={2}
                          id="new-evidence-content"
                          value={evidenceSnippetContent}
                          onChange={(e) => setEvidenceSnippetContent(e.target.value)}
                          placeholder="State the explicit rule validated by human operator..."
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500 leading-relaxed"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Specialist Action Buttons */}
                <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    id="approve-draft-btn"
                    onClick={handleApprove}
                    disabled={isLoading}
                    className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs sm:text-sm font-medium flex items-center gap-2 transition-all cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Approve Verbatim Draft</span>
                  </button>

                  <button
                    type="button"
                    id="save-and-learn-btn"
                    onClick={handleEditAndLearn}
                    disabled={isLoading || !editedResponse.trim()}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-semibold text-xs sm:text-sm flex items-center gap-2 shadow-lg shadow-emerald-950/60 transition-all cursor-pointer"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Save Response & Learn Evidence</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-16 text-center text-slate-400">
              Select a ticket from the queue on the left to inspect its trust evaluation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
