"""Async Tavily MCP client wrapper."""

from __future__ import annotations

from typing import Any, List

from langchain_core.tools import BaseTool

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:  # pragma: no cover - dependency checked at runtime
    MultiServerMCPClient = None


class AsyncTavilyMCPClient:
    """Async wrapper for Tavily MCP search tools."""

    def __init__(self, *, server_url: str):
        """Initialize Tavily MCP client.

        Args:
            server_url: Tavily MCP server URL.
        """
        if MultiServerMCPClient is None:
            raise RuntimeError("langchain-mcp-adapters is required")

        self._server_url = server_url
        self._client = MultiServerMCPClient(
            {
                "tavily": {
                    "transport": "streamable_http",
                    "url": self._server_url,
                }
            }
        )
        self._tools: List[BaseTool] | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the client and cleanup resources if supported."""
        close_method = getattr(self._client, "aclose", None)
        if callable(close_method):
            await close_method()
        self._tools = None

    async def get_tools(self) -> List[BaseTool]:
        """Load Tavily MCP tools lazily."""
        if self._tools is None:
            self._tools = await self._client.get_tools()
        return self._tools

    async def tavily_search(self, query: str, max_results: int = 5) -> Any:
        """Run Tavily search through MCP."""
        tool = await self._get_search_tool()
        try:
            return await tool.ainvoke({"query": query, "max_results": max_results})
        except Exception:
            return await tool.ainvoke({"query": query})

    async def _get_search_tool(self) -> BaseTool:
        tools = await self.get_tools()
        preferred_names = {"tavily_search", "tavily-search", "search"}

        for tool in tools:
            if tool.name in preferred_names:
                return tool

        for tool in tools:
            normalized = tool.name.replace("-", "_").lower()
            if "search" in normalized:
                return tool

        raise RuntimeError("No Tavily MCP search tool found")


# Global async client instance
_async_client: AsyncTavilyMCPClient | None = None
_async_client_signature: str | None = None


def get_async_client(*, server_url: str) -> AsyncTavilyMCPClient:
    """Get or create the global async Tavily MCP client instance."""
    global _async_client, _async_client_signature

    if _async_client is None or _async_client_signature != server_url:
        _async_client = AsyncTavilyMCPClient(server_url=server_url)
        _async_client_signature = server_url
    return _async_client


async def close_async_client():
    """Close the global async client instance."""
    global _async_client, _async_client_signature
    if _async_client is not None:
        await _async_client.close()
        _async_client = None
        _async_client_signature = None
