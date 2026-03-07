# 01｜LangGraph 核心概念（初学者详细版）

这篇文档的目标：

- 你不需要先会 LangGraph
- 读完后能把核心名词讲给别人听
- 并知道它们在本项目里的具体位置

---

## 1. LangGraph 到底在解决什么问题

如果任务只有一步（例如“把一句话翻译成英文”），普通函数就够了。

但 Agent 常见任务是多步骤的：

- 先拆问题
- 再检索
- 再判断信息够不够
- 不够就继续检索
- 最后再生成答案

这类任务有 3 个典型难点：

1. **状态管理**：中间结果放哪里？
2. **流程控制**：何时循环、何时结束？
3. **并行执行**：多个检索任务如何同时跑并合并结果？

LangGraph 的价值就是：把这三件事做成统一框架。

---

## 2. 六个核心对象（必须会）

## 2.1 `State`

`State` 是整个图的共享数据容器，可以理解为“全局工作内存”。

在本项目里，关键字段有：

- `messages`：用户问题与模型回复
- `search_query`：已生成/已执行的查询词
- `web_research_result`：检索摘要
- `sources_gathered`：来源列表
- `research_loop_count`：已执行轮数

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/state.py`

---

## 2.2 `Node`

`Node` 是一个步骤函数。它做一件事：

- 读 `state`
- 执行逻辑
- 返回状态更新

典型节点：

- `generate_query`
- `web_research`
- `reflection`
- `finalize_answer`

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/graph.py`

---

## 2.3 `Edge`

`Edge` 是固定连线：执行完 A 一定去 B。

例子：

- `web_research -> reflection`
- `finalize_answer -> END`

适合“顺序明确”的路径。

---

## 2.4 `Conditional Edge`

条件边是动态路由：下一步由函数根据当前状态决定。

本项目中 `reflection` 后并不固定走向，而是由 `evaluate_research` 判断：

- 信息足够：去 `finalize_answer`
- 信息不足：继续去 `web_research`

这就是循环闭环的核心。

---

## 2.5 `Send`

`Send` 是“派发任务”的对象，常用于并行。

形式：

```python
Send("web_research", {"search_query": "...", "id": 0})
```

含义：

- 把一份输入发送给某个节点
- 可以一次返回多个 `Send`
- 这样就能扇出多个并行分支

本项目用它并发执行多个搜索查询。

---

## 2.6 `Reducer`

并发分支结束后，状态需要合并。Reducer 就是合并规则。

本项目核心 reducer：

- `operator.add`：列表拼接
- `add_messages`：消息合并

定义写在 `Annotated[类型, reducer]` 里。

没有 reducer，分支结果容易互相覆盖。

---

## 3. `Send` 和条件边的关系（重点）

很多初学者会混淆：

- 条件边负责“决定走哪条路”
- `Send` 负责“给目标节点发几份任务”

你可以把它理解为：

1. 先判断“是否继续研究”
2. 如果继续，再返回多个 `Send` 并行执行

所以 `Conditional Edge + Send` 组合就能实现“可判断 + 可并发”的高级路由。

---

## 4. 为什么这个项目要用 LangGraph 而不是 while + for

你当然可以手写：

- `while not enough:`
- `for query in queries:`

但很快会出现：

- 状态字段越来越多，传参变混乱
- 并发回流时不清楚谁覆盖了谁
- 每加一个步骤都改大量流程代码

LangGraph 的结构化好处：

- 节点职责单一
- 路由显式可读
- 状态合并有规则
- 扩展新节点时改动可控

---

## 5. 最小心智模型（一句话）

LangGraph = `状态容器` + `步骤函数` + `路由逻辑` + `合并规则`。

掌握这四块，你就已经入门。

---

## 6. 阅读建议（接下来做什么）

下一篇请看：`docs/02-state-node-edge.md`。

重点关注：

- 节点到底返回什么格式
- 并发结果如何合并
- 条件边返回值有哪些合法形态
