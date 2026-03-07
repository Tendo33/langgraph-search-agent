#!/usr/bin/env python3
"""Performance testing script against the new research API contract."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List

import aiohttp
import requests

BASE_URL = "http://localhost:8000"


def build_payload(question: str, max_loops: int = 2) -> Dict[str, Any]:
    return {
        "question": question,
        "options": {
            "max_research_loops": max_loops,
            "initial_search_query_count": 2,
            "return_debug": False,
        },
    }


def test_sync_research(question: str, max_loops: int = 2) -> Dict[str, Any]:
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/research", json=build_payload(question, max_loops))
    end_time = time.time()
    body = response.json()

    return {
        "duration": end_time - start_time,
        "status": response.status_code,
        "success": response.status_code == 200 and body.get("ok", False),
        "question": question,
    }


async def test_async_research(question: str, max_loops: int = 2) -> Dict[str, Any]:
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/research", json=build_payload(question, max_loops)
        ) as response:
            body = await response.json()
            end_time = time.time()
            return {
                "duration": end_time - start_time,
                "status": response.status,
                "success": response.status == 200 and body.get("ok", False),
                "question": question,
            }


def test_sync_parallel(questions: List[str]) -> List[Dict[str, Any]]:
    return [test_sync_research(question) for question in questions]


async def test_async_parallel(questions: List[str]) -> List[Dict[str, Any]]:
    tasks = [test_async_research(question) for question in questions]
    return await asyncio.gather(*tasks)


def run_performance_test() -> None:
    print("Performance Test: Sync vs Async")
    print("=" * 60)

    questions = [
        "What are the latest developments in artificial intelligence?",
        "How does renewable energy work?",
        "What are the benefits of machine learning?",
    ]

    print("\n1) Single request")
    sync_result = test_sync_research(questions[0])
    async_result = asyncio.run(test_async_research(questions[0]))
    print(f"Sync : {sync_result['duration']:.2f}s, success={sync_result['success']}")
    print(f"Async: {async_result['duration']:.2f}s, success={async_result['success']}")

    print("\n2) Parallel requests")
    sync_start = time.time()
    sync_results = test_sync_parallel(questions)
    sync_total = time.time() - sync_start

    async_start = time.time()
    async_results = asyncio.run(test_async_parallel(questions))
    async_total = time.time() - async_start

    print(f"Sync total : {sync_total:.2f}s")
    print(f"Async total: {async_total:.2f}s")

    successful_sync = sum(1 for item in sync_results if item["success"])
    successful_async = sum(1 for item in async_results if item["success"])
    print(f"Sync success : {successful_sync}/{len(sync_results)}")
    print(f"Async success: {successful_async}/{len(async_results)}")


if __name__ == "__main__":
    try:
        run_performance_test()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Run: python run_server.py")
