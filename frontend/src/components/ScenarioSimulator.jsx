import { useState } from 'react';
import StatusBadge from './StatusBadge';

export default function ScenarioSimulator({
  scenarioResult,
  onRunScenario,
  busy,
  duration,
  setDuration,
  reduction,
  setReduction,
  reserves = {},
}) {
  const [selectedPreset, setSelectedPreset] = useState('HORMUZ_FULL');

  const presets = [
    {
      type: 'HORMUZ_FULL',
      label: 'Hormuz Total Blockade',
      desc: '42% national crude inflow blocked (30 days, 100% reduction)',
      defaultDays: 30,
      defaultRed: 100,
    },
    {
      type: 'HORMUZ_PARTIAL',
      label: 'Hormuz Escalation (50%)',
      desc: 'Severe transit delays & 50% flow reduction (45 days)',
      defaultDays: 45,
      defaultRed: 50,
    },
    {
      type: 'RED_SEA',
      label: 'Red Sea Cape Rerouting',
      desc: '5% direct flow blocked + +12d transit expansion via Cape (60 days)',
      defaultDays: 60,
      defaultRed: 100,
    },
    {
      type: 'RUSSIA_LOSS',
      label: 'Russian Urals Disruption',
      desc: '37% discounted crude shortfall from sanctions/insurance (45 days)',
      defaultDays: 45,
      defaultRed: 70,
    },
  ];

  const handleSelectPreset = (preset) => {
    setSelectedPreset(preset.type);
    setDuration(preset.defaultDays);
    setReduction(preset.defaultRed);
    onRunScenario && onRunScenario(preset.type, preset.defaultDays, preset.defaultRed);
  };

  const handleManualRun = () => {
    onRunScenario && onRunScenario(selectedPreset, duration, reduction);
  };

  const sprTotalMmt = reserves.total_capacity_mmt || 5.33;
  const supplyGap = scenarioResult?.supply_gap_mmt || (0.56 * 0.42 * (reduction / 100) * duration);
  const dailyShortfall = scenarioResult?.affected_volume_per_day_mmt || (0.56 * 0.42 * (reduction / 100));
  const daysSprCoverage = dailyShortfall > 0 ? (sprTotalMmt / dailyShortfall).toFixed(1) : '—';

  return (
    <section className="section-wrapper" id="simulator">
      <div className="section-header">
        <div className="section-title-group">
          <span className="section-eyebrow">● PARAMETRIC SIMULATION</span>
          <h2 className="section-title">Crude Disruption Scenario Simulator</h2>
          <p className="section-desc">
            Model national crude shortfalls, SPR drawdown durations, and refinery feed deficiencies under varying chokepoint closure horizons.
          </p>
        </div>
        <StatusBadge value={scenarioResult?.data_semantic || 'DERIVED'} />
      </div>

      <div className="grid-overview">
        {/* Simulator Controls Card */}
        <div className="panel-card elevated">
          <div className="card-header">
            <h3 className="card-title">
              <span>🕹️</span> Disruption Parameters & Presets
            </h3>
            <StatusBadge value="SIMULATED" />
          </div>

          {/* Scenario Preset Selection */}
          <div style={{ marginBottom: '18px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
              Scenario Presets
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginTop: '8px' }}>
              {presets.map((p) => (
                <button
                  key={p.type}
                  className={`preset-pill-btn ${selectedPreset === p.type ? 'active' : ''}`}
                  onClick={() => handleSelectPreset(p)}
                  style={{
                    padding: '10px 12px',
                    textAlign: 'left',
                    background: selectedPreset === p.type ? 'rgba(6, 182, 212, 0.12)' : 'rgba(8, 14, 22, 0.6)',
                    borderColor: selectedPreset === p.type ? 'var(--cyan-bright)' : 'var(--border-subtle)',
                    borderRadius: '8px',
                  }}
                >
                  <div style={{ fontWeight: 600, color: selectedPreset === p.type ? 'var(--cyan-bright)' : '#fff', fontSize: '0.84rem' }}>
                    {p.label}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    {p.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Sliders */}
          <div className="slider-control-group">
            <div className="slider-item">
              <div className="slider-header">
                <span>Disruption Horizon Duration</span>
                <output>{duration} Days</output>
              </div>
              <input
                type="range"
                min="5"
                max="90"
                step="5"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>5 Days (Flash disruption)</span>
                <span>90 Days (Prolonged crisis)</span>
              </div>
            </div>

            <div className="slider-item">
              <div className="slider-header">
                <span>Flow Restriction Severity</span>
                <output>{reduction}% Volume Cut</output>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={reduction}
                onChange={(e) => setReduction(Number(e.target.value))}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>10% (Minor delays)</span>
                <span>100% (Complete corridor denial)</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Deterministic Parametric Model
            </span>
            <button
              className="btn-primary"
              onClick={handleManualRun}
              disabled={busy}
              style={{ padding: '8px 18px' }}
            >
              {busy ? 'Calculating…' : '▶ Run Simulation'}
            </button>
          </div>
        </div>

        {/* Live Simulation Output Card */}
        <div className="panel-card">
          <div className="card-header">
            <h3 className="card-title">
              <span>📊</span> Modeled Supply Shortfall
            </h3>
            <StatusBadge value={scenarioResult?.data_semantic || 'DERIVED'} />
          </div>

          <div className="result-metric-card">
            <div>
              <div className="result-metric-title">Total Cumulative Crude Deficit</div>
              <div className="result-metric-big" style={{ color: 'var(--coral)' }}>
                {Number(supplyGap).toFixed(3)} <small style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>MMT</small>
              </div>
            </div>
            <StatusBadge value="CRITICAL" />
          </div>

          <div className="grid-2" style={{ gap: '12px', marginTop: '16px' }}>
            <div style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Daily Deficit Rate</span>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--amber)', margin: '4px 0' }}>
                {Number(dailyShortfall).toFixed(3)} <small style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>MMT/day</small>
              </div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                ~{(dailyShortfall * 7.33).toFixed(1)}M barrels/day deficit
              </span>
            </div>

            <div style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>SPR Buffer Duration</span>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--cyan-bright)', margin: '4px 0' }}>
                {daysSprCoverage} <small style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Days Capacity</small>
              </div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                Before emergency drawdown exhaustion
              </span>
            </div>
          </div>

          <div style={{ marginTop: '16px', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: '8px', padding: '10px 14px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            ⚠️ <strong>Downstream Action Required:</strong> At current deficit rates, western coastal refiners (Jamnagar, Vadinar, Mumbai) will hit minimum crude inventory thresholds by Day 12 without emergency swap allocations.
          </div>
        </div>
      </div>
    </section>
  );
}
