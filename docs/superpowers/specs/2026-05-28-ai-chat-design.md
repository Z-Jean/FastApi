# AI 聊天功能设计规格

## 目标

在现有全栈管理系统中添加"米兔"AI 聊天功能模块，用户登录后可在独立页面与 AI 实时对话，支持流式逐字输出。

## 架构

```
浏览器                    Nginx                   Backend                 mimo API
  │                        │                       │                       │
  │ POST /api/chat/stream  │                       │                       │
  │ ──────────────────────→│                       │                       │
  │                        │ proxy_pass /api/      │                       │
  │                        │ ─────────────────────→│                       │
  │                        │                       │ openai.stream()       │
  │                        │                       │ ─────────────────────→│
  │                        │                       │                       │
  │                        │   SSE text/event-stream                       │
  │  ←─────────────────────│←──────────────────────│←─────────────────────│
  │  逐字渲染              │                       │                       │
```

**技术选型：SSE（Server-Sent Events）**
- AI 聊天是单向流（用户发一条，AI 逐字回复），SSE 天然适合
- FastAPI 原生支持 `StreamingResponse`，代码简洁
- Nginx 无需额外配置（WebSocket 需要修改 nginx.conf）
- 前端用 `fetch` + `ReadableStream` 接收，不需要额外库

## 技术栈

- **后端**：FastAPI StreamingResponse + openai Python SDK
- **前端**：fetch ReadableStream + React useState/useRef
- **API**：mimo-v2.5-pro（OpenAI 兼容接口，base_url: `https://token-plan-cn.xiaomimimo.com/v1`）
- **认证**：复用现有 JWT 认证（`Depends(get_current_admin)`）

## 后端设计

### 新增文件

#### `backend/app/schemas/chat.py`

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str                    # 用户消息
    history: list[dict] | None = None  # 可选的历史消息（前端维护）

class ChatChunk(BaseModel):
    content: str                    # 一个 chunk 的文本
    done: bool = False              # 是否结束
```

#### `backend/app/services/chat_service.py`

职责：调用 mimo API，流式返回 AI 回复。

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY"),
    base_url=os.getenv("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1"),
)

SYSTEM_PROMPT = "我给你的别名是'米兔'。回答用中文，清晰简洁。思考过程请用<thinking>标签包裹，不要省略思考过程。"

async def stream_chat(message: str, history: list[dict] | None = None):
    """流式返回 AI 回复的生成器"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model="mimo-v2.5-pro",
        messages=messages,
        temperature=0.3,
        top_p=0.75,
        max_completion_tokens=1024,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

#### `backend/app/routers/chat.py`

```python
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services import chat_service
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/stream")
async def chat_stream(req: ChatRequest, _admin=Depends(get_current_admin)):
    """SSE 流式聊天接口"""
    async def event_generator():
        for chunk in chat_service.stream_chat(req.message, req.history):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

### 依赖变更

`backend/requirements.txt` 新增：
```
openai>=1.0.0
```

### 环境变量

`backend/.env` 新增：
```
MIMO_API_KEY=tp-cfrufxh4pbuetx6vifcz9guzaj4y7ytowjl6ddakgvd3g3id
MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

## 前端设计

### 新增文件

#### `frontend/lib/chat.ts`

```typescript
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function streamChat(
  message: string,
  history: ChatMessage[],
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: Error) => void
) {
  const token = localStorage.getItem("token");
  const res = await fetch("/api/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message, history }),
  });

  if (!res.ok) {
    onError(new Error(`HTTP ${res.status}`));
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") {
          onDone();
          return;
        }
        onChunk(data);
      }
    }
  }
  onDone();
}
```

#### `frontend/app/chat/page.tsx`

独立聊天页面，包含：
- 顶部 Header（复用现有组件）
- 消息列表区域（自动滚动到底部）
- 底部输入框 + 发送按钮
- 流式逐字渲染 AI 回复
- 发送时显示"米兔正在思考中..."加载状态
- 登录校验（复用 dashboard 的 localStorage token 检查）

### 修改文件

#### `frontend/app/dashboard/page.tsx`

在现有 4 个卡片后添加第 5 个：

```tsx
<Link href="/chat" className="card hover:shadow-lg transition-shadow">
  <div className="text-4xl mb-3">🤖</div>
  <h3 className="text-lg font-semibold text-gray-900">米兔聊天</h3>
  <p className="text-gray-500 text-sm mt-1">AI 智能助手</p>
</Link>
```

## 认证

- 聊天接口复用现有 JWT 认证，通过 `Depends(get_current_admin)` 保护
- 前端请求自动携带 `Authorization: Bearer <token>`（已有 axios 拦截器）
- 注意：SSE 用的是 `fetch` 而非 `axios`，需要手动附加 token

## 错误处理

| 场景 | 后端处理 | 前端处理 |
|------|---------|---------|
| API Key 无效 | OpenAI SDK 抛异常，返回 500 | 显示"AI 服务暂时不可用" |
| 网络中断 | 流中断 | 显示"连接中断，请重试" |
| Token 过期 | 401 响应 | 跳转登录页 |
| 用户未登录 | 前端拦截 | 跳转 /login |

## 不做的事（YAGNI）

- 不保存聊天记录到数据库
- 不支持多轮上下文（首轮只有当前消息，history 为空）
- 不支持图片/文件上传
- 不支持 Markdown 渲染（纯文本显示）
- 不支持 WebSocket（SSE 足够）
