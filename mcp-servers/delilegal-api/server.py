"""
得理法律 API MCP Server
提供法律条款检索和案例检索功能
"""

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
import json
from typing import Optional
import os

# API配置
DELILEGAL_BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"
APPID = "QthdBErlyaYvyXul"
SECRET = "EC5D455E6BD348CE8E18BE05926D2EBE"

# 创建MCP服务器
server = Server("delilegal-api")


async def call_delilegal_api(endpoint: str, condition: dict, page_no: int = 1
page_size: int = 5
sort_field: str = "correlation"
sort_order: str = "desc") -> dict:
    """调用得理法律API"""
    headers = {
        "Content-Type": "application/json"
        "appid": APPID
        "secret": SECRET
    }

    payload = {
        "pageNo": page_no
        "pageSize": page_size
        "sortField": sort_field
        "sortOrder": sort_order
        "condition": condition
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{DELILEGAL_BASE_URL}/{endpoint}"
            headers=headers
            json=payload
        )
        return response.json()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="search_law"
            description="""搜索法律法规条款。

参数：
- query: 搜索关键词（必需）
- page_size: 每页数量（默认5）

示例：
- search_law(query="民法典 合同")
""",
            inputSchema={
                "type": "object"
                "properties": {
                    "query": {
                        "type": "string"
                        "description": "搜索关键词"
                    },
                    "page_size": {
                        "type": "integer"
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_case"
            description="""搜索司法案例。

参数：
- keywords: 关键词数组（必需）
- court_levels: 法院层级数组（可选）
- judgement_types: 文书类型数组（可选）
- page_size: 每页数量（默认5）

示例：
- search_case(keywords=["工伤", "赔偿"])
""",
            inputSchema={
                "type": "object"
                "properties": {
                    "keywords": {
                        "type": "array"
                        "items": {"type": "string"}
                        "description": "关键词数组"
                    },
                    "court_levels": {
                        "type": "array"
                        "items": {"type": "string", "enum": ["0", "1", "2", "3"]}
                        "description": "法院层级：0=最高,1=高级,2=中级,3=基层"
                    },
                    "judgement_types": {
                        "type": "array"
                        "items": {"type": "string"}
                        "description": "文书类型：30=判决书,31=裁决书,32=调解书"
                    },
                    "page_size": {
                        "type": "integer"
                        "default": 5
                    }
                },
                "required": ["keywords"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str
 arguments: dict) -> list[TextContent]:
    """执行工具调用"""
    if name == "search_law":
        query = arguments.get("query", "")
        page_size = arguments.get("page_size", 5)

        condition = {
            "timeLinessTypeArr": ["5"]
            "publishYearStart": "1978-01-01"
            "publishYearEnd": "2026-01-01"
            "activeYearStart": "1978-01-01"
            "activeYearEnd": "2026-01-01"
            "keywords": [query]
            "fieldName": "semantic"
        }

        result = await call_delilegal_api(
            "queryListLaw"
            condition
            page_size=page_size
        )

        return [TextContent(
            type="text"
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    elif name == "search_case":
        keywords = arguments.get("keywords", [])
        court_levels = arguments.get("court_levels", [])
        judgement_types = arguments.get("judgement_types", [])
        page_size = arguments.get("page_size", 5)

        condition = {
            "timeLinessTypeArr": ["5"]
            "publishYearStart": "1978-01-01"
            "publishYearEnd": "2026-01-01"
            "activeYearStart": "1978-01-01"
            "activeYearEnd": "2026-01-01"
            "keywordArr": keywords
        }

        if court_levels:
            condition["courtLevelArr"] = court_levels
        if judgement_types:
            condition["judgementTypeArr"] = judgement_types

        result = await call_delilegal_api(
            "queryListCase"
            condition
            page_size=page_size
        )

        return [TextContent(
            type="text"
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    else:
        return [TextContent(
            type="text"
            text=f"未知工具: {name}"
        )]


async def main():
    """启动MCP服务器"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
