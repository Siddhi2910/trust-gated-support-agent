import React, { useState, useEffect } from 'react';
import { Header, AppTab } from './components/Header';
import { HumanReviewWorkspace } from './components/HumanReviewWorkspace';
import { CustomerPortal } from './components/CustomerPortal';
import { SpecialistQueue } from './components/SpecialistQueue';
import { EvidenceHub } from './components/EvidenceHub';
import { TrustSandbox } from './components/TrustSandbox';
import {
  CustomerTicket,
  EvidenceSnippet,
  TrustGateConfig,
  SystemMetrics,
  TicketCategory
} from './types';
import { initialEvidenceBase, initialTickets, defaultConfig } from './mockData';

export default function App() {
  const [currentTab, setCurrentTab] = useState<AppTab>('golden-review');
  const [tickets, setTickets] = useState<CustomerTicket[]>(initialTickets);
  const [evidenceList, setEvidenceList] = useState<EvidenceSnippet[]>(initialEvidenceBase);
  const [config, setConfig] = useState<TrustGateConfig>(defaultConfig);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    totalTickets: initialTickets.length,
    autonomousDispatchedCount: initialTickets.filter(t => t.status === 'autonomous_dispatched').length,
    gatedReviewedCount: initialTickets.filter(t => t.status === 'gated_review').length,
    escalatedCount: initialTickets.filter(t => t.status === 'escalated').length,
    evidenceCount: initialEvidenceBase.length,
    avgTrustScore: 64,
    humanLearnedCount: 0
  });

  const [selectedTicketId, setSelectedTicketId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  // Fetch initial data from server
  const fetchAllData = async () => {
    try {
      const [ticketsRes, evidenceRes, configRes] = await Promise.all([
        fetch('/api/tickets').then(r => r.ok ? r.json() : null),
        fetch('/api/evidence').then(r => r.ok ? r.json() : null),
        fetch('/api/config').then(r => r.ok ? r.json() : null)
      ]);

      if (ticketsRes?.tickets) {
        setTickets(ticketsRes.tickets);
      }
      if (evidenceRes?.evidence) {
        setEvidenceList(evidenceRes.evidence);
      }
      if (configRes) {
        if (configRes.config) setConfig(configRes.config);
        if (configRes.metrics) setMetrics(configRes.metrics);
      }
    } catch (e) {
      console.warn('Backend loading or offline, utilizing active state');
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // Update metrics dynamically
  const recalculateMetrics = (currentTickets: CustomerTicket[], currentEvidence: EvidenceSnippet[]) => {
    const total = currentTickets.length;
    const auto = currentTickets.filter(t => t.status === 'autonomous_dispatched').length;
    const gated = currentTickets.filter(t => t.status === 'gated_review').length;
    const escalated = currentTickets.filter(t => t.status === 'escalated').length;
    const learned = currentTickets.filter(t => t.humanReview?.newEvidenceExtracted).length;
    const avgTrust = total > 0
      ? Math.round(currentTickets.reduce((acc, t) => acc + t.trustEvaluation.trustScore, 0) / total)
      : 0;

    setMetrics({
      totalTickets: total,
      autonomousDispatchedCount: auto,
      gatedReviewedCount: gated,
      escalatedCount: escalated,
      evidenceCount: currentEvidence.length,
      avgTrustScore: avgTrust,
      humanLearnedCount: learned
    });
  };

  // Submit new ticket from customer portal
  const handleSubmitTicket = async (ticketData: {
    customerName: string;
    customerEmail: string;
    companyName: string;
    tier: 'Starter' | 'Professional' | 'Enterprise';
    category: TicketCategory;
    query: string;
    transactionAmount?: number;
  }): Promise<CustomerTicket | null> => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ticketData)
      });

      if (res.ok) {
        const data = await res.json();
        const newTicket: CustomerTicket = data.ticket;
        const updated = [newTicket, ...tickets];
        setTickets(updated);
        recalculateMetrics(updated, evidenceList);
        showToast(
          newTicket.status === 'autonomous_dispatched'
            ? 'Ticket evaluated with High Trust: Dispatched Autonomously!'
            : 'Ticket held in Trust Gate Escrow for Specialist Review'
        );
        return newTicket;
      }
    } catch (e) {
      console.error('Submit error:', e);
    } finally {
      setIsLoading(false);
    }
    return null;
  };

  // Review & Learn from Specialist Queue
  const handleReviewTicket = async (reviewData: {
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
  }) => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/tickets/${reviewData.ticketId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData)
      });

      if (res.ok) {
        const data = await res.json();
        const updatedTicket: CustomerTicket = data.ticket;
        const newEvidenceBase: EvidenceSnippet[] = data.evidenceBase;

        const updatedTickets = tickets.map(t => (t.id === updatedTicket.id ? updatedTicket : t));
        setTickets(updatedTickets);
        setEvidenceList(newEvidenceBase);
        recalculateMetrics(updatedTickets, newEvidenceBase);

        showToast(
          reviewData.newEvidenceSnippet
            ? `Learned new ground-truth evidence: "${reviewData.newEvidenceSnippet.title}"`
            : `Ticket ${reviewData.ticketId} successfully resolved`
        );
      }
    } catch (e) {
      console.error('Review error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  // Add new evidence directly
  const handleAddEvidence = async (newEvidence: {
    title: string;
    content: string;
    category: TicketCategory;
    validator: string;
    tags: string[];
    trustWeight: number;
  }) => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/evidence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEvidence)
      });

      if (res.ok) {
        const data = await res.json();
        setEvidenceList(data.allEvidence);
        recalculateMetrics(tickets, data.allEvidence);
        showToast(`Ground Truth Rule "${newEvidence.title}" added to active graph`);
      }
    } catch (e) {
      console.error('Add evidence error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  // Delete evidence
  const handleDeleteEvidence = async (id: string) => {
    try {
      const res = await fetch(`/api/evidence/${id}`, { method: 'DELETE' });
      if (res.ok) {
        const data = await res.json();
        setEvidenceList(data.allEvidence);
        recalculateMetrics(tickets, data.allEvidence);
        showToast('Evidence rule removed from knowledge graph');
      }
    } catch (e) {
      console.error('Delete evidence error:', e);
    }
  };

  // Update Trust Gate configuration
  const handleUpdateConfig = async (newConfig: Partial<TrustGateConfig>) => {
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      if (res.ok) {
        const data = await res.json();
        setConfig(data.config);
        showToast('Trust Gate parameters updated');
      }
    } catch (e) {
      console.error('Config update error:', e);
    }
  };

  // Simulate query
  const handleSimulateQuery = async (queryData: any) => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/simulate-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryData)
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setIsLoading(false);
    }
    return null;
  };

  // Reset demo
  const handleResetDemo = async () => {
    setIsResetting(true);
    try {
      const res = await fetch('/api/reset-demo', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setTickets(data.tickets);
        setEvidenceList(data.evidence);
        setConfig(data.config);
        recalculateMetrics(data.tickets, data.evidence);
        showToast('Demo data and knowledge graph reset to initial benchmark state');
      }
    } catch (e) {
      console.error('Reset error:', e);
    } finally {
      setIsResetting(false);
    }
  };

  const navigateToSpecialist = (ticketId?: string) => {
    if (ticketId) {
      setSelectedTicketId(ticketId);
    }
    setCurrentTab('specialist');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-slate-100 px-4 py-3 rounded-xl border border-cyan-500/40 shadow-2xl shadow-cyan-950 text-xs sm:text-sm font-medium flex items-center gap-2 animate-bounce">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Main Header & Tab Navigation */}
      <Header
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        metrics={metrics}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
      />

      {/* Body View by Tab */}
      <main className="flex-1">
        {currentTab === 'golden-review' && (
          <div className="p-4 sm:p-6 lg:p-8">
            <HumanReviewWorkspace />
          </div>
        )}

        {currentTab === 'customer' && (
          <CustomerPortal
            tickets={tickets}
            onSubmitTicket={handleSubmitTicket}
            onNavigateToSpecialist={navigateToSpecialist}
            isLoading={isLoading}
          />
        )}

        {currentTab === 'specialist' && (
          <SpecialistQueue
            tickets={tickets}
            selectedTicketId={selectedTicketId}
            onSelectTicket={setSelectedTicketId}
            onReviewTicket={handleReviewTicket}
            isLoading={isLoading}
          />
        )}

        {currentTab === 'evidence' && (
          <EvidenceHub
            evidenceList={evidenceList}
            onAddEvidence={handleAddEvidence}
            onDeleteEvidence={handleDeleteEvidence}
            isLoading={isLoading}
          />
        )}

        {currentTab === 'sandbox' && (
          <TrustSandbox
            config={config}
            onUpdateConfig={handleUpdateConfig}
            onSimulateQuery={handleSimulateQuery}
            onAddEvidence={handleAddEvidence}
            isLoading={isLoading}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 px-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Trust-Gated Support Agent — Human-Validated Evidence Learning</span>
          <span className="text-slate-400">
            Engineered with Google AI Studio • TypeScript & Vite
          </span>
        </div>
      </footer>
    </div>
  );
}
