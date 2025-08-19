"""Gradio前端界面，用于调用LangGraph Research Agent API。"""

import json

import gradio as gr
import requests

API_URL = "http://localhost:8000/research"


def call_research_api(question, max_loops, query_count):
    """调用后端/research API，返回答案、循环信息和引用来源。"""
    payload = {
        "question": question,
        "max_research_loops": int(max_loops),
        "initial_search_query_count": int(query_count)
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                answer = data["data"].get("answer", "无结果")
                sources = data["data"].get("sources", [])
                loops = data["data"].get("research_loops", 0)
                return (
                    answer,
                    f"循环次数: {loops}",
                    json.dumps(sources, ensure_ascii=False, indent=2)
                )
            else:
                return (f"❌ 失败: {data.get('message')}", "-", "-")
        else:
            return (f"❌ HTTP错误: {response.status_code}", "-", "-")
    except Exception as e:
        return (f"❌ 请求异常: {str(e)}", "-", "-")

with gr.Blocks(theme=gr.themes.Soft(), title="LangGraph Research Agent UI") as demo:
    gr.Markdown("""
    # 🌐 LangGraph Research Agent
    <p style='color: #888;'>基于Gradio的智能研究助手前端</p>
    """)
    with gr.Row():
        with gr.Column(scale=2):
            question = gr.Textbox(label="研究问题 (支持中英文)", placeholder="请输入你的研究问题...", lines=3)
            max_loops = gr.Slider(1, 10, value=3, step=1, label="最大研究循环次数")
            query_count = gr.Slider(1, 10, value=3, step=1, label="初始搜索查询数")
            submit_btn = gr.Button("开始研究", variant="primary")
        with gr.Column(scale=3):
            answer = gr.Markdown(label="研究结果")
            loops = gr.Textbox(label="循环信息", interactive=False)
            sources = gr.Code(label="引用来源 (JSON)", language="json", interactive=False)
    submit_btn.click(
        call_research_api,
        inputs=[question, max_loops, query_count],
        outputs=[answer, loops, sources]
    )
    gr.Markdown("""
    ---
    <div style='text-align:right;font-size:12px;color:#aaa;'>Powered by Gradio & LangGraph</div>
    """)

def main():
    """Gradio应用入口。"""
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)

if __name__ == "__main__":
    main()
