import React, { useState } from 'react';
import {
  BookOpen,
  PlusCircle,
  Search,
  CheckCircle,
  Star,
  Trash2,
  Tag,
  Clock,
  UserCheck,
  Shield,
  Filter,
  Sparkles
} from 'lucide-react';
import { EvidenceSnippet, TicketCategory } from '../types';

interface EvidenceHubProps {
  evidenceList: EvidenceSnippet[];
  onAddEvidence: (newEvidence: {
    title: string;
    content: string;
    category: TicketCategory;
    validator: string;
    tags: string[];
    trustWeight: number;
  }) => Promise<void>;
  onDeleteEvidence: (id: string) => Promise<void>;
  isLoading: boolean;
}

export const EvidenceHub: React.FC<EvidenceHubProps> = ({
  evidenceList,
  onAddEvidence,
  onDeleteEvidence,
  isLoading
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);

  // New Evidence Form state
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newCategory, setNewCategory] = useState<TicketCategory>('Billing & Refunds');
  const [newValidator, setNewValidator] = useState('Elena Rostova (Compliance Officer)');
  const [newTags, setNewTags] = useState('policy, compliance');
  const [newTrustWeight, setNewTrustWeight] = useState(5);

  const filteredEvidence = evidenceList.filter((ev) => {
    const matchesSearch =
      ev.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.tags.some(t => t.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || ev.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleCreateEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;

    await onAddEvidence({
      title: newTitle.trim(),
      content: newContent.trim(),
      category: newCategory,
      validator: newValidator.trim(),
      tags: newTags.split(',').map(s => s.trim()),
      trustWeight: newTrustWeight
    });

    setNewTitle('');
    setNewContent('');
    setShowAddModal(false);
  };

  const categories = [
    'all',
    'Billing & Refunds',
    'Technical Integration',
    'Security & Compliance',
    'Account & Access',
    'Product & Subscriptions'
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 border border-emerald-800/40 p-6 rounded-2xl shadow-lg">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <BookOpen className="w-4 h-4" />
            <span>Human-Validated Evidence Graph</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-100">
            Ground Truth Knowledge Repository
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
            The AI agent derives its confidence directly from these human-verified policy rules.
            Every validated rule raises the autonomous resolution ceiling while eliminating hallucinations.
          </p>
        </div>

        <button
          type="button"
          id="add-evidence-modal-btn"
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-medium text-xs sm:text-sm flex items-center gap-2 shadow-lg shadow-emerald-950/50 transition-all shrink-0 cursor-pointer"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Add Ground Truth Rule</span>
        </button>
      </div>

      {/* Search & Category Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            id="search-evidence-input"
            placeholder="Search policies, tags, or content..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm rounded-xl bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              id={`cat-filter-${cat.toLowerCase().replace(/\s+/g, '-')}`}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {cat === 'all' ? 'All Categories' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Evidence Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredEvidence.map((ev) => (
          <div
            key={ev.id}
            id={`evidence-card-${ev.id}`}
            className="bg-slate-900/80 border border-slate-800 hover:border-emerald-500/40 rounded-2xl p-5 space-y-4 transition-all flex flex-col justify-between shadow-lg"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {ev.category}
                </span>
                <div className="flex items-center gap-1 text-amber-400" title={`Trust Weight: ${ev.trustWeight}/5`}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className={`w-3 h-3 ${i < ev.trustWeight ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`}
                    />
                  ))}
                </div>
              </div>

              <h3 className="text-sm font-bold text-slate-100 leading-snug">
                {ev.title}
              </h3>

              <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                "{ev.content}"
              </p>
            </div>

            <div className="space-y-3 pt-3 border-t border-slate-800/80 text-xs">
              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {ev.tags.map((tag, i) => (
                  <span
                    key={i}
                    className="text-[10px] px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Validator & Citations */}
              <div className="flex items-center justify-between text-slate-400 text-[11px]">
                <span className="flex items-center gap-1 text-emerald-400 font-medium">
                  <UserCheck className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[160px]">{ev.validator}</span>
                </span>
                <span className="text-slate-400 bg-slate-800 px-2 py-0.5 rounded text-[10px]">
                  {ev.useCount} citations
                </span>
              </div>

              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(ev.validatedAt).toLocaleDateString()}
                </span>
                <button
                  type="button"
                  id={`delete-ev-btn-${ev.id}`}
                  onClick={() => onDeleteEvidence(ev.id)}
                  className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                  title="Remove from active evidence"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Evidence Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Inject Validated Ground Truth Rule</span>
              </h3>
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateEvidence} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Rule Title</label>
                <input
                  type="text"
                  required
                  id="modal-evidence-title"
                  placeholder="e.g. Enterprise Annual Commitment Termination Terms"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
                  <select
                    id="modal-evidence-category"
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value as any)}
                    className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="Billing & Refunds">Billing & Refunds</option>
                    <option value="Technical Integration">Technical Integration</option>
                    <option value="Security & Compliance">Security & Compliance</option>
                    <option value="Product & Subscriptions">Product & Subscriptions</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Trust Weight (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    id="modal-evidence-weight"
                    value={newTrustWeight}
                    onChange={(e) => setNewTrustWeight(parseInt(e.target.value) || 5)}
                    className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Authoritative Rule Text</label>
                <textarea
                  rows={4}
                  required
                  id="modal-evidence-content"
                  placeholder="State the exact policy conditions, constraints, and instructions..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500 leading-relaxed"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Human Validator</label>
                  <input
                    type="text"
                    required
                    id="modal-evidence-validator"
                    value={newValidator}
                    onChange={(e) => setNewValidator(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Tags (comma separated)</label>
                  <input
                    type="text"
                    id="modal-evidence-tags"
                    placeholder="sla, enterprise, billing"
                    value={newTags}
                    onChange={(e) => setNewTags(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  id="modal-save-evidence-btn"
                  disabled={isLoading}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-md shadow-emerald-950/50"
                >
                  Confirm & Commit Ground Truth
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
