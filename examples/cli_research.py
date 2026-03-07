"""Run the LangGraph research agent from the command line.

Usage:
    python examples/cli_research.py "What is LangGraph?"
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List

from langchain_core.messages import AnyMessage, HumanMessage

from search_agent.graph import graph
from search_agent.state import AgentState


def main() -> None:
    """Run the research agent from the command line."""
    parser = argparse.ArgumentParser(description="Run the LangGraph research agent")
    parser.add_argument("question", help="Research question")
    parser.add_argument("--initial-queries", type=int, default=3)
    parser.add_argument("--max-loops", type=int, default=2)
    parser.add_argument("--query-generator-model", default="gemini-2.5-flash")
    parser.add_argument("--reflection-model", default="gemini-2.5-flash")
    parser.add_argument("--answer-model", default="gemini-2.5-pro")
    args = parser.parse_args()

    state: AgentState = {
        "messages": [HumanMessage(content=args.question)],
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "research_loop_count": 0,
        "initial_search_query_count": args.initial_queries,
        "max_research_loops": args.max_loops,
        "reasoning_model": args.answer_model,
    }

    configurable: Dict[str, Any] = {
        "number_of_initial_queries": args.initial_queries,
        "max_research_loops": args.max_loops,
        "query_generator_model": args.query_generator_model,
        "reflection_model": args.reflection_model,
        "answer_model": args.answer_model,
    }

    result: AgentState = graph.invoke(state, config={"configurable": configurable})
    messages: List[AnyMessage] = result.get("messages", [])
    if messages:
        print(messages[-1].content)


if __name__ == "__main__":
    main()
