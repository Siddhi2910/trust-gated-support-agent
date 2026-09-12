import React, { useState } from 'react';
import {
  Send,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  CheckCircle2,
  Clock,
  ArrowRight,
  HelpCircle,
  FileText,
  Building2,
  User,
  DollarSign
} from 'lucide-react';
import { CustomerTicket, TicketCategory } from '../types';
import { TrustScoreBadge } from './TrustScoreBadge';

interface CustomerPortalProps {
  tickets: CustomerTicket[];
  onSubmitTicket: (ticketData: {
    customerName: string;
    customerEmail: string;
    companyName: string;
    tier: 'Starter' | 'Professional' | 'Enterprise';
    category: TicketCategory;
    query: string;
    transactionAmount?: number;
  }) => Promise<CustomerTicket | null>;
  onNavigateToSpecialist: (ticketId?: string) => void;
  isLoading: boolean;
}

const PRESET_SCENARIOS = [
  {
    title: 'Refund Within 14-Day Policy ($49)',
    description: 'Satisfies human-validated quota and timeframe conditions',
    category: 'Billing & Refunds' as TicketCategory,
    tier: 'Professional' as const,
    amount: 49,
    query: 'Hi team, we were billed $49 on our account last week for an accidental upgrade. We have only used 4% of our quota and are within the 14 days. Can we please get a refund to our original payment card?'
  },
  {
    title: 'High-Value Seat Reallocation ($375)',
    description: 'Exceeds financial cap & lacks inter-subsidiary precedent',
    category: 'Product & Subscriptions' as TicketCategory,
    tier: 'Professional' as const,
    amount: 375,
    query: 'We have 5 unused Pro seats in our Germany entity and want to transfer them to our US subsidiary without double paying. Can you apply a direct inter-company voucher credit?'
  },
  {
    title: 'Bypass 2FA During Outage',
    description: 'Triggers SOC2 security boundary & mandatory human takeover',
    category: 'Security & Compliance' as TicketCategory,
    tier: 'Enterprise' as const,
    amount: 0,
    query: 'Emergency! Our lead engineer lost their phone and cannot log in with 2FA. We have a production deployment right now. Please disable 2FA for this user immediately!'
  },
  {
    title: 'Enterprise Severity-1 Outage SLA',
    description: 'Matches human-validated 15-minute engineering SLA',
    category: 'Technical Integration' as TicketCategory,
    tier: 'Enterprise' as const,
    amount: 0,
    query: 'Our production API is experiencing 502 Bad Gateway responses across all endpoints. We are on the Enterprise plan and need immediate Severity-1 escalation.'
  }
];

