# 09｜状态字段字典（`AgentState`）

文件：`D:/TuDou/langgraph-search-agent/src/search_agent/state.py`

## 核心字段

- `messages`：消息历史（用户问题 + 最终答案）
- `search_query`：已生成/已执行查询词列表（累积）
- `web_research_result`：检索摘要列表（累积）
- `sources_gathered`：来源片段列表（累积）

## 路由控制字段

- `is_sufficient`：反思节点判断是否足够
- `follow_up_queries`：下一轮需要继续检索的查询词
- `knowledge_gap`：当前知识缺口说明
- `number_of_ran_queries`：已执行查询总数（用于给新查询编号）

## 运行参数字段

- `initial_search_query_count`：初始查询数量
- `max_research_loops`：最大循环次数
- `research_loop_count`：当前已执行循环次数
- `reasoning_model`：最终答案模型覆盖值

## reducer 规则

- `messages`：`add_messages`
- `search_query` / `web_research_result` / `sources_gathered`：`operator.add`

这保证了并发分支回流后不会丢数据。

## 注意事项

- 节点返回“增量更新”即可，不需要返回完整状态。
- 只有并发累积字段才需要 reducer。
- 非累积字段（如 `is_sufficient`）通常使用覆盖更新。
