from search_agent.configuration import Configuration


def test_config_priority_request_over_env(monkeypatch):
    monkeypatch.setenv("QUERY_GENERATOR_MODEL", "env-model")

    config = Configuration.from_runnable_config(
        {
            "configurable": {
                "query_generator_model": "request-model",
            }
        }
    )

    assert config.query_generator_model == "request-model"


def test_config_falls_back_to_env(monkeypatch):
    monkeypatch.setenv("MAX_RESEARCH_LOOPS", "5")

    config = Configuration.from_runnable_config({"configurable": {}})

    assert config.max_research_loops == 5


def test_config_falls_back_to_defaults(monkeypatch):
    monkeypatch.delenv("ANSWER_MODEL", raising=False)

    config = Configuration.from_runnable_config(None)

    assert config.answer_model == "gemini-2.5-pro"
