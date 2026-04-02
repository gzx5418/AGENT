# -*- coding: utf-8 -*-
"""
法律检索命令行工具
用于对话中直接调用，返回JSON格式结果
"""

import sys
import json
import re

# 确保UTF-8输出
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from legal_search import legal_search, search_law, search_case, _clean_text


def extract_keywords(text: str) -> list:
    """从问题中提取关键词"""
    # 停用词
    stop_words = {'的', '了', '是', '在', '有', '和', '与', '或', '我', '你', '他', '她', '它',
                  '这', '那', '什么', '怎么', '如何', '为什么', '吗', '呢', '吧', '啊', '呀',
                  '请问', '想要', '需要', '可以', '能够', '应该', '会', '能', '要', '想',
                  '如果', '假如', '假设', '比如', '例如', '一个', '这个', '那个', '哪些'}

    # 法律领域关键词扩展
    legal_keywords = {
        '工伤': ['工伤', '工伤保险', '工伤认定', '职业病'],
        '劳动': ['劳动', '劳动合同', '工资', '加班', '解雇'],
        '合同': ['合同', '违约', '解除', '定金', '赔偿'],
        '房产': ['房产', '房屋', '租房', '买卖', '产权'],
        '婚姻': ['婚姻', '离婚', '抚养', '财产分割'],
        '债务': ['债务', '借贷', '欠款', '利息', '还款'],
        '交通': ['交通', '事故', '肇事', '赔偿'],
        '医疗': ['医疗', '纠纷', '损害', '赔偿'],
    }

    # 提取关键词
    keywords = []

    # 先检查是否有法律领域关键词
    for key, related in legal_keywords.items():
        if key in text:
            keywords.append(key)
            # 添加相关词
            for r in related:
                if r in text and r not in keywords:
                    keywords.append(r)

    # 如果没有找到领域关键词，提取其他词
    if not keywords:
        # 简单分词（按空格和标点）
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        for word in words:
            if word not in stop_words and len(word) >= 2:
                keywords.append(word)

    # 去重并限制数量
    keywords = list(dict.fromkeys(keywords))[:5]

    # 如果还是没有关键词，用整个问题
    if not keywords:
        keywords = [text[:20]]

    return keywords


def search_law_cli(query: str, page_size: int = 5) -> str:
    """法规检索 - 返回JSON"""
    result = search_law(query, page_size)
    return json.dumps(result, ensure_ascii=False, indent=2)


def search_case_cli(query: str, page_size: int = 5) -> str:
    """案例检索 - 返回JSON"""
    keywords = extract_keywords(query)
    result = search_case(keywords, page_size=page_size)
    return json.dumps(result, ensure_ascii=False, indent=2)


def search_all_cli(query: str, page_size: int = 5) -> str:
    """综合检索 - 返回JSON"""
    result = legal_search(query, page_size)
    return json.dumps(result, ensure_ascii=False, indent=2)


def search_smart_cli(question: str, page_size: int = 5) -> str:
    """智能检索 - 分析问题后检索，返回结构化结果"""
    keywords = extract_keywords(question)

    # 使用第一个关键词进行检索
    primary_keyword = keywords[0] if keywords else question

    result = legal_search(primary_keyword, page_size)
    result["extracted_keywords"] = keywords

    return json.dumps(result, ensure_ascii=False, indent=2)


def print_usage():
    """打印使用说明"""
    print("""
法律检索工具

用法:
    python legal_cli.py <命令> <查询词> [数量]

命令:
    law      法规检索
    case     案例检索
    all      综合检索（法规+案例）
    smart    智能检索（自动提取关键词）

示例:
    python legal_cli.py law 工伤 5
    python legal_cli.py case 劳动纠纷 3
    python legal_cli.py all 合同违约
    python legal_cli.py smart 上班途中发生车祸算工伤吗
""")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()
    query = sys.argv[2]
    page_size = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if command == "law":
        print(search_law_cli(query, page_size))
    elif command == "case":
        print(search_case_cli(query, page_size))
    elif command == "all":
        print(search_all_cli(query, page_size))
    elif command == "smart":
        print(search_smart_cli(query, page_size))
    else:
        print(f"未知命令: {command}")
        print_usage()
        sys.exit(1)
