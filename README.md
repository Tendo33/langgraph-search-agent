# LangGraph Research Agent API

一个基于LangGraph的研究代理API服务，使用Google Gemini和Google Search进行网络研究。

## 功能特性

- 🤖 基于LangGraph的智能研究代理
- 🔍 自动生成搜索查询并进行网络研究
- 📚 收集和整理信息来源
- 🧠 使用Gemini 2.0 Flash进行推理和答案生成
- 🔄 支持多轮研究循环
- 📊 RESTful API接口

## 快速开始

### 1. 环境要求

- Python 3.11+
- Google Gemini API密钥
- Google Search API密钥

### 2. 安装依赖

```bash
pip install -e .
```

### 3. 配置环境变量

创建 `.env` 文件并添加以下配置：

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
```

### 4. 启动服务器

```bash
python run_server.py
```

服务器将在 `http://localhost:8000` 启动。

## API 端点

### 健康检查

```bash
GET /health
```

返回服务器状态和LangGraph代理是否就绪。

### 配置信息

```bash
GET /config
```

返回当前配置信息，包括API密钥状态。

### 研究查询

```bash
POST /research
```

**请求体：**
```json
{
  "question": "你的研究问题",
  "max_research_loops": 3,
  "initial_search_query_count": 3
}
```

**响应：**
```json
{
  "success": true,
  "message": "Research completed successfully",
  "data": {
    "answer": "研究结果...",
    "sources": ["来源1", "来源2"],
    "research_loops": 2,
    "full_result": {...}
  }
}
```

## 使用示例

运行示例脚本测试API：

```bash
python api_example.py
```

## API 文档

启动服务器后，访问以下地址查看交互式API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 项目结构

```
langgraph-search-agent/
├── src/agent/
│   ├── app.py              # FastAPI应用主文件
│   ├── graph.py            # LangGraph代理定义
│   ├── state.py            # 状态管理
│   ├── prompts.py          # 提示词模板
│   ├── tools_and_schemas.py # 工具和模式定义
│   ├── utils.py            # 工具函数
│   └── configuration.py    # 配置管理
├── run_server.py           # 服务器启动脚本
├── api_example.py          # API使用示例
└── pyproject.toml          # 项目配置
```

## 开发

### 运行测试

```bash
python api_example.py
```

### 代码格式化

```bash
ruff format .
```

### 代码检查

```bash
ruff check .
```

## 许可证

MIT License