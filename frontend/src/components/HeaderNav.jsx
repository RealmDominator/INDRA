import { useEffect, useState } from 'react';
import StatusBadge from './StatusBadge';

export default function HeaderNav({ health, loading, onRefresh, activeSection }) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'situation', label: 'Situation' },
    { id: 'intelligence', label: 'Event Intel' },
    { id: 'network', label: 'Supply Network' },
    { id: 'pipeline', label: 'Pipeline' },
    { id: 'simulator', label: 'Simulator' },
    { id: 'procurement', label: 'Procurement' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'health', label: 'Data Health' },
  ];

  const dbStatus = health?.database === 'connected' ? 'CONNECTED' : (loading ? 'LOADING' : 'UNAVAILABLE');
  const isHealthy = health?.database === 'connected';

  return (
    <header className="top-nav">
      <div className="top-nav-inner">
        <div className="brand-group">
          <span className="brand-badge">INDRA</span>
          <div className="brand-title">
            ENERGY DECISION CONSOLE
            <span className="brand-sub">India Disruption Response</span>
          </div>
        </div>

        <nav className="nav-links">
          {navItems.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`nav-link-btn ${activeSection === item.id ? 'active' : ''}`}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="nav-telemetry">
          <div className="telemetry-item">
            <span className={`pulse-dot ${isHealthy ? '' : 'pulse-amber'}`} />
            <span>DB:</span>
            <StatusBadge value={dbStatus} />
          </div>

          <div className="telemetry-item" style={{ borderLeft: '1px solid var(--border-subtle)', paddingLeft: '12px' }}>
            <span>{timeStr || 'LIVE TELEMETRY'}</span>
          </div>

          <button
            className="btn-secondary"
            onClick={onRefresh}
            disabled={loading}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            title="Refresh All System Data"
          >
            {loading ? 'Refreshing…' : '↻ Refresh'}
          </button>
        </div>
      </div>
    </header>
  );
}
