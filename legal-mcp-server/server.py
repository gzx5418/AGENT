import os
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

DELILEGAL_BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"
APPID = os.environ.get("DELILEGAL_APPID", "")
SECRET = os.environ.get("DELILEGAL_SECRET", "")

mcp = FastMCP(
    "Legal Search MCP",
    json_response=True,
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            "host.docker.internal:*",
            "localhost:*",
            "127.0.0.1:*",
        ]
    ),
)


def _headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "appid": APPID,
        "secret": SECRET,
    }


@mcp.tool()
async def search_law(query: str, page_size: int = 5) -> dict:
    """Search Chinese laws and regulations by keyword."""
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
            "fieldName": "semantic",
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{DELILEGAL_BASE_URL}/queryListLaw",
            headers=_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    if not data.get("success"):
        return {"error": data.get("msg", "legal search failed")}

    results = []
    for item in data.get("body", {}).get("data", []):
        results.append(
            {
                "title": item.get("title", ""),
                "level": item.get("levelName", ""),
                "status": item.get("timelinessName", ""),
                "publish_date": item.get("publishDate", ""),
                "summary": (item.get("content") or "")[:200],
            }
        )

    return {
        "total": data.get("body", {}).get("totalCount", 0),
        "results": results,
    }


@mcp.tool()
async def search_case(keywords: list[str], page_size: int = 5) -> dict:
    """Search Chinese court cases by keywords."""
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
            "keywordArr": keywords,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{DELILEGAL_BASE_URL}/queryListCase",
            headers=_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    if not data.get("success"):
        return {"error": data.get("msg", "case search failed")}

    results = []
    for item in data.get("body", {}).get("data", []):
        results.append(
            {
                "title": item.get("title") or item.get("caseName", ""),
                "court": item.get("courtName", ""),
                "date": item.get("judgeDate", ""),
                "type": item.get("caseType", ""),
                "summary": (item.get("content") or "")[:200],
            }
        )

    return {
        "total": data.get("body", {}).get("totalCount", 0),
        "results": results,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Legal Search MCP Server", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/", mcp.streamable_http_app())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
