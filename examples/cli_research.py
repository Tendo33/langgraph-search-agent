"""Run the LangGraph research agent from the command line.

Usage:
    python cli_research.py "What is the capital of France?"

Options:
    --initial-queries=N  Number of initial search queries (default: 3)
    --max-loops=N        Maximum number of research loops (default: 2)
    --reasoning-model=M  Model for the final answer (default: gemini-2.5-pro-preview-05-06)
"""

import argparse
from typing import Any, Dict, List

from langchain_core.messages import AnyMessage, HumanMessage

from search_agent.graph import graph
from search_agent.state import OverallState


def main() -> None:
    """Run the research agent from the command line."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run the LangGraph research agent"
    )
    parser.add_argument("question", help="Research question")
    parser.add_argument(
        "--initial-queries",
        type=int,
        default=3,
        help="Number of initial search queries",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=2,
        help="Maximum number of research loops",
    )
    parser.add_argument(
        "--reasoning-model",
        default="gemini-2.5-pro-preview-05-06",
        help="Model for the final answer",
    )
    args: argparse.Namespace = parser.parse_args()

    state: Dict[str, Any] = {
        "messages": [HumanMessage(content=args.question)],
        "initial_search_query_count": args.initial_queries,
        "max_research_loops": args.max_loops,
        "reasoning_model": args.reasoning_model,
    }

    result: OverallState = graph.invoke(state)
    messages: List[AnyMessage] = result.get("messages", [])
    if messages:
        print(messages[-1].content)


if __name__ == "__main__":
    main()
