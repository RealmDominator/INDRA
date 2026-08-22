#!/usr/bin/env python3
"""Run one-shot ingestion for all configured sources."""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import AsyncSessionLocal
from app.ingestion.runner import run_all


async def main():
    async with AsyncSessionLocal() as session:
        results = await run_all(session)
    for result in results:
        print(
            f"{result.source_name:8} status={result.status.value:7} "
            f"accepted={result.records_accepted} duplicate={result.records_duplicate} "
            f"freshness={result.freshness} error={result.error or '-'}"
        )


if __name__ == "__main__":
    asyncio.run(main())
