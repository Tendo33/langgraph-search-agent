# 03｜项目架构走读：把源码和概念完全对上（详细版）

## 1. 核心流程图

当前图结构仍是：

`generate_query -> web_research -> reflection -> (web_research | finalize_answer)`

关键在两点：

- `generate_query` 后使用 `Send` 并发检索
- `reflection` 后使用条件边决定继续或结束

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/graph.py`

## 2. 状态契约统一

本版本把状态统一为 `AgentState`，不再使用分裂的 `OverallState/ReflectionState/...`。

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/state.py`

你可以按三类理解字段：

1. 输入上下文：`messages`
2. 过程累积：`search_query`、`web_research_result`、`sources_gathered`
3. 路由控制：`is_sufficient`、`follow_up_queries`、`research_loop_count`

## 3. 节点与路由职责

- `generate_query`：生成初始查询词
- `continue_to_web_research`：把查询词转成 `List[Send]`
- `web_research`：执行单条检索任务并返回摘要/来源
- `reflection`：判断信息是否充分并产出 follow-up
- `evaluate_research`：返回节点名或 `List[Send]`
- `finalize_answer`：生成最终答案并替换短链接

## 4. 配置链路

`Configuration.from_runnable_config` 已按优先级解析：

1. 请求级 `configurable`
2. 环境变量
3. 默认值

这让 API 与 CLI 都能在调用时显式覆盖模型和循环参数。

## 5. API 层调用

`/research` 会：

1. 组装 `AgentState`
2. 构建 `config={"configurable": ...}`
3. 调用 `graph_instance.ainvoke(...)`
4. 返回统一结构 `ok/data/error`

## 6. 你应重点观察的两个点

1. `Send` 并发后，为什么列表字段不会丢结果（看 reducer）。
2. 条件边为何既可返回字符串也可返回 `List[Send]`。
