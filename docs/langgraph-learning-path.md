# LangGraph 入门学习路径（结合本项目，详细版）

> 目标读者：第一次接触 LangGraph，知道 Python 基础，但不了解 Agent 工作流。

这套文档专门围绕你的项目 `langgraph-search-agent` 设计，不讲空泛概念，尽量做到“看完就能改代码”。

## 你最终会掌握

- 能解释清楚：`State`、`Node`、`Edge`、`Conditional Edge`、`Send`、`Reducer`
- 能看懂本项目图结构如何循环和并发
- 能从 `/research` 请求一路追踪到最终答案
- 能自己写一个最小 LangGraph，并加上条件路由
- 能定位 80% 新手常见问题（状态覆盖、循环不退出、并发不合并）

## 文档地图（按顺序阅读）

1. `docs/01-langgraph-core-concepts.md`
   - 讲清 LangGraph 的核心对象和它们为什么存在
2. `docs/02-state-node-edge.md`
   - 讲清“信息传递机制”：状态如何写入、合并、回流
3. `docs/03-project-architecture-walkthrough.md`
   - 对照你项目源码做完整走读
4. `docs/04-minimal-graph-hands-on.md`
   - 从零写最小图，再升级到 `Send + 条件边`
5. `docs/05-debugging-and-common-pitfalls.md`
   - 系统化排错与日志方法
6. `docs/06-practice-tasks.md`
   - 递进练习，从“会跑”到“会设计”
7. `docs/07-glossary.md`
   - 术语速查表（复习时非常好用）

## 建议学习节奏（4 天）

- 第 1 天：文档 1 + 2
- 第 2 天：文档 3
- 第 3 天：文档 4 + 跑 demo
- 第 4 天：文档 5 + 6 + 术语复盘

## 上手前准备

1. 安装依赖：`pip install -e .`
2. 准备环境变量：`.env` 里至少有 `GEMINI_API_KEY`
3. 启动服务：`python run_server.py`
4. 打开文档页：`http://localhost:8000/docs`

## 推荐“边学边看”的源码文件

- `D:/TuDou/langgraph-search-agent/src/search_agent/graph.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/state.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/configuration.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/app.py`
- `D:/TuDou/langgraph-search-agent/src/search_agent/utils.py`

## 快速提醒（避免你一开始踩坑）

- 节点之间不是直接传参，而是通过共享 `state`
- 节点返回的是“增量更新”，不是完整状态
- 并行后结果能不能保留，关键看 reducer 定义
- 条件边可以返回“节点名”或 `Send` 列表

读到这里就可以进入 `01` 了。
