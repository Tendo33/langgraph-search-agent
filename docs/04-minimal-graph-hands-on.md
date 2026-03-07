# 04｜动手实战：从最小图到 `Send + 条件边`

这一篇你会亲手写两个 demo：

1. 单路径 + 条件路由
2. 并行 `Send` + 状态合并

建议你先只跑本地逻辑，不依赖外部 API。

---

## 1. 创建练习文件

新建：`D:/TuDou/langgraph-search-agent/examples/min_graph_demo.py`

下面给出完整代码（可直接运行）。

```python
from __future__ import annotations

import operator
from typing import Annotated, List, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class DemoState(TypedDict):
    question: str
    queries: Annotated[List[str], operator.add]
    notes: Annotated[List[str], operator.add]
    is_enough: bool
    loop_count: int


def generate_queries(state: DemoState) -> DemoState:
    q1 = f"{state['question']} definition"
    q2 = f"{state['question']} example"
    return {"queries": [q1, q2]}


def dispatch_queries(state: DemoState) -> List[Send]:
    return [
        Send("search", {"queries": [query], "notes": [], "loop_count": state.get("loop_count", 0)})
        for query in state["queries"]
    ]


def search(state: DemoState) -> DemoState:
    current_query = state["queries"][-1]
    return {"notes": [f"result for: {current_query}"]}


def reflect(state: DemoState) -> DemoState:
    next_loop = state.get("loop_count", 0) + 1
    enough = len(state.get("notes", [])) >= 2 or next_loop >= 2
    return {"is_enough": enough, "loop_count": next_loop}


def route_after_reflect(state: DemoState):
    if state["is_enough"]:
        return "finalize"
    return [Send("search", {"queries": ["follow-up query"], "notes": [], "loop_count": state["loop_count"]})]


def finalize(state: DemoState) -> DemoState:
    summary = "\n".join(state.get("notes", []))
    return {"notes": [f"FINAL ANSWER\n{summary}"]}


builder = StateGraph(DemoState)
builder.add_node("generate_queries", generate_queries)
builder.add_node("search", search)
builder.add_node("reflect", reflect)
builder.add_node("finalize", finalize)

builder.add_edge(START, "generate_queries")
builder.add_conditional_edges("generate_queries", dispatch_queries, ["search"])
builder.add_edge("search", "reflect")
builder.add_conditional_edges("reflect", route_after_reflect, ["search", "finalize"])
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke(
        {
            "question": "LangGraph",
            "queries": [],
            "notes": [],
            "is_enough": False,
            "loop_count": 0,
        }
    )
    print(result["notes"][-1])
```

---

## 2. 运行方式

```bash
python examples/min_graph_demo.py
```

如果成功，你会看到 `FINAL ANSWER` 开头的输出。

---

## 3. 从这个 demo 你要观察 4 件事

1. `dispatch_queries` 返回的是 `List[Send]`，不是字符串
2. `search` 被执行多次，每次只处理一个查询
3. `notes` 是列表字段，借助 reducer 自动累积
4. `route_after_reflect` 可返回字符串或 `Send` 列表

---

## 4. 常见问题与修复

## 4.1 `KeyError`

原因：`Send` payload 缺字段。

修复：给目标节点所需字段默认值。

## 4.2 结果丢失

原因：`notes` 没用 `Annotated[List[str], operator.add]`。

修复：加 reducer。

## 4.3 死循环

原因：反思节点永远返回 `is_enough=False`。

修复：加上循环上限字段并在路由里判断。

---

## 5. 将 demo 思路迁移到本项目

你项目里对应关系如下：

- `generate_queries` ↔ `generate_query`
- `search` ↔ `web_research`
- `reflect` ↔ `reflection`
- `route_after_reflect` ↔ `evaluate_research`
- `finalize` ↔ `finalize_answer`

当你把这组映射看懂，就说明你已经能读真实项目图了。
