# AI Portfolio · 问答服务

一个可演示的 LLM 应用后端：接收问题、调用大模型、返回答案与耗时统计。
**定位**：从零搭建 AI 应用的最小完整骨架（接口 / 分层 / 配置 / 日志 / 测试 / 风格）。

## 功能

- `GET /health`：健康检查
- `POST /ask`：调用大模型回答问题，返回答案与耗时
- `GET /metrics`：累计调用次数

## 技术栈

Python 3.12 · FastAPI · Pydantic · OpenAI SDK（兼容 DeepSeek）· tenacity · pytest · ruff · uv

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置密钥
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 3. 启动
uv run uvicorn app.main:app --reload

# 4. 打开文档
# http://127.0.0.1:8000/docs
```

## 接口

| 方法 | 路径 | 说明 | 示例响应 |
|---|---|---|---|
| GET | `/health` | 健康检查 | `{"status":"ok"}` |
| POST | `/ask` | 提问 | `{"answer":"...","cost_ms":1420}` |
| GET | `/metrics` | 调用次数 | `{"calls":3}` |

请求示例：

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是 RAG"}'
```

## 项目结构

```
app/
├── main.py          # 组装：创建 app、挂路由、配日志
├── api/routes.py    # 接口层：收参数、返回响应
├── core/config.py   # 配置层：读 .env
└── services/
    ├── llm.py       # 业务层：调模型、重试、错误映射
    └── metrics.py   # 状态：调用计数
```

## 测试

```bash
uv run pytest -v      # 7 passed，全部离线（模型调用已 mock）
uv run ruff check .   # All checks passed
```

## 设计说明

- **分层**：接口层只管参数与响应，业务层管模型调用，配置层管环境差异。换模型只改 `services/llm.py`。
- **错误处理**：SDK 异常统一翻译为 `LLMError`，接口层映射为 503 + 人话提示；401/402 不重试，超时/连接失败指数退避重试 3 次。
- **测试策略**：用 `monkeypatch` 替换 `routes.ask_llm`，保证测试不联网、不花钱、不受网络波动影响。
- **已知局限**：`/metrics` 用进程内存，多 worker 部署时计数不准确；生产环境应改用 Prometheus。

## 后续计划

- [ ] W2：Prompt 模板 + 结构化输出（JSON）
- [ ] W3：文档解析 + 向量检索
- [ ] W4：RAG 知识库（带引用溯源）