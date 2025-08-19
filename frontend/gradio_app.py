"""Gradio前端界面，用于调用LangGraph Research Agent API."""

from typing import Tuple

import gradio as gr
import requests

API_URL = "http://localhost:8000/research"


def call_research_api(
    question: str, max_loops: int, query_count: int
) -> Tuple[str, str, str]:
    """调用后端/research API，返回答案、循环信息和引用来源."""
    if not question or not question.strip():
        return create_error_response("请输入研究问题")

    payload = {
        "question": question,
        "max_research_loops": int(max_loops),
        "initial_search_query_count": int(query_count),
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                answer = data["data"].get("answer", "无结果")
                sources = data["data"].get("sources", [])
                loops = data["data"].get("research_loops", 0)

                # 格式化答案，使其更加美观
                formatted_answer = format_answer(answer, sources)
                formatted_loops = format_loop_info(loops, query_count)
                formatted_sources = format_sources(sources)

                return formatted_answer, formatted_loops, formatted_sources
            else:
                error_msg = data.get("message", "未知错误")
                return create_error_response(f"研究失败: {error_msg}")
        else:
            return create_error_response(f"HTTP错误: {response.status_code}")
    except requests.Timeout:
        return create_error_response("请求超时，请稍后重试")
    except requests.ConnectionError:
        return create_error_response("无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        return create_error_response(f"请求异常: {str(e)}")


def create_loading_state():
    """创建加载状态显示."""
    loading_answer = """
## 🔍 正在进行研究...

<div class="loading-spinner"></div>

请稍候，AI助手正在为您深度研究相关问题...

- 🔄 分析问题关键词
- 🔍 生成搜索查询
- 🌐 执行网络搜索
- 📊 分析研究结果
- 📝 整合答案
"""

    loading_loops = """
### 📈 研究进度
- **状态**: 🔄 研究中...
- **预计时间**: 30-120秒
- **进度**: 0%
"""

    loading_sources = """
### 📚 信息来源
正在收集信息来源...
"""

    return loading_answer, loading_loops, loading_sources


def format_answer(answer: str, sources: list) -> str:
    """格式化答案，添加样式和引用."""
    if not answer or answer == "无结果":
        return "❌ 抱歉，没有找到相关的研究结果."

    # 添加标题和分隔线
    formatted = f"""
## 📊 研究结果

{answer}

---
*🔍 研究完成，共找到 {len(sources)} 个信息来源*
"""
    return formatted


def format_loop_info(loops: int, query_count: int) -> str:
    """格式化循环信息."""
    return f"""
### 📈 研究统计
- **实际循环次数**: {loops}
- **初始查询数量**: {query_count}
- **研究状态**: {"✅ 完成" if loops > 0 else "⚠️ 无结果"}
"""


def format_sources(sources: list) -> str:
    """格式化来源信息."""
    if not sources:
        return "暂无来源信息"

    formatted_sources = []
    for i, source in enumerate(sources, 1):
        title = source.get("title", f"来源 {i}")
        url = source.get("url", "#")
        formatted_sources.append(f"{i}. **{title}**\n   {url}")

    return f"""
### 📚 信息来源 ({len(sources)} 个)

{"\n\n".join(formatted_sources)}
"""


def create_error_response(error_msg: str) -> Tuple[str, str, str]:
    """创建错误响应."""
    error_display = f"""
## ❌ 研究失败

{error_msg}

请检查：
1. 后端服务是否正在运行
2. API密钥是否正确配置
3. 网络连接是否正常
"""
    return error_display, "❌ 研究失败", "错误信息: " + error_msg


# 自定义主题
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="cyan",
    neutral_hue="gray",
    font=["Source Sans Pro", "ui-sans-serif", "system-ui"],
    font_mono=["ui-monospace", "Consolas", "Liberation Mono"],
).set(
    body_background_fill="#f8fafc",
    body_background_fill_dark="#1a1a1a",
    button_primary_background_fill="#2563eb",
    button_primary_background_fill_hover="#1d4ed8",
    button_primary_text_color="white",
    button_secondary_background_fill="#f1f5f9",
    button_secondary_background_fill_hover="#e2e8f0",
    block_background_fill="#ffffff",
    block_background_fill_dark="#2d2d2d",
    block_border_color="#e5e7eb",
    block_border_color_dark="#404040",
    block_label_text_color="#374151",
    block_label_text_color_dark="#d1d5db",
    input_background_fill="#ffffff",
    input_background_fill_dark="#2d2d2d",
    input_border_color="#d1d5db",
    input_border_color_dark="#4b5563",
    input_text_color="#111827",
    input_text_color_dark="#f9fafb",
)

with gr.Blocks(
    theme=custom_theme,
    title="LangGraph Research Agent UI",
    css="""
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    .input-section {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    .result-section {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    """,
) as demo:
    # 主标题区域
    gr.HTML("""
    <div class="main-header">
        <h1>🌐 LangGraph Research Agent</h1>
        <p>基于AI的智能研究助手，为您提供深度网络研究</p>
    </div>
    """)

    with gr.Row():
        # 左侧输入区域
        with gr.Column(scale=1):
            gr.HTML("""
            <div class="input-section">
                <h3>🔍 研究设置</h3>
            </div>
            """)

            question = gr.Textbox(
                label="研究问题",
                placeholder="请输入您想了解的问题（支持中英文）...",
                lines=4,
                max_lines=6,
                info="请详细描述您想研究的问题，系统将为您进行深度搜索和分析",
            )

            with gr.Row():
                max_loops = gr.Slider(
                    1,
                    10,
                    value=3,
                    step=1,
                    label="最大研究循环次数",
                    info="控制研究的深度和广度",
                )

                query_count = gr.Slider(
                    1,
                    10,
                    value=3,
                    step=1,
                    label="初始搜索查询数",
                    info="同时进行的搜索查询数量",
                )

            with gr.Row():
                submit_btn = gr.Button("🚀 开始研究", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ 清空", variant="secondary")

            # 使用示例
            gr.Examples(
                examples=[
                    ["人工智能的最新发展趋势是什么？", 3, 3],
                    ["量子计算在医疗领域的应用前景", 4, 4],
                    ["气候变化对全球经济的影响", 2, 3],
                    ["What are the latest developments in renewable energy?", 3, 4],
                ],
                inputs=[question, max_loops, query_count],
                label="💡 示例问题",
            )

        # 右侧结果区域
        with gr.Column(scale=2):
            gr.HTML("""
            <div class="result-section">
                <h3>📊 研究结果</h3>
            </div>
            """)

            # 研究状态
            with gr.Accordion("📈 研究统计", open=True):
                loops = gr.Markdown(value="等待研究开始...", label="研究统计")

            # 主要研究结果
            with gr.Accordion("📝 详细答案", open=True):
                answer = gr.Markdown(
                    value="请在上方输入研究问题并点击开始研究", label="研究结果"
                )

            # 信息来源
            with gr.Accordion("📚 信息来源", open=False):
                sources = gr.Markdown(value="暂无来源信息", label="信息来源")

    # 事件处理
    submit_btn.click(fn=create_loading_state, outputs=[answer, loops, sources]).then(
        fn=call_research_api,
        inputs=[question, max_loops, query_count],
        outputs=[answer, loops, sources],
    )

    # 清空功能
    def clear_outputs():
        return "请在上方输入研究问题并点击开始研究", "等待研究开始...", "暂无来源信息"

    clear_btn.click(fn=clear_outputs, outputs=[answer, loops, sources])

    # 页脚
    gr.HTML("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8fafc; border-radius: 0.5rem; color: #6b7280;">
        <p>🤖 Powered by Gradio & LangGraph | 🚀 AI Research Assistant</p>
    </div>
    """)


def main():
    """Gradio应用入口."""
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False,
        favicon_path="🌐",
        quiet=False,
    )


if __name__ == "__main__":
    print("🚀 启动 LangGraph Research Agent UI...")
    print("📍 访问地址: http://localhost:7860")
    print("🔧 确保后端服务运行在: http://localhost:8000")
    main()
