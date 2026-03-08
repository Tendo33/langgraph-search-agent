# LangGraph Search Agent（项目详细文档）

基于 **LangGraph + Gemini + Google Search grounding** 的研究型 Agent API 服务。

该项目将“问题拆解 -> 检索 -> 反思补查 -> 最终回答”组织成可循环的图工作流，并通过 FastAPI 暴露统一 API。

## 1. 功能概览

- 多轮研究流程：`generate_query -> web_research -> reflection -> (loop | finalize_answer)`
- 并行检索：通过 `Send` 将多个查询并发扇出到 `web_research`
- 反思补查：自动判断信息是否充分，不充分时生成 follow-up 查询继续研究
- 引用处理：从 grounding 元数据中提取来源并映射到最终回答
- 统一 API 响应：`ok / data / error` 结构，便于前端与脚本统一处理
- 请求级参数覆盖：支持模型、初始查询数、最大循环数按请求动态覆盖

## 2. 技术栈

- Python `>=3.11,<4.0`
- LangGraph / LangChain
- Google Gemini（`langchain-google-genai` + `google-genai`）
- FastAPI + Uvicorn
- Gradio（可选前端）
- Ruff + Pytest

## 3. 目录结构

```text
src/search_agent/
  app.py                 # FastAPI 接口、请求/响应模型、错误处理
  graph.py               # LangGraph 工作流节点与路由
  state.py               # AgentState / WebSearchTask 定义
  configuration.py       # 配置模型与优先级解析
  prompts.py             # 各阶段 Prompt 模板
  tools_and_schemas.py   # 结构化输出 Schema
  utils.py               # 引用提取、短链映射、标记插入
  async_client.py        # Google 异步客户端封装

examples/
  api_example.py         # 同步 API 调用示例
  async_api_example.py   # 异步 API 调用示例
  cli_research.py        # 直接调用 graph 的 CLI 示例
  performance_test.py    # 性能测试脚本
  min_graph_demo.py      # 最小图示例

frontend/
  gradio_app.py          # Gradio 界面

docs/
  langgraph-learning-path.md
  01-09 系列学习文档      # LangGraph 与本项目实现解读
```

## 4. 环境准备

### 4.1 安装依赖

```bash
pip install -e .
```

开发依赖（可选）：

```bash
pip install -e .[dev]
```

### 4.2 配置环境变量

项目根目录可使用 `.env`（已集成 `python-dotenv`）。

必需：

```env
GEMINI_API_KEY=your_key_here
```

可选（当前主要用于配置可见性展示，未来扩展检索实现时可直接复用）：

```env
GOOGLE_SEARCH_API_KEY=your_key_here
```

## 5. 快速启动

### 5.1 启动 API 服务

```bash
python run_server.py
```

默认地址：

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5.2 验证服务状态

```bash
curl http://localhost:8000/health
```

### 5.3 运行示例脚本

```bash
python examples/api_example.py
python examples/async_api_example.py
python examples/cli_research.py "What is LangGraph?"
python frontend/gradio_app.py
```

## 6. API 文档（当前契约）

### 6.1 `GET /health`

用于健康检查。

返回示例：

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "graph_ready": true,
  "gemini_api_key_set": true
}
```

### 6.2 `GET /config`

返回当前运行上下文、默认配置和 key 可用性。

返回示例：

```json
{
  "ok": true,
  "data": {
    "graph_ready": true,
    "environment": "development",
    "api_keys": {
      "gemini": true,
      "google_search": false
    },
    "defaults": {
      "query_generator_model": "gemini-2.5-flash",
      "reflection_model": "gemini-2.5-flash",
      "answer_model": "gemini-2.5-pro",
      "number_of_initial_queries": 3,
      "max_research_loops": 2
    }
  }
}
```

### 6.3 `POST /research`

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
      {
        "title": "Source 1",
        "url": "https://example.com"
      }
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
    "details": "GEMINI_API_KEY is not set"
  }
}
```

常见错误码：

- `validation_error`：请求体校验失败（HTTP 422）
- `graph_unavailable`：图未正常初始化（HTTP 503）
- `missing_api_key`：缺少 `GEMINI_API_KEY`（HTTP 503）
- `runtime_error` / `internal_error`：执行异常（HTTP 500）

## 7. 配置说明

配置来源优先级（高 -> 低）：

1. `POST /research` 的 `options`（通过 `RunnableConfig.configurable` 注入）
2. 环境变量（如 `QUERY_GENERATOR_MODEL`）
3. `Configuration` 默认值

对应配置项：

- `query_generator_model`（默认：`gemini-2.5-flash`）
- `reflection_model`（默认：`gemini-2.5-flash`）
- `answer_model`（默认：`gemini-2.5-pro`）
- `number_of_initial_queries`（默认：`3`）
- `max_research_loops`（默认：`2`）

请求体与配置映射关系：

- `options.initial_search_query_count` -> `number_of_initial_queries`
- `options.max_research_loops` -> `max_research_loops`
- `options.models.query_generator` -> `query_generator_model`
- `options.models.reflection` -> `reflection_model`
- `options.models.answer` -> `answer_model`

## 8. 工作流执行机制

图节点（`src/search_agent/graph.py`）：

1. `generate_query`
2. `web_research`（并发执行）
3. `reflection`
4. `evaluate_research`（路由判定）
5. `finalize_answer`

状态核心字段（`src/search_agent/state.py`）：

- `messages`：消息历史
- `search_query`：累计查询词
- `web_research_result`：累计检索摘要
- `sources_gathered`：累计来源片段
- `research_loop_count`：已执行循环次数
- `is_sufficient` / `follow_up_queries`：反思与路由依据

路由逻辑：

- `is_sufficient == true` 或达到 `max_research_loops` -> `finalize_answer`
- 否则进入下一轮 `web_research`

## 9. 前端使用（Gradio）

启动：

```bash
python frontend/gradio_app.py
```

默认地址：`http://localhost:7860`

前端调用后端固定地址：`http://localhost:8000/research`。
请先启动后端再启动前端。

## 10. 测试与质量检查

运行测试：

```bash
pytest -q
```

静态检查：

```bash
ruff check .
```

格式化：

```bash
ruff format .
```

当前测试覆盖重点：

- API 契约与错误结构
- 配置优先级（请求 > 环境 > 默认）
- 图路由行为（是否继续研究）
- 工具函数（引用插入等）

## 11. 常见问题（FAQ）

### Q1：`/research` 返回 `missing_api_key`

确认环境变量已生效：

```bash
# PowerShell
$env:GEMINI_API_KEY="your_key"
python run_server.py
```

或写入 `.env` 后重启服务。

### Q2：前端显示无法连接后端

确认后端是否运行在 `http://localhost:8000`，并检查端口占用。

### Q3：想减少延迟，应该调什么？

优先降低以下参数：

- `options.max_research_loops`
- `options.initial_search_query_count`
- `options.models.answer`（可换为更快模型）

### Q4：如何查看内部调试状态？

在请求里设置 `options.return_debug=true`，响应中的 `data.debug` 会返回关键状态快照。

## 12. 扩展建议

- 在 `prompts.py` 细化不同领域的提示模板
- 在 `graph.py` 增加专门的来源去重/可信度过滤节点
- 在 `app.py` 增加鉴权、限流与 tracing
- 为 `examples/performance_test.py` 输出结构化基准报告

## 13. 相关文档入口

- 学习路径：`docs/langgraph-learning-path.md`
- API 迁移：`docs/08-api-migration.md`
- 状态字典：`docs/09-state-dictionary.md`

## License

MIT

