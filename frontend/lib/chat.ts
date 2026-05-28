/**
 * AI 聊天 API - SSE 流式调用
 */

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

/**
 * 流式发送聊天消息
 * @param message 用户消息
 * @param history 历史消息
 * @param onChunk 收到一个 chunk 时回调
 * @param onDone 流结束时回调
 * @param onError 出错时回调
 */
export async function streamChat(
  message: string,
  history: ChatMessage[],
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: Error) => void
) {
  const token = localStorage.getItem("token");

  let res: Response;
  try {
    res = await fetch("/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message, history }),
    });
  } catch {
    onError(new Error("网络连接失败"));
    return;
  }

  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    return;
  }

  if (!res.ok) {
    onError(new Error(`请求失败 (${res.status})`));
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
        if (data.startsWith("[ERROR]")) {
          onError(new Error(data));
          return;
        }
        onChunk(data);
      }
    }
  }
  onDone();
}
