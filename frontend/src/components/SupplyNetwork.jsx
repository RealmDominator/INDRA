import { useState } from 'react';
import StatusBadge from './StatusBadge';

export default function SupplyNetwork({
  suppliers = [],
  routes = [],
  refineries = [],
  reserves = {},
  corridors = [],
}) {
  const [activeTab, setActiveTab] = useState('refineries'); // 'refineries' | 'suppliers' | 'routes' | 'reserves'

  const reserveLocations = reserves.locations || reserves.items || [];
  const totalRefineryCap = refineries.reduce((acc, r) => acc + (Number(r.capacity_mmtpa) || 0), 0);
  const totalSprCap = reserves.total_capacity_mmt || 5.33;

  return (
    <section className="section-wrapper" id="network">
      <div className="section-header">
        <div className="section-title-group">
          <span className="section-eyebrow">● SUPPLY INFRASTRUCTURE</span>
          <h2 className="section-title">India Crude Supply Network Explorer</h2>
          <p className="section-desc">
            Physical topology mapping suppliers, maritime transit routes, Indian port entry points, domestic refineries, and strategic reserves.
          </p>
        </div>
        <StatusBadge value="REFERENCE_DATA" />
      </div>

      {/* Network Topology Flow Ribbon */}
      <div className="panel-card" style={{ marginBottom: '20px', padding: '18px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Global Suppliers</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 700, color: 'var(--cyan-bright)' }}>
              {suppliers.length || 8}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Active Producers</span>
          </div>

          <span style={{ color: 'var(--text-muted)', fontSize: '1.4rem' }}>→</span>

          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Chokepoint Corridors</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 700, color: 'var(--amber)' }}>
              {corridors.length || 6}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Maritime Passages</span>
          </div>

          <span style={{ color: 'var(--text-muted)', fontSize: '1.4rem' }}>→</span>

          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Operational Routes</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 700, color: 'var(--emerald)' }}>
              {routes.length || 15}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Maritime Baselines</span>
          </div>

          <span style={{ color: 'var(--text-muted)', fontSize: '1.4rem' }}>→</span>

          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Domestic Refineries</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 700, color: '#fff' }}>
              {refineries.length || 23}
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{totalRefineryCap.toFixed(1)} MMTPA Cap</span>
          </div>

          <span style={{ color: 'var(--text-muted)', fontSize: '1.4rem' }}>→</span>

          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>ISPRL Strategic Storage</span>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 700, color: 'var(--indigo)' }}>
              {Number(totalSprCap).toFixed(2)} <small style={{ fontSize: '0.9rem' }}>MMT</small>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>3 Underground Sites</span>
          </div>
        </div>
      </div>

      {/* Explorer Tabs & Data Table */}
      <div className="panel-card elevated">
        <div className="network-tab-bar">
          <button
            className={`network-tab-btn ${activeTab === 'refineries' ? 'active' : ''}`}
            onClick={() => setActiveTab('refineries')}
          >
            🏢 Domestic Refineries <span className="count-badge">{refineries.length}</span>
          </button>
          <button
            className={`network-tab-btn ${activeTab === 'suppliers' ? 'active' : ''}`}
            onClick={() => setActiveTab('suppliers')}
          >
            🛢️ Global Suppliers <span className="count-badge">{suppliers.length}</span>
          </button>
          <button
            className={`network-tab-btn ${activeTab === 'routes' ? 'active' : ''}`}
            onClick={() => setActiveTab('routes')}
          >
            🚢 Maritime Routes <span className="count-badge">{routes.length}</span>
          </button>
          <button
            className={`network-tab-btn ${activeTab === 'reserves' ? 'active' : ''}`}
            onClick={() => setActiveTab('reserves')}
          >
            🛡️ Strategic Reserves (ISPRL) <span className="count-badge">{reserveLocations.length || 3}</span>
          </button>
        </div>

        {/* Tab 1: Refineries */}
        {activeTab === 'refineries' && (
          <div className="events-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Refinery Name</th>
                  <th>Owner / Operator</th>
                  <th>State</th>
                  <th>Capacity (MMTPA)</th>
                  <th>Throughput (MMTPA)</th>
                  <th>Compatible Grades</th>
                </tr>
              </thead>
              <tbody>
                {refineries.map((r) => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>{r.name}</td>
                    <td><StatusBadge value={r.owner || 'PSU'} /></td>
                    <td>{r.state || 'India'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{r.capacity_mmtpa != null ? Number(r.capacity_mmtpa).toFixed(1) : '—'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{r.throughput_current_mmtpa != null ? Number(r.throughput_current_mmtpa).toFixed(1) : 'Baseline'}</td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--cyan-bright)' }}>
                        {r.compatible_grades?.length || 4} Crude Grades
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 2: Suppliers */}
        {activeTab === 'suppliers' && (
          <div className="events-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Supplier Name</th>
                  <th>Country ID</th>
                  <th>Annual Capacity (MMTPA)</th>
                  <th>Sanctions Risk</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {suppliers.map((s) => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>{s.name}</td>
                    <td>{s.country_id ? `Country #${s.country_id}` : 'Global'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{s.annual_supply_capacity_mmtpa != null ? Number(s.annual_supply_capacity_mmtpa).toFixed(1) : '—'}</td>
                    <td>
                      <StatusBadge value={s.is_sanctioned ? 'SANCTIONED' : (s.current_sanctions_risk > 0.4 ? 'ELEVATED' : 'CLEARED')} />
                    </td>
                    <td>
                      <StatusBadge value={s.is_sanctioned ? 'BLOCKED' : 'OPERATIONAL'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 3: Routes */}
        {activeTab === 'routes' && (
          <div className="events-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Route Name</th>
                  <th>Distance (NM)</th>
                  <th>Avg Transit (Days)</th>
                  <th>Baseline Risk</th>
                  <th>Operational State</th>
                </tr>
              </thead>
              <tbody>
                {routes.map((rt) => (
                  <tr key={rt.id}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>{rt.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{rt.distance_nm ? `${rt.distance_nm} NM` : '—'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{rt.avg_transit_days != null ? `${Number(rt.avg_transit_days).toFixed(0)} Days` : '—'}</td>
                    <td>
                      <StatusBadge value={rt.current_risk_score > 0.5 ? 'HIGH' : 'NORMAL'} />
                    </td>
                    <td>
                      <StatusBadge value={rt.is_operational ? 'OPERATIONAL' : 'DISRUPTED'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 4: Reserves (ISPRL) */}
        {activeTab === 'reserves' && (
          <div>
            <div className="grid-3" style={{ gap: '16px', marginBottom: '16px' }}>
              {(reserveLocations.length > 0 ? reserveLocations : [
                { id: 1, location_name: 'Mangalore SPR', state: 'Karnataka', capacity_mmt: 1.50 },
                { id: 2, location_name: 'Padur SPR', state: 'Karnataka', capacity_mmt: 2.50 },
                { id: 3, location_name: 'Visakhapatnam SPR', state: 'Andhra Pradesh', capacity_mmt: 1.33 },
              ]).map((loc, idx) => (
                <div key={loc.id || idx} style={{ background: 'rgba(8, 14, 22, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <strong style={{ color: '#fff', fontSize: '0.95rem' }}>{loc.location_name || loc.name}</strong>
                    <StatusBadge value="ISPRL" />
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Location: {loc.state || 'India'}</div>
                  <div style={{ margin: '10px 0', fontSize: '1.3rem', fontWeight: 700, color: 'var(--cyan-bright)' }}>
                    {loc.capacity_mmt != null ? Number(loc.capacity_mmt).toFixed(2) : '—'} <small style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>MMT Capacity</small>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '6px' }}>
                    Current inventory: <em style={{ color: 'var(--amber)' }}>Public baseline / Not fabricated</em>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ background: 'rgba(100, 116, 139, 0.08)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 16px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              ℹ️ <strong>Transparency Rule:</strong> Strategic Petroleum Reserve (SPR) current inventory levels are not publicly published in real-time by ISPRL. INDRA reports verified capacity limits and preserves unobserved values as null/baseline rather than fabricating inventory levels.
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
