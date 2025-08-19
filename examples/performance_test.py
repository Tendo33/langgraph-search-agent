#!/usr/bin/env python3
"""Performance testing script to compare sync vs async implementations."""

import asyncio
import time
from typing import Any, Dict, List

import aiohttp
import requests


# API base URL
BASE_URL: str = "http://localhost:8000"


def test_sync_research(question: str, max_loops: int = 2) -> Dict[str, Any]:
    """Test synchronous research using requests library."""
    research_data = {
        "question": question,
        "max_research_loops": max_loops,
        "initial_search_query_count": 2,
    }

    start_time = time.time()
    response = requests.post(f"{BASE_URL}/research", json=research_data)
    end_time = time.time()

    return {
        "duration": end_time - start_time,
        "status": response.status_code,
        "success": response.status_code == 200,
        "question": question,
    }


async def test_async_research(question: str, max_loops: int = 2) -> Dict[str, Any]:
    """Test asynchronous research using aiohttp."""
    research_data = {
        "question": question,
        "max_research_loops": max_loops,
        "initial_search_query_count": 2,
    }

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/research", json=research_data) as response:
            end_time = time.time()

            return {
                "duration": end_time - start_time,
                "status": response.status,
                "success": response.status == 200,
                "question": question,
            }


def test_sync_parallel(questions: List[str]) -> List[Dict[str, Any]]:
    """Test multiple synchronous requests sequentially."""
    results = []
    for question in questions:
        result = test_sync_research(question)
        results.append(result)
    return results


async def test_async_parallel(questions: List[str]) -> List[Dict[str, Any]]:
    """Test multiple asynchronous requests in parallel."""
    tasks = [test_async_research(question) for question in questions]
    return await asyncio.gather(*tasks)


def run_performance_test():
    """Run comprehensive performance tests."""
    print("Performance Test: Sync vs Async Implementation")
    print("=" * 60)

    # Test questions
    questions = [
        "What are the latest developments in artificial intelligence?",
        "How does renewable energy work?",
        "What are the benefits of machine learning?",
        "Explain quantum computing basics",
        "What is the future of space exploration?",
    ]

    # Test single request performance
    print("\n1. Single Request Performance Test")
    print("-" * 40)

    question = questions[0]
    sync_result = test_sync_research(question)

    async_result = asyncio.run(test_async_research(question))

    print(
        f"Sync - Duration: {sync_result['duration']:.2f}s, Status: {sync_result['status']}"
    )
    print(
        f"Async - Duration: {async_result['duration']:.2f}s, Status: {async_result['status']}"
    )

    if sync_result["success"] and async_result["success"]:
        improvement = (
            (sync_result["duration"] - async_result["duration"])
            / sync_result["duration"]
        ) * 100
        print(f"Performance improvement: {improvement:.1f}%")

    # Test parallel performance
    print("\n2. Parallel Request Performance Test")
    print("-" * 40)

    # Sync parallel (sequential)
    sync_start = time.time()
    sync_results = test_sync_parallel(questions[:3])
    sync_end = time.time()
    sync_total = sync_end - sync_start

    # Async parallel (concurrent)
    async_start = time.time()
    async_results = asyncio.run(test_async_parallel(questions[:3]))
    async_end = time.time()
    async_total = async_end - async_start

    print(f"Sync (sequential) - Total duration: {sync_total:.2f}s")
    print(f"Async (parallel) - Total duration: {async_total:.2f}s")

    sync_avg = sum(r["duration"] for r in sync_results) / len(sync_results)
    async_avg = sum(r["duration"] for r in async_results) / len(async_results)

    print(f"Sync average per request: {sync_avg:.2f}s")
    print(f"Async average per request: {async_avg:.2f}s")

    improvement = ((sync_total - async_total) / sync_total) * 100
    print(f"Parallel performance improvement: {improvement:.1f}%")

    # Test throughput
    print("\n3. Throughput Test")
    print("-" * 40)

    sync_throughput = len(questions[:3]) / sync_total
    async_throughput = len(questions[:3]) / async_total

    print(f"Sync throughput: {sync_throughput:.2f} requests/second")
    print(f"Async throughput: {async_throughput:.2f} requests/second")

    throughput_improvement = (
        (async_throughput - sync_throughput) / sync_throughput
    ) * 100
    print(f"Throughput improvement: {throughput_improvement:.1f}%")

    # Summary
    print("\n4. Test Summary")
    print("-" * 40)

    successful_sync = sum(1 for r in sync_results if r["success"])
    successful_async = sum(1 for r in async_results if r["success"])

    print(
        f"Sync success rate: {successful_sync}/{len(sync_results)} ({successful_sync / len(sync_results) * 100:.1f}%)"
    )
    print(
        f"Async success rate: {successful_async}/{len(async_results)} ({successful_async / len(async_results) * 100:.1f}%)"
    )


if __name__ == "__main__":
    try:
        run_performance_test()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python run_server.py")
    except Exception as e:
        print(f"Error: {e}")
