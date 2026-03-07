"""State definitions for the LangGraph research agent."""

from __future__ import annotations

import operator
from typing import List, NotRequired, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


class SourceSegment(TypedDict):
    """Source segment extracted from grounded search output."""

    label: str
    short_url: str
    value: str


class AgentState(TypedDict):
    """Single shared state contract for the entire graph."""

    messages: Annotated[List[AnyMessage], add_messages]
    search_query: Annotated[List[str], operator.add]
    web_research_result: Annotated[List[str], operator.add]
    sources_gathered: Annotated[List[SourceSegment], operator.add]

    follow_up_queries: NotRequired[List[str]]

    initial_search_query_count: NotRequired[int]
    max_research_loops: NotRequired[int]
    research_loop_count: NotRequired[int]
    reasoning_model: NotRequired[str]

    is_sufficient: NotRequired[bool]
    knowledge_gap: NotRequired[str]
    number_of_ran_queries: NotRequired[int]


class WebSearchTask(TypedDict):
    """Task payload sent to the web research node."""

    search_query: str
    id: int
