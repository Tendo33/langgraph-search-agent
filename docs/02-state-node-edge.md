# 02｜State、Node、Edge：信息到底怎么传递（详细版）

这篇是最关键的一篇：你会真正看懂“图内部怎么传值”。

---

## 1. 执行从哪里开始

本项目在 API 层创建 `initial_state`，再执行：

```python
result = await graph_instance.ainvoke(initial_state)
```

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/app.py`

这表示：

- 图只吃一个输入：`state`
- 执行过程中不断更新它
- 最终返回新的完整状态

---

## 2. 节点函数签名与返回值

本项目节点一般长这样：

```python
async def some_node(state: SomeState, config: RunnableConfig) -> PartialState:
    ...
    return {"field_a": value_a, "field_b": value_b}
```

关键点：

- 输入是“当前状态快照”
- 返回是“增量更新字典”（只返回你想改的字段）

这就是为什么节点之间不需要手动传参。

---

## 3. 状态字段为什么要写 reducer

在并发场景里，多个分支可能同时写同一字段。

如果没有 reducer：

- 后写的分支可能覆盖先写的结果

如果有 reducer：

- LangGraph 按你指定规则合并

本项目字段定义示例：

- `search_query: Annotated[List[str], operator.add]`
- `web_research_result: Annotated[List[str], operator.add]`
- `sources_gathered: Annotated[List[SourceSegment], operator.add]`

含义：多个分支写入时，统一“列表拼接”。

---

## 4. 普通边 vs 条件边

## 4.1 普通边（固定流向）

```python
builder.add_edge("web_research", "reflection")
```

只要 `web_research` 结束，就一定到 `reflection`。

## 4.2 条件边（动态流向）

```python
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
```

由 `evaluate_research` 返回值决定去向。

---

## 5. 条件函数可以返回什么

这是很多新手最容易卡的地方。

在本项目里，条件函数可能返回两类值：

1. **字符串节点名**（单路径）
   - 例如：`"finalize_answer"`
2. **`List[Send]`**（并行多路径）
   - 例如：多个 `Send("web_research", {...})`

所以条件边既可以“做判断”，也可以“顺便并发扇出”。

---

## 6. `Send` 到底会做什么

当你返回 `Send("web_research", payload)`：

- LangGraph 会调度一次 `web_research`
- 这次调用拿到的输入来自 `payload`
- 多个 `Send` 表示多个分支并行（或可并行）执行

本项目两个地方使用 `Send`：

- 初始查询后的并发检索
- 反思后 follow-up 查询的并发检索

---

## 7. 一次请求的状态演进（简化示例）

初始：

```text
messages=[HumanMessage],
search_query=[],
web_research_result=[],
sources_gathered=[]
```

执行过程：

1. `generate_query` 返回 `{"search_query": [q1, q2, q3]}`
2. 路由返回 `Send x 3` 到 `web_research`
3. 三个分支分别返回各自摘要和来源
4. reducer 把三个分支的列表字段拼接
5. `reflection` 写入 `is_sufficient/follow_up_queries`
6. 条件边决定“结束”或“继续 Send”
7. `finalize_answer` 写入最终消息

---

## 8. 返回值速查卡（建议收藏）

- 普通节点：返回 `dict`（状态更新）
- 条件函数：返回 `str` 或 `List[Send]`
- 不要从普通节点直接返回 `Send`
- 不要让 reducer 字段返回非预期类型

---

## 9. 新手常见错法

1. 路由函数返回了不存在的节点名
2. 返回 `Send` 的 payload 字段和目标节点输入不匹配
3. 并行字段没配 reducer，结果丢失
4. 节点把列表字段返回成字符串，导致合并异常

---

## 10. 一个非常实用的检查动作

每个节点打印：

- 节点名
- 输入关键字段长度
- 输出字段名和长度

你会很快发现“哪一步状态没按预期更新”。
