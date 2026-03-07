import asyncio
from typing import Any, Dict

from langgraph.types import Send

from search_agent.graph import continue_to_web_research, evaluate_research


def _extract_payload(send_obj: Send) -> Dict[str, Any]:
    for attr in ("arg", "payload", "kwargs", "value"):
        value = getattr(send_obj, attr, None)
        if isinstance(value, dict):
            return value
    return {}


def test_continue_to_web_research_returns_send_list():
    result = asyncio.run(
        continue_to_web_research(
            {
                "search_query": ["query-1", "query-2"],
            }
        )
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, Send) for item in result)


def test_evaluate_research_routes_to_finalize_when_sufficient():
    route = asyncio.run(
        evaluate_research(
            {
                "is_sufficient": True,
                "research_loop_count": 1,
                "follow_up_queries": ["q"],
                "number_of_ran_queries": 1,
            },
            {"configurable": {"max_research_loops": 3}},
        )
    )

    assert route == "finalize_answer"


def test_evaluate_research_returns_send_when_not_sufficient():
    route = asyncio.run(
        evaluate_research(
            {
                "is_sufficient": False,
                "research_loop_count": 1,
                "follow_up_queries": ["f1", "f2"],
                "number_of_ran_queries": 3,
            },
            {"configurable": {"max_research_loops": 3}},
        )
    )

    assert isinstance(route, list)
    assert len(route) == 2

    payload = _extract_payload(route[0])
    assert payload.get("id") == 3
