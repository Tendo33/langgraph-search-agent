from types import SimpleNamespace

from fastapi.testclient import TestClient

import search_agent.app as app_module


class FakeGraph:
    async def ainvoke(self, initial_state, config=None):
        assert "configurable" in config
        return {
            "messages": [SimpleNamespace(content="final answer")],
            "sources_gathered": [
                {"label": "source-a", "short_url": "s1", "value": "https://a.com"}
            ],
            "research_loop_count": 2,
            "search_query": ["q1", "q2"],
            "web_research_result": ["r1", "r2"],
            "is_sufficient": True,
            "knowledge_gap": "",
            "number_of_ran_queries": 2,
        }


class ErrorGraph:
    async def ainvoke(self, initial_state, config=None):
        raise RuntimeError("OPENAI_API_KEY is not set")


def test_research_success(monkeypatch):
    monkeypatch.setattr(app_module, "graph_instance", FakeGraph())
    client = TestClient(app_module.app)

    response = client.post(
        "/research",
        json={
            "question": "What is LangGraph?",
            "options": {
                "max_research_loops": 2,
                "initial_search_query_count": 2,
                "return_debug": True,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["answer"] == "final answer"
    assert data["data"]["meta"]["queries_ran"] == 2


def test_research_error_when_missing_key(monkeypatch):
    monkeypatch.setattr(app_module, "graph_instance", ErrorGraph())
    client = TestClient(app_module.app)

    response = client.post(
        "/research",
        json={
            "question": "Q",
            "options": {},
        },
    )

    assert response.status_code == 503
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "missing_api_key"


def test_research_validation_error_shape(monkeypatch):
    monkeypatch.setattr(app_module, "graph_instance", FakeGraph())
    client = TestClient(app_module.app)

    response = client.post("/research", json={"options": {}})

    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "validation_error"


def test_research_unavailable(monkeypatch):
    monkeypatch.setattr(app_module, "graph_instance", None)
    client = TestClient(app_module.app)

    response = client.post(
        "/research",
        json={"question": "Q", "options": {}},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "graph_unavailable"
