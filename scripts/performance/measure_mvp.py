#!/usr/bin/env python3
"""Small local performance probe for the deterministic MVP surface.

This is not a load test. It records real request timings and failures for a
bounded sample, using only local API endpoints and deterministic payloads.
External-provider latency is deliberately not measured here.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
import time
from typing import Any, Callable

import httpx


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, math.ceil(p * len(ordered)) - 1))]


def summary(name: str, values: list[float], failures: list[str], requested: int) -> dict[str, Any]:
    return {
        "name": name,
        "requests": requested,
        "successes": len(values),
        "failures": len(failures),
        "average_ms": round(statistics.mean(values), 2) if values else None,
        "median_ms": round(statistics.median(values), 2) if values else None,
        "p95_ms": round(percentile(values, 0.95), 2) if values else None,
        "failure_examples": failures[:3],
    }


async def run_probe(
    client: httpx.AsyncClient,
    name: str,
    request: Callable[[], Any],
    count: int,
    concurrency: int,
) -> dict[str, Any]:
    semaphore = asyncio.Semaphore(concurrency)
    timings: list[float] = []
    failures: list[str] = []

    async def one() -> None:
        async with semaphore:
            started = time.perf_counter()
            try:
                response = await request()
                elapsed = (time.perf_counter() - started) * 1000
                if response.status_code >= 400:
                    failures.append(f"HTTP {response.status_code}: {response.text[:160]}")
                else:
                    timings.append(elapsed)
            except Exception as exc:  # pragma: no cover - exercised by live probe
                failures.append(f"{type(exc).__name__}: {str(exc)[:160]}")

    await asyncio.gather(*(one() for _ in range(count)))
    return summary(name, timings, failures, count)


async def main(base_url: str, count: int, concurrency: int) -> None:
    timeout = httpx.Timeout(20.0, connect=5.0)
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        checks: list[tuple[str, Callable[[], Any]]] = [
            ("GET /health", lambda: client.get("/health")),
            ("GET /countries", lambda: client.get("/countries")),
            ("GET /corridors/risk", lambda: client.get("/corridors/risk")),
            ("GET /routes", lambda: client.get("/routes")),
            ("POST /risk", lambda: client.post("/risk", json={"features": {
                "event_severity": 0.6, "event_recency": 0.7,
                "chokepoint_exposure": 0.65, "conflict_sanctions": 0.4,
                "historical_rate": 0.3, "india_dependency": 0.8,
            }})),
            ("POST /scenarios", lambda: client.post("/scenarios", json={
                "scenario_type": "HORMUZ_FULL", "duration_days": 30, "reduction_pct": 100,
            })),
            ("POST /recommendations", lambda: client.post("/recommendations", json={
                "target_volume": 1,
                "candidates": [{"id": 1, "available_volume": 2, "unit_cost": 70,
                                "risk_score": 0.2, "transit_days": 12,
                                "compatibility_score": 0.9, "is_operational": True}],
            })),
            ("GET /ingestion/status", lambda: client.get("/ingestion/status")),
        ]

        results = []
        for name, request in checks:
            results.append(await run_probe(client, name, request, count, concurrency))

        events = await client.get("/events")
        items = events.json().get("items", []) if events.status_code < 400 else []
        if items:
            event_id = items[0]["id"]
            # Existing-event processing exercises the deterministic pipeline without
            # creating new events or claiming live-provider timing.
            results.append(await run_probe(
                client,
                "POST /events/process (local deterministic pipeline)",
                lambda: client.post("/events/process", json={"event_id": event_id}),
                max(1, min(count, 5)),
                1,
            ))
        else:
            results.append({"name": "POST /events/process", "skipped": True, "reason": "no persisted event"})

        print(json.dumps({
            "base_url": base_url,
            "sample_count": count,
            "concurrency": concurrency,
            "external_provider_timing": "not measured",
            "results": results,
        }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()
    if args.count < 1 or args.concurrency < 1:
        parser.error("--count and --concurrency must be positive")
    asyncio.run(main(args.base_url.rstrip("/"), args.count, args.concurrency))
