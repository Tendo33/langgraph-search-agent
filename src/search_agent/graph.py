"""LangGraph orchestration for automated web research."""

from __future__ import annotations

import os
from typing import Dict, List, Union

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - validated at runtime
    ChatOpenAI = None

from search_agent.async_client import get_async_client
from search_agent.configuration import Configuration
from search_agent.prompts import (
    get_answer_instructions,
    get_current_date,
    get_query_writer_instructions,
    get_reflection_instructions,
)
from search_agent.state import AgentState, SourceSegment, WebSearchTask
from search_agent.tools_and_schemas import Reflection, SearchQueryList
from search_agent.utils import (
    get_research_topic,
    normalize_tavily_sources,
    resolve_urls,
)

load_dotenv()


def _require_openai_api_key() -> str:
    """Return OpenAI API key or raise runtime error."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return api_key


def _resolve_tavily_connection() -> str:
    """Resolve Tavily MCP server URL."""
    explicit_server_url = os.getenv("TAVILY_MCP_SERVER_URL")
    if explicit_server_url:
        return explicit_server_url

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")

    return f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_api_key}"


def _build_chat_model(*, model: str, temperature: float) -> ChatOpenAI:
    """Build ChatOpenAI instance with OpenAI-compatible endpoint support."""
    if ChatOpenAI is None:
        raise RuntimeError("langchain-openai is required")

    kwargs = {
        "model": model,
        "temperature": temperature,
        "max_retries": 2,
        "api_key": _require_openai_api_key(),
    }

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)


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

    llm = _build_chat_model(
        model=configurable.query_generator_model,
        temperature=1.0,
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


async def web_research(state: WebSearchTask, _config: RunnableConfig) -> AgentState:
    """Run one Tavily MCP web research task."""
    server_url = _resolve_tavily_connection()
    async_client = get_async_client(server_url=server_url)

    search_payload = await async_client.tavily_search(state["search_query"], max_results=6)
    normalized_sources = normalize_tavily_sources(search_payload)

    if not normalized_sources:
        return {
            "sources_gathered": [],
            "search_query": [state["search_query"]],
            "web_research_result": [
                f"Query: {state['search_query']}\nNo reliable results were returned by Tavily MCP."
            ],
        }

    resolved_urls: Dict[str, str] = resolve_urls(
        urls_to_resolve=[item["url"] for item in normalized_sources],
        id=state["id"],
        prefix="https://source.local/id/",
    )

    sources_gathered: List[SourceSegment] = []
    evidence_lines: List[str] = [f"Query: {state['search_query']}", "Findings:"]

    for index, item in enumerate(normalized_sources, start=1):
        url = item["url"]
        short_url = resolved_urls.get(url)
        if not short_url:
            continue

        label = item.get("title") or f"Source {index}"
        snippet = item.get("snippet") or f"Source related to '{state['search_query']}'."
        evidence_lines.append(f"- {snippet} [{label}]({short_url})")
        sources_gathered.append(
            {
                "label": label,
                "short_url": short_url,
                "value": url,
            }
        )

    if len(evidence_lines) == 2:
        evidence_lines.append("- Tavily MCP returned sources but without usable snippets.")

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": ["\n".join(evidence_lines)],
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

    llm = _build_chat_model(
        model=reasoning_model,
        temperature=1.0,
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

    llm = _build_chat_model(
        model=reasoning_model,
        temperature=0,
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
