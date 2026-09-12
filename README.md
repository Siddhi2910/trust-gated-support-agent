# trust-gated-support-agent

> **Trust-gated AI customer support agent with human-validated evidence learning**

## Overview

The **Trust-Gated Support Agent** is a human-in-the-loop AI customer service platform designed to eliminate hallucinations and enforce operational compliance. Instead of unconstrained generation, the agent scores every incoming customer inquiry against a **Human-Validated Evidence Graph** to determine its trust and safety level:

1. **Autonomous Dispatch (High Trust, ≥ 80%)**: Queries matching verified ground truth policies with zero policy risks are resolved and dispatched instantly to the customer with citation badges.
2. **Trust-Gated Escrow (Medium Trust, 50% - 79%)**: Edge-cases, mid-tier transactions, or incomplete evidence matches hold AI-drafted responses in an escrow queue for human specialist review.
3. **Human Takeover & Escalation (Low Trust / Critical Risk, < 50%)**: Direct policy or security breaches (such as 2FA bypass requests, chargeback threats, or enterprise Sev-1 outages) trigger mandatory human specialist takeover.

## Active Evidence Learning Loop

When a human specialist audits, refines, or answers a gated inquiry, they can promote their decision to **Validated Ground Truth**:
- Captures the authoritative rule text, category, validator identity, and index tags.
- Injects the snippet into the active Knowledge Graph with high trust weight.
- Subsequent similar customer requests automatically match the newly validated evidence, elevating their trust score and moving them from gated review to autonomous resolution.

## Features & Modules

- **Customer Live Portal**: Real-time ticket submission, preset test scenarios (14-day refund, seat reallocations, 2FA emergencies), trust badge diagnostics, and response citations.
- **Specialist Review Station**: Human-in-the-loop triage queue with composite Trust Score breakdown (Evidence Match, Policy Safety, Semantic Certainty, Domain Precedent), response editor, and one-click "Promote to Validated Evidence" tool.
- **Evidence Learning Hub**: Ground-truth policy repository with validator attribution, usage citations, category filters, and manual rule injection.
- **Trust Gate Governance & Sandbox**: Interactive query simulator and threshold calibration controls (Auto-Dispatch threshold, Takeover floor, Financial caps). Includes an interactive 3-step demonstration of active evidence learning.

## Quickstart

```bash
# Install dependencies
npm install

# Start the dev server on port 3000
npm run dev

# Build for production
npm run build
```
