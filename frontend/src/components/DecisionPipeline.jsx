import { useState } from 'react';
import StatusBadge from './StatusBadge';

export default function DecisionPipeline() {
  const [activeStageIndex, setActiveStageIndex] = useState(0);

  const stages = [
    {
      id: 'event',
      step: 1,
      title: 'Geopolitical Event',
      sub: 'Signal Ingestion',
      engine: 'GDELT / RSS / Manual',
      semantic: 'OBSERVED',
      description: 'External raw text dispatches, news articles, or crisis bulletins are ingested via deduplicated adapters or manual console submission.',
      input: 'Unstructured news text, timestamp, source URL',
      output: 'NormalizedEvent record with SHA-256 deduplication',
      role: 'Signal detection & ingestion boundary',
    },
    {
      id: 'extraction',
      step: 2,
      title: 'AI Extraction',
      sub: 'Bounded JSON Schema',
      engine: 'OpenRouter (GPT-4o-mini)',
      semantic: 'DERIVED',
      description: 'The LLM extracts structured event type (SANCTION, ATTACK, etc.), severity (1-10), confidence (0-1), and human-readable country/corridor names. The LLM NEVER touches database IDs or numerical risk math.',
      input: 'Cleaned article text',
      output: 'Strict StructuredEvent Pydantic JSON',
      role: 'Unstructured text to structured metadata',
    },
    {
      id: 'resolution',
      step: 3,
      title: 'Entity Resolution',
      sub: 'Deterministic Fuzzy Match',
      engine: 'RapidFuzz + Postgres Aliases',
      semantic: 'DERIVED',
      description: 'Extracted entity names (e.g. "Strait of Hurmuz", "Bandar Abbas") are matched deterministically against canonical PostgreSQL records with confidence scoring.',
      input: 'Country, corridor, and route strings',
      output: 'Resolved PostgreSQL primary keys & foreign key links',
      role: 'Schema grounding & foreign key integrity',
    },
    {
      id: 'risk',
      step: 4,
      title: 'Risk Calculation',
      sub: 'Weighted Scoring',
      engine: 'Phase-1 Deterministic Formula',
      semantic: 'DERIVED',
      description: 'Weighted 6-factor deterministic risk calculation: 0.25×severity + 0.20×recency + 0.20×chokepoint + 0.15×sanctions + 0.10×history + 0.10×dependency. 100% reproducible math.',
      input: 'Resolved event severity, recency decay, baseline corridor dependency',
      output: '0.0–1.0 risk score, 0–100 display index, risk level (LOW to EXTREME)',
      role: 'Quantitative risk indexing',
    },
    {
      id: 'network',
      step: 5,
      title: 'Network Impact',
      sub: 'Graph Traversal',
      engine: 'NetworkX DiGraph',
      semantic: 'DERIVED',
      description: 'Traverses the India supply topology (corridor → affected route → receiving port → domestic refinery) to identify disrupted logistics links.',
      input: 'Disrupted corridor IDs',
      output: 'Set of affected routes and downstream refineries',
      role: 'Physical supply-chain reachability mapping',
    },
    {
      id: 'scenario',
      step: 6,
      title: 'Scenario Simulator',
      sub: 'Parametric Gap Arithmetic',
      engine: 'Parametric Supply Gap Engine',
      semantic: 'DERIVED',
      description: 'Computes national crude shortfall based on baseline daily import share (0.56 MMT/day), chokepoint dependency factor (e.g. Hormuz 42%), disruption severity, and duration horizon.',
      input: 'Scenario type, duration days (0-365), disruption reduction %',
      output: 'Total crude supply gap (MMT) and daily deficit rate',
      role: 'Crisis volume estimation',
    },
    {
      id: 'procurement',
      step: 7,
      title: 'Procurement Optimizer',
      sub: 'Alternative Crude Solver',
      engine: 'SciPy LP / Deterministic Ranker',
      semantic: 'DERIVED',
      description: 'Ranks and allocates replacement crude from unsanctioned alternative suppliers (West Africa, US Gulf, Latin America) constrained by refinery compatibility, transit days, and cost premiums.',
      input: 'Supply gap target volume (MMT), candidate crude options, refinery constraints',
      output: 'Ranked crude allocation, feasibility status, unmet volume',
      role: 'Actionable purchasing recommendations',
    },
    {
      id: 'evidence',
      step: 8,
      title: 'Evidence Trail',
      sub: 'Audit Provenance',
      engine: 'Staged Evidence Record Store',
      semantic: 'PROVENANCE',
      description: 'Every recommendation preserves its complete provenance chain: Source → Extraction → Entity Resolution → Risk → Scenario → Optimization. Complete institutional accountability.',
      input: 'Intermediate outputs from all preceding stages',
      output: 'Immutable audit trail for policy & procurement officers',
      role: 'Full decision explainability',
    },
  ];

  const current = stages[activeStageIndex];

  return (
    <section className="section-wrapper" id="pipeline">
      <div className="section-header">
        <div className="section-title-group">
          <span className="section-eyebrow">● ARCHITECTURE & METHODOLOGY</span>
          <h2 className="section-title">The Traceable Decision Pipeline</h2>
          <p className="section-desc">
            How INDRA transforms an external geopolitical disruption signal into actionable, explainable crude procurement orders.
          </p>
        </div>
        <StatusBadge value="FROZEN_PIPELINE" />
      </div>

      {/* 8-Stage Step Flow Navigation */}
      <div className="pipeline-stepper" style={{ gridTemplateColumns: 'repeat(8, 1fr)' }}>
        {stages.map((stg, idx) => (
          <div
            key={stg.id}
            className={`pipeline-step-node ${activeStageIndex === idx ? 'active' : ''}`}
            onClick={() => setActiveStageIndex(idx)}
            style={{ cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="step-num-badge">{stg.step}</span>
              <StatusBadge value={stg.semantic} />
            </div>
            <div className="step-node-name">{stg.title}</div>
            <div className="step-node-sub">{stg.sub}</div>
          </div>
        ))}
      </div>

      {/* Selected Stage Detail Card */}
      <div className="panel-card elevated" style={{ borderLeft: '4px solid var(--cyan-bright)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--cyan-bright)', textTransform: 'uppercase' }}>
              Stage {current.step} of 8 · {current.role}
            </span>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', color: '#fff', marginTop: '2px' }}>
              {current.title} — {current.sub}
            </h3>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Engine:</span>
            <strong style={{ color: '#fff', fontSize: '0.85rem' }}>{current.engine}</strong>
            <StatusBadge value={current.semantic} />
          </div>
        </div>

        <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', marginBottom: '18px', lineHeight: '1.6' }}>
          {current.description}
        </p>

        <div className="grid-2" style={{ gap: '16px' }}>
          <div style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Input Contract
            </span>
            <div style={{ color: '#fff', fontSize: '0.85rem', marginTop: '4px', fontWeight: 500 }}>
              {current.input}
            </div>
          </div>

          <div style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Output Artifact
            </span>
            <div style={{ color: 'var(--emerald)', fontSize: '0.85rem', marginTop: '4px', fontWeight: 500 }}>
              {current.output}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
