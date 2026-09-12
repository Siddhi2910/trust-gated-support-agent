import React from 'react';
import {
  Shield,
  Layers,
  Sparkles,
  Sliders,
  CheckCircle2,
  Clock,
  BookOpen,
  RotateCcw,
  Bot,
  FileCheck
} from 'lucide-react';
import { SystemMetrics } from '../types';

export type AppTab = 'golden-review' | 'customer' | 'specialist' | 'evidence' | 'sandbox';

interface HeaderProps {
  currentTab: AppTab;
  onTabChange: (tab: AppTab) => void;
  metrics: SystemMetrics;
  onResetDemo: () => void;
  isResetting: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onTabChange,
  metrics,
  onResetDemo,
  isResetting
}) => {
  const autoRate = metrics.totalTickets > 0
    ? Math.round((metrics.autonomousDispatchedCount / metrics.totalTickets) * 100)
    : 0;

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Logo and Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-900/30 border border-cyan-400/30">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-lg font-bold text-slate-100 tracking-tight flex items-center gap-2">
                  Trust-Gated Support Agent
                </h1>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800/80 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Active Gate
                </span>
              </div>
              <p className="text-xs text-slate-400">
                AI Customer Support with Human-Validated Evidence Learning
              </p>
            </div>
          </div>

          {/* KPI Snapshot Pills */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <div className="bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-slate-400">Auto-Resolved:</span>
              <span className="font-semibold text-emerald-300">{autoRate}%</span>
              <span className="text-slate-400 text-[11px]">({metrics.autonomousDispatchedCount}/{metrics.totalTickets})</span>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-slate-400">Gated Queue:</span>
              <span className="font-semibold text-amber-300">{metrics.gatedReviewedCount}</span>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400">Ground Truth:</span>
              <span className="font-semibold text-cyan-300">{metrics.evidenceCount} rules</span>
            </div>

            <button
              id="reset-demo-btn"
              type="button"
              onClick={onResetDemo}
              disabled={isResetting}
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-xs flex items-center gap-1 transition-all disabled:opacity-50"
              title="Reset initial demo data"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-2 mt-4 pt-2 border-t border-slate-800/80 overflow-x-auto no-scrollbar">
          <button
            id="nav-tab-golden-review"
            type="button"
            onClick={() => onTabChange('golden-review')}
            className={`px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all flex items-center gap-2 whitespace-nowrap ${
              currentTab === 'golden-review'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/40'
                : 'text-indigo-300 bg-indigo-950/40 hover:bg-indigo-900/50 hover:text-white border border-indigo-800/60'
            }`}
          >
            <FileCheck className="w-4 h-4 text-indigo-400" />
            <span>Golden Set Human Review (170 Cases)</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-800 text-indigo-200">
              Active
            </span>
          </button>

          <button
            id="nav-tab-customer"
            type="button"
            onClick={() => onTabChange('customer')}
            className={`px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
              currentTab === 'customer'
                ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>Customer Live Portal</span>
          </button>

          <button
            id="nav-tab-specialist"
            type="button"
            onClick={() => onTabChange('specialist')}
            className={`px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap relative ${
              currentTab === 'specialist'
                ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Specialist Review Station</span>
            {metrics.gatedReviewedCount > 0 && (
              <span className="w-5 h-5 rounded-full bg-amber-500 text-slate-950 font-bold text-[10px] flex items-center justify-center">
                {metrics.gatedReviewedCount}
              </span>
            )}
          </button>

          <button
            id="nav-tab-evidence"
            type="button"
            onClick={() => onTabChange('evidence')}
            className={`px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
              currentTab === 'evidence'
                ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Evidence Learning Hub</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
              {metrics.evidenceCount}
            </span>
          </button>

          <button
            id="nav-tab-sandbox"
            type="button"
            onClick={() => onTabChange('sandbox')}
            className={`px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
              currentTab === 'sandbox'
                ? 'bg-purple-500/10 text-purple-300 border border-purple-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Trust Gate Governance & Sandbox</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
