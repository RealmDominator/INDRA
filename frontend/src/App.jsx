import { useCallback, useEffect, useState } from 'react';
import { api } from './services/api';

import HeaderNav from './components/HeaderNav';
import HeroSection from './components/HeroSection';
import CurrentSituation from './components/CurrentSituation';
import EventIntelligence from './components/EventIntelligence';
import SupplyNetwork from './components/SupplyNetwork';
import DecisionPipeline from './components/DecisionPipeline';
import ScenarioSimulator from './components/ScenarioSimulator';
import ProcurementSection from './components/ProcurementSection';
import EvidenceSection from './components/EvidenceSection';
import DataSourceHealth from './components/DataSourceHealth';

const defaultRiskFeatures = {
  event_severity: 0.65,
  event_recency: 0.70,
  chokepoint_exposure: 0.65,
  conflict_sanctions: 0.40,
  historical_rate: 0.30,
  india_dependency: 0.80,
};

export default function App() {
  // Core Data States
  const [health, setHealth] = useState(null);
  const [corridors, setCorridors] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [refineries, setRefineries] = useState([]);
  const [reserves, setReserves] = useState({});
  const [events, setEvents] = useState([]);
  const [ingestionStatus, setIngestionStatus] = useState(null);

  // Engine Calculation States
  const [riskData, setRiskData] = useState(null);
  const [scenarioResult, setScenarioResult] = useState(null);
  const [recommendationData, setRecommendationData] = useState(null);

  // Interactive Ingestion / Lab States
  const [extractionResult, setExtractionResult] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [impactData, setImpactData] = useState(null);
  const [selectedCorridorId, setSelectedCorridorId] = useState(null);

  // Scenario Simulator Inputs
  const [duration, setDuration] = useState(30);
  const [reduction, setReduction] = useState(100);

  // Status & Telemetry
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');

  // 1. Initial Load of Reference & Baseline State
  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [
        healthRes,
        corridorsRiskRes,
        suppliersRes,
        routesRes,
        refineriesRes,
        reservesRes,
        eventsRes,
      ] = await Promise.all([
        api.health().catch(() => ({ database: 'unavailable' })),
        api.corridorRisk().catch(() => ({ items: [] })),
        api.suppliers().catch(() => []),
        api.routes().catch(() => []),
        api.refineries().catch(() => []),
        api.reserves().catch(() => ({ locations: [], total_capacity_mmt: 5.33 })),
        api.events().catch(() => ({ items: [] })),
      ]);

      setHealth(healthRes);
      setCorridors(corridorsRiskRes.items || []);
      setSuppliers(suppliersRes || []);
      setRoutes(routesRes || []);
      setRefineries(refineriesRes || []);
      setReserves(reservesRes || {});
      setEvents(eventsRes.items || []);

      // Calculate initial reference baseline risk & scenario
      const initialRisk = await api.risk(defaultRiskFeatures).catch(() => null);
      const initialScenario = await api.scenario({
        scenario_type: 'HORMUZ_FULL',
        duration_days: 30,
        reduction_pct: 100,
      }).catch(() => null);

      if (initialRisk) setRiskData(initialRisk);
      if (initialScenario) setScenarioResult(initialScenario);

      // Silently fetch ingestion telemetry
      api.ingestionStatus().then(setIngestionStatus).catch(() => {});

      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message || 'Unable to connect to the INDRA backend API.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  // 2. Execute Reference Decision Loop (Event → Risk → Scenario → Procurement)
  const handleRunDemo = async () => {
    setBusy(true);
    setError('');
    try {
      // Step A: Calculate Risk
      const risk = await api.risk(defaultRiskFeatures);
      setRiskData(risk);

      // Step B: Calculate Scenario Disruption Gap
      const scenario = await api.scenario({
        scenario_type: 'HORMUZ_FULL',
        duration_days: duration,
        reduction_pct: reduction,
      });
      setScenarioResult(scenario);

      // Step C: Run Alternative Procurement Optimization
      const candidates = suppliers.slice(0, 5).map((s) => ({
        id: s.id,
        supplier_name: s.name,
        available_volume: Number(s.annual_supply_capacity_mmtpa || 2.0),
        unit_cost: 74.0,
        risk_score: Number(s.current_sanctions_risk || 0.2),
        transit_days: 14,
        compatibility_score: 0.92,
        is_operational: true,
        is_sanctioned: Boolean(s.is_sanctioned),
      }));

      const rec = await api.recommendations({
        target_volume: Math.min(2.0, Math.max(0.5, scenario.supply_gap_mmt ? scenario.supply_gap_mmt / 10 : 1.0)),
        candidates: candidates.length > 0 ? candidates : [
          { id: 1, supplier_name: 'West Africa Sweet', available_volume: 2.0, unit_cost: 74, risk_score: 0.2, transit_days: 14, compatibility_score: 0.94, is_operational: true },
          { id: 2, supplier_name: 'US Gulf Coast WTI', available_volume: 1.5, unit_cost: 76, risk_score: 0.15, transit_days: 24, compatibility_score: 0.91, is_operational: true },
        ],
      });
      setRecommendationData(rec);

      // Step D: Inspect Primary Disrupted Corridor (Hormuz ID: 1)
      if (corridors.length > 0) {
        const hormuz = corridors.find((c) => c.code === 'HORMUZ') || corridors[0];
        if (hormuz) {
          handleInspectCorridor(hormuz.id, hormuz.code);
        }
      }
    } catch (err) {
      setError(err.message || 'Error running the decision loop.');
    } finally {
      setBusy(false);
    }
  };

  // 3. Extract Event via LLM
  const handleExtractEvent = async (text) => {
    setProcessing(true);
    setError('');
    try {
      const res = await api.extractEvent(text);
      setExtractionResult(res);
    } catch (err) {
      setError(err.message || 'LLM extraction failed.');
    } finally {
      setProcessing(false);
    }
  };

  // 4. Ingest and Process Raw Event Text (Full Pipeline)
  const handleIngestAndProcess = async (text, sourceName = 'manual') => {
    setProcessing(true);
    setError('');
    try {
      const res = await api.ingestAndProcess(text, sourceName);
      setPipelineResult(res);

      if (res.risk) setRiskData(res.risk);
      if (res.scenario) setScenarioResult(res.scenario);
      if (res.procurement) setRecommendationData(res.procurement);

      // Refresh events and corridor risk
      const [eventsRes, corridorsRes] = await Promise.all([
        api.events(),
        api.corridorRisk(),
      ]);
      setEvents(eventsRes.items || []);
      setCorridors(corridorsRes.items || []);
    } catch (err) {
      setError(err.message || 'Event ingestion and processing failed.');
    } finally {
      setProcessing(false);
    }
  };

  // 5. Process Existing Persisted Event
  const handleProcessExistingEvent = async (eventId) => {
    setProcessing(true);
    setError('');
    try {
      const res = await api.processEvent(eventId);
      setPipelineResult(res);
      if (res.risk) setRiskData(res.risk);
      if (res.scenario) setScenarioResult(res.scenario);
      if (res.procurement) setRecommendationData(res.procurement);
    } catch (err) {
      setError(err.message || 'Processing event failed.');
    } finally {
      setProcessing(false);
    }
  };

  // 6. Inspect Network Impact for Corridor (NetworkX Graph Traversal)
  const handleInspectCorridor = async (corridorId, corridorCode) => {
    setSelectedCorridorId(corridorId);
    try {
      const impact = await api.corridorImpact(corridorId);
      setImpactData(impact);
    } catch (err) {
      // Graceful fallback if corridor impact endpoint errors
      setImpactData({
        affected_corridors: [{ id: corridorId, code: corridorCode, name: corridorCode }],
        affected_routes: routes.filter((r) => r.corridor_ids && r.corridor_ids.includes(corridorId)),
        affected_refineries: refineries.slice(0, 4),
        data_semantic: 'DERIVED',
      });
    }
  };

  // 7. Run Scenario Simulation
  const handleRunScenario = async (type, days, red) => {
    setBusy(true);
    try {
      const res = await api.scenario({
        scenario_type: type,
        duration_days: days,
        reduction_pct: red,
      });
      setScenarioResult(res);

      // Also update procurement target
      const target = Math.min(2.0, Math.max(0.5, res.supply_gap_mmt ? res.supply_gap_mmt / 10 : 1.0));
      const rec = await api.recommendations({
        target_volume: target,
        candidates: suppliers.slice(0, 5).map((s) => ({
          id: s.id,
          supplier_name: s.name,
          available_volume: Number(s.annual_supply_capacity_mmtpa || 2.0),
          unit_cost: 74.0,
          risk_score: Number(s.current_sanctions_risk || 0.2),
          transit_days: 14,
          compatibility_score: 0.92,
          is_operational: true,
          is_sanctioned: Boolean(s.is_sanctioned),
        })),
      });
      setRecommendationData(rec);
    } catch (err) {
      setError(err.message || 'Scenario calculation failed.');
    } finally {
      setBusy(false);
    }
  };

  // 8. Trigger Ingestion Sweep
  const handleRunIngestion = async () => {
    setIngesting(true);
    try {
      await api.runIngestion();
      const [ingestStatus, eventsRes] = await Promise.all([
        api.ingestionStatus(),
        api.events(),
      ]);
      setIngestionStatus(ingestStatus);
      setEvents(eventsRes.items || []);
    } catch (err) {
      setError(err.message || 'Ingestion sweep failed.');
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Telemetry & Navigation */}
      <HeaderNav
        health={health}
        loading={loading}
        onRefresh={loadDashboard}
      />

      {/* Global Error Banner */}
      {error && (
        <div className="alert" role="alert">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
          <button className="button-secondary" onClick={loadDashboard}>
            Retry Connection
          </button>
        </div>
      )}

      {/* 1. Hero / System Overview */}
      <HeroSection
        health={health}
        corridors={corridors}
        reserves={reserves}
        onRunDemo={handleRunDemo}
        busy={busy}
        lastUpdated={lastUpdated}
      />

      {/* 2. Current Situation Assessment */}
      <CurrentSituation
        riskData={riskData}
        corridors={corridors}
        onInspectCorridor={handleInspectCorridor}
        selectedCorridorId={selectedCorridorId}
        impactData={impactData}
      />

      {/* 3. Event Intelligence & Extraction Lab */}
      <EventIntelligence
        events={events}
        onExtractEvent={handleExtractEvent}
        onIngestAndProcess={handleIngestAndProcess}
        onProcessExistingEvent={handleProcessExistingEvent}
        processing={processing}
        extractionResult={extractionResult}
        pipelineResult={pipelineResult}
      />

      {/* 4. India Supply Network Explorer */}
      <SupplyNetwork
        suppliers={suppliers}
        routes={routes}
        refineries={refineries}
        reserves={reserves}
        corridors={corridors}
      />

      {/* 5. Traceable Decision Pipeline */}
      <DecisionPipeline />

      {/* 6. Scenario Simulator */}
      <ScenarioSimulator
        scenarioResult={scenarioResult}
        onRunScenario={handleRunScenario}
        busy={busy}
        duration={duration}
        setDuration={setDuration}
        reduction={reduction}
        setReduction={setReduction}
        reserves={reserves}
      />

      {/* 7. Strategic Procurement Recommendation */}
      <ProcurementSection
        recommendationData={recommendationData}
        scenarioResult={scenarioResult}
        onRunProcurement={handleRunDemo}
        busy={busy}
      />

      {/* 8. Evidence & Audit-Ready Provenance */}
      <EvidenceSection
        evidenceChain={pipelineResult?.evidence}
        pipelineResult={pipelineResult}
        riskData={riskData}
        scenarioResult={scenarioResult}
        recommendationData={recommendationData}
      />

      {/* 9. Data Source Health & Telemetry */}
      <DataSourceHealth
        ingestionStatus={ingestionStatus}
        onRunIngestion={handleRunIngestion}
        ingesting={ingesting}
      />

      {/* Institutional Footer */}
      <footer style={{ marginTop: '48px', paddingTop: '24px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: 'var(--text-muted)', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <strong>INDRA — India Disruption Response Architecture</strong> · Phase 1 Submission Release
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <span>PostgreSQL Ground Truth</span>
          <span>Deterministic Numerical Engines</span>
          <span>OpenRouter Bounded Extraction</span>
        </div>
      </footer>
    </div>
  );
}
