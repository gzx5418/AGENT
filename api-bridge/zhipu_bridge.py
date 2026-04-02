"""
智谱AI到Anthropic API转换代理
简单的FastAPI服务，将Anthropic格式请求转换为智谱AI格式
"""

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import os

app = FastAPI(title="Zhipu to Anthropic Bridge")

# 智谱AI配置
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

# 模型映射：Anthropic格式 -> 智谱格式
MODEL_MAPPING = {
    "claude-3-5-sonnet-20241022": "glm-5",
    "claude-3-opus-20240229": "glm-5",
    "claude-3-haiku-20240307": "glm-5",
    "claude-sonnet-4-20250514": "glm-5",
}


class AnthropicMessage(BaseModel):
    role: str
    content: str | list


class AnthropicRequest(BaseModel):
    model: str
    messages: list[AnthropicMessage]
    max_tokens: Optional[int] = 4096
    stream: Optional[bool] = False
    system: Optional[str] = None


def convert_to_zhipu(anthropic_req: AnthropicRequest) -> dict:
    """将Anthropic格式转换为智谱格式"""
    messages = []

    # 添加system消息
    if anthropic_req.system:
        messages.append({"role": "system", "content": anthropic_req.system})

    # 转换消息
    for msg in anthropic_req.messages:
        content = msg.content
        if isinstance(content, list):
            # 提取文本内容
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            content = "\n".join(text_parts)

        messages.append({"role": msg.role, "content": content})

    # 映射模型名称
    zhipu_model = MODEL_MAPPING.get(anthropic_req.model, "glm-4-plus")

    return {
        "model": zhipu_model,
        "messages": messages,
        "max_tokens": anthropic_req.max_tokens,
        "stream": anthropic_req.stream,
    }


@app.post("/v1/messages")
async def create_message(
    request: AnthropicRequest,
    x_api_key: str = Header(None, alias="x-api-key"),
    authorization: str = Header(None),
):
    """Anthropic兼容的messages端点"""
    # 获取API Key
    api_key = x_api_key or (authorization.replace("Bearer ", "") if authorization else ZHIPU_API_KEY)

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    # 转换请求
    zhipu_req = convert_to_zhipu(request)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        if request.stream:
            # 流式响应
            return StreamingResponse(
                stream_zhipu_response(client, zhipu_req, headers, request.model),
                media_type="text/event-stream",
            )
        else:
            # 非流式响应
            response = await client.post(
                f"{ZHIPU_BASE_URL}/chat/completions",
                json=zhipu_req,
                headers=headers,
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            zhipu_resp = response.json()
            return convert_to_anthropic_response(zhipu_resp, request.model)


async def stream_zhipu_response(client, zhipu_req, headers, model):
    """转换流式响应"""
    zhipu_req["stream"] = True

    async with client.stream(
        "POST",
        f"{ZHIPU_BASE_URL}/chat/completions",
        json=zhipu_req,
        headers=headers,
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    yield f"event: message_stop\ndata: {{}}\n\n"
                    break

                try:
                    zhipu_chunk = json.loads(data)
                    anthropic_chunk = convert_stream_chunk(zhipu_chunk, model)
                    yield f"event: content_block_delta\ndata: {json.dumps(anthropic_chunk)}\n\n"
                except json.JSONDecodeError:
                    continue


def convert_to_anthropic_response(zhipu_resp: dict, model: str) -> dict:
    """将智谱响应转换为Anthropic格式"""
    choice = zhipu_resp.get("choices", [{}])[0]
    message = choice.get("message", {})

    return {
        "id": zhipu_resp.get("id", "msg_xxx"),
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [{"type": "text", "text": message.get("content", "")}],
        "stop_reason": "end_turn" if choice.get("finish_reason") == "stop" else "max_tokens",
        "usage": {
            "input_tokens": zhipu_resp.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": zhipu_resp.get("usage", {}).get("completion_tokens", 0),
        },
    }


def convert_stream_chunk(zhipu_chunk: dict, model: str) -> dict:
    """转换流式响应块"""
    choice = zhipu_chunk.get("choices", [{}])[0]
    delta = choice.get("delta", {})

    return {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": delta.get("content", "")},
    }


@app.get("/v1/models")
async def list_models():
    """列出可用模型"""
    return {
        "data": [
            {"id": model, "type": "model", "display_name": model}
            for model in MODEL_MAPPING.keys()
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
