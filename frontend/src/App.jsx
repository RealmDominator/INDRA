import { useEffect, useState } from 'react';
import { api } from './services/api';
import Panel from './components/Panel';
import StatusBadge from './components/StatusBadge';

const features = { event_severity: .6, event_recency: .7, chokepoint_exposure: .65, conflict_sanctions: .4, historical_rate: .3, india_dependency: .8 };
const candidates = [{ id: 1, available_volume: 2, unit_cost: 70, risk_score: .2, transit_days: 12, compatibility_score: .9, is_operational: true }];

export default function App() {
  const [data, setData] = useState({}); const [error, setError] = useState(''); const [busy, setBusy] = useState(false); const [scenario, setScenario] = useState(null); const [recommendation, setRecommendation] = useState(null);
  useEffect(() => { Promise.all([api.get('/health'), api.get('/corridors/risk'), api.get('/events'), api.get('/reserves'), api.get('/suppliers'), api.get('/routes'), api.get('/refineries')]).then(([health, corridors, events, reserves, suppliers, routes, refineries]) => setData({ health, corridors, events, reserves, suppliers, routes, refineries })).catch(e => setError(e.message)); }, []);
  const runFlow = async () => { setBusy(true); setError(''); try { const risk = await api.risk(features); const nextScenario = await api.scenario({ scenario_type: 'HORMUZ_FULL', duration_days: 30, reduction_pct: 100 }); const nextRecommendation = await api.recommendations({ target_volume: 1, candidates }); setData(d => ({ ...d, risk })); setScenario(nextScenario); setRecommendation(nextRecommendation); } catch (e) { setError(e.message); } finally { setBusy(false); } };
  const corridors = data.corridors?.items || []; const reserves = data.reserves?.items || data.reserves?.reserves || [];
  return <main className="app-shell"><header><div><p className="eyebrow">INDRA / DECISION SUPPORT</p><h1>India disruption response console</h1><p className="muted">Event → risk → scenario → procurement → evidence</p></div><StatusBadge value={data.health?.database || 'LOADING'} /></header>
    {error && <div className="alert">{error} <button onClick={() => window.location.reload()}>Retry</button></div>}
    <div className="toolbar"><button onClick={runFlow} disabled={busy}>{busy ? 'Running deterministic flow…' : 'Run demo flow'}</button><span className="muted">Backend-derived values only · no frontend recalculation</span></div>
    <div className="grid"><Panel title="Overall supply-chain risk"><div className="score">{data.risk ? data.risk.display_score.toFixed(1) : '—'}<small>/100</small></div><StatusBadge value={data.risk?.risk_level || 'UNAVAILABLE'} /><p className="muted">{data.risk?.data_semantic || 'Awaiting risk calculation'}</p></Panel>
      <Panel title="Corridor risk">{corridors.length ? corridors.map(c => <div className="row" key={c.id}><span>{c.name}</span><strong>{Number(c.display_score).toFixed(1)}</strong><StatusBadge value={c.risk_level} /></div>) : <p className="empty">No corridor risk available.</p>}</Panel>
      <Panel title="Recent events">{data.events?.items?.length ? data.events.items.map(e => <div className="row" key={e.id}><span>{e.title}</span><StatusBadge value={e.data_semantic} /></div>) : <p className="empty">No persisted events. Event ingestion is planned.</p>}</Panel>
      <Panel title="Strategic reserves">{reserves.length ? reserves.map(r => <div className="row" key={r.id}><span>{r.location || r.name}</span><strong>{r.current_level_mmt ?? '—'} MMT</strong></div>) : <p className="empty">Reserve levels unavailable / not seeded.</p>}</Panel></div>
    <div className="grid wide"><Panel title="India supply network"><div className="network"><span>Suppliers ({data.suppliers?.length || 0})</span><i>→</i><span>Routes ({data.routes?.length || 0})</span><i>→</i><span>Ports</span><i>→</i><span>Refineries ({data.refineries?.length || 0})</span></div><p className="muted">Network view uses reference data; corridor interpretation remains backend-owned.</p></Panel>
      <Panel title="Scenario simulator">{scenario ? <><div className="metric"><span>Supply gap</span><strong>{scenario.supply_gap_mmt.toFixed(3)} MMT</strong></div><StatusBadge value={scenario.data_semantic} /></> : <p className="empty">Run the demo flow to simulate a 30-day Hormuz disruption.</p>}</Panel>
      <Panel title="Procurement recommendation">{recommendation ? <><div className="metric"><span>Feasible</span><strong>{recommendation.feasible ? 'YES' : 'NO'}</strong></div><div className="metric"><span>Unmet volume</span><strong>{recommendation.unmet_volume}</strong></div><StatusBadge value="DERIVED" /></> : <p className="empty">No recommendation generated.</p>}</Panel>
      <Panel title="Evidence drawer"><div className="evidence">Source <b>→</b> extraction <b>→</b> entity resolution <b>→</b> risk <b>→</b> scenario <b>→</b> optimization</div><p className="muted">Each computed result is marked DERIVED; unavailable observations remain visibly unavailable.</p></Panel></div>
  </main>;
}
