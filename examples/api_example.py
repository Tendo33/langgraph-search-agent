#!/usr/bin/env python3
"""Example script showing how to use the LangGraph Research Agent API."""

import json

import requests

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_config():
    """Test the config endpoint."""
    print("Testing config endpoint...")
    response = requests.get(f"{BASE_URL}/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_research():
    """Test the research endpoint."""
    print("Testing research endpoint...")
    
    # Example research request
    research_data = {
        "question": "What are the latest developments in artificial intelligence?",
        "max_research_loops": 2,
        "initial_search_query_count": 2
    }
    
    print(f"Sending research request: {json.dumps(research_data, indent=2)}")
    print("This may take a while...")
    
    response = requests.post(f"{BASE_URL}/research", json=research_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Research completed successfully!")
        print(f"Answer: {result['data']['answer'][:200]}...")  # Show first 200 chars
        print(f"Sources found: {len(result['data']['sources'])}")
        print(f"Research loops: {result['data']['research_loops']}")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests."""
    print("LangGraph Research Agent API Test")
    print("=" * 40)
    
    try:
        test_health()
        test_config()
        test_research()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python run_server.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 