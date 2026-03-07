# 01｜LangGraph 核心概念（初学者详细版）

这篇文档的目标：

- 不假设你有 LangGraph 经验
- 读完能准确解释核心术语
- 能把术语映射到本项目最新代码

---

## 1. LangGraph 解决的本质问题

Agent 常见任务不是一步完成，而是：

1. 拆问题
2. 执行检索
3. 反思是否足够
4. 不够就继续
5. 最后汇总回答

这类任务的难点是：

- **状态如何共享**（中间结果放哪）
- **流程如何决策**（何时循环/结束）
- **并发如何合并**（多分支结果不丢）

LangGraph 本质上是“状态驱动的流程编排器”。

---

## 2. 六个必须掌握的对象

## 2.1 `State`

`State` 是图的共享内存。本项目已统一为 `AgentState`：

- 文件：`src/search_agent/state.py`
- 关键字段：`messages`、`search_query`、`web_research_result`、`sources_gathered`
- 路由字段：`is_sufficient`、`follow_up_queries`、`research_loop_count`

理解方式：它像“全过程公共黑板”。

## 2.2 `Node`

`Node` 是一个步骤函数：

- 读 `state`
- 做一件事
- 返回“增量状态更新”

本项目节点：`generate_query`、`web_research`、`reflection`、`finalize_answer`。

## 2.3 `Edge`

固定连线，执行完 A 总是去 B。示例：`web_research -> reflection`。

## 2.4 `Conditional Edge`

动态连线，下一步由函数返回值决定。示例：`reflection` 后走 `evaluate_research`。

## 2.5 `Send`

扇出任务对象，用于并行调度同一节点：

```python
Send("web_research", {"search_query": "...", "id": 0})
```

多个 `Send` = 多分支并行执行。

## 2.6 `Reducer`

并发分支回流时的字段合并规则。本项目常用：

- `operator.add`：列表拼接
- `add_messages`：消息合并

没有 reducer，分支结果容易覆盖丢失。

---

## 3. 本项目里最关键的组合

### `Conditional Edge + Send`

这是“边判断边并发”的核心模式：

1. 条件边先判断是否继续研究
2. 若继续，返回 `List[Send]` 扇出 follow-up 查询

这就是本项目多轮研究的关键机制。

---

## 4. 新版工程化补充（改造后）

除了图结构，你还要知道两个现实工程点：

1. **统一状态契约**：由 `AgentState` 统一所有节点读写字段
2. **请求级配置透传**：API 调 `graph.ainvoke(..., config={"configurable": ...})`

这两点让流程更稳定、可维护、可调参。

---

## 5. 一句话心智模型

LangGraph = `State` + `Node` + `Routing` + `Reducer`。

你能解释这四个组件如何配合，就算真正入门。

---

## 6. 下一篇建议

请继续看 `docs/02-state-node-edge.md`，那里会讲“状态到底如何在图中传递 + 新接口如何触发图执行”。
