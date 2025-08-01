#!/usr/bin/env python3
"""Simple script to run the FastAPI server."""

import uvicorn

from src.search_agent.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
    )
