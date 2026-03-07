from __future__ import annotations

import operator
from typing import Annotated, List, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class DemoState(TypedDict):
    question: str
    queries: Annotated[List[str], operator.add]
    notes: Annotated[List[str], operator.add]
    is_enough: bool
    loop_count: int


def generate_queries(state: DemoState) -> DemoState:
    q1 = f"{state['question']} definition"
    q2 = f"{state['question']} example"
    return {"queries": [q1, q2]}


def dispatch_queries(state: DemoState) -> List[Send]:
    return [
        Send("search", {"queries": [query], "notes": [], "loop_count": state.get("loop_count", 0)})
        for query in state["queries"]
    ]


def search(state: DemoState) -> DemoState:
    current_query = state["queries"][-1]
    return {"notes": [f"result for: {current_query}"]}


def reflect(state: DemoState) -> DemoState:
    next_loop = state.get("loop_count", 0) + 1
    enough = len(state.get("notes", [])) >= 2 or next_loop >= 2
    return {"is_enough": enough, "loop_count": next_loop}


def route_after_reflect(state: DemoState):
    if state["is_enough"]:
        return "finalize"
    return [Send("search", {"queries": ["follow-up query"], "notes": [], "loop_count": state["loop_count"]})]


def finalize(state: DemoState) -> DemoState:
    summary = "\n".join(state.get("notes", []))
    return {"notes": [f"FINAL ANSWER\n{summary}"]}


builder = StateGraph(DemoState)
builder.add_node("generate_queries", generate_queries)
builder.add_node("search", search)
builder.add_node("reflect", reflect)
builder.add_node("finalize", finalize)

builder.add_edge(START, "generate_queries")
builder.add_conditional_edges("generate_queries", dispatch_queries, ["search"])
builder.add_edge("search", "reflect")
builder.add_conditional_edges("reflect", route_after_reflect, ["search", "finalize"])
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke(
        {
            "question": "LangGraph",
            "queries": [],
            "notes": [],
            "is_enough": False,
            "loop_count": 0,
        }
    )
    print(result["notes"][-1])
