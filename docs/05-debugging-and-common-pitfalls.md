# 05｜调试指南：从“跑不通”到“定位根因”（详细版）

本篇按“症状 -> 根因 -> 排查 -> 修复”组织，并对齐当前新版接口。

---

## 1. 症状：`/research` 返回 `ok=false`

先看错误码：

- `validation_error`：请求体不符合 schema
- `missing_api_key`：缺少 `GEMINI_API_KEY`
- `graph_unavailable`：图初始化失败
- `runtime_error/internal_error`：执行期异常

排查顺序：

1. `GET /health` 看 `graph_ready`
2. `GET /config` 看 key 状态与默认配置
3. 查看 `error.details`

---

## 2. 症状：请求级配置不生效

常见根因：

- 调图时未传 `configurable`
- 传参字段名不匹配

验证点：

- `app.py` 是否调用：
  `graph_instance.ainvoke(..., config={"configurable": configurable})`
- `configuration.py` 是否按“请求 > 环境变量 > 默认值”解析

---

## 3. 症状：并发后结果数量异常

常见根因：

- reducer 缺失
- 返回字段类型不一致

检查：

- `state.py` 中累积字段是否 `Annotated[List[...], operator.add]`
- 节点返回是否总是列表

---

## 4. 症状：循环不按预期结束

常见根因：

- `is_sufficient` 总是 `False`
- `follow_up_queries` 空但仍继续路由
- `max_research_loops` 传值不正确

检查：

- `evaluate_research` 是否对空 follow-up 直接收敛
- `research_loop_count` 与 `max_research_loops` 比较逻辑

---

## 5. 症状：来源链接缺失或重复

检查链路：

1. `resolve_urls` 生成短链是否稳定
2. `get_citations` 是否提取到有效片段
3. `finalize_answer` 是否做去重替换

建议：

- 打印 `sources_gathered` 数量变化
- 检查最终答案是否包含短链标记

---

## 6. 日志模板（推荐）

```python
print(
    "[node=reflection]",
    "loop=", state.get("research_loop_count"),
    "queries=", len(state.get("search_query", [])),
    "results=", len(state.get("web_research_result", [])),
)
```

原则：

- 打印长度、计数、布尔值
- 不打印大段正文
- 路由函数必须打印“最终去向”

---

## 7. 排障优先级

1. 接口契约（请求体/响应体）
2. 配置透传（configurable）
3. 图路由与循环
4. 并发合并（reducer）
5. 模型/提示词质量

先把流程跑对，再追求答案质量。
