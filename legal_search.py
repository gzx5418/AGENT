# -*- coding: utf-8 -*-
"""
法律检索工具 - 直接调用得理法律API
支持法规检索和案例检索，整合结果后综合分析
"""

import requests
import json
from typing import Optional, List

# API配置 - 从环境变量读取
import os

APPID = os.environ.get("DELILEGAL_APPID", "")
SECRET = os.environ.get("DELILEGAL_SECRET", "")
BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"

if not APPID or not SECRET:
    print("警告: 请设置环境变量 DELILEGAL_APPID 和 DELILEGAL_SECRET")


def get_headers():
    """获取请求头"""
    return {
        "Content-Type": "application/json",
        "appid": APPID,
        "secret": SECRET
    }


def search_law(query: str, page_size: int = 5) -> dict:
    """法规检索

    Args:
        query: 搜索关键词
        page_size: 返回数量

    Returns:
        法规检索结果，包含:
        - success: 是否成功
        - code: 状态码
        - body: {data: [...], totalCount: int, totalPage: int, queryId: str}
    """
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

    response = requests.post(
        f"{BASE_URL}/queryListLaw",
        headers=get_headers(),
        json=payload,
        timeout=30
    )
    response.encoding = 'utf-8'
    return response.json()


def search_case(keywords: List[str], court_levels: Optional[List[str]] = None,
                judgement_types: Optional[List[str]] = None, page_size: int = 5) -> dict:
    """案例检索

    Args:
        keywords: 关键词列表
        court_levels: 法院层级 ["0"最高,"1"高级,"2"中级,"3"基层]
        judgement_types: 文书类型 ["30"判决书,"31"裁决书,"32"调解书]
        page_size: 返回数量

    Returns:
        案例检索结果
    """
    condition = {
        "timeLinessTypeArr": ["5"],
        "publishYearStart": "1978-01-01",
        "publishYearEnd": "2026-01-01",
        "activeYearStart": "1978-01-01",
        "activeYearEnd": "2026-01-01",
        "keywordArr": keywords
    }

    if court_levels:
        condition["courtLevelArr"] = court_levels
    if judgement_types:
        condition["judgementTypeArr"] = judgement_types

    payload = {
        "pageNo": 1,
        "pageSize": page_size,
        "sortField": "correlation",
        "sortOrder": "desc",
        "condition": condition
    }

    response = requests.post(
        f"{BASE_URL}/queryListCase",
        headers=get_headers(),
        json=payload,
        timeout=30
    )
    response.encoding = 'utf-8'
    return response.json()


def _clean_text(text: str) -> str:
    """清理HTML标签"""
    import re
    if not text:
        return ""
    # 移除<em>标签
    text = re.sub(r'</?em>', '', text)
    return text.strip()


def extract_law_summary(law_result: dict) -> list:
    """提取法规摘要信息"""
    summaries = []
    body = law_result.get("body", {})
    data = body.get("data", [])

    if law_result.get("success") and data:
        for item in data:
            summaries.append({
                "title": _clean_text(item.get("title", "")),
                "publish_date": item.get("publishDate", ""),
                "source": item.get("publisherName", ""),
                "timeliness": item.get("timelinessName", ""),
                "level": item.get("levelName", ""),
                "issued_no": item.get("issuedNo", ""),
                "summary": _clean_text(item.get("summary", ""))[:300] if item.get("summary") else ""
            })
    return summaries


def extract_case_summary(case_result: dict) -> list:
    """提取案例摘要信息"""
    summaries = []
    body = case_result.get("body", {})
    data = body.get("data", [])

    if case_result.get("success") and data:
        for item in data:
            summaries.append({
                "title": _clean_text(item.get("title", "")),
                "court": item.get("court", ""),
                "judgement_date": item.get("judgementDate", ""),
                "case_no": item.get("caseNo", ""),
                "judgement_type": item.get("judgementTypeName", ""),
                "court_level": item.get("courtLevelName", ""),
                "summary": _clean_text(item.get("summary", ""))[:300] if item.get("summary") else ""
            })
    return summaries


def legal_search(query: str, page_size: int = 5) -> dict:
    """综合法律检索 - 同时检索法规和案例

    Args:
        query: 搜索关键词
        page_size: 每类返回数量

    Returns:
        包含法规和案例的综合结果:
        {
            "query": "搜索词",
            "total_laws": 法规总数,
            "total_cases": 案例总数,
            "laws": [...],  # 法规列表
            "cases": [...]  # 案例列表
        }
    """
    law_result = search_law(query, page_size)
    case_result = search_case([query], page_size=page_size)

    law_body = law_result.get("body", {})
    case_body = case_result.get("body", {})

    return {
        "query": query,
        "total_laws": law_body.get("totalCount", 0),
        "total_cases": case_body.get("totalCount", 0),
        "laws": extract_law_summary(law_result),
        "cases": extract_case_summary(case_result)
    }


def legal_search_raw(query: str, page_size: int = 5) -> dict:
    """综合法律检索（返回原始数据）

    Args:
        query: 搜索关键词
        page_size: 每类返回数量

    Returns:
        包含原始法规和案例数据
    """
    law_result = search_law(query, page_size)
    case_result = search_case([query], page_size=page_size)

    return {
        "query": query,
        "laws": law_result,
        "cases": case_result
    }


def format_search_result(result: dict) -> str:
    """格式化检索结果为可读文本"""
    lines = []
    lines.append(f"=== 法律检索结果: {result['query']} ===")
    lines.append(f"相关法规: {result['total_laws']} 条")
    lines.append(f"相关案例: {result['total_cases']} 个")
    lines.append("")

    if result['laws']:
        lines.append("【法规条款】")
        for i, law in enumerate(result['laws'], 1):
            lines.append(f"{i}. {law['title']}")
            lines.append(f"   发布: {law['source']} | {law['publish_date']}")
            lines.append(f"   效力: {law['timeliness']} | 层级: {law['level']}")
            if law['summary']:
                lines.append(f"   摘要: {law['summary'][:100]}...")
            lines.append("")

    if result['cases']:
        lines.append("【相关案例】")
        for i, case in enumerate(result['cases'], 1):
            lines.append(f"{i}. {case['title']}")
            lines.append(f"   法院: {case['court']} | {case['judgement_date']}")
            lines.append(f"   案号: {case['case_no']}")
            if case['summary']:
                lines.append(f"   摘要: {case['summary'][:100]}...")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "工伤"
    result = legal_search(query, 3)

    # 写入文件避免编码问题
    with open("search_result.txt", "w", encoding="utf-8") as f:
        f.write(format_search_result(result))

    print(f"结果已写入 search_result.txt")
    print(f"法规: {result['total_laws']} 条, 案例: {result['total_cases']} 个")
