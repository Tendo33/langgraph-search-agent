# LangGraph Search Agent（全面改进版）

基于 LangGraph 的研究型 Agent API，使用 Gemini + Google Search 实现多轮检索、反思和带来源答案生成。

## 主要能力

- 多阶段研究流程：`generate_query -> web_research -> reflection -> finalize_answer`
- 并行检索：通过 `Send` 扇出多个搜索任务
- 条件循环：根据反思结果决定继续研究或结束
- 结构化 API：统一成功/失败响应
- 可配置模型与循环参数：支持请求级配置（`RunnableConfig`）

## 环境要求

- Python `>=3.11`
- `GEMINI_API_KEY`（必需）
- `GOOGLE_SEARCH_API_KEY`（建议提供，视工具策略而定）

## 快速开始

```bash
pip install -e .
python run_server.py
```

服务默认地址：`http://localhost:8000`

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 新版 API 契约（已替换旧结构）

### `POST /research`

请求体：

```json
{
  "question": "请解释 LangGraph 的核心概念",
  "options": {
    "max_research_loops": 2,
    "initial_search_query_count": 3,
    "models": {
      "query_generator": "gemini-2.5-flash",
      "reflection": "gemini-2.5-flash",
      "answer": "gemini-2.5-pro"
    },
    "return_debug": false
  }
}
```

成功响应：

```json
{
  "ok": true,
  "data": {
    "answer": "...",
    "sources": [
      {"title": "Example", "url": "https://example.com"}
    ],
    "meta": {
      "research_loop_count": 2,
      "queries_ran": 4,
      "duration_ms": 1820
    },
    "debug": null
  },
  "error": null
}
```

失败响应：

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "missing_api_key",
    "message": "GEMINI_API_KEY is required",
    "details": "..."
  }
}
```

### `GET /health`

返回服务状态、图是否可用、API Key 是否存在。

### `GET /config`

返回默认配置、运行环境与 key 可用性。

## 配置优先级

当前配置解析顺序：

1. 请求 `options`（通过 `RunnableConfig.configurable` 传入）
2. 环境变量
3. 代码默认值（`Configuration`）

## 项目结构

```text
src/search_agent/
  app.py                 # FastAPI 接口与请求/响应模型
  graph.py               # LangGraph 工作流定义
  state.py               # 统一 AgentState 契约
  configuration.py       # 配置解析（请求 > 环境 > 默认）
  tools_and_schemas.py   # 结构化输出模型
  utils.py               # 引用提取与文本插入
frontend/
  gradio_app.py          # Gradio 前端
examples/
  api_example.py         # API 调用示例（新契约）
  async_api_example.py   # 异步调用示例（新契约）
  cli_research.py        # CLI 调用图示例
  min_graph_demo.py      # LangGraph 最小教学示例
```

## 运行示例

```bash
python examples/api_example.py
python examples/async_api_example.py
python examples/cli_research.py "What is LangGraph?"
python frontend/gradio_app.py
```

## 测试与检查

```bash
pytest -q
ruff check .
```

> 当前测试设计以 Mock 为主，不依赖真实外网调用。

## 学习文档

阅读入口：`docs/langgraph-learning-path.md`

新增文档：

- `docs/08-api-migration.md`
- `docs/09-state-dictionary.md`

## 许可证

MIT
