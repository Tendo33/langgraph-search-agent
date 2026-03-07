#!/usr/bin/env python3
"""Simple script to run the FastAPI server."""

import uvicorn

from search_agent.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        workers=1,
        http="httptools",
        limit_concurrency=100,
        timeout_keep_alive=30,
    )
