# 02｜State、Node、Edge：信息到底怎么传递（详细版）

这篇只回答一个核心问题：

> 一次 `/research` 请求进来后，数据如何在 LangGraph 里流动？

---

## 1. 入口：API 如何触发图

当前接口请求体：

```json
{
  "question": "...",
  "options": {
    "max_research_loops": 2,
    "initial_search_query_count": 3,
    "models": {
      "query_generator": "gemini-2.5-flash",
      "reflection": "gemini-2.5-flash",
      "answer": "gemini-2.5-pro"
    }
  }
}
```

在 `app.py` 中：

1. 构造 `initial_state: AgentState`
2. 构造 `configurable` 配置
3. 调用：

```python
result = await graph_instance.ainvoke(
    initial_state,
    config={"configurable": configurable},
)
```

关键点：现在是显式传入 `RunnableConfig`，不再隐式依赖默认值。

---

## 2. 节点返回值为什么是“增量”

节点通常返回类似：

```python
{"search_query": [...], "research_loop_count": 1}
```

不是返回完整状态。这样做的好处：

- 节点职责更单一
- 并发合并更清晰
- 少复制大对象

---

## 3. reducer 如何保证并发不丢结果

`AgentState` 中这些字段是累积字段：

- `search_query`
- `web_research_result`
- `sources_gathered`

它们都用了 `Annotated[List[...], operator.add]`。

含义：多个分支写入时自动拼接，而不是覆盖。

---

## 4. 条件边的返回值契约

`evaluate_research` 可能返回：

1. `"finalize_answer"`（单路径）
2. `List[Send(...)]`（并行路径）

这使条件边既能路由，也能扇出任务。

---

## 5. `Send` 的真实作用

`Send("web_research", payload)` 的含义是：

- 给 `web_research` 派发一条任务
- `payload` 就是该分支输入
- 多个 `Send` 即并发/多分支执行

本项目用于：

- 首轮多查询并发检索
- 反思后 follow-up 并发检索

---

## 6. 一次请求的状态演进

初始状态：

```text
messages=[HumanMessage], search_query=[], web_research_result=[], sources_gathered=[]
```

流程：

1. `generate_query` 生成查询词
2. 路由返回多个 `Send` 到 `web_research`
3. 多分支写入摘要与来源
4. reducer 自动合并累积字段
5. `reflection` 产出 `is_sufficient/follow_up_queries`
6. 条件边决定继续研究或进入 `finalize_answer`

---

## 7. 返回值速查卡

- 普通节点：返回 `dict`
- 路由函数：返回 `str` 或 `List[Send]`
- 并发累积字段：必须有 reducer
- 非累积控制字段：通常覆盖更新

---

## 8. 常见错误（新版）

1. 忘记传 `config={"configurable": ...}`，导致请求级模型不生效
2. `Send` payload 字段与目标节点输入不匹配
3. 把列表字段返回成标量，破坏 reducer 合并
4. 把旧 API 响应结构（`success/data`）当新版解析

---

## 9. 你现在可做的验证

- 打开 `src/search_agent/app.py` 看 `ainvoke` 调用
- 打开 `src/search_agent/graph.py` 看 `evaluate_research` 返回值
- 打开 `src/search_agent/state.py` 看 reducer 定义

只要这三处看懂，状态流就彻底通了。
