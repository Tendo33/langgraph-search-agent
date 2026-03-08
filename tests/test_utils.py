from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

from search_agent.utils import (
    get_research_topic,
    normalize_tavily_sources,
    resolve_urls,
)


def test_get_research_topic_single_message():
    topic = get_research_topic([HumanMessage(content="What is LangGraph?")])
    assert topic == "What is LangGraph?"


def test_get_research_topic_multi_message():
    topic = get_research_topic(
        [
            HumanMessage(content="Q1"),
            AIMessage(content="A1"),
            HumanMessage(content="Q2"),
        ]
    )
    assert "User: Q1" in topic
    assert "Assistant: A1" in topic


def test_resolve_urls_deduplicates_and_uses_id_prefix():
    urls = [
        SimpleNamespace(web=SimpleNamespace(uri="https://a.com")),
        SimpleNamespace(web=SimpleNamespace(uri="https://a.com")),
        SimpleNamespace(web=SimpleNamespace(uri="https://b.com")),
    ]

    resolved = resolve_urls(urls, id=7)

    assert len(resolved) == 2
    assert resolved["https://a.com"].endswith("7-0")
    assert resolved["https://b.com"].endswith("7-2")


def test_normalize_tavily_sources_extracts_results():
    payload = {
        "query": "langgraph",
        "results": [
            {
                "title": "LangGraph Docs",
                "url": "https://langchain-ai.github.io/langgraph/",
                "content": "LangGraph is a library for building stateful agents.",
            }
        ],
    }

    sources = normalize_tavily_sources(payload)

    assert len(sources) == 1
    assert sources[0]["title"] == "LangGraph Docs"
    assert sources[0]["url"] == "https://langchain-ai.github.io/langgraph/"
