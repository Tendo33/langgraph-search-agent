"""State definitions and data structures for the agent's operation.

This module defines TypedDicts used to manage and track the state
of the agent, including overall state, reflection, query generation, and web search.
"""

from __future__ import annotations

import operator
from typing import List, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


class SourceSegment(TypedDict):
    """Type definition for source segment."""

    label: str
    short_url: str
    value: str


class OverallState(TypedDict):
    """Overall state of the agent.

    Args:
        TypedDict (TypedDict): A dictionary representing the overall state.
    """

    messages: Annotated[List[AnyMessage], add_messages]
    search_query: Annotated[List[str], operator.add]
    web_research_result: Annotated[List[str], operator.add]
    sources_gathered: Annotated[List[SourceSegment], operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str


class ReflectionState(TypedDict):
    """State for reflection on the research process."""

    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[List[str], operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    """Representation of a search query."""

    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    """State for generating search queries."""

    search_query: List[Query]


class WebSearchState(TypedDict):
    """State for web search operations."""

    search_query: str
    id: int
