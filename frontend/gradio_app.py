"""Gradio front-end for LangGraph Research Agent API."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import gradio as gr
import requests

API_URL = "http://localhost:8000/research"


def _format_sources(sources: List[Dict[str, Any]]) -> str:
    if not sources:
        return "暂无来源信息"

    lines = []
    for index, source in enumerate(sources, start=1):
        title = source.get("title", f"来源 {index}")
        url = source.get("url", "")
        lines.append(f"{index}. **{title}**\n   {url}")
    return "\n\n".join(lines)


def _build_payload(question: str, max_loops: int, query_count: int) -> Dict[str, Any]:
    return {
        "question": question,
        "options": {
            "max_research_loops": int(max_loops),
            "initial_search_query_count": int(query_count),
            "return_debug": False,
        },
    }


def _error_view(message: str) -> Tuple[str, str, str]:
    return (
        f"## ❌ 请求失败\n\n{message}",
        "状态：失败",
        "暂无来源信息",
    )


def call_research_api(
    question: str,
    max_loops: int,
    query_count: int,
) -> Tuple[str, str, str]:
    """Call backend `/research` endpoint and return formatted content."""
    if not question.strip():
        return _error_view("请输入研究问题。")

    payload = _build_payload(question=question.strip(), max_loops=max_loops, query_count=query_count)

    try:
        response = requests.post(API_URL, json=payload, timeout=240)
    except requests.Timeout:
        return _error_view("请求超时，请稍后重试。")
    except requests.ConnectionError:
        return _error_view("无法连接后端服务，请确认 http://localhost:8000 已启动。")
    except Exception as exc:  # pragma: no cover
        return _error_view(f"请求异常: {exc}")

    try:
        result = response.json()
    except ValueError:
        return _error_view(f"后端返回非 JSON 内容，HTTP {response.status_code}")

    if response.status_code != 200 or not result.get("ok"):
        error = result.get("error", {})
        message = error.get("message", "未知错误")
        details = error.get("details")
        if details:
            return _error_view(f"{message}\n\n详情: {details}")
        return _error_view(message)

    data = result["data"]
    answer = data.get("answer", "")
    sources = data.get("sources", [])
    meta = data.get("meta", {})

    answer_markdown = f"## 📘 研究结果\n\n{answer}"
    meta_markdown = (
        "### 📊 运行信息\n"
        f"- 循环次数: {meta.get('research_loop_count', 0)}\n"
        f"- 执行查询数: {meta.get('queries_ran', 0)}\n"
        f"- 耗时: {meta.get('duration_ms', 0)} ms"
    )
    source_markdown = f"### 🔗 信息来源\n\n{_format_sources(sources)}"

    return answer_markdown, meta_markdown, source_markdown


def create_loading_state() -> Tuple[str, str, str]:
    """Return loading placeholders while request is in progress."""
    return (
        "## ⏳ 正在研究中\n\n请稍候，系统正在执行检索与总结。",
        "### 📊 运行信息\n- 状态: 处理中",
        "### 🔗 信息来源\n\n正在收集来源...",
    )


def clear_outputs() -> Tuple[str, str, str]:
    """Reset output panels."""
    return (
        "请输入问题后点击“开始研究”。",
        "等待执行",
        "暂无来源信息",
    )


with gr.Blocks(title="LangGraph Research Agent") as demo:
    gr.Markdown(
        """
# 🌐 LangGraph Research Agent
输入问题后，系统会自动执行多轮检索并返回带来源的答案。
"""
    )

    with gr.Row():
        with gr.Column(scale=1):
            question = gr.Textbox(
                label="研究问题",
                placeholder="例如：RAG 在 2026 年有哪些新趋势？",
                lines=4,
            )
            max_loops = gr.Slider(1, 8, value=2, step=1, label="最大研究轮数")
            query_count = gr.Slider(1, 8, value=3, step=1, label="初始查询数量")

            with gr.Row():
                submit_btn = gr.Button("开始研究", variant="primary")
                clear_btn = gr.Button("清空")

            gr.Examples(
                examples=[
                    ["LangGraph 的核心概念是什么？", 2, 3],
                    ["2026 年多模态大模型应用进展", 3, 3],
                    ["What are recent advances in AI agents?", 2, 2],
                ],
                inputs=[question, max_loops, query_count],
            )

        with gr.Column(scale=2):
            answer = gr.Markdown("请输入问题后点击“开始研究”。")
            meta = gr.Markdown("等待执行")
            sources = gr.Markdown("暂无来源信息")

    submit_btn.click(fn=create_loading_state, outputs=[answer, meta, sources]).then(
        fn=call_research_api,
        inputs=[question, max_loops, query_count],
        outputs=[answer, meta, sources],
    )
    clear_btn.click(fn=clear_outputs, outputs=[answer, meta, sources])


def main() -> None:
    """Gradio app entrypoint."""
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)


if __name__ == "__main__":
    main()
