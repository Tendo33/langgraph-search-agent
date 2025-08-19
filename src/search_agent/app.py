"""FastAPI application for serving the LangGraph agent API.

This module sets up the FastAPI app with endpoints for interacting with the
LangGraph research agent.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from search_agent.async_client import close_async_client
from search_agent.graph import graph
from search_agent.state import OverallState

load_dotenv()

# Define the FastAPI app
app: FastAPI = FastAPI(
    title="LangGraph Research Agent API",
    description="API for interacting with a LangGraph-powered research agent",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LangGraph
try:
    graph_instance = graph
except Exception as e:
    print(f"Warning: Failed to initialize graph: {e}")
    graph_instance = None


# Pydantic models for API requests/responses
class ResearchRequest(BaseModel):
    """Request model for research queries."""

    question: str = Field(..., description="The research question to investigate")
    max_research_loops: int = Field(
        default=3, description="Maximum number of research loops"
    )
    initial_search_query_count: int = Field(
        default=3, description="Number of initial search queries to generate"
    )


class ResearchResponse(BaseModel):
    """Response model for research results."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    graph_ready: bool


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "LangGraph Research Agent API", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy", version="1.0.0", graph_ready=graph_instance is not None
    )


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    """Perform research using the LangGraph agent."""
    if graph_instance is None:
        raise HTTPException(status_code=503, detail="LangGraph agent is not available")

    try:
        # Prepare the initial state
        initial_state: OverallState = {
            "messages": [HumanMessage(content=request.question)],
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": request.initial_search_query_count,
            "max_research_loops": request.max_research_loops,
            "research_loop_count": 0,
            "reasoning_model": "gemini-2.0-flash-exp",
        }

        # Execute the graph asynchronously
        result: Dict[str, Any] = await graph_instance.ainvoke(initial_state)

        # Extract the final answer from the result
        final_answer: Optional[str] = None
        if "messages" in result and result["messages"]:
            # Find the last AI message
            for message in reversed(result["messages"]):
                if hasattr(message, "content"):
                    final_answer = message.content
                    break

        return ResearchResponse(
            success=True,
            message="Research completed successfully",
            data={
                "answer": final_answer,
                "sources": result.get("sources_gathered", []),
                "research_loops": result.get("research_loop_count", 0),
                "full_result": result,
            },
        )

    except Exception as e:
        return ResearchResponse(
            success=False, message=f"Research failed: {str(e)}", data={"error": str(e)}
        )


@app.get("/config")
async def get_config() -> Dict[str, Any]:
    """Get current configuration information."""
    config: Dict[str, Any] = {
        "gemini_api_key_set": bool(os.getenv("GEMINI_API_KEY")),
        "graph_ready": graph_instance is not None,
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
    return config


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources when the app shuts down."""
    await close_async_client()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
