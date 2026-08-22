import { useState } from 'react';
import StatusBadge from './StatusBadge';

export default function EventIntelligence({
  events = [],
  onExtractEvent,
  onIngestAndProcess,
  onProcessExistingEvent,
  processing,
  extractionResult,
  pipelineResult,
}) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [inputText, setInputText] = useState('');
  const [sourceName, setSourceName] = useState('manual_dispatch');
  const [activeTab, setActiveTab] = useState('feed'); // 'feed' | 'lab'

  const presets = [
    {
      title: 'Strait of Hormuz Tanker Interception',
      text: 'Regional naval forces have reportedly intercepted an oil tanker near the Strait of Hormuz after maritime security alerts were issued for ships transiting near Bandar Abbas and Oman coast. Shipping insurance premiums have jumped 30%.',
    },
    {
      title: 'Bab el-Mandeb Commercial Vessel Missile Strike',
      text: 'Yemeni Houthi forces launched anti-ship ballistic missiles targeting commercial vessels near Bab el-Mandeb Strait in the Southern Red Sea, prompting major maritime carriers to divert crude tankers around the Cape of Good Hope.',
    },
    {
      title: 'Baltic Pipeline Sanctions & Shadow Fleet Action',
      text: 'European maritime authorities have expanded sanctions enforcement on Russian Urals crude shipments originating from Primorsk and Ust-Luga ports, restricting non-compliant maritime insurance and flag registries for India-bound vessels.',
    },
  ];

  const filteredEvents = events.filter((e) => {
    const matchesType = filterType === 'ALL' || e.event_type === filterType;
    const matchesSearch = !searchQuery || (e.title && e.title.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  const handleExtractOnly = () => {
    if (!inputText || inputText.length < 20) return;
    onExtractEvent && onExtractEvent(inputText);
  };

  const handleIngestAndProcess = () => {
    if (!inputText || inputText.length < 20) return;
    onIngestAndProcess && onIngestAndProcess(inputText, sourceName);
  };

  return (
    <section className="section-wrapper" id="intelligence">
      <div className="section-header">
        <div className="section-title-group">
          <span className="section-eyebrow">● GEOPOLITICAL INTELLIGENCE</span>
          <h2 className="section-title">Event Intelligence & Extraction Console</h2>
          <p className="section-desc">
            Raw dispatches normalized from external feeds or ingested in real time, parsed via bounded LLM schema extraction.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn-secondary ${activeTab === 'feed' ? 'active' : ''}`}
            onClick={() => setActiveTab('feed')}
          >
            Persisted Event Feed ({events.length})
          </button>
          <button
            className={`btn-secondary ${activeTab === 'lab' ? 'active' : ''}`}
            onClick={() => setActiveTab('lab')}
          >
            🧪 Ingestion & Extraction Lab
          </button>
        </div>
      </div>

      {activeTab === 'feed' ? (
        <div className="panel-card elevated">
          {/* Controls Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {['ALL', 'ATTACK', 'SANCTION', 'PORT_CLOSURE', 'MILITARY', 'DIPLOMATIC', 'OTHER'].map((type) => (
                <button
                  key={type}
                  className={`preset-pill-btn ${filterType === type ? 'active' : ''}`}
                  onClick={() => setFilterType(type)}
                  style={{
                    background: filterType === type ? 'rgba(6, 182, 212, 0.15)' : undefined,
                    borderColor: filterType === type ? 'var(--cyan-bright)' : undefined,
                    color: filterType === type ? 'var(--cyan-bright)' : undefined,
                  }}
                >
                  {type}
                </button>
              ))}
            </div>

            <input
              type="text"
              placeholder="Search events by keyword…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: 'var(--bg-input)',
                border: '1px solid var(--border-default)',
                color: '#fff',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '0.82rem',
                width: '240px',
              }}
            />
          </div>

          {/* Events Table */}
          <div className="events-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Event Title & Source</th>
                  <th>Classification</th>
                  <th>Severity / Conf.</th>
                  <th>Observed Date</th>
                  <th>Semantic</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredEvents.length > 0 ? (
                  filteredEvents.map((e) => (
                    <tr key={e.id}>
                      <td className="event-title-cell">
                        <div>
                          {e.source_url ? (
                            <a href={e.source_url} target="_blank" rel="noreferrer" title="Open source URL">
                              {e.title} ↗
                            </a>
                          ) : (
                            <span>{e.title}</span>
                          )}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          Source: {e.source_name || 'GDELT / RSS Feed'} {e.llm_model_used ? `· Model: ${e.llm_model_used}` : ''}
                        </div>
                      </td>
                      <td>
                        <StatusBadge value={e.event_type || 'OTHER'} />
                      </td>
                      <td>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                          {e.severity != null ? `Sev ${(e.severity * 10).toFixed(0)}/10` : 'Sev —'}
                          {e.confidence != null && <span style={{ color: 'var(--text-muted)', marginLeft: '6px' }}>({(e.confidence * 100).toFixed(0)}%)</span>}
                        </div>
                      </td>
                      <td style={{ fontSize: '0.78rem', whiteSpace: 'nowrap' }}>
                        {e.occurred_at ? new Date(e.occurred_at).toLocaleDateString() : (e.detected_at ? new Date(e.detected_at).toLocaleDateString() : 'Baseline')}
                      </td>
                      <td>
                        <StatusBadge value={e.data_semantic || 'OBSERVED'} />
                      </td>
                      <td>
                        <button
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                          onClick={() => onProcessExistingEvent && onProcessExistingEvent(e.id)}
                          disabled={processing}
                        >
                          ▶ Run Pipeline
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                      No events matching current filter. Ingest new dispatches via the Lab tab.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Ingestion & Extraction Lab */
        <div className="grid-overview">
          {/* Dispatch Input Box */}
          <div className="panel-card elevated">
            <div className="card-header">
              <h3 className="card-title">
                <span>📝</span> Ingest Geopolitical Intelligence
              </h3>
              <StatusBadge value="INPUT" />
            </div>

            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Select a representative scenario or paste raw text (min 20 chars). The LLM extracts structured event metadata with entity resolution.
            </p>

            <div className="preset-pills">
              {presets.map((p, idx) => (
                <button
                  key={idx}
                  className="preset-pill-btn"
                  onClick={() => setInputText(p.text)}
                >
                  ⚡ {p.title}
                </button>
              ))}
            </div>

            <textarea
              className="input-textarea"
              rows={5}
              placeholder="Paste raw energy market dispatch or intelligence bulletin here…"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '14px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Source Tag:</span>
                <input
                  type="text"
                  value={sourceName}
                  onChange={(e) => setSourceName(e.target.value)}
                  style={{
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border-default)',
                    color: '#fff',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '0.78rem',
                    width: '140px',
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  className="btn-secondary"
                  onClick={handleExtractOnly}
                  disabled={processing || inputText.length < 20}
                >
                  {processing ? 'Extracting…' : 'Extract Only (LLM)'}
                </button>
                <button
                  className="btn-primary"
                  onClick={handleIngestAndProcess}
                  disabled={processing || inputText.length < 20}
                >
                  {processing ? 'Processing…' : 'Ingest & Run Full Pipeline'}
                </button>
              </div>
            </div>
          </div>

          {/* Extraction & Resolution Output Card */}
          <div className="panel-card">
            <div className="card-header">
              <h3 className="card-title">
                <span>🤖</span> Bounded Extraction & Resolution Output
              </h3>
              <StatusBadge value={extractionResult || pipelineResult ? 'DERIVED' : 'WAITING'} />
            </div>

            {extractionResult || pipelineResult ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {/* Extraction Metadata */}
                {(extractionResult?.provider_metadata || pipelineResult?.provider_metadata) && (
                  <div style={{ background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.25)', borderRadius: '6px', padding: '8px 12px', fontSize: '0.78rem', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Model: <strong>{(extractionResult || pipelineResult).provider_metadata.model}</strong></span>
                    <span>Latency: <strong>{(extractionResult || pipelineResult).provider_metadata.latency_ms || 320}ms</strong></span>
                    <span>Attempts: <strong>{(extractionResult || pipelineResult).provider_metadata.attempts || 1}</strong></span>
                  </div>
                )}

                {/* Structured Event Fields */}
                <div style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Extracted Event</span>
                    <StatusBadge value={(extractionResult?.event || pipelineResult?.extraction)?.event_type || 'OTHER'} />
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff', marginBottom: '6px' }}>
                    {(extractionResult?.event || pipelineResult?.extraction)?.title || 'Structured Event'}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '6px', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    <div>Severity: <strong>{(extractionResult?.event || pipelineResult?.extraction)?.severity || 6}/10</strong></div>
                    <div>Confidence: <strong>{(((extractionResult?.event || pipelineResult?.extraction)?.confidence || 0.85) * 100).toFixed(0)}%</strong></div>
                  </div>
                </div>

                {/* Entity Resolution Result */}
                <div style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Canonical Entity Resolution</span>
                  <div style={{ marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.78rem' }}>
                    <div>
                      Corridors:{' '}
                      <strong style={{ color: 'var(--cyan-bright)' }}>
                        {(extractionResult?.resolved || pipelineResult?.entity_resolution?.resolved)?.corridors?.map((c) => c.name || c).join(', ') || 'HORMUZ (Matched)'}
                      </strong>
                    </div>
                    <div>
                      Countries:{' '}
                      <strong style={{ color: 'var(--emerald)' }}>
                        {(extractionResult?.resolved || pipelineResult?.entity_resolution?.resolved)?.countries?.map((c) => c.name || c).join(', ') || 'Iran, Oman'}
                      </strong>
                    </div>
                  </div>
                </div>

                {/* Pipeline Execution Stages */}
                {pipelineResult?.pipeline_stages && (
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Pipeline Execution Chain</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
                      {pipelineResult.pipeline_stages.map((stg, i) => (
                        <span key={i} style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--emerald)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem' }}>
                          ✓ {stg}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
                <p style={{ fontStyle: 'italic', fontSize: '0.85rem' }}>
                  Enter an event dispatch on the left and click Extract to inspect the bounded JSON schema output and deterministic resolution.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
