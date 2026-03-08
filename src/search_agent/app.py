"""FastAPI application for serving the LangGraph research agent."""

from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from search_agent.async_client import close_async_client
from search_agent.configuration import Configuration
from search_agent.graph import graph
from search_agent.state import AgentState

load_dotenv()

APP_VERSION = "2.0.0"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup/shutdown resources."""
    try:
        yield
    finally:
        await close_async_client()


app: FastAPI = FastAPI(
    title="LangGraph Research Agent API",
    description="API for interacting with a LangGraph-powered research agent",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    graph_instance = graph
except Exception as exc:  # pragma: no cover
    print(f"Warning: Failed to initialize graph: {exc}")
    graph_instance = None


class ErrorInfo(BaseModel):
    """Structured error payload."""

    code: str
    message: str
    details: Any | None = None


class SourceItem(BaseModel):
    """Public source model returned by the API."""

    title: str
    url: str


class ResearchMeta(BaseModel):
    """Metadata for research execution."""

    research_loop_count: int
    queries_ran: int
    duration_ms: int


class ResearchData(BaseModel):
    """Successful research response payload."""

    answer: str
    sources: List[SourceItem]
    meta: ResearchMeta
    debug: Dict[str, Any] | None = None


class ResearchResponse(BaseModel):
    """Unified research response."""

    ok: bool
    data: ResearchData | None = None
    error: ErrorInfo | None = None


class ModelOptions(BaseModel):
    """Model override options."""

    query_generator: str | None = None
    reflection: str | None = None
    answer: str | None = None


class ResearchOptions(BaseModel):
    """Research runtime options."""

    max_research_loops: int | None = Field(default=None, ge=1)
    initial_search_query_count: int | None = Field(default=None, ge=1)
    models: ModelOptions | None = None
    return_debug: bool = False


class ResearchRequest(BaseModel):
    """Request model for research queries."""

    question: str = Field(..., min_length=1, description="The research question")
    options: ResearchOptions = Field(default_factory=ResearchOptions)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    graph_ready: bool
    openai_api_key_set: bool
    tavily_api_key_set: bool
    tavily_mcp_server_url_set: bool


def _build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    payload = ResearchResponse(
        ok=False,
        error=ErrorInfo(code=code, message=message, details=details),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def _build_configurable(options: ResearchOptions) -> Dict[str, Any]:
    configurable: Dict[str, Any] = {}
    if options.max_research_loops is not None:
        configurable["max_research_loops"] = options.max_research_loops
    if options.initial_search_query_count is not None:
        configurable["number_of_initial_queries"] = options.initial_search_query_count

    if options.models:
        if options.models.query_generator:
            configurable["query_generator_model"] = options.models.query_generator
        if options.models.reflection:
            configurable["reflection_model"] = options.models.reflection
        if options.models.answer:
            configurable["answer_model"] = options.models.answer

    return configurable


def _extract_answer(result_state: AgentState) -> str:
    messages = result_state.get("messages", [])
    for message in reversed(messages):
        content = getattr(message, "content", None)
        if content:
            return str(content)
    return ""


def _extract_sources(result_state: AgentState) -> List[SourceItem]:
    response_sources: List[SourceItem] = []
    for index, source in enumerate(result_state.get("sources_gathered", []), start=1):
        title = source.get("label") or f"Source {index}"
        url = source.get("value") or ""
        if url:
            response_sources.append(SourceItem(title=title, url=url))
    return response_sources


def _serialize_state_for_debug(state: AgentState) -> Dict[str, Any]:
    messages = [
        {
            "type": message.__class__.__name__,
            "content": str(getattr(message, "content", "")),
        }
        for message in state.get("messages", [])
    ]
    return {
        "messages": messages,
        "search_query": state.get("search_query", []),
        "web_research_result_count": len(state.get("web_research_result", [])),
        "sources_gathered_count": len(state.get("sources_gathered", [])),
        "follow_up_queries": state.get("follow_up_queries", []),
        "is_sufficient": state.get("is_sufficient"),
        "knowledge_gap": state.get("knowledge_gap"),
        "number_of_ran_queries": state.get("number_of_ran_queries"),
        "research_loop_count": state.get("research_loop_count", 0),
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return structured validation errors."""
    return _build_error_response(
        status_code=422,
        code="validation_error",
        message="Request payload validation failed",
        details=exc.errors(),
    )


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "LangGraph Research Agent API",
        "version": APP_VERSION,
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if graph_instance is not None else "degraded",
        version=APP_VERSION,
        graph_ready=graph_instance is not None,
        openai_api_key_set=bool(os.getenv("OPENAI_API_KEY")),
        tavily_api_key_set=bool(os.getenv("TAVILY_API_KEY")),
        tavily_mcp_server_url_set=bool(os.getenv("TAVILY_MCP_SERVER_URL")),
    )


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Perform research using the LangGraph agent."""
    if graph_instance is None:
        return _build_error_response(
            status_code=503,
            code="graph_unavailable",
            message="LangGraph agent is not available",
        )

    start_time = time.perf_counter()
    configurable = _build_configurable(request.options)

    initial_state: AgentState = {
        "messages": [HumanMessage(content=request.question.strip())],
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "research_loop_count": 0,
    }

    if request.options.initial_search_query_count is not None:
        initial_state["initial_search_query_count"] = (
            request.options.initial_search_query_count
        )
    if request.options.max_research_loops is not None:
        initial_state["max_research_loops"] = request.options.max_research_loops
    if request.options.models and request.options.models.answer:
        initial_state["reasoning_model"] = request.options.models.answer

    try:
        result: AgentState = await graph_instance.ainvoke(
            initial_state,
            config={"configurable": configurable},
        )
    except RuntimeError as exc:
        error_text = str(exc)
        if "OPENAI_API_KEY" in error_text or "TAVILY_API_KEY" in error_text:
            return _build_error_response(
                status_code=503,
                code="missing_api_key",
                message="OPENAI_API_KEY and TAVILY_API_KEY are required",
                details=error_text,
            )
        if (
            "langchain-openai is required" in error_text
            or "langchain-mcp-adapters is required" in error_text
        ):
            return _build_error_response(
                status_code=503,
                code="missing_dependency",
                message="Required dependencies are missing",
                details=error_text,
            )
        return _build_error_response(
            status_code=500,
            code="runtime_error",
            message="Research execution failed",
            details=error_text,
        )
    except Exception as exc:  # pragma: no cover
        return _build_error_response(
            status_code=500,
            code="internal_error",
            message="Research execution failed",
            details=str(exc),
        )

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    response_data = ResearchData(
        answer=_extract_answer(result),
        sources=_extract_sources(result),
        meta=ResearchMeta(
            research_loop_count=result.get("research_loop_count", 0),
            queries_ran=len(result.get("search_query", [])),
            duration_ms=duration_ms,
        ),
        debug=_serialize_state_for_debug(result) if request.options.return_debug else None,
    )

    return ResearchResponse(ok=True, data=response_data)


@app.get("/config")
async def get_config() -> Dict[str, Any]:
    """Return current runtime configuration context."""
    defaults = Configuration().model_dump()
    return {
        "ok": True,
        "data": {
            "graph_ready": graph_instance is not None,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "api_keys": {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "tavily": bool(os.getenv("TAVILY_API_KEY")),
                "tavily_mcp_server_url": bool(os.getenv("TAVILY_MCP_SERVER_URL")),
            },
            "defaults": defaults,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
