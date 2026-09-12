import React, { useState } from 'react';
import {
  Sliders,
  Play,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  Info,
  Layers,
  Zap
} from 'lucide-react';
import { TrustGateConfig, TicketCategory } from '../types';
import { TrustScoreBadge } from './TrustScoreBadge';

interface TrustSandboxProps {
  config: TrustGateConfig;
  onUpdateConfig: (newConfig: Partial<TrustGateConfig>) => Promise<void>;
  onSimulateQuery: (data: {
    query: string;
    category: TicketCategory;
    transactionAmount?: number;
    companyTier: 'Starter' | 'Professional' | 'Enterprise';
  }) => Promise<any>;
  onAddEvidence: (newEvidence: any) => Promise<void>;
  isLoading: boolean;
}

export const TrustSandbox: React.FC<TrustSandboxProps> = ({
  config,
  onUpdateConfig,
  onSimulateQuery,
  onAddEvidence,
  isLoading
}) => {
  // Sandbox form state
  const [simQuery, setSimQuery] = useState(
    'Can we pause our subscription for 3 months during our off-season downtime?'
  );
  const [simCategory, setSimCategory] = useState<TicketCategory>('Product & Subscriptions');
  const [simTier, setSimTier] = useState<'Starter' | 'Professional' | 'Enterprise'>('Professional');
  const [simAmount, setSimAmount] = useState<string>('');
  const [simulationResult, setSimulationResult] = useState<any | null>(null);

  // Evidence Learning Demo State
  const [demoStep, setDemoStep] = useState<1 | 2 | 3>(1);
  const [demoStatusMessage, setDemoStatusMessage] = useState<string | null>(null);

  const handleRunSimulation = async () => {
    if (!simQuery.trim()) return;
    const result = await onSimulateQuery({
      query: simQuery.trim(),
      category: simCategory,
      transactionAmount: simAmount ? parseFloat(simAmount) : undefined,
      companyTier: simTier
    });
    setSimulationResult(result);
  };

  // 3-step interactive learning walkthrough
  const handleRunDemoStep1 = async () => {
    setSimQuery('Can we pause our subscription for 3 months during our off-season downtime?');
    setSimCategory('Product & Subscriptions');
    const result = await onSimulateQuery({
      query: 'Can we pause our subscription for 3 months during our off-season downtime?',
      category: 'Product & Subscriptions',
      companyTier: 'Professional'
    });
    setSimulationResult(result);
    setDemoStep(2);
    setDemoStatusMessage('Query tested without ground truth: Trust Gate holds the ticket in Escrow because no human-validated evidence exists for subscription pausing.');
  };

  const handleRunDemoStep2 = async () => {
    // Inject the human-validated policy
    await onAddEvidence({
      title: 'Seasonal Subscription Pausing Terms',
      content: 'Pro and Enterprise accounts in good standing may pause their recurring subscription for up to 90 consecutive days once per calendar year with a $10/month seat reservation fee. Access to existing archived projects remains read-only during the pause.',
      category: 'Product & Subscriptions',
      validator: 'Rachel Thorne (VP Customer Experience)',
      tags: ['pause', 'seasonal', 'off-season', 'subscription', 'downtime'],
      trustWeight: 5
    });
    setDemoStep(3);
    setDemoStatusMessage('Human specialist validated new Ground Truth policy: "Seasonal Subscription Pausing Terms" (5/5 weight). Ready to re-test.');
  };

  const handleRunDemoStep3 = async () => {
    const result = await onSimulateQuery({
      query: 'Can we pause our subscription for 3 months during our off-season downtime?',
      category: 'Product & Subscriptions',
      companyTier: 'Professional'
    });
    setSimulationResult(result);
    setDemoStep(1);
    setDemoStatusMessage('Active Evidence Learning in action! The exact same query now scores high trust and dispatches autonomously with zero hallucinations.');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-purple-950/40 to-slate-900 border border-purple-800/40 p-6 rounded-2xl shadow-lg">
        <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold uppercase tracking-wider mb-1">
          <Sliders className="w-4 h-4" />
          <span>Trust Gate Governance & Sandbox</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-slate-100">
          Threshold Calibration & Learning Simulation
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Fine-tune the security boundaries, financial limits, and confidence thresholds that govern the automated trust gate. Test live queries to inspect decision criteria before deploying to production.
        </p>
      </div>

      {/* Guided Walkthrough: Evidence Learning in 3 Steps */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Interactive Demonstration: Active Evidence Learning
            </h3>
          </div>
          <span className="text-xs text-slate-400">Step {demoStep} of 3</span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          See how the Trust Gate protects customer experience by holding unfamiliar queries in escrow, and how validating a human decision instantly enables autonomous handling for all future requests.
        </p>

        {demoStatusMessage && (
          <div className="p-3.5 rounded-xl bg-purple-950/60 border border-purple-800/50 text-purple-200 text-xs flex items-start gap-2">
            <Info className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
            <span>{demoStatusMessage}</span>
          </div>
        )}

        <div className="flex flex-wrap gap-3 pt-1">
          {demoStep === 1 && (
            <button
              type="button"
              id="demo-step-1-btn"
              onClick={handleRunDemoStep1}
              disabled={isLoading}
              className="px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md transition-all cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Step 1: Test Unverified Query (Expect Gated Review)</span>
            </button>
          )}

          {demoStep === 2 && (
            <button
              type="button"
              id="demo-step-2-btn"
              onClick={handleRunDemoStep2}
              disabled={isLoading}
              className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md transition-all cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Step 2: Validate Policy & Teach AI (Learn Evidence)</span>
            </button>
          )}

          {demoStep === 3 && (
            <button
              type="button"
              id="demo-step-3-btn"
              onClick={handleRunDemoStep3}
              disabled={isLoading}
              className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md transition-all cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Step 3: Retest Same Query (Expect Auto-Dispatch)</span>
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Governance Settings */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-5 shadow-lg">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              <span>Trust Gate Parameters</span>
            </h3>

            {/* Threshold 1: Auto Dispatch */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Autonomous Dispatch Threshold</span>
                <span className="font-bold text-emerald-400 font-mono">
                  {config.autoDispatchThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="60"
                max="95"
                id="slider-auto-threshold"
                value={config.autoDispatchThreshold}
                onChange={(e) => onUpdateConfig({ autoDispatchThreshold: parseInt(e.target.value) })}
                className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
              />
              <p className="text-[11px] text-slate-400">
                Queries scoring at or above this confidence level with zero risk flags are dispatched instantly.
              </p>
            </div>

            {/* Threshold 2: Human Takeover */}
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Mandatory Human Takeover Floor</span>
                <span className="font-bold text-rose-400 font-mono">
                  {config.humanTakeoverThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="20"
                max="60"
                id="slider-takeover-threshold"
                value={config.humanTakeoverThreshold}
                onChange={(e) => onUpdateConfig({ humanTakeoverThreshold: parseInt(e.target.value) })}
                className="w-full accent-rose-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
              />
              <p className="text-[11px] text-slate-400">
                Queries below this threshold trigger direct human takeover and priority escalation.
              </p>
            </div>

            {/* Threshold 3: Financial Cap */}
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Financial Cap Requiring Sign-off</span>
                <span className="font-bold text-amber-400 font-mono">
                  ${config.refundLimitRequiringHuman}
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="500"
                step="25"
                id="slider-refund-limit"
                value={config.refundLimitRequiringHuman}
                onChange={(e) => onUpdateConfig({ refundLimitRequiringHuman: parseInt(e.target.value) })}
                className="w-full accent-amber-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
              />
              <p className="text-[11px] text-slate-400">
                Any refund or credit request exceeding this amount is held in Trust Gate Escrow.
              </p>
            </div>

            {/* Active Learning Toggle */}
            <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-slate-200 block">
                  Continuous Evidence Learning
                </span>
                <span className="text-[11px] text-slate-400">
                  Automatically register verified human edits as ground truth
                </span>
              </div>
              <input
                type="checkbox"
                id="toggle-active-learning"
                checked={config.activeLearningEnabled}
                onChange={(e) => onUpdateConfig({ activeLearningEnabled: e.target.checked })}
                className="w-4 h-4 rounded text-emerald-500 bg-slate-950 border-slate-700 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Live Simulator Workspace */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-lg">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <Play className="w-4 h-4 text-cyan-400" />
              <span>Live Query Simulator</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
                <select
                  value={simCategory}
                  onChange={(e) => setSimCategory(e.target.value as any)}
                  className="w-full px-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="Billing & Refunds">Billing & Refunds</option>
                  <option value="Technical Integration">Technical Integration</option>
                  <option value="Security & Compliance">Security & Compliance</option>
                  <option value="Product & Subscriptions">Product & Subscriptions</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Account Tier</label>
                <select
                  value={simTier}
                  onChange={(e) => setSimTier(e.target.value as any)}
                  className="w-full px-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="Starter">Starter</option>
                  <option value="Professional">Professional</option>
                  <option value="Enterprise">Enterprise</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Customer Query Prompt</label>
              <textarea
                rows={3}
                value={simQuery}
                onChange={(e) => setSimQuery(e.target.value)}
                placeholder="Enter query to evaluate against active trust gate..."
                className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed"
              />
            </div>

            <button
              type="button"
              id="run-simulation-btn"
              onClick={handleRunSimulation}
              disabled={isLoading || !simQuery.trim()}
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-medium text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-purple-950/50 transition-all cursor-pointer"
            >
              <Play className="w-4 h-4" />
              <span>Evaluate Trust Gate Rationale</span>
            </button>

            {/* Simulation Diagnostic Output */}
            {simulationResult && (
              <div className="mt-4 pt-4 border-t border-slate-800 space-y-4">
                <TrustScoreBadge
                  evaluation={simulationResult.evaluation}
                  showBreakdown={true}
                  size="lg"
                />

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
                  <span className="font-semibold text-slate-300 block">Generated Response Draft:</span>
                  <p className="text-slate-300 italic whitespace-pre-wrap leading-relaxed">
                    {simulationResult.draft}
                  </p>
                </div>

                {simulationResult.matchedEvidence && simulationResult.matchedEvidence.length > 0 && (
                  <div className="space-y-1.5 text-xs">
                    <span className="font-semibold text-slate-400">
                      Matched Ground Truth Rules ({simulationResult.matchedEvidence.length}):
                    </span>
                    <div className="space-y-1.5">
                      {simulationResult.matchedEvidence.map((m: any) => (
                        <div key={m.id} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-300">
                          <div className="font-semibold text-cyan-300">{m.title}</div>
                          <div className="text-[11px] text-slate-400 mt-0.5">{m.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Real Trust Receipt Metadata */}
                {simulationResult.pipelineResult?.trust_receipt && (
                  <div className="p-3.5 rounded-xl bg-slate-950 border border-cyan-900/40 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 font-mono text-cyan-400 font-semibold">
                        <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                        <span>TrustReceipt: {simulationResult.pipelineResult.trust_receipt.receipt_id}</span>
                      </div>
                      <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                        Taxonomy {simulationResult.pipelineResult.trust_receipt.taxonomy_version}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] pt-1">
                      <div className="p-1.5 rounded bg-slate-900/80 border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Decision</span>
                        <span className="font-medium text-slate-200">
                          {simulationResult.pipelineResult.trust_receipt.decision}
                        </span>
                      </div>
                      <div className="p-1.5 rounded bg-slate-900/80 border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Queue</span>
                        <span className="font-medium text-slate-200">
                          {simulationResult.pipelineResult.trust_receipt.target_queue}
                        </span>
                      </div>
                      <div className="p-1.5 rounded bg-slate-900/80 border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Groundedness</span>
                        <span className="font-medium text-emerald-400">
                          {Math.round((simulationResult.pipelineResult.trust_receipt.groundedness_score ?? 1.0) * 100)}%
                        </span>
                      </div>
                      <div className="p-1.5 rounded bg-slate-900/80 border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Claims Status</span>
                        <span className="font-medium text-cyan-300">
                          {simulationResult.pipelineResult.trust_receipt.claims_verified ? 'Verified Grounded' : 'Abstention'}
                        </span>
                      </div>
                    </div>

                    <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-800/80">
                      <span>Classifier: {simulationResult.pipelineResult.trust_receipt.model_versions?.intent_classifier}</span>
                      <span>Gate: {simulationResult.pipelineResult.trust_receipt.model_versions?.risk_gate}</span>
                      <span>Verifier: {simulationResult.pipelineResult.trust_receipt.model_versions?.claim_verifier}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
