#!/usr/bin/env python3
"""Async example script for the new research API contract."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

import aiohttp

BASE_URL = "http://localhost:8000"


def build_payload(question: str, max_loops: int = 2, query_count: int = 2) -> Dict[str, Any]:
    return {
        "question": question,
        "options": {
            "max_research_loops": max_loops,
            "initial_search_query_count": query_count,
            "return_debug": False,
        },
    }


async def test_health() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            print("/health", response.status)
            print(json.dumps(await response.json(), indent=2, ensure_ascii=False))


async def test_config() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/config") as response:
            print("/config", response.status)
            print(json.dumps(await response.json(), indent=2, ensure_ascii=False))


async def test_research() -> None:
    payload = build_payload(
        question="What are the latest developments in artificial intelligence?",
        max_loops=2,
        query_count=2,
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/research", json=payload) as response:
            result = await response.json()
            print("/research", response.status)
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1200])

            if response.status == 200 and result.get("ok"):
                print("Answer preview:", result["data"]["answer"][:120])
                print("Sources:", len(result["data"]["sources"]))


async def test_parallel_research() -> None:
    questions = [
        "What are the benefits of renewable energy?",
        "How does machine learning work?",
        "What is the future of space exploration?",
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post(
                f"{BASE_URL}/research",
                json=build_payload(question=question, max_loops=1, query_count=1),
            )
            for question in questions
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for index, response in enumerate(responses, start=1):
            if isinstance(response, Exception):
                print(f"Request {index} failed: {response}")
                continue
            data = await response.json()
            print(f"Request {index}: status={response.status}, ok={data.get('ok')}")


async def main() -> None:
    print("LangGraph Research Agent API Async Test")
    print("=" * 50)

    try:
        await test_health()
        await test_config()
        await test_research()
        await test_parallel_research()
    except aiohttp.ClientConnectorError:
        print("Error: Could not connect to the server.")
        print("Run: python run_server.py")


if __name__ == "__main__":
    asyncio.run(main())
