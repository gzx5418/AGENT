# -*- coding: utf-8 -*-
"""
智能法律助手 - 对话式法律咨询
自动分析问题、检索法规案例、综合回答
"""

import json
import re
from typing import List, Dict, Optional
from legal_search import legal_search, search_law, search_case, _clean_text


class LegalAssistant:
    """法律助手类"""

    # 法律领域关键词映射
    DOMAIN_KEYWORDS = {
        "劳动": ["劳动", "工资", "加班", "解雇", "辞退", "离职", "社保", "公积金", "劳动合同", "工伤", "职业病"],
        "婚姻": ["婚姻", "离婚", "结婚", "夫妻", "子女", "抚养", "赡养", "财产分割", "彩礼"],
        "房产": ["房产", "房屋", "租房", "买卖", "物业", "拆迁", "产权", "过户", "抵押"],
        "合同": ["合同", "违约", "解除", "定金", "赔偿", "条款", "协议", "效力"],
        "债务": ["债务", "借贷", "欠款", "还款", "利息", "担保", "抵押", "催收"],
        "侵权": ["侵权", "赔偿", "损害", "责任", "医疗", "交通", "事故"],
        "刑事": ["刑事", "犯罪", "刑罚", "量刑", "辩护", "取保", "拘留", "逮捕"],
        "行政": ["行政", "处罚", "复议", "诉讼", "许可", "执照"],
        "知识产权": ["专利", "商标", "著作权", "版权", "侵权", "知识产权"],
        "公司": ["公司", "股东", "股权", "董事", "清算", "破产", "注册"]
    }

    def __init__(self):
        self.history = []

    def extract_keywords(self, question: str) -> List[str]:
        """从问题中提取法律关键词"""
        keywords = []

        # 提取领域关键词
        for domain, words in self.DOMAIN_KEYWORDS.items():
            for word in words:
                if word in question and word not in keywords:
                    keywords.append(word)

        # 提取引号中的内容
        quoted = re.findall(r'[""「」『』【】]([^""「」『』【】]+)[""「」『』【】]', question)
        keywords.extend(quoted)

        # 如果没有提取到关键词，使用分词或简单提取
        if not keywords:
            # 简单提取2-4字的词
            words = re.findall(r'[\u4e00-\u9fa5]{2,4}', question)
            keywords = list(set(words))[:3]

        return keywords[:5]  # 最多5个关键词

    def detect_domain(self, question: str) -> List[str]:
        """检测问题所属法律领域"""
        domains = []
        for domain, words in self.DOMAIN_KEYWORDS.items():
            for word in words:
                if word in question:
                    domains.append(domain)
                    break
        return domains

    def analyze_question(self, question: str) -> dict:
        """分析法律问题"""
        keywords = self.extract_keywords(question)
        domains = self.detect_domain(question)

        return {
            "question": question,
            "keywords": keywords,
            "domains": domains,
            "primary_keyword": keywords[0] if keywords else question[:10]
        }

    def search(self, question: str, page_size: int = 5) -> dict:
        """根据问题进行法律检索"""
        analysis = self.analyze_question(question)

        # 使用主要关键词检索
        primary_keyword = analysis["primary_keyword"]

        # 综合检索
        result = legal_search(primary_keyword, page_size)

        # 如果有多个关键词，补充检索
        if len(analysis["keywords"]) > 1:
            extra_keyword = analysis["keywords"][1]
            extra_result = legal_search(extra_keyword, 2)
            # 合并结果（去重）
            existing_titles = {l["title"] for l in result["laws"]}
            for law in extra_result["laws"]:
                if law["title"] not in existing_titles:
                    result["laws"].append(law)
                    existing_titles.add(law["title"])

        result["analysis"] = analysis
        return result

    def format_response(self, result: dict) -> str:
        """格式化检索结果为回答"""
        analysis = result.get("analysis", {})
        lines = []

        # 问题分析
        lines.append(f"📋 **问题分析**")
        lines.append(f"- 关键词: {', '.join(analysis.get('keywords', []))}")
        lines.append(f"- 涉及领域: {', '.join(analysis.get('domains', [])) or '通用法律'}")
        lines.append("")

        # 法规部分
        lines.append(f"📚 **相关法规** (共 {result['total_laws']} 条)")
        if result["laws"]:
            for i, law in enumerate(result["laws"][:5], 1):
                lines.append(f"\n{i}. **{law['title']}**")
                if law.get("issued_no"):
                    lines.append(f"   文号: {law['issued_no']}")
                lines.append(f"   来源: {law['source']} | {law['publish_date']}")
                lines.append(f"   效力: {law.get('timeliness', '有效')}")
        else:
            lines.append("未找到相关法规")
        lines.append("")

        # 案例部分
        lines.append(f"⚖️ **相关案例** (共 {result['total_cases']} 个)")
        if result["cases"]:
            for i, case in enumerate(result["cases"][:5], 1):
                lines.append(f"\n{i}. **{case['title']}**")
                if case.get("case_no"):
                    lines.append(f"   案号: {case['case_no']}")
                lines.append(f"   法院: {case.get('court', '未知')} | {case.get('judgement_date', '')}")
                if case.get("summary"):
                    lines.append(f"   摘要: {case['summary'][:100]}...")
        else:
            lines.append("未找到相关案例")

        return "\n".join(lines)

    def ask(self, question: str) -> dict:
        """提问并获取检索结果"""
        result = self.search(question)
        self.history.append({
            "question": question,
            "result": result
        })
        return result

    def interactive(self):
        """交互式对话模式"""
        print("=" * 50)
        print("智能法律助手 - 输入法律问题进行咨询")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 50)
        print()

        while True:
            try:
                question = input("👤 请输入问题: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    print("再见!")
                    break

                print("\n🔍 正在检索相关法规和案例...\n")

                result = self.ask(question)
                print(self.format_response(result))
                print("\n" + "-" * 50 + "\n")

            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}\n")


def quick_search(question: str) -> str:
    """快速检索 - 简单接口"""
    assistant = LegalAssistant()
    result = assistant.ask(question)
    return assistant.format_response(result)


def search_json(question: str) -> dict:
    """检索并返回JSON结果"""
    assistant = LegalAssistant()
    return assistant.ask(question)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # 命令行模式
        question = " ".join(sys.argv[1:])
        print(quick_search(question))
    else:
        # 交互模式
        assistant = LegalAssistant()
        assistant.interactive()
