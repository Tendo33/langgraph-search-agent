"""Utility functions for the LangGraph search agent."""

from __future__ import annotations

import re
from typing import Any, Dict, List, TypedDict
from urllib.parse import urlparse

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage


class WebSource(TypedDict):
    """Normalized web source item."""

    title: str
    url: str
    snippet: str


_URL_PATTERN = re.compile(r"https?://[^\s\]\)\"'>]+")


def get_research_topic(messages: List[AnyMessage]) -> str:
    """Get the research topic from the messages."""
    if len(messages) == 1:
        return str(messages[-1].content)

    research_topic = ""
    for message in messages:
        if isinstance(message, HumanMessage):
            research_topic += f"User: {message.content}\n"
        elif isinstance(message, AIMessage):
            research_topic += f"Assistant: {message.content}\n"
    return research_topic


def resolve_urls(
    urls_to_resolve: List[Any],
    id: int,
    prefix: str = "https://source.local/id/",
) -> Dict[str, str]:
    """Create a stable short-url map for URLs.

    Supports URL entries as raw strings, dict payloads, or objects carrying `web.uri`.
    """
    resolved_map: Dict[str, str] = {}

    for index, item in enumerate(urls_to_resolve):
        url = _extract_url(item)
        if not url or url in resolved_map:
            continue
        resolved_map[url] = f"{prefix}{id}-{index}"

    return resolved_map


def normalize_tavily_sources(search_payload: Any, max_items: int = 8) -> List[WebSource]:
    """Extract normalized source items from Tavily MCP payload."""
    flattened: List[Dict[str, str]] = []
    _walk_payload(search_payload, flattened)

    if not flattened:
        text = str(search_payload)
        for url in _URL_PATTERN.findall(text):
            flattened.append({"title": _domain_label(url), "url": url, "snippet": ""})

    dedup: Dict[str, WebSource] = {}
    for item in flattened:
        url = item.get("url", "").strip()
        if not url or not url.startswith(("http://", "https://")):
            continue
        if url in dedup:
            continue
        title = item.get("title", "").strip() or _domain_label(url)
        snippet = item.get("snippet", "").strip()
        dedup[url] = {"title": title, "url": url, "snippet": snippet}
        if len(dedup) >= max_items:
            break

    return list(dedup.values())


def _walk_payload(node: Any, output: List[Dict[str, str]]) -> None:
    if isinstance(node, list):
        for item in node:
            _walk_payload(item, output)
        return

    if not isinstance(node, dict):
        return

    url = _extract_url(node)
    if url:
        title = (
            str(node.get("title") or node.get("name") or node.get("source") or "")
        ).strip()
        snippet = (
            str(
                node.get("content")
                or node.get("snippet")
                or node.get("raw_content")
                or node.get("text")
                or ""
            )
        ).strip()
        output.append({"title": title, "url": url, "snippet": snippet})

    for value in node.values():
        if isinstance(value, (dict, list)):
            _walk_payload(value, output)


def _extract_url(item: Any) -> str:
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        for key in ("url", "link", "uri", "source_url", "value"):
            value = item.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
        return ""

    web = getattr(item, "web", None)
    if web is not None:
        uri = getattr(web, "uri", None)
        if isinstance(uri, str):
            return uri

    value = getattr(item, "value", None)
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value

    return ""


def _domain_label(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or "source"
