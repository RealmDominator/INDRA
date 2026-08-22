import StatusBadge from './StatusBadge';

export default function HeroSection({
  health,
  corridors = [],
  reserves = {},
  onRunDemo,
  busy,
  lastUpdated,
}) {
  const totalCapacity = reserves.total_capacity_mmt || 5.33;
  const corridorCount = corridors.length || 6;

  return (
    <section className="hero-section" id="overview">
      <div className="hero-header">
        <div>
          <div className="hero-eyebrow">
            <span>● DECISION SUPPORT ARCHITECTURE</span>
            <span style={{ color: 'var(--border-default)' }}>|</span>
            <span>PHASE 1 OPERATIONAL SYSTEM</span>
          </div>
          <h1 className="hero-title">
            From disruption signal <span>to procurement action.</span>
          </h1>
          <p className="hero-lede">
            INDRA monitors maritime chokepoints, extracts structured geopolitical events via bounded AI, computes deterministic supply-chain risk, and generates alternative crude procurement allocations for Indian refiners.
          </p>
        </div>

        <div className="hero-actions">
          <button
            className="btn-primary"
            onClick={onRunDemo}
            disabled={busy}
            style={{ minWidth: '220px', padding: '12px 24px', fontSize: '0.95rem' }}
          >
            {busy ? 'Running Decision Loop…' : '▶ Run Reference Decision Loop'}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span>Backend engine:</span>
            <StatusBadge value="DERIVED" />
            <span>Deterministic Math</span>
          </div>
        </div>
      </div>

      <div className="hero-stats-ribbon">
        <div className="stat-card">
          <span className="stat-label">Daily Crude Inflow</span>
          <div className="stat-value">
            0.56 <small>MMT/day</small>
          </div>
          <div className="stat-sub">
            ~4.1M bpd · 88% Net National Import Share
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-label">Hormuz Dependency</span>
          <div className="stat-value" style={{ color: 'var(--amber)' }}>
            42% <small>of total</small>
          </div>
          <div className="stat-sub">
            Primary Chokepoint · Middle East Crude
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-label">Strategic Reserves (ISPRL)</span>
          <div className="stat-value">
            {Number(totalCapacity).toFixed(2)} <small>MMT</small>
          </div>
          <div className="stat-sub">
            3 Sites (Mangalore, Padur, Vizag) · 9.5d Base
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-label">Monitored Corridors</span>
          <div className="stat-value" style={{ color: 'var(--cyan-bright)' }}>
            {corridorCount} <small>Corridors</small>
          </div>
          <div className="stat-sub">
            Live Risk Tracking · NetworkX Reachability
          </div>
        </div>
      </div>
    </section>
  );
}
