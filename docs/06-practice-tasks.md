# 06｜练习任务：从“能跑”到“会设计”

你可以把这篇当作训练营。每个任务都给了目标、步骤、验收标准。

---

## 任务 1：读图不迷路

## 目标

看懂本项目主流程图与每个节点职责。

## 步骤

1. 打开 `src/search_agent/graph.py`
2. 找到 `add_node`、`add_edge`、`add_conditional_edges`
3. 画出你自己的流程图

## 验收标准

你能口头解释：

- 为什么 `reflection` 后是条件边
- 为什么 `generate_query` 后是并行 `Send`

---

## 任务 2：观察状态流

## 目标

理解状态字段如何在多轮中增长。

## 步骤

1. 在 4 个节点加日志
2. 发起一个 `/research` 请求
3. 记录每步 `search_query`、`web_research_result`、`sources_gathered` 长度

## 验收标准

你能指出：

- 哪些字段是累积的
- 哪些字段是控制流程的

---

## 任务 3：操控循环次数

## 目标

验证条件边如何受 `max_research_loops` 影响。

## 步骤

1. 分别用 `max_research_loops=1/2/3` 请求同一个问题
2. 比较 `research_loops` 和答案长度

## 验收标准

你能解释：

- 为什么循环次数变化会影响结果深度和耗时

---

## 任务 4：写一个最小图

## 目标

独立写出一个带条件路由的 LangGraph。

## 步骤

1. 跟着 `docs/04-minimal-graph-hands-on.md` 完成 demo
2. 把 `is_enough` 条件改成至少两条 notes 才结束

## 验收标准

你能展示：

- 路由返回字符串时的单路径
- 路由返回 `Send` 时的并行或再派发

---

## 任务 5：新增一个节点（项目实战）

## 目标

在现有项目中添加一个中间步骤且不破坏主流程。

## 推荐方向

- `finalize_answer` 前新增 `quality_check`
- 作用：检测答案里是否包含来源链接

## 步骤

1. 新建节点函数
2. `add_node("quality_check", quality_check)`
3. 调整边：`reflection -> quality_check -> finalize_answer`

## 验收标准

- 服务可正常返回
- `quality_check` 被触发
- 最终输出结构不变

---

## 任务 6：并行深入理解

## 目标

真正掌握 `Send` + reducer。

## 步骤

1. 在最小 demo 里扇出 3 个 `Send`
2. 每个分支返回不同 `notes`
3. 检查最终 `notes` 是否完整保留

## 验收标准

你能解释：

- 为什么没有 reducer 会丢结果
- reducer 如何决定合并行为

---

## 任务 7：你是否已入门（自测）

如果你能独立回答以下问题，说明你已完成入门：

1. 条件边何时返回字符串，何时返回 `Send` 列表？
2. 节点为什么只返回增量状态？
3. 如何在不影响并行合并的前提下新增字段？
4. 为什么说“API 只是图的外壳”？

---

## 进阶建议

下一步你可以做：

- 把 `reflection` 做成更严格的结构化评估
- 把来源质量（时效性/权威性）做成独立打分节点
- 用 LangGraph Studio 或可视化工具观察执行轨迹
