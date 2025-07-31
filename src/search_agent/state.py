"""State definitions and data structures for the agent's operation.

This module defines TypedDicts and dataclasses used to manage and track the state
of the agent, including overall state, reflection, query generation, and web search.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated


class OverallState(TypedDict):
    """Overall state of the agent.

    Args:
        TypedDict (TypedDict): A dictionary representing the overall state.
    """

    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str


class ReflectionState(TypedDict):
    """State for reflection on the research process."""

    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    """Representation of a search query."""

    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    """State for generating search queries."""

    search_query: list[Query]


class WebSearchState(TypedDict):
    """State for web search operations."""

    search_query: str
    id: str


@dataclass(kw_only=True)
class SearchStateOutput:
    """Output state for search operations."""

    running_summary: str = field(default=None)  # Final report
