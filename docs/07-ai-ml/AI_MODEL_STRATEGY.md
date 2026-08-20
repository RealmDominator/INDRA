# INDRA — AI Model Strategy

> This document describes how INDRA manages AI models for two distinct purposes:
> 1. **Development-agent models** — AI models used by the development team/agents to build and maintain the project
> 2. **Application LLM** — The AI model embedded within INDRA itself for event extraction and explanation

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

### Current Status: NOT SELECTED

The application LLM — the model INDRA calls at runtime for event extraction and recommendation explanation — has **not been chosen yet.**

### Why Not Choose Now?

1. Task-specific performance varies significantly between models
2. Structured output reliability differs across providers
3. Cost and latency profiles matter for production but can't be evaluated without running the actual pipeline
4. Free tier availability and rate limits affect hackathon viability

### Abstraction Layer Requirement

INDRA must implement an LLM abstraction/provider layer so that the actual model can be swapped without rewriting application code:

```python
# Conceptual interface
class LLMProvider(ABC):
    @abstractmethod
    async def extract_event(self, article_text: str) -> StructuredEvent:
        pass

    @abstractmethod
    async def generate_explanation(self, results: dict) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        """Return model name, provider, version for evidence trail"""
        pass
```

Every LLM call in the application must go through this abstraction. Direct API calls to any specific provider are prohibited.

### Benchmark Plan

When the pipeline is functional, benchmark candidate models on representative INDRA tasks:

#### Benchmark Tasks

1. **Event extraction accuracy** — Given 50 curated news articles about energy/geopolitical events, how accurately does the model extract structured event data?
2. **Structured output reliability** — Does the model consistently return valid JSON matching the required schema?
3. **Entity extraction accuracy** — Are countries, organizations, chokepoints correctly identified?
4. **Severity calibration** — Are severity scores reasonable and consistent across similar events?
5. **Explanation quality** — Are generated explanations accurate, coherent, and free of hallucinated numbers?

#### Evaluation Criteria

| Criterion | Weight | Measurement |
|---|---|---|
| Structured output reliability | 30% | % of responses that parse as valid JSON matching schema |
| Event extraction accuracy | 25% | F1 score on event type, entities, corridors |
| Latency | 15% | p50 and p95 response time |
| Cost | 15% | Cost per 1000 extractions |
| Failure rate | 15% | % of API calls that error or timeout |

#### Candidate Models for Benchmarking

Based on the available model landscape, the following are candidates for the application LLM role:

| Model | Provider | Potential Fit |
|---|---|---|
| GPT-4o-mini / GPT-4.1-mini | OpenAI | Low cost, good structured output |
| Claude Haiku / Claude Sonnet | Anthropic | Good extraction quality |
| Gemini Flash | Google | Low cost, fast |
| Nemotron 3 Nano / Lightning | NVIDIA | Open model, potentially self-hosted |
| GLM 5.2 (smaller variants) | Zhipu | Fast, cost-effective |
| Other approved models | Various | Only after explicit evaluation |

### Selection Timeline

1. Build the LLM abstraction layer (implementation step)
2. Implement at least two provider backends (e.g., OpenAI + Anthropic)
3. Create the benchmark dataset (50 curated articles with ground-truth extractions)
4. Run benchmarks
5. Select based on results
6. Document the selection rationale

> **IMPORTANT:** Do not select the final application LLM based on general benchmarks, marketing claims, or personal preference. Select based on task-specific evaluation using INDRA's actual extraction tasks.

---

## Model Evidence Trail

Every LLM call in INDRA must record:
- Which model was used (provider + model name + version)
- Input token count
- Output token count
- Latency
- Whether the output passed validation

This supports the evidence chain and enables later analysis of model performance.

---

## Cost Management

| Usage | Expected Volume | Cost Sensitivity |
|---|---|---|
| Event extraction | ~100–500 articles/day (demo) | LOW — essentially free at demo volumes |
| Explanation generation | ~10–50 explanations/day | LOW |
| Hackathon total | ~1000 LLM calls | < $1 total with any provider |

Cost is not a meaningful constraint for the hackathon phase. It becomes relevant at production volumes (Phase 2+).
