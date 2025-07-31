"""FastAPI application for serving the LangGraph agent API.

This module sets up the FastAPI app with endpoints for interacting with the
LangGraph research agent.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from search_agent.graph import create_graph
from search_agent.state import OverallState

load_dotenv()

# Define the FastAPI app
app = FastAPI(
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
    graph = create_graph()
except Exception as e:
    print(f"Warning: Failed to initialize graph: {e}")
    graph = None


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
    data: Dict[str, Any] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    graph_ready: bool


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {"message": "LangGraph Research Agent API", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy", version="1.0.0", graph_ready=graph is not None
    )


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Perform research using the LangGraph agent."""
    if graph is None:
        raise HTTPException(status_code=503, detail="LangGraph agent is not available")

    try:
        # Prepare the initial state
        initial_state: OverallState = {
            "messages": [{"role": "user", "content": request.question}],
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": request.initial_search_query_count,
            "max_research_loops": request.max_research_loops,
            "research_loop_count": 0,
            "reasoning_model": "gemini-2.0-flash-exp",
        }

        # Execute the graph
        result = graph.invoke(initial_state)

        # Extract the final answer from the result
        final_answer = None
        if "messages" in result and result["messages"]:
            # Find the last AI message
            for message in reversed(result["messages"]):
                if message.get("role") == "assistant":
                    final_answer = message.get("content")
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
async def get_config():
    """Get current configuration information."""
    config = {
        "gemini_api_key_set": bool(os.getenv("GEMINI_API_KEY")),
        "graph_ready": graph is not None,
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
    return config


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
