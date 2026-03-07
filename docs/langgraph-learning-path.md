# LangGraph 入门学习路径（结合本项目，详细版）

> 目标读者：第一次接触 LangGraph，知道 Python 基础，但不了解 Agent 工作流。

这套文档围绕当前改造后的项目实现，重点强调：统一状态契约、`Send` 并行、条件边路由、以及新 API 契约。

## 文档地图（按顺序阅读）

1. `docs/01-langgraph-core-concepts.md`
2. `docs/02-state-node-edge.md`
3. `docs/03-project-architecture-walkthrough.md`
4. `docs/04-minimal-graph-hands-on.md`
5. `docs/05-debugging-and-common-pitfalls.md`
6. `docs/06-practice-tasks.md`
7. `docs/07-glossary.md`
8. `docs/08-api-migration.md`
9. `docs/09-state-dictionary.md`

## 当前版本重点变化

- 全局状态统一为 `AgentState`
- `/research` 使用 `ok/data/error` 结构
- 请求参数集中在 `question + options`
- 配置优先级：请求 > 环境变量 > 默认值

## 推荐源码对照

- `D:/TuDou/langgraph-search-agent/src/search_agent/state.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/graph.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/app.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/configuration.py`
- `D:/TuDou/langgraph-search-agent/frontend/gradio_app.py`
