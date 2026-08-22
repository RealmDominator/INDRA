# INDRA — AI Model Strategy

> This document describes how INDRA manages AI models for two distinct purposes:
> 1. **Development-agent models** — AI models used by the development team/agents to build and maintain the project
> 2. **Application LLM** — The AI model embedded within INDRA itself for event extraction and explanation
>
> **Revision:** Step 8A complete. Provisional runtime model: `openai/gpt-4o-mini` via OpenRouter. Live benchmark pending API-key availability.

---

## Principle: Development Agents ≠ Application Model

The model used by a coding agent to write INDRA's code is a completely separate decision from the model INDRA calls at runtime to extract events from news articles.

- **Development agents** are chosen for coding quality, reasoning, context handling, and speed
- **Application LLM** is chosen for structured-output reliability, extraction accuracy, latency, cost, and failure rate on INDRA-specific tasks

Do not conflate these. Do not assume the best coding model is the best extraction model.

---

## Development-Agent Model Roles

The following models are available for development tasks. These are **task role assignments, NOT a universal model ranking.**

| Model | Recommended Role | Strengths |
|---|---|---|
| **GPT-5.6 Terra** | Architecture review, complex reasoning, system design, code review | Deep reasoning, nuanced analysis |
| **GPT-5.6 Luna** | Fast implementation, debugging, iterative code changes | Speed, good code generation |
| **Kimi K2.6** | Large-context repository analysis, documentation review, codebase comprehension | Very large context window |
| **GLM 5.2** | Rapid implementation, UI/frontend coding, quick prototyping | Fast coding, good at UI patterns |
| **MiniMax M3** | Agentic coding workflows, multi-step task execution | Agentic workflow strength |
| **Nemotron 3 Super** | Open/free frontier reasoning candidate, agentic reasoning | Open model, strong reasoning |
| **Nemotron 3 Nano / Lightning** | Possible high-volume application inference candidates | Low latency, low cost |
| **GitHub Copilot** | Inline coding, autocomplete, boilerplate generation | IDE integration, speed |

### Usage Guidelines

- Use the model best suited for the **specific task**, not a default model for everything
- For architecture decisions and complex refactoring: prefer Terra-class reasoning models
- For rapid implementation and debugging: prefer Luna/GLM-class speed models
- For reviewing large codebases or documentation: prefer Kimi-class large-context models
- For agentic multi-step workflows: prefer MiniMax/Nemotron Super-class models

### Adding New Development Models

New models may only be added to this list after explicit evaluation demonstrating they are suitable for the assigned role. Do not adopt models based on benchmarks alone — test on INDRA-relevant tasks.

---

## Application LLM Strategy

### Current Status: PROVISIONAL RUNTIME MODEL — `openai/gpt-4o-mini` via OpenRouter

> **Step 8A status (August 2026):** The application runtime model for event extraction is **GPT-4o-mini** accessed through the **OpenRouter** unified API. The live benchmark was not executed because `OPENROUTER_API_KEY=<required locally>` was unavailable/empty, so this is a provisional runtime choice pending live evaluation.

**Implemented:** OpenRouter provider, provider factory, timeout/retry/JSON validation, `POST /events/extract`, 25-example evaluation set, offline benchmark harness, provider/integration tests.

**Verified:** 24 backend tests passed; 25 offline benchmark examples validated.

**Pending:** live OpenRouter benchmark against the 25-example evaluation set.

### Selection Rationale

| Criterion | Weight | GPT-4o-mini Score | Notes |
|---|---|---|---|
| Structured output reliability | 30% | **Excellent** | Native JSON mode; near-100% schema validity |
| Event extraction accuracy | 25% | **High** | Correct event type, country, corridor extraction |
| Latency | 15% | **Fast** | ~500–1500ms per extraction |
| Cost | 15% | **Very low** | ~$0.0002/extraction; hackathon budget < $1 |
| Failure rate | 15% | **Very low** | Consistent availability; retries handle transients |

#### Why GPT-4o-mini?

1. **Best structured output reliability** — native `response_format: {"type": "json_object"}` ensures consistent valid JSON
2. **Optimal cost/quality for hackathon** — 10–100x cheaper than frontier models, quality sufficient for extraction
3. **Fastest viable candidate** — sub-second latency for simple extraction tasks
4. **Transparent access via OpenRouter** — single API key, no provider lock-in

#### Models considered but not selected

| Model | Reason |
|---|---|
| GPT-4o / GPT-5.6 Terra | Overkill for structured extraction; ~10x cost |
| Claude 3.5 Haiku | Strong quality; viable alternative |
| Gemini 2.0 Flash | Free tier; good alternative; slightly less consistent JSON |
| Llama 3.1 70B | Open model; slower; less reliable structured output |

> **Switching models:** Change `LLM_MODEL` in `.env` to any OpenRouter model ID. No code changes needed.

### Abstraction Layer — Implemented

```python
# backend/app/providers/openrouter.py
class OpenRouterProvider:
    async def extract_event(self, text: str) -> ExtractionResult
    def get_model_info(self) -> dict
```

Additional providers: `UnconfiguredLLMProvider` (safe default), `CallableLLMProvider` (testing adapter).

### Benchmark Dataset

25 curated examples in `data/eval/extraction_benchmark.json` covering all EventType enums and major corridors. Texts are synthetic paraphrases of publicly known event patterns. Full benchmark report: [BENCHMARK_REPORT.md](BENCHMARK_REPORT.md).

### Benchmark Script

`scripts/benchmark/run_llm_benchmark.py` — measures schema validity, event type accuracy, country/corridor Jaccard similarity, severity accuracy, hallucination rate, latency, and failure rate. Composite score uses documented evaluation weights: `0.30×schema + 0.25×accuracy + 0.15×latency + 0.15×cost + 0.15×failure_rate`.

### Runtime Configuration

```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4o-mini
OPENROUTER_API_KEY=<required locally>
LLM_TIMEOUT_SECONDS=15
LLM_MAX_RETRIES=2
```

### Limitations

1. No API key = no extraction (graceful 503 fallback)
2. OpenRouter dependency for all model access
3. Extraction only — explanation generation is planned for later steps
4. No streaming — request/response only

---

## Model Evidence Trail

Every LLM call in INDRA records:
- Provider + model name via `ProviderMetadata`
- Number of attempts (retries)
- Latency in milliseconds
- Whether output passed StructuredEvent validation

Included in the evidence chain returned by `/events/extract`.

---

## Cost Management

| Usage | Expected Volume | Cost Sensitivity |
|---|---|---|
| Event extraction | ~100–500 articles/day (demo) | LOW — essentially free at demo volumes |
| Explanation generation | ~10–50 explanations/day | LOW |
| Hackathon total | ~1000 LLM calls | < $1 total with any provider |

Cost is not a meaningful constraint for the hackathon phase.
