const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...options, signal: controller.signal, headers: { 'Content-Type': 'application/json', ...(options.headers || {}) } });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${response.status})`);
    }
    return await response.json();
  } finally { clearTimeout(timer); }
}

export const api = {
  get: request,
  risk: (features) => request('/risk', { method: 'POST', body: JSON.stringify({ features }) }),
  scenario: (body) => request('/scenarios', { method: 'POST', body: JSON.stringify(body) }),
  recommendations: (body) => request('/recommendations', { method: 'POST', body: JSON.stringify(body) }),
  // Step 8C — pipeline endpoints
  extractEvent: (text) => request('/events/extract', { method: 'POST', body: JSON.stringify({ text }) }),
  ingestAndProcess: (text, source_name = 'manual') => request('/events/ingest-and-process', { method: 'POST', body: JSON.stringify({ text, source_name }) }),
  processEvent: (event_id) => request('/events/process', { method: 'POST', body: JSON.stringify({ event_id }) }),
  ingestionStatus: () => request('/ingestion/status'),
  runIngestion: () => request('/ingestion/run', { method: 'POST' }),
  corridorImpact: (corridorId) => request(`/corridors/${corridorId}/impact`),
  corridorRiskLive: () => request('/corridors/risk/live'),
};
