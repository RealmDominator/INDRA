import StatusBadge from './StatusBadge';

export default function CurrentSituation({
  riskData,
  corridors = [],
  onInspectCorridor,
  selectedCorridorId,
  impactLoading,
  impactData,
}) {
  const score = riskData?.display_score != null ? Number(riskData.display_score).toFixed(1) : '—';
  const riskLevel = riskData?.risk_level || 'LOW';
  const components = riskData?.components || {};

  // Standard factor names & fallback weights
  const factors = [
    { key: 'event_severity', label: 'Event Severity (25%)', defaultVal: 0.6 },
    { key: 'event_recency', label: 'Event Recency (20%)', defaultVal: 0.7 },
    { key: 'chokepoint_exposure', label: 'Chokepoint Exposure (20%)', defaultVal: 0.65 },
    { key: 'conflict_sanctions', label: 'Conflict & Sanctions (15%)', defaultVal: 0.4 },
    { key: 'historical_rate', label: 'Historical Disruption Rate (10%)', defaultVal: 0.3 },
    { key: 'india_dependency', label: 'India Dependency Share (10%)', defaultVal: 0.8 },
  ];

  return (
    <section className="section-wrapper" id="situation">
      <div className="section-header">
        <div className="section-title-group">
          <span className="section-eyebrow">● SITUATION ASSESSMENT</span>
          <h2 className="section-title">Current National Risk Matrix</h2>
          <p className="section-desc">
            Multi-factor weighted deterministic risk assessment combined with maritime chokepoint telemetry.
          </p>
        </div>
        <StatusBadge value={riskData?.data_semantic || 'DERIVED'} />
      </div>

      <div className="grid-overview" style={{ marginBottom: '24px' }}>
        {/* Composite National Risk Card */}
        <div className="panel-card elevated">
          <div className="card-header">
            <h3 className="card-title">
              <span>🛡️</span> Composite Disruption Risk
            </h3>
            <StatusBadge value={riskLevel} />
          </div>

          <div className="risk-meter-container">
            <div className="risk-big-score">
              <span className="score-num">{score}</span>
              <span className="score-max">/ 100 INDEX</span>
              <div style={{ marginTop: '8px' }}>
                <StatusBadge value={riskLevel} />
              </div>
            </div>

            <div className="risk-factors-grid">
              {factors.map((f) => {
                const comp = components[f.key];
                const rawVal = comp ? comp.value : f.defaultVal;
                const pct = Math.min(100, Math.max(0, rawVal * 100));
                return (
                  <div className="factor-item" key={f.key}>
                    <div className="factor-label">
                      <span>{f.label}</span>
                      <strong>{pct.toFixed(0)}%</strong>
                    </div>
                    <div className="factor-bar">
                      <div className="factor-bar-fill" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '14px' }}>
            Calculated via Phase-1 deterministic formula: <code style={{ color: 'var(--cyan-bright)', fontFamily: 'var(--font-mono)' }}>risk = 0.25×severity + 0.20×recency + 0.20×chokepoint + 0.15×sanctions + 0.10×history + 0.10×dependency</code>
          </p>
        </div>

        {/* Executive Summary Card */}
        <div className="panel-card">
          <div className="card-header">
            <h3 className="card-title">
              <span>⚡</span> Operational Readiness Alert
            </h3>
            <StatusBadge value="ACTIVE" />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: '8px', padding: '12px 14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <strong style={{ color: 'var(--amber)', fontSize: '0.88rem' }}>HORMUZ CHOKEPOINT CONCENTRATION</strong>
                <StatusBadge value="MONITORED" />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                42% of Indian crude supply transits through the Strait of Hormuz. Elevated regional security posture requires active alternate routing preparedness via Cape of Good Hope.
              </p>
            </div>

            <div style={{ background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.25)', borderRadius: '8px', padding: '12px 14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <strong style={{ color: 'var(--cyan-bright)', fontSize: '0.88rem' }}>RED SEA / SUEZ CANAL PASSAGE</strong>
                <StatusBadge value="ELEVATED" />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                Bab el-Mandeb security advisories remain in effect. Mediterranean and Russian crude parcels experiencing transit time expansion (+10 to 14 days) on Cape rerouting.
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: 'var(--text-muted)', paddingTop: '4px' }}>
              <span>Deterministic Risk Engine</span>
              <span>Model ID: weighted_rule_v1</span>
            </div>
          </div>
        </div>
      </div>

      {/* Maritime Corridors Grid */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', color: '#fff' }}>
            Maritime Supply Corridors ({corridors.length})
          </h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Click corridor card to compute NetworkX graph impact
          </span>
        </div>

        <div className="corridor-matrix">
          {corridors.map((c) => {
            const rawScore = Number(c.display_score || (c.base_risk_score ? c.base_risk_score * 100 : 0));
            const isSelected = selectedCorridorId === c.id;
            const progressClass = rawScore >= 75 ? 'risk-crit' : rawScore >= 55 ? 'risk-high' : rawScore >= 35 ? 'risk-mod' : 'risk-low';

            return (
              <div
                key={c.id || c.code}
                className={`corridor-card ${isSelected ? 'selected' : ''}`}
                onClick={() => onInspectCorridor && onInspectCorridor(c.id, c.code)}
                title="Click to inspect downstream refinery & route impact"
              >
                <div className="corridor-header">
                  <div>
                    <div className="corridor-code">{c.code}</div>
                    <div className="corridor-name">{c.name}</div>
                  </div>
                  <StatusBadge value={c.risk_level || 'MODERATE'} />
                </div>

                <div className="corridor-score-row">
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>RISK INDEX</span>
                  <span className="corridor-score-value">{rawScore.toFixed(1)}</span>
                </div>

                <div className="corridor-progress">
                  <div
                    className={`corridor-progress-fill ${progressClass}`}
                    style={{ width: `${Math.min(100, Math.max(5, rawScore))}%` }}
                  />
                </div>

                <div className="corridor-meta">
                  <span>Dep. Share: {c.india_dependency_share ? `${(Number(c.india_dependency_share) * 100).toFixed(0)}%` : '—'}</span>
                  <span style={{ color: isSelected ? 'var(--cyan-bright)' : 'var(--text-muted)' }}>
                    {isSelected ? '● Graph Loaded' : '→ Inspect Impact'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Network Impact Traversal Drawer (if corridor selected) */}
        {impactData && (
          <div style={{ marginTop: '16px', background: 'rgba(6, 182, 212, 0.06)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '10px', padding: '16px 20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '1.2rem' }}>🕸️</span>
                <strong style={{ color: 'var(--cyan-bright)', fontFamily: 'var(--font-display)' }}>
                  NetworkX Supply Graph Impact Traversal
                </strong>
              </div>
              <StatusBadge value="DERIVED" />
            </div>

            <div className="grid-3" style={{ gap: '12px' }}>
              <div style={{ background: 'rgba(8, 14, 22, 0.6)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Affected Routes</span>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', margin: '4px 0' }}>
                  {impactData.affected_routes?.length || 0} Routes Disrupted
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {impactData.affected_routes?.slice(0, 3).map((r) => r.name).join(', ') || 'None directly mapped'}
                </div>
              </div>

              <div style={{ background: 'rgba(8, 14, 22, 0.6)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Affected Refineries</span>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', margin: '4px 0' }}>
                  {impactData.affected_refineries?.length || 0} Refineries Reached
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {impactData.affected_refineries?.slice(0, 3).map((r) => r.name).join(', ') || 'None directly mapped'}
                </div>
              </div>

              <div style={{ background: 'rgba(8, 14, 22, 0.6)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Source Verification</span>
                <div style={{ fontSize: '0.9rem', color: 'var(--emerald)', margin: '4px 0', fontWeight: 600 }}>
                  PostgreSQL Seed Graph
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  Traversed in-memory via NetworkX (No Neo4j)
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
