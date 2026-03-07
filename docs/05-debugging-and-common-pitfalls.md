# 05｜调试指南：从“跑不通”到“定位根因”（详细版）

本篇按“症状 -> 原因 -> 排查 -> 修复”组织。

---

## 1. 症状：服务能启动，但 `/research` 报错

## 常见原因

- `GEMINI_API_KEY` 未配置
- 图初始化失败（`graph_instance = None`）

## 排查

1. 调 `/health` 看 `graph_ready`
2. 调 `/config` 看 key 状态
3. 查看启动日志是否有 `Failed to initialize graph`

## 修复

- 设置 `.env` 后重启服务
- 先用最小问题验证（例如“法国首都是什么”）

---

## 2. 症状：某节点看起来没有执行

## 常见原因

- 上游条件路由没把它选中
- 节点名字符串写错
- 路由返回值不在允许列表中

## 排查

- 在路由函数打印返回值
- 确认 `add_conditional_edges` 的允许目标列表

## 修复

- 统一节点名常量或严格检查拼写
- 路由只返回合法节点名或合法 `Send`

---

## 3. 症状：并发后结果数量不对

## 常见原因

- reducer 缺失或定义错误
- 节点返回字段类型不一致

## 排查

- 检查 `state.py` 的 `Annotated[..., reducer]`
- 检查节点返回值是列表还是标量

## 修复

- 列表累积字段使用 `operator.add`
- 单值字段避免多分支同时写

---

## 4. 症状：循环不结束

## 常见原因

- `is_sufficient` 永远为 `False`
- `max_research_loops` 未生效

## 排查

在 `reflection` 与 `evaluate_research` 打印：

- `research_loop_count`
- `max_research_loops`
- `is_sufficient`
- `follow_up_queries` 长度

## 修复

- 添加或修正循环上限逻辑
- 没有 follow-up 时应直接收敛

---

## 5. 症状：最终来源链接不完整

## 常见原因

- 模型生成文本里未出现短链接标记
- 引用提取时某些 chunk 不完整

## 排查

- 查看 `get_citations` 输出长度
- 查看 `insert_citation_markers` 之后文本
- 查看 `finalize_answer` 中短链接替换命中情况

## 修复

- 强化回答提示词对引用格式的约束
- 对空引用情况增加兜底处理

---

## 6. 日志模板（建议直接复制）

```python
print(
    "[node=reflection]",
    "loop=", state.get("research_loop_count"),
    "results=", len(state.get("web_research_result", [])),
)
```

原则：

- 打印长度、计数、布尔值
- 不打印完整长文本（噪音太大）
- 在路由函数里一定打印返回路径

---

## 7. 排障优先级（高效顺序）

1. 图能否初始化
2. 节点是否按预期触发
3. 状态字段是否正确合并
4. 路由是否正确分支
5. 最后再调模型和 prompt

先保证“流程正确”，再优化“答案质量”。

---

## 8. 版本与配置一致性提醒

当你看到“配置没生效”，优先检查：

- 是否通过 `RunnableConfig` 传入
- 是否被环境变量覆盖
- API 里初始状态是否硬编码了某些字段

这样可以避免误以为模型行为随机。
