#!/usr/bin/env python3
"""Async example script showing how to use the LangGraph Research Agent API."""

import asyncio
import json
from typing import Any, Dict

import aiohttp


# API base URL
BASE_URL: str = "http://localhost:8000"


async def test_health() -> None:
    """Test the health endpoint."""
    print("Testing health endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
    print()


async def test_config() -> None:
    """Test the config endpoint."""
    print("Testing config endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/config") as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
    print()


async def test_research() -> None:
    """Test the research endpoint."""
    print("Testing research endpoint...")

    # Example research request
    research_data: Dict[str, Any] = {
        "question": "What are the latest developments in artificial intelligence?",
        "max_research_loops": 2,
        "initial_search_query_count": 2,
    }

    print(f"Sending research request: {json.dumps(research_data, indent=2)}")
    print("This may take a while...")

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/research", json=research_data) as response:
            print(f"Status: {response.status}")

            if response.status == 200:
                result: Dict[str, Any] = await response.json()
                print("Research completed successfully!")
                print(
                    f"Answer: {result['data']['answer'][:200]}..."
                )  # Show first 200 chars
                print(f"Sources found: {len(result['data']['sources'])}")
                print(f"Research loops: {result['data']['research_loops']}")
            else:
                error_text = await response.text()
                print(f"Error: {error_text}")
    print()


async def test_parallel_research() -> None:
    """Test multiple research requests in parallel."""
    print("Testing parallel research requests...")

    questions = [
        "What are the benefits of renewable energy?",
        "How does machine learning work?",
        "What is the future of space exploration?",
    ]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, question in enumerate(questions):
            research_data = {
                "question": question,
                "max_research_loops": 1,
                "initial_search_query_count": 1,
            }
            task = session.post(f"{BASE_URL}/research", json=research_data)
            tasks.append((i + 1, question, task))

        # Execute all requests in parallel
        responses = await asyncio.gather(
            *[task for _, _, task in tasks], return_exceptions=True
        )

        for (i, question, _), response in zip(tasks, responses):
            if isinstance(response, Exception):
                print(f"Request {i} failed: {response}")
            else:
                print(f"Request {i} completed: {question}")
                result = await response.json()
                print(f"  Status: {response.status}")
                print(f"  Answer preview: {result['data']['answer'][:100]}...")
    print()


async def main() -> None:
    """Run all tests."""
    print("LangGraph Research Agent API Async Test")
    print("=" * 50)

    try:
        await test_health()
        await test_config()
        await test_research()
        await test_parallel_research()
    except aiohttp.ClientConnectorError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python run_server.py")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
