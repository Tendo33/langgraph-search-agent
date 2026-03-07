# 06｜练习任务：从“能跑”到“会设计”

本练习完全基于当前新版契约（`ok/data/error`、`AgentState`、请求级 `options`）。

## 任务 1：读图不迷路

目标：看懂主流程和节点职责。

步骤：

1. 打开 `src/search_agent/graph.py`
2. 找到 `add_node`、`add_edge`、`add_conditional_edges`
3. 画出流程图并标出路由函数

验收：能解释为什么 `generate_query` 后是 `Send` 并行，`reflection` 后是条件路由。

## 任务 2：观察状态流

目标：理解 `AgentState` 的生命周期。

步骤：

1. 在节点中打印关键字段长度
2. 调用 `/research`
3. 追踪 `search_query`、`web_research_result`、`sources_gathered`

验收：能区分累积字段、控制字段、配置字段。

## 任务 3：操控循环与配置

目标：验证请求级配置生效。

步骤：

1. 用同一问题分别传 `options.max_research_loops=1/2/3`
2. 比较 `data.meta.research_loop_count`
3. 额外切换 `options.models.answer`

验收：能解释“请求参数如何覆盖默认值”。

## 任务 4：写最小图

目标：独立写出带条件路由的最小 LangGraph。

步骤：

1. 跟 `docs/04-minimal-graph-hands-on.md` 完成 demo
2. 把 `reflect` 改为至少循环两轮

验收：能同时演示路由返回节点名与 `List[Send]` 两种模式。

## 任务 5：扩展项目节点

目标：在不破坏主流程前提下扩展图。

建议方向：

- 在 `finalize_answer` 前增加质量检查节点

验收：

- 服务可正常返回
- 新节点被触发
- API 输出仍符合 `ok/data/error`

## 任务 6：并发与 reducer

目标：彻底掌握并发回流。

步骤：

1. 在最小 demo 扇出 3 个 `Send`
2. 每个分支返回不同 note
3. 验证最终列表是否完整保留

验收：能解释 reducer 缺失时为何发生覆盖。

## 自测题

1. 条件边何时返回字符串，何时返回 `List[Send]`？
2. 为什么节点只返回增量状态就够了？
3. 请求级配置是如何传到节点模型选择逻辑中的？
4. 为什么新版 API 用 `ok/data/error` 比旧格式更利于调试？
