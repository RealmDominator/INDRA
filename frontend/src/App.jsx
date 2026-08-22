import { useCallback, useEffect, useState } from 'react';
import { api } from './services/api';
import Panel from './components/Panel';
import StatusBadge from './components/StatusBadge';

const riskFeatures = { event_severity: .6, event_recency: .7, chokepoint_exposure: .65, conflict_sanctions: .4, historical_rate: .3, india_dependency: .8 };
const candidates = [{ id: 1, available_volume: 2, unit_cost: 70, risk_score: .2, transit_days: 12, compatibility_score: .9, is_operational: true }];

export default function App() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [scenario, setScenario] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [duration, setDuration] = useState(30);
  const [reduction, setReduction] = useState(100);
  const [ingestion, setIngestion] = useState(null);
  const [eventText, setEventText] = useState('');
  const [pipelineResult, setPipelineResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const [health, corridors, events, reserves, suppliers, routes, refineries] = await Promise.all([
        api.get('/health'), api.get('/corridors/risk'), api.get('/events'),
        api.get('/reserves'), api.get('/suppliers'), api.get('/routes'), api.get('/refineries'),
      ]);
      setData({ health, corridors, events, reserves, suppliers, routes, refineries });
      // Load ingestion status silently
      api.ingestionStatus().then(setIngestion).catch(() => {});
    } catch (e) {
      setError(e.message || 'Unable to load the INDRA API.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  const runFlow = async () => {
    setBusy(true); setError('');
    try {
      const risk = await api.risk(riskFeatures);
      const result = await api.scenario({ scenario_type: 'HORMUZ_FULL', duration_days: duration, reduction_pct: reduction });
      const rec = await api.recommendations({ target_volume: 1, candidates });
      setData((current) => ({ ...current, risk }));
      setScenario(result); setRecommendation(rec);
    } catch (e) { setError(e.message || 'The demo flow could not be completed.'); }
    finally { setBusy(false); }
  };

  const submitEvent = async () => {
    if (!eventText || eventText.length < 20) return;
    setSubmitting(true); setError(''); setPipelineResult(null);
    try {
      const result = await api.ingestAndProcess(eventText);
      setPipelineResult(result);
      setScenario(result.scenario || null);
      setRecommendation(result.procurement || null);
      // Refresh events and corridor risk after processing
      const [events, corridors] = await Promise.all([api.get('/events'), api.get('/corridors/risk')]);
      setData((current) => ({ ...current, events, corridors }));
      setEventText('');
    } catch (e) { setError(e.message || 'Event processing failed.'); }
    finally { setSubmitting(false); }
  };

  const corridors = data.corridors?.items || [];
  const reserves = data.reserves?.locations || data.reserves?.items || [];
  const count = (value) => Array.isArray(value) ? value.length : '—';
  const sources = ingestion?.sources || [];

  return <main className="app-shell">
    <header className="topbar">
      <div>
        <p className="eyebrow">INDRA / INDIA ENERGY DISRUPTION MONITOR</p>
        <h1>From disruption signal to procurement action.</h1>
        <p className="lede">A traceable decision console for crude supply-chain resilience.</p>
      </div>
      <div className="connection">
        <span className="muted">API STATUS</span>
        <StatusBadge value={loading ? 'LOADING' : data.health?.database || 'UNAVAILABLE'} />
      </div>
    </header>

    {error && <div className="alert" role="alert"><span>{error}</span><button className="button-secondary" onClick={loadDashboard}>Retry connection</button></div>}

    <div className="toolbar">
      <button onClick={runFlow} disabled={busy || loading}>{busy ? 'Calculating…' : 'Run demo scenario'}</button>
      <button className="button-secondary" onClick={loadDashboard} disabled={loading}>↻ Refresh</button>
      <span className="muted">Backend-derived calculations · deterministic Phase 1 engine</span>
    </div>

    {/* Event Submission */}
    <div className="grid overview-grid">
      <Panel title="Submit event" eyebrow="PIPELINE INPUT">
        <textarea
          className="event-input"
          rows={3}
          placeholder="Paste a news article or event description (min 20 characters)…"
          value={eventText}
          onChange={(e) => setEventText(e.target.value)}
        />
        <button onClick={submitEvent} disabled={submitting || eventText.length < 20}>
          {submitting ? 'Processing…' : 'Ingest & Process'}
        </button>
        {pipelineResult && <div className="pipeline-result">
          <div className="metric"><span>Pipeline stages</span><strong>{pipelineResult.pipeline_stages?.join(' → ') || '—'}</strong></div>
          {pipelineResult.risk && <div className="metric"><span>Risk score</span><strong>{pipelineResult.risk.display_score?.toFixed(1)}/100 ({pipelineResult.risk.risk_level})</strong></div>}
          {pipelineResult.scenario && <div className="metric"><span>Supply gap</span><strong>{pipelineResult.scenario.supply_gap_mmt?.toFixed(3)} MMT</strong></div>}
          {pipelineResult.procurement && <div className="metric"><span>Procurement</span><strong>{pipelineResult.procurement.feasible ? 'FEASIBLE' : 'UNMET GAP'}</strong></div>}
          {pipelineResult.network_impact && <div className="metric"><span>Affected refineries</span><strong>{pipelineResult.network_impact.affected_refineries?.length || 0}</strong></div>}
          {pipelineResult.evidence?.length > 0 && <div className="metric"><span>Evidence stages</span><strong>{pipelineResult.evidence.map((item) => item.stage).join(' → ')}</strong></div>}
          {pipelineResult.provider_metadata && <div className="metric"><span>LLM model</span><strong>{pipelineResult.provider_metadata.model}</strong></div>}
          {pipelineResult.errors?.length > 0 && <div className="metric"><span>Warnings</span><strong className="warn">{pipelineResult.errors.join('; ')}</strong></div>}
          <StatusBadge value="DERIVED" />
        </div>}
      </Panel>

      <Panel title="Overall risk" eyebrow="DERIVED">
        <div className="score">{data.risk ? data.risk.display_score.toFixed(1) : '—'}<small>/100</small></div>
        <StatusBadge value={data.risk?.risk_level || (loading ? 'LOADING' : 'UNAVAILABLE')} />
        <p className="muted">{data.risk?.data_semantic || 'Run the demo scenario to calculate risk.'}</p>
      </Panel>

      <Panel title="Corridor risk" eyebrow="OBSERVED">
        <div className="corridor-list">{loading ? <Skeleton /> : corridors.length ? corridors.map((c) =>
          <div className="corridor-row" key={c.id}>
            <div className="corridor-name"><span>{c.name}</span><StatusBadge value={c.risk_level} /></div>
            <div className="bar-track"><span style={{ width: `${Math.min(100, c.display_score)}%` }} /></div>
            <strong>{Number(c.display_score).toFixed(1)}</strong>
          </div>) : <Empty text="No corridor risk is available." />}
        </div>
      </Panel>

      <Panel title="Recent events" eyebrow="OBSERVED">
        {loading ? <Skeleton /> : data.events?.items?.length ? data.events.items.slice(0, 8).map((e) =>
          <div className="row" key={e.id}>
            <div>
              <span>{e.title?.slice(0, 80)}</span>
              {e.severity && <small className="muted"> · sev {(e.severity * 10).toFixed(0)}</small>}
            </div>
            <StatusBadge value={e.data_semantic} />
          </div>) : <Empty text="No persisted events in this window." />}
      </Panel>
    </div>

    <div className="grid wide-grid">
      {/* Ingestion Status */}
      <Panel title="Data source status" eyebrow="INGESTION">
        {sources.length ? <div className="source-list">{sources.map((s) =>
          <div className="row" key={s.name}>
            <span>{s.name}</span>
            <StatusBadge value={s.freshness || s.status || 'UNKNOWN'} />
            {s.last_error && <small className="warn" title={s.last_error}>⚠</small>}
          </div>)}
        </div> : <Empty text="Ingestion status unavailable." />}
      </Panel>

      <Panel title="Strategic reserves" eyebrow="OBSERVED">
        {loading ? <Skeleton /> : reserves.length ? reserves.map((r) =>
          <div className="row" key={r.id}><span>{r.location_name || r.location || r.name}</span><strong>{r.current_level_mmt ?? '—'} MMT</strong></div>
        ) : <Empty text="Current reserve levels unavailable." />}
      </Panel>

      <Panel title="India supply network" eyebrow="REFERENCE DATA">
        <div className="network">
          <Node label="Suppliers" value={count(data.suppliers)} />
          <i>→</i><Node label="Routes" value={count(data.routes)} />
          <i>→</i><Node label="Ports" value="—" />
          <i>→</i><Node label="Refineries" value={count(data.refineries)} />
        </div>
        <p className="muted">Reference topology only. No live tanker positions are shown.</p>
      </Panel>

      <Panel title="Scenario simulator" eyebrow="SIMULATED">
        <div className="controls">
          <label>Horizon <output>{duration} days</output><input type="range" min="0" max="90" step="5" value={duration} onChange={(e) => setDuration(Number(e.target.value))} /></label>
          <label>Disruption <output>{reduction}%</output><input type="range" min="0" max="100" step="10" value={reduction} onChange={(e) => setReduction(Number(e.target.value))} /></label>
        </div>
        {scenario ? <div className="result-card"><div><span className="muted">Modeled supply gap</span><strong>{scenario.supply_gap_mmt.toFixed(3)} MMT</strong></div><StatusBadge value={scenario.data_semantic} /></div> : <Empty text="Choose assumptions, then run the demo scenario." />}
      </Panel>

      <Panel title="Procurement recommendation" eyebrow="DERIVED">
        {recommendation ? <>
          <div className="metric"><span>Feasible target</span><strong>{recommendation.feasible ? 'YES' : 'NO'}</strong></div>
          <div className="metric"><span>Unmet volume</span><strong>{recommendation.unmet_volume} MMT</strong></div>
          <StatusBadge value="DERIVED" />
        </> : <Empty text="Recommendations appear after scenario execution." />}
      </Panel>

      <Panel title="Evidence trail" eyebrow="PROVENANCE">
        <div className="evidence">{['Source', 'Extraction', 'Entity resolution', 'Risk', 'Scenario', 'Optimization'].map((step, i) =>
          <span key={step}><b>{i + 1}</b>{step}{i < 5 && <em>→</em>}</span>)}
        </div>
        <p className="muted">Observed inputs stay distinct from derived and simulated outputs.</p>
      </Panel>
    </div>
  </main>;
}

function Empty({ text }) { return <p className="empty">{text}</p>; }
function Skeleton() { return <div aria-label="Loading"><span className="skeleton-line" /><span className="skeleton-line short" /><span className="skeleton-line" /></div>; }
function Node({ label, value }) { return <div className="node"><strong>{value}</strong><span>{label}</span></div>; }
