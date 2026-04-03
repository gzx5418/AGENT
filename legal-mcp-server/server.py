# 法律检索 MCP HTTP 服务
# 提供法规检索和案例检索功能

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import json

app = FastAPI(title="Legal Search MCP Server")

# API 配置
DELILEGAL_BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"
APPID = os.environ.get("DELILEGAL_APPID", "")
SECRET = os.environ.get("DELILEGAL_SECRET", "")


class ToolCall(BaseModel):
    name: str
    arguments: dict


class MCPRequest(BaseModel):
    method: str
    params: Optional[dict] = None


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


@app.get("/tools")
async def list_tools():
    """列出可用工具"""
    return {
        "tools": [
            {
                "name": "search_law",
                "description": "搜索法律法规条款。输入关键词搜索相关法律法规。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_case",
                "description": "搜索司法案例。输入关键词搜索相关判例。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "关键词数组"
                        }
                    },
                    "required": ["keywords"]
                }
            }
        ]
    }


@app.post("/call_tool")
async def call_tool(request: ToolCall):
    """执行工具调用"""
    if request.name == "search_law":
        return await search_law(request.arguments.get("query", ""))
    elif request.name == "search_case":
        return await search_case(request.arguments.get("keywords", []))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")


async def search_law(query: str, page_size: int = 5) -> dict:
    """法规检索"""
    headers = {
        "Content-Type": "application/json",
        "appid": APPID,
        "secret": SECRET
    }

    payload = {
        "pageNo": 1,
        "pageSize": page_size,
        "sortField": "correlation",
        "sortOrder": "desc",
        "condition": {
            "timeLinessTypeArr": ["5"],
            "publishYearStart": "1978-01-01",
            "publishYearEnd": "2026-01-01",
            "activeYearStart": "1978-01-01",
            "activeYearEnd": "2026-01-01",
            "keywords": [query],
            "fieldName": "semantic"
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{DELILEGAL_BASE_URL}/queryListLaw",
            headers=headers,
            json=payload
        )
        data = response.json()

    if not data.get("success"):
        return {"error": data.get("msg", "检索失败")}

    results = []
    for item in data.get("body", {}).get("data", []):
        results.append({
            "title": item.get("title", ""),
            "level": item.get("levelName", ""),
            "status": item.get("timelinessName", ""),
            "publish_date": item.get("publishDate", ""),
            "summary": item.get("content", "")[:200] if item.get("content") else ""
        })

    return {
        "total": data.get("body", {}).get("totalCount", 0),
        "results": results
    }


async def search_case(keywords: list, page_size: int = 5) -> dict:
    """案例检索"""
    headers = {
        "Content-Type": "application/json",
        "appid": APPID,
        "secret": SECRET
    }

    payload = {
        "pageNo": 1,
        "pageSize": page_size,
        "sortField": "correlation",
        "sortOrder": "desc",
        "condition": {
            "timeLinessTypeArr": ["5"],
            "publishYearStart": "1978-01-01",
            "publishYearEnd": "2026-01-01",
            "activeYearStart": "1978-01-01",
            "activeYearEnd": "2026-01-01",
            "keywordArr": keywords
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{DELILEGAL_BASE_URL}/queryListCase",
            headers=headers,
            json=payload
        )
        data = response.json()

    if not data.get("success"):
        return {"error": data.get("msg", "检索失败")}

    results = []
    for item in data.get("body", {}).get("data", []):
        results.append({
            "title": item.get("title") or item.get("caseName", ""),
            "court": item.get("courtName", ""),
            "date": item.get("judgeDate", ""),
            "type": item.get("caseType", ""),
            "summary": item.get("content", "")[:200] if item.get("content") else ""
        })

    return {
        "total": data.get("body", {}).get("totalCount", 0),
        "results": results
    }


# MCP 协议兼容端点
@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """MCP 协议兼容端点"""
    if request.method == "tools/list":
        return await list_tools()
    elif request.method == "tools/call":
        params = request.params or {}
        call_req = ToolCall(
            name=params.get("name", ""),
            arguments=params.get("arguments", {})
        )
        result = await call_tool(call_req)
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
