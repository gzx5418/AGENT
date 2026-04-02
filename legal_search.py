"""
法律检索工具 - 直接调用得理法律API
支持法规检索和案例检索，整合结果后综合分析
"""

import requests
import json
from typing import Optional, List

# API配置
APPID = "QthdBErlyaYvyXul"
SECRET = "EC5D455E6BD348CE8E18BE05926D2EBE"
BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"

# 通用请求头
HEADERS = {
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
        法规检索结果
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
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    return response.json()


def search_case(keywords: List[str], court_levels: List[str] = None,
                judgement_types: List[str] = None, page_size: int = 5) -> dict:
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
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    return response.json()


def extract_law_summary(law_result: dict) -> list:
    """提取法规摘要信息"""
    summaries = []
    if law_result.get("code") == 200 and law_result.get("data"):
        for item in law_result["data"].get("list", []):
            summaries.append({
                "title": item.get("title", ""),
                "publish_date": item.get("publishDate", ""),
                "active_date": item.get("activeDate", ""),
                "source": item.get("source", ""),
                "summary": item.get("summary", "")[:200] if item.get("summary") else ""
            })
    return summaries


def extract_case_summary(case_result: dict) -> list:
    """提取案例摘要信息"""
    summaries = []
    if case_result.get("code") == 200 and case_result.get("data"):
        for item in case_result["data"].get("list", []):
            summaries.append({
                "title": item.get("title", ""),
                "court": item.get("court", ""),
                "judgement_date": item.get("judgementDate", ""),
                "case_no": item.get("caseNo", ""),
                "judgement_type": item.get("judgementType", ""),
                "summary": item.get("summary", "")[:200] if item.get("summary") else ""
            })
    return summaries


def legal_search(query: str, page_size: int = 5) -> dict:
    """综合法律检索 - 同时检索法规和案例

    Args:
        query: 搜索关键词
        page_size: 每类返回数量

    Returns:
        包含法规和案例的综合结果
    """
    law_result = search_law(query, page_size)
    case_result = search_case([query], page_size=page_size)

    return {
        "query": query,
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


if __name__ == "__main__":
    # 测试
    result = legal_search("工伤", 3)
    print(json.dumps(result, ensure_ascii=False, indent=2))
