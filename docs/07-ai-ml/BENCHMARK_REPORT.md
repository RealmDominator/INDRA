# INDRA — Application LLM Benchmark Report (Step 8A)

> **Date:** 22 August 2026
> **Status:** Step 11A activation attempt; provider integrated; live benchmark pending API-key availability
> **Provisional runtime model:** `openai/gpt-4o-mini` via OpenRouter

---

## 1. Evaluation Dataset

| Property | Value |
|---|---|
| File | `data/eval/extraction_benchmark.json` |
| Version | v1.0 |
| Examples | **25** (within 20–50 target) |
| License | Evaluation use only |
| Content | Synthetic paraphrases of publicly known geopolitical/energy event patterns |

Each example includes:
- `input_text` — simulated news snippet
- `expected.event_type`, `severity`, `country_names`, `corridor_names`, `route_names`, `confidence`, `disruption_description`

All six `EventType` values and all six Phase-1 corridors (HORMUZ, RED_SEA, SUEZ, MALACCA, RUSSIA, CAPE) are represented.

---

## 2. Candidate Pool (Limited Set)

Benchmarked candidates (OpenRouter model IDs):

| Candidate | Role in evaluation |
|---|---|
| `openai/gpt-4o-mini` | Primary candidate — structured JSON, low cost, fast |
| `google/gemini-2.0-flash-001` | OpenRouter free/low-cost candidate |
| `anthropic/claude-3.5-haiku` | Quality/reference candidate |

Not benchmarked (development-agent models only): GPT-5.6 Terra/Luna, Kimi K2.6, GLM 5.2, MiniMax M3, Nemotron 3 Super — these are coding/reasoning agents, not runtime extraction candidates.

---

## 3. Evaluation Methodology

Script: `scripts/benchmark/run_llm_benchmark.py`

### Per-example metrics

| Metric | Description |
|---|---|
| Schema validity | Output validates as `StructuredEvent` |
| Event type accuracy | Exact match to expected `event_type` |
| Severity accuracy | Within ±2 of expected severity |
| Country Jaccard | Overlap of expected vs extracted country names |
| Corridor Jaccard | Overlap of expected vs extracted corridor names |
| Hallucination rate | Integer database IDs in name fields (must be 0%) |
| Latency | Milliseconds per extraction call |
| Failure rate | HTTP/JSON/validation errors |

### Composite score weights

```
composite = 0.30 × schema_valid
          + 0.25 × accuracy (0.4×event_type + 0.3×country_jaccard + 0.3×corridor_jaccard)
          + 0.15 × latency_score (1 − avg_ms/5000)
          + 0.15 × (1 − error_rate)
          + 0.15 × cost_score (all candidates ~free at demo volume)
```

### Reproducibility

```powershell
# Live benchmark (requires OpenRouter API key)
$env:OPENROUTER_API_KEY = "sk-or-..."
python scripts/benchmark/run_llm_benchmark.py

# Offline harness validation (no API key; validates scoring pipeline only)
python scripts/benchmark/run_llm_benchmark.py --offline
```

**Live benchmark status (22 Aug 2026):** Not executed because
`OPENROUTER_API_KEY` was unavailable/empty. The repository therefore does not
claim a benchmark winner: the current runtime model is provisional, while the
offline harness and provider/integration tests are verified. Re-run the live
benchmark after setting a valid key.

---

## 4. Provisional Runtime Model — `openai/gpt-4o-mini`

### Weighted criteria (explicit, not quality-only)

| Criterion | Weight | GPT-4o-mini assessment |
|---|---|---|
| Structured output reliability | 30% | Native JSON mode (`response_format: json_object`); highest expected schema validity |
| Extraction field accuracy | 25% | Strong on entity/country/corridor extraction in comparable benchmarks |
| Latency | 15% | Sub-second to ~1.5s typical; suitable for demo workflow |
| Cost / accessibility | 15% | ~$0.0002/extraction; accessible via OpenRouter single API key |
| Failure / retry rate | 15% | High availability; retries handle transient JSON errors |

> **Important:** This is a provisional runtime choice only. The live benchmark has not run because `OPENROUTER_API_KEY=<required locally>` was unavailable/empty, so this model is not yet the empirically proven benchmark winner.

### Why not others?

| Model | Reason not selected |
|---|---|
| Claude 3.5 Haiku | Strong quality; viable fallback; slightly higher cost/latency for equivalent structured tasks |
| Gemini 2.0 Flash | Good free-tier option; slightly less consistent JSON formatting in testing literature |
| GPT-4o / frontier models | Overkill for structured extraction; 10×+ cost with marginal extraction gain |
| Nemotron / Kimi / GLM / MiniMax | Development-agent models; not evaluated as runtime extraction candidates |

### Implementation simplicity

- Single OpenRouter HTTP endpoint
- OpenAI-compatible JSON response format
- No vendor-specific SDK required (`httpx` only)
- Model swappable via `LLM_MODEL` environment variable

---

## 5. Provider Integration Summary

| Component | Location |
|---|---|
| Protocol + contracts | `backend/app/intelligence.py` |
| OpenRouter provider | `backend/app/providers/openrouter.py` |
| Provider factory | `backend/app/providers/factory.py` |
| Extraction endpoint | `POST /events/extract` |
| Configuration | `LLM_PROVIDER`, `LLM_MODEL`, `OPENROUTER_API_KEY`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES` |

### Pipeline (unchanged architecture)

```
Article text
  → LLM extraction (names/codes only)
  → StructuredEvent validation
  → entity resolution (exact alias + RapidFuzz)
  → internal IDs
  → evidence chain
```

The LLM does **not** calculate risk, scenarios, procurement, prices, or database IDs.

---

## 6. Test Verification (Step 8A)

| Suite | Result |
|---|---|
| `backend/tests/test_provider.py` | 18 passed (mocked; no external LLM) |
| `backend/tests/test_intelligence.py` | 3 passed (deterministic engines) |
| `backend/tests/test_domain.py` | 3 passed |
| **Total** | **24 passed** |

Provider tests cover: successful extraction, malformed JSON, API errors, retries, timeout, missing fields, database-ID rejection, unconfigured fallback, `/events/extract` 503/422/200 paths, entity-resolution compatibility.

---

## 7. Limitations

1. Live benchmark scores require a configured `OPENROUTER_API_KEY`
2. Explanation generation (second LLM call) is not implemented — extraction only
3. No streaming; request/response JSON only
4. Entity resolution depends on seed data + fuzzy matching; empty `entity_aliases` table limits exact-alias hits
5. Application LLM selection is for **extraction**; development-agent models remain separate

---

## 8. Runtime Configuration

```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4o-mini
OPENROUTER_API_KEY=<required locally>
LLM_TIMEOUT_SECONDS=15
LLM_MAX_RETRIES=2
```

See [AI_MODEL_STRATEGY.md](AI_MODEL_STRATEGY.md) and [AI_PIPELINE.md](AI_PIPELINE.md) for full pipeline documentation.
