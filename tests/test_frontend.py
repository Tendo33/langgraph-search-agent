import pytest


gr = pytest.importorskip("gradio")

from frontend.gradio_app import _build_payload, _format_sources  # noqa: E402


def test_build_payload_matches_new_contract():
    payload = _build_payload("Q", max_loops=2, query_count=3)

    assert payload["question"] == "Q"
    assert payload["options"]["max_research_loops"] == 2
    assert payload["options"]["initial_search_query_count"] == 3


def test_format_sources_handles_empty():
    assert _format_sources([]) == "暂无来源信息"
