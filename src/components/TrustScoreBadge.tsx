import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX, HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { TrustEvaluation } from '../types';

interface TrustScoreBadgeProps {
  evaluation: TrustEvaluation;
  showBreakdown?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const TrustScoreBadge: React.FC<TrustScoreBadgeProps> = ({
  evaluation,
  showBreakdown = false,
  size = 'md'
}) => {
  const [expanded, setExpanded] = React.useState(showBreakdown);
  const { trustScore, gateDecision, factors, riskFlags, reasoning } = evaluation;

  // Determine badge styling based on decision
  const config = {
    AUTO_DISPATCH: {
      label: 'Auto-Dispatched',
      sublabel: 'Safe to send autonomously',
      icon: ShieldCheck,
      bgColor: 'bg-emerald-950/80',
      borderColor: 'border-emerald-500/40',
      textColor: 'text-emerald-300',
      barColor: 'bg-emerald-500',
      ringColor: 'ring-emerald-500/30'
    },
    GATE_REVIEW: {
      label: 'Trust-Gated Escrow',
      sublabel: 'Held for specialist review',
      icon: ShieldAlert,
      bgColor: 'bg-amber-950/80',
      borderColor: 'border-amber-500/40',
      textColor: 'text-amber-300',
      barColor: 'bg-amber-500',
      ringColor: 'ring-amber-500/30'
    },
    HUMAN_TAKEOVER: {
      label: 'Human Takeover Required',
      sublabel: 'Critical policy/risk trigger',
      icon: ShieldX,
      bgColor: 'bg-rose-950/80',
      borderColor: 'border-rose-500/40',
      textColor: 'text-rose-300',
      barColor: 'bg-rose-500',
      ringColor: 'ring-rose-500/30'
    }
  }[gateDecision];

  const Icon = config.icon;

  if (size === 'sm') {
    return (
      <div
        id={`trust-badge-${trustScore}`}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${config.bgColor} ${config.borderColor} ${config.textColor}`}
      >
        <Icon className="w-3.5 h-3.5" />
        <span>{trustScore}%</span>
        <span className="text-slate-400 font-normal">| {config.label}</span>
      </div>
    );
  }

  return (
    <div
      id={`trust-evaluation-card-${trustScore}`}
      className={`rounded-xl border ${config.borderColor} ${config.bgColor} p-3.5 transition-all`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.textColor} bg-slate-900/60 border ${config.borderColor}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-100">{config.label}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${config.textColor} bg-slate-900/80 border ${config.borderColor}`}>
                {trustScore}% Trust Score
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">{config.sublabel}</p>
          </div>
        </div>

        <button
          type="button"
          id="toggle-trust-breakdown-btn"
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 p-1 rounded hover:bg-slate-800/50 transition-colors"
        >
          <span>Factors</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-800/80 rounded-full h-1.5 mt-3 overflow-hidden">
        <div
          className={`h-full rounded-full ${config.barColor} transition-all duration-500`}
          style={{ width: `${Math.min(100, Math.max(5, trustScore))}%` }}
        />
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2.5 text-xs">
          <div className="grid grid-cols-2 gap-2 text-slate-300">
            <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 mb-1">
                <span>Evidence Match</span>
                <span className="font-semibold text-slate-200">{factors.evidenceMatchScore}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-blue-400 h-full" style={{ width: `${factors.evidenceMatchScore}%` }} />
              </div>
            </div>

            <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 mb-1">
                <span>Policy Safety</span>
                <span className="font-semibold text-slate-200">{factors.policySafetyScore}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-emerald-400 h-full" style={{ width: `${factors.policySafetyScore}%` }} />
              </div>
            </div>

            <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 mb-1">
                <span>Semantic Certainty</span>
                <span className="font-semibold text-slate-200">{factors.semanticCertaintyScore}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-purple-400 h-full" style={{ width: `${factors.semanticCertaintyScore}%` }} />
              </div>
            </div>

            <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <div className="flex justify-between items-center text-slate-400 mb-1">
                <span>Domain Precedent</span>
                <span className="font-semibold text-slate-200">{factors.domainPrecedentScore}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-cyan-400 h-full" style={{ width: `${factors.domainPrecedentScore}%` }} />
              </div>
            </div>
          </div>

          {/* Reasoning */}
          {reasoning && (
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 text-slate-300">
              <span className="font-medium text-slate-200">Gate Rationale: </span>
              {reasoning}
            </div>
          )}

          {/* Risk Flags */}
          {riskFlags.length > 0 && (
            <div className="space-y-1">
              <span className="text-[11px] font-semibold text-rose-300 uppercase tracking-wider">Triggered Risk Flags:</span>
              <div className="space-y-1">
                {riskFlags.map((flag, idx) => (
                  <div key={idx} className="flex items-start gap-1.5 text-rose-200 bg-rose-950/40 px-2 py-1 rounded border border-rose-900/50">
                    <span className="text-rose-400 mt-0.5">•</span>
                    <span>{flag}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
