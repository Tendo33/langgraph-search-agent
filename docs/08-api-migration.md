# 08｜API 迁移说明（旧 `/research` -> 新契约）

## 变更结论

本次改造直接替换了旧 `/research` 请求体和响应体，不提供兼容层。

## 请求体迁移

旧：

```json
{
  "question": "...",
  "max_research_loops": 2,
  "initial_search_query_count": 3
}
```

新：

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
    },
    "return_debug": false
  }
}
```

## 响应体迁移

旧：

- `success`
- `message`
- `data.answer`
- `data.sources`
- `data.research_loops`

新：

- `ok`
- `data.answer`
- `data.sources`
- `data.meta.research_loop_count`
- `data.meta.queries_ran`
- `data.meta.duration_ms`
- `error{code,message,details}`

## 前端与脚本改造要点

- 统一判断 `result.ok`
- 成功数据改从 `result.data` 读取
- 失败数据改从 `result.error` 读取

## 常见迁移错误

1. 继续发送旧顶层字段 `max_research_loops`
2. 继续读取 `success/message`
3. 忽略 `error.details` 导致排障困难
