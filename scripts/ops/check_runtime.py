"""Check safe runtime and ingestion status for local maintenance."""

import json
import os
import sys
from urllib.error import URLError
from urllib.request import urlopen


def fetch(base_url: str, path: str) -> dict:
    with urlopen(f"{base_url.rstrip('/')}{path}", timeout=5) as response:
        return json.load(response)


def main() -> int:
    base_url = os.getenv("INDRA_API_URL", "http://127.0.0.1:8000")
    try:
        health = fetch(base_url, "/health")
        status = fetch(base_url, "/ingestion/status")
    except (OSError, URLError, ValueError) as exc:
        print(f"RUNTIME UNAVAILABLE: {type(exc).__name__}")
        return 1

    print(f"application={health.get('components', {}).get('application', health.get('status'))}")
    print(f"database={health.get('components', {}).get('database', health.get('database'))}")
    print(f"llm_provider={health.get('components', {}).get('llm_provider', 'UNKNOWN')}")
    print(f"external_sources={health.get('components', {}).get('external_sources', 'UNKNOWN')}")
    for source in status.get("sources", []):
        print(f"source={source.get('name')} freshness={source.get('freshness')} status={source.get('status')}")
    return 0 if health.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())

