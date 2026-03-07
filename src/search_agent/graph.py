"""LangGraph orchestration for automated web research."""

from __future__ import annotations

import os
from typing import Dict, List, Union

from dotenv import load_dotenv
from google.genai.types import GenerateContentResponse
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from search_agent.async_client import get_async_client
from search_agent.configuration import Configuration
from search_agent.prompts import (
    get_answer_instructions,
    get_current_date,
    get_query_writer_instructions,
    get_reflection_instructions,
    get_web_searcher_instructions,
)
from search_agent.state import AgentState, SourceSegment, WebSearchTask
from search_agent.tools_and_schemas import Reflection, SearchQueryList
from search_agent.utils import (
    Citation,
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)

load_dotenv()


def _require_gemini_api_key() -> str:
    """Return Gemini API key or raise a runtime error."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return api_key


def _build_research_sends(queries: List[str], start_id: int = 0) -> List[Send]:
    """Create stable web research tasks with deterministic ids."""
    return [
        Send(
            "web_research",
            {
                "search_query": query,
                "id": start_id + index,
            },
        )
        for index, query in enumerate(queries)
    ]


async def generate_query(state: AgentState, config: RunnableConfig) -> AgentState:
    """Generate initial search queries from the user question."""
    configurable = Configuration.from_runnable_config(config)
    initial_count = state.get("initial_search_query_count")
    if initial_count is None:
        initial_count = configurable.number_of_initial_queries

    api_key = _require_gemini_api_key()
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=api_key,
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    formatted_prompt = get_query_writer_instructions(
        current_date=get_current_date(),
        research_topic=get_research_topic(state["messages"]),
        number_queries=initial_count,
    )
    result: SearchQueryList = await structured_llm.ainvoke(formatted_prompt)

    return {
        "search_query": result.query,
        "initial_search_query_count": initial_count,
    }


async def continue_to_web_research(state: AgentState) -> List[Send]:
    """Fan out generated queries into web research tasks."""
    queries = state.get("search_query", [])
    return _build_research_sends(queries=queries, start_id=0)


async def web_research(state: WebSearchTask, config: RunnableConfig) -> AgentState:
    """Run one grounded web research task."""
    configurable = Configuration.from_runnable_config(config)
    api_key = _require_gemini_api_key()
    async_client = get_async_client(api_key)

    formatted_prompt = get_web_searcher_instructions(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    response: GenerateContentResponse = await async_client.generate_content(
        model=configurable.query_generator_model,
        contents=formatted_prompt,
        config={
            "tools": [{"google_search": {}}],
            "temperature": 0,
        },
    )

    resolved_urls: Dict[str, str] = resolve_urls(
        urls_to_resolve=response.candidates[0].grounding_metadata.grounding_chunks,
        id=state["id"],
    )
    citations: List[Citation] = get_citations(response, resolved_urls)
    modified_text: str = insert_citation_markers(response.text, citations)
    sources_gathered: List[SourceSegment] = [
        item for citation in citations for item in citation["segments"]
    ]

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [modified_text],
    }


async def reflection(state: AgentState, config: RunnableConfig) -> AgentState:
    """Evaluate sufficiency and generate follow-up queries."""
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.reflection_model
    next_loop_count = state.get("research_loop_count", 0) + 1

    formatted_prompt = get_reflection_instructions(
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state.get("web_research_result", [])),
    )

    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=1.0,
        max_retries=2,
        api_key=_require_gemini_api_key(),
    )
    result: Reflection = await llm.with_structured_output(Reflection).ainvoke(
        formatted_prompt
    )

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": next_loop_count,
        "number_of_ran_queries": len(state.get("search_query", [])),
    }


async def evaluate_research(
    state: AgentState,
    config: RunnableConfig,
) -> Union[str, List[Send]]:
    """Route to finalization or another research loop."""
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = state.get("max_research_loops", configurable.max_research_loops)
    current_loop = state.get("research_loop_count", 0)

    if state.get("is_sufficient") or current_loop >= max_research_loops:
        return "finalize_answer"

    follow_up_queries = state.get("follow_up_queries", [])
    if not follow_up_queries:
        return "finalize_answer"

    start_id = state.get("number_of_ran_queries", len(state.get("search_query", [])))
    return _build_research_sends(queries=follow_up_queries, start_id=start_id)


async def finalize_answer(state: AgentState, config: RunnableConfig) -> AgentState:
    """Generate final answer with resolved citations."""
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model

    formatted_prompt = get_answer_instructions(
        current_date=get_current_date(),
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state.get("web_research_result", [])),
    )

    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=0,
        max_retries=2,
        api_key=_require_gemini_api_key(),
    )
    result: AIMessage = await llm.ainvoke(formatted_prompt)

    final_content = str(result.content)
    unique_sources: List[SourceSegment] = []
    seen_short_urls = set()
    for source in state.get("sources_gathered", []):
        short_url = source["short_url"]
        if short_url in final_content:
            final_content = final_content.replace(short_url, source["value"])
            if short_url not in seen_short_urls:
                unique_sources.append(source)
                seen_short_urls.add(short_url)

    return {
        "messages": [AIMessage(content=final_content)],
        "sources_gathered": unique_sources,
    }


builder: StateGraph = StateGraph(AgentState, config_schema=Configuration)

builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

builder.add_edge(START, "generate_query")
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
builder.add_edge("web_research", "reflection")
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
