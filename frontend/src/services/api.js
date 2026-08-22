const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutMs = options.timeout || 15000;
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(`Request to ${path} timed out after ${timeoutMs / 1000}s`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  get: (path, options) => request(path, { method: 'GET', ...options }),
  post: (path, body, options) => request(path, { method: 'POST', body: JSON.stringify(body), ...options }),
  
  // Health & Reference
  health: () => request('/health'),
  countries: () => request('/countries'),
  corridors: () => request('/corridors'),
  crudeGrades: () => request('/crude-grades'),
  suppliers: () => request('/suppliers'),
  routes: (corridor) => request(corridor ? `/routes?corridor=${encodeURIComponent(corridor)}` : '/routes'),
  refineries: () => request('/refineries'),
  reserves: () => request('/reserves'),
  
  // Events & Intelligence
  events: (limit = 50) => request(`/events?limit=${limit}`),
  extractEvent: (text) => request('/events/extract', { method: 'POST', body: JSON.stringify({ text }) }),
  ingestAndProcess: (text, source_name = 'manual') => request('/events/ingest-and-process', { method: 'POST', body: JSON.stringify({ text, source_name }) }),
  processEvent: (event_id) => request('/events/process', { method: 'POST', body: JSON.stringify({ event_id }) }),
  
  // Risk & Network
  risk: (features, weights) => request('/risk', { method: 'POST', body: JSON.stringify({ features, weights }) }),
  corridorRisk: () => request('/corridors/risk'),
  corridorRiskLive: () => request('/corridors/risk/live'),
  corridorImpact: (corridorId) => request(`/corridors/${corridorId}/impact`),
  
  // Engines
  scenario: (body) => request('/scenarios', { method: 'POST', body: JSON.stringify(body) }),
  recommendations: (body) => request('/recommendations', { method: 'POST', body: JSON.stringify(body) }),
  
  // Ingestion
  ingestionStatus: () => request('/ingestion/status'),
  runIngestion: () => request('/ingestion/run', { method: 'POST' }),
};
