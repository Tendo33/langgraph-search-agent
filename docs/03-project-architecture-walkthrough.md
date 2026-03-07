# 03｜项目架构走读：把源码和概念完全对上（详细版）

这篇目标：你可以把“LangGraph 概念”一一映射到项目代码。

---

## 1. 项目核心执行链

本项目逻辑链：

`generate_query -> web_research -> reflection -> (web_research | finalize_answer)`

图定义文件：`D:/TuDou/langgraph-search-agent/src/search_agent/graph.py`

你可以把它看成“研究循环”：

- 先搜
- 再反思
- 不够就继续
- 够了就收敛

---

## 2. 图是如何被构建的

核心代码：

```python
builder = StateGraph(OverallState, config_schema=Configuration)
builder.add_node(...)
builder.add_edge(...)
builder.add_conditional_edges(...)
graph = builder.compile(name="pro-search-agent")
```

拆解：

1. `StateGraph(...)`：定义状态与配置约束
2. `add_node`：注册步骤
3. `add_edge`：固定连线
4. `add_conditional_edges`：路由与循环
5. `compile`：生成可执行图对象

---

## 3. 逐节点解剖（输入/输出/作用）

## 3.1 `generate_query`

- 输入：`messages`（用户问题）
- 输出：`search_query`（查询列表）
- 关键点：结构化输出 `SearchQueryList`

## 3.2 `continue_to_web_research`

- 输入：`search_query`
- 输出：`List[Send]`
- 关键点：把多查询扇出为多个检索任务

## 3.3 `web_research`

- 输入：单个查询和 `id`
- 输出：`sources_gathered`、`search_query`、`web_research_result`
- 关键点：调用 Google Search + 生成带引用摘要

## 3.4 `reflection`

- 输入：当前累计检索结果
- 输出：`is_sufficient`、`knowledge_gap`、`follow_up_queries`
- 关键点：这是是否继续循环的判断源头

## 3.5 `evaluate_research`

- 输入：反思结果 + 循环计数
- 输出：`"finalize_answer"` 或 `List[Send]`
- 关键点：条件边路由中枢

## 3.6 `finalize_answer`

- 输入：所有摘要与来源
- 输出：最终 `messages` + 去重后的来源
- 关键点：短链接替换回真实 URL

---

## 4. 状态模型为何这样设计

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/state.py`

你可以把它分三类字段：

1. **输入上下文**：`messages`
2. **过程累积**：`search_query`、`web_research_result`、`sources_gathered`
3. **流程控制**：`research_loop_count`、`max_research_loops`

其中“过程累积”字段都需要 reducer，才能安全接收并行结果。

---

## 5. 配置层如何影响图行为

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/configuration.py`

配置影响：

- 用哪个模型生成 query
- 反思阶段用哪个模型
- 最终答案用哪个模型
- 初始查询数量
- 最大循环次数

读取来源：

- `RunnableConfig.configurable`
- 环境变量覆盖

---

## 6. API 层如何触发图

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/app.py`

`/research` 的调用路径：

1. 创建 `initial_state`
2. `await graph_instance.ainvoke(initial_state)`
3. 从 `messages` 中提取最后一个 AI 输出
4. 返回 `answer/sources/research_loops/full_result`

这说明 API 层不做“研究决策”，只负责 I/O 包装。

---

## 7. 引用系统（值得重点学习）

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/utils.py`

链路：

1. `resolve_urls`：把超长 URL 映射为短 id 链接
2. `get_citations`：从 grounding metadata 提取证据片段
3. `insert_citation_markers`：把引用标记插入段落
4. `finalize_answer`：把短链接替回原链接

这是“先压缩，再还原”的 token 优化思路。

---

## 8. 你现在应该能自己回答

1. 为什么要 `add_conditional_edges`？
   - 因为流程不是固定直线，需要根据状态动态决定继续或结束。
2. 为什么要 `Send`？
   - 因为同一节点要并发处理多条查询。
3. 为什么要 reducer？
   - 因为并发分支都在写同一状态字段，需要明确合并规则。