export const CustomerPortal: React.FC<CustomerPortalProps> = ({
  tickets,
  onSubmitTicket,
  onNavigateToSpecialist,
  isLoading
}) => {
  const [customerName, setCustomerName] = useState('Elena Rostova');
  const [customerEmail, setCustomerEmail] = useState('elena@quantumscale.ai');
  const [companyName, setCompanyName] = useState('QuantumScale AI');
  const [tier, setTier] = useState<'Starter' | 'Professional' | 'Enterprise'>('Professional');
  const [category, setCategory] = useState<TicketCategory>('Billing & Refunds');
  const [query, setQuery] = useState('');
  const [transactionAmount, setTransactionAmount] = useState<string>('');
  const [latestSubmittedTicket, setLatestSubmittedTicket] = useState<CustomerTicket | null>(null);

  const handleApplyPreset = (preset: typeof PRESET_SCENARIOS[0]) => {
    setCategory(preset.category);
    setTier(preset.tier);
    setQuery(preset.query);
    setTransactionAmount(preset.amount > 0 ? preset.amount.toString() : '');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const ticket = await onSubmitTicket({
      customerName,
      customerEmail,
      companyName,
      tier,
      category,
      query: query.trim(),
      transactionAmount: transactionAmount ? parseFloat(transactionAmount) : undefined
    });

    if (ticket) {
      setLatestSubmittedTicket(ticket);
      setQuery('');
      setTransactionAmount('');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Intro Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 border border-cyan-800/40 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" />
            <span>Interactive Customer Helpdesk</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-100 mb-2">
            Experience the Trust-Gated Customer Support Workflow
          </h2>
          <p className="text-slate-300 text-sm leading-relaxed">
            Every customer inquiry is evaluated in real time against our{' '}
            <strong className="text-cyan-300">Human-Validated Evidence Graph</strong>.
            Queries meeting safety criteria are dispatched autonomously, while policy edge-cases
            and high-risk requests are gated in escrow for specialist review.
          </p>
        </div>

        {/* Preset Buttons */}
        <div className="mt-5 pt-4 border-t border-slate-800/80">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2.5">
            Quick-Test Scenarios:
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {PRESET_SCENARIOS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                id={`preset-btn-${idx}`}
                onClick={() => handleApplyPreset(p)}
                className="text-left p-3 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-800 hover:border-cyan-500/50 transition-all group"
              >
                <div className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors">
                  {p.title}
                </div>
                <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                  {p.description}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Ticket Submission Form */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 mb-4">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Submit a Customer Inquiry</span>
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Customer Name</label>
                  <div className="relative">
                    <User className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      id="ticket-customer-name"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      required
                      className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Account Tier</label>
                  <select
                    id="ticket-tier"
                    value={tier}
                    onChange={(e) => setTier(e.target.value as any)}
                    className="w-full px-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Starter">Starter Plan</option>
                    <option value="Professional">Professional Plan</option>
                    <option value="Enterprise">Enterprise Plan</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Inquiry Category</label>
                  <select
                    id="ticket-category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value as any)}
                    className="w-full px-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Billing & Refunds">Billing & Refunds</option>
                    <option value="Technical Integration">Technical Integration</option>
                    <option value="Security & Compliance">Security & Compliance</option>
                    <option value="Product & Subscriptions">Product & Subscriptions</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Invoice / Amount ($) <span className="text-slate-500 font-normal">(Optional)</span>
                  </label>
                  <div className="relative">
                    <DollarSign className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                    <input
                      type="number"
                      id="ticket-amount"
                      placeholder="e.g. 49"
                      value={transactionAmount}
                      onChange={(e) => setTransactionAmount(e.target.value)}
                      className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Message / Question</label>
                <textarea
                  id="ticket-query-textarea"
                  rows={4}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Describe your issue or question in detail..."
                  required
                  className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 leading-relaxed"
                />
              </div>

              <button
                type="submit"
                id="submit-ticket-btn"
                disabled={isLoading || !query.trim()}
                className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-medium text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Evaluating Through Trust Gate...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit & Run Trust Gate Evaluation</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Live Evaluation Result & Response Stream */}
        <div className="lg:col-span-7 space-y-6">
          {latestSubmittedTicket ? (
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-cyan-400 font-bold">
                    {latestSubmittedTicket.id}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                    {latestSubmittedTicket.category}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">
                  {new Date(latestSubmittedTicket.createdAt).toLocaleTimeString()}
                </span>
              </div>

              {/* Trust Evaluation Meter */}
              <TrustScoreBadge
                evaluation={latestSubmittedTicket.trustEvaluation}
                showBreakdown={true}
              />

              {/* Customer Inquiry Echo */}
              <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 text-xs space-y-1">
                <span className="text-slate-400 font-medium">Customer Prompt:</span>
                <p className="text-slate-200 italic leading-relaxed">
                  "{latestSubmittedTicket.query}"
                </p>
              </div>

              {/* System Response Outcome */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                    {latestSubmittedTicket.status === 'autonomous_dispatched' ? (
                      <>
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        <span className="text-emerald-400">Autonomous Instant Resolution</span>
                      </>
                    ) : latestSubmittedTicket.status === 'gated_review' ? (
                      <>
                        <ShieldAlert className="w-4 h-4 text-amber-400" />
                        <span className="text-amber-400">Held in Trust Gate Escrow</span>
                      </>
                    ) : (
                      <>
                        <ShieldX className="w-4 h-4 text-rose-400" />
                        <span className="text-rose-400">Escalated to Human Specialist</span>
                      </>
                    )}
                  </span>

                  {latestSubmittedTicket.status !== 'autonomous_dispatched' && (
                    <button
                      id="view-in-specialist-queue-btn"
                      type="button"
                      onClick={() => onNavigateToSpecialist(latestSubmittedTicket.id)}
                      className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium bg-cyan-950/50 px-2 py-1 rounded border border-cyan-800/60 hover:bg-cyan-900/50 transition-colors"
                    >
                      <span>Review in Specialist Station</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs sm:text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {latestSubmittedTicket.finalResponse || latestSubmittedTicket.aiDraft}
                </div>
              </div>

              {/* Matched Ground Truth Evidence Citations */}
              {latestSubmittedTicket.matchedEvidence.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Cited Human-Validated Evidence Sources:</span>
                  </span>
                  <div className="space-y-2">
                    {latestSubmittedTicket.matchedEvidence.map((ev) => (
                      <div
                        key={ev.id}
                        className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between text-slate-300">
                          <span className="font-semibold text-cyan-300">{ev.title}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                            Validated by {ev.validator}
                          </span>
                        </div>
                        <p className="text-slate-400 text-[11px] leading-relaxed line-clamp-2">
                          {ev.content}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-12 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-800/80 flex items-center justify-center mx-auto text-slate-400">
                <Sparkles className="w-6 h-6 text-cyan-400" />
              </div>
              <h4 className="text-sm font-semibold text-slate-200">No Active Query Selected</h4>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                Choose one of the quick presets above or submit a custom inquiry to inspect how the Trust Gate evaluates confidence and policy safety.
              </p>
            </div>
          )}

          {/* Recent Tickets History */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
              <span>Recent Inquiries in Session</span>
              <span className="text-slate-400 font-normal">{tickets.length} total</span>
            </h4>

            <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
              {tickets.map((t) => (
                <div
                  key={t.id}
                  onClick={() => setLatestSubmittedTicket(t)}
                  className="p-3 rounded-xl bg-slate-950/60 hover:bg-slate-850 border border-slate-800/80 hover:border-slate-700 cursor-pointer transition-all flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-cyan-400 font-semibold">{t.id}</span>
                      <span className="text-xs text-slate-300 font-medium truncate">
                        {t.customerName} ({t.companyName})
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 truncate mt-0.5">{t.query}</p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <TrustScoreBadge evaluation={t.trustEvaluation} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
