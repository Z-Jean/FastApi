"""
聊天服务 - 调用 mimo API，流式返回 AI 回复
"""
import os
from openai import OpenAI

SYSTEM_PROMPT = "我给你的别名是'米兔'。回答用中文，清晰简洁。思考过程请用<thinking>标签包裹，不要省略思考过程。"

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("MIMO_API_KEY"),
            base_url=os.getenv("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1"),
        )
    return _client


def stream_chat(message: str, history: list[dict] | None = None):
    """
    流式返回 AI 回复的生成器
    :param message: 用户当前消息
    :param history: 可选的历史消息列表 [{"role": "user/assistant", "content": "..."}]
    :return: 生成器，每次 yield 一个 chunk 文本
    """
    client = _get_client()
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
