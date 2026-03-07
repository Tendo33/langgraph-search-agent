# 07｜术语表（LangGraph 初学者速查）

## A

- **Agent**
  - 能在多步骤中自主决策、循环和并发执行的程序。

- **AgentState**
  - 本项目统一后的全局状态契约，定义在 `src/search_agent/state.py`。

## C

- **Conditional Edge（条件边）**
  - 根据当前状态动态决定下一步去向。

- **Compile（编译图）**
  - 将图定义编译为可执行对象。

## E

- **Edge（边）**
  - 节点之间的固定连线。

- **END**
  - 图执行结束标记。

## N

- **Node（节点）**
  - 单一职责步骤函数：读状态、产出状态更新。

## R

- **Reducer（归并器）**
  - 多分支更新同一字段时的合并规则。

- **RunnableConfig**
  - 运行时配置容器；本项目通过 `configurable` 注入模型与循环参数。

## S

- **Send**
  - 扇出任务对象，用于并行调用同一节点。

- **START**
  - 图执行起点标记。

- **StateGraph**
  - 以共享状态为核心的图构建器。

## 本项目字段速查

- `messages`：消息历史
- `search_query`：查询词累积列表
- `web_research_result`：检索摘要累积列表
- `sources_gathered`：来源片段累积列表
- `is_sufficient`：反思结果是否足够
- `follow_up_queries`：后续检索查询
- `research_loop_count`：当前循环计数

## 记忆口诀

- 状态承载数据
- 节点处理数据
- 条件边做决策
- Send 做并发
- reducer 做合并
