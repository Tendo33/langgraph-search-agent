# 07｜术语表（LangGraph 初学者速查）

这份术语表建议你放在旁边随时查。

## A

- **Agent**
  - 由多个步骤组成、可根据中间结果自我调整流程的程序。

## C

- **Conditional Edge（条件边）**
  - 动态路由连线。由函数返回值决定下一步节点。

- **Compile（编译图）**
  - 把声明好的节点和边转换成可执行图对象的过程。

## E

- **Edge（边）**
  - 节点之间的连接关系。普通边是固定流向。

- **END**
  - 图执行结束标记。

## N

- **Node（节点）**
  - 图中的一个步骤函数。输入状态，输出状态更新。

## R

- **Reducer（归并器）**
  - 多分支同时更新同一字段时的合并规则。

- **RunnableConfig**
  - 运行时配置容器，可向节点传模型和参数配置。

## S

- **Send**
  - 向某个节点派发一份任务输入的对象，常用于并行扇出。

- **START**
  - 图执行起点标记。

- **State（状态）**
  - 图中共享数据容器，所有节点读写它。

- **StateGraph**
  - 以状态为核心的图构建器。

## 本项目专有字段速查

- `messages`：对话消息历史
- `search_query`：查询词列表
- `web_research_result`：检索结果摘要
- `sources_gathered`：来源列表
- `research_loop_count`：当前循环次数
- `max_research_loops`：最大循环次数

## 初学者最容易混淆的三对概念

1. `Edge` vs `Conditional Edge`
   - 前者固定路径，后者动态路径。

2. `Conditional Edge` vs `Send`
   - 前者做决策，后者做派发。

3. `State` vs `RunnableConfig`
   - `State` 是任务数据，`RunnableConfig` 是运行配置。

## 口诀（方便记忆）

- 状态承载数据
- 节点处理数据
- 边决定顺序
- 条件边决定分支
- Send 决定并发
- reducer 决定合并
