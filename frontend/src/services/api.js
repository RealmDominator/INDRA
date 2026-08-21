const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...options, signal: controller.signal, headers: { 'Content-Type': 'application/json', ...(options.headers || {}) } });
    if (!response.ok) throw new Error(`Request failed (${response.status})`);
    return await response.json();
  } finally { clearTimeout(timer); }
}

export const api = {
  get: request,
  risk: (features) => request('/risk', { method: 'POST', body: JSON.stringify({ features }) }),
  scenario: (body) => request('/scenarios', { method: 'POST', body: JSON.stringify(body) }),
  recommendations: (body) => request('/recommendations', { method: 'POST', body: JSON.stringify(body) }),
};
