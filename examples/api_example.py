#!/usr/bin/env python3
"""Example script showing how to use the v2 research API contract."""

from __future__ import annotations

import json
from typing import Any, Dict

import requests

BASE_URL = "http://localhost:8000"


def test_health() -> None:
    """Test the health endpoint."""
    response = requests.get(f"{BASE_URL}/health", timeout=30)
    print("/health", response.status_code)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_config() -> None:
    """Test the config endpoint."""
    response = requests.get(f"{BASE_URL}/config", timeout=30)
    print("/config", response.status_code)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_research() -> None:
    """Test the new research endpoint contract."""
    payload: Dict[str, Any] = {
        "question": "What are the latest developments in artificial intelligence?",
        "options": {
            "max_research_loops": 2,
            "initial_search_query_count": 2,
            "models": {
                "query_generator": "gpt-4o-mini",
                "reflection": "gpt-4o-mini",
                "answer": "gpt-4o",
            },
            "return_debug": True,
        },
    }

    response = requests.post(f"{BASE_URL}/research", json=payload, timeout=240)
    print("/research", response.status_code)
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])

    if result.get("ok"):
        data = result["data"]
        print("Answer preview:", data["answer"][:200])
        print("Sources:", len(data["sources"]))
        print("Loops:", data["meta"]["research_loop_count"])
    else:
        print("Error:", result.get("error"))


def main() -> None:
    """Run all sample requests."""
    try:
        test_health()
        test_config()
        test_research()
    except requests.exceptions.ConnectionError:
        print("鏃犳硶杩炴帴鍒版湇鍔★紝璇峰厛杩愯: python run_server.py")


if __name__ == "__main__":
    main()
