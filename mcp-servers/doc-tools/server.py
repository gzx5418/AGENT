"""
法律文档分析与文书生成 MCP Server
提供合同审查、判决书分析、法律文书生成功能
"""

import os
import json
import re
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("legal-doc-tools")

# 模板目录
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def load_template(template_name: str) -> str:
    """加载文书模板"""
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.txt")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="analyze_contract",
            description="""分析合同文件，识别风险条款。

功能：
- 识别不利条款
- 标注风险等级（高/中/低）
- 提供修改建议

参数：
- contract_text: 合同全文内容（必需）
- contract_type: 合同类型（可选），如：劳动合同、租赁合同、买卖合同等

返回：
- 风险条款列表
- 每个条款的风险等级和修改建议
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_text": {
                        "type": "string",
                        "description": "合同全文内容"
                    },
                    "contract_type": {
                        "type": "string",
                        "description": "合同类型（可选）"
                    }
                },
                "required": ["contract_text"]
            }
        ),
        Tool(
            name="analyze_judgment",
            description="""分析判决书，提取关键信息。

功能：
- 提取当事人信息
- 识别争议焦点
- 总结裁判要旨
- 提取适用法条

参数：
- judgment_text: 判决书全文内容（必需）

返回：
- 案件基本信息
- 争议焦点
- 裁判要旨
- 适用法条列表
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "judgment_text": {
                        "type": "string",
                        "description": "判决书全文内容"
                    }
                },
                "required": ["judgment_text"]
            }
        ),
        Tool(
            name="extract_facts",
            description="""从案件材料中提取关键事实。

功能：
- 识别时间线
- 提取关键人物和关系
- 识别争议点
- 整理证据清单

参数：
- materials_text: 案件材料内容（必需）

返回：
- 时间线
- 关键事实
- 争议点
- 证据清单
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "materials_text": {
                        "type": "string",
                        "description": "案件材料内容"
                    }
                },
                "required": ["materials_text"]
            }
        ),
        Tool(
            name="generate_complaint",
            description="""生成民事起诉状。

参数：
- plaintiff: 原告信息（姓名、身份证号、地址、电话）
- defendant: 被告信息（姓名/名称、地址）
- cause: 案由（如：买卖合同纠纷、民间借贷纠纷）
- facts: 案件事实描述
- claims: 诉讼请求列表
- evidence: 证据清单（可选）

返回：
- 完整的民事起诉状
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "plaintiff": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "id_number": {"type": "string"},
                            "address": {"type": "string"},
                            "phone": {"type": "string"}
                        }
                    },
                    "defendant": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "address": {"type": "string"}
                        }
                    },
                    "cause": {
                        "type": "string",
                        "description": "案由"
                    },
                    "facts": {
                        "type": "string",
                        "description": "案件事实"
                    },
                    "claims": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "诉讼请求"
                    },
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "证据清单"
                    }
                },
                "required": ["plaintiff", "defendant", "cause", "facts", "claims"]
            }
        ),
        Tool(
            name="generate_defense",
            description="""生成民事答辩状。

参数：
- defendant: 答辩人信息
- plaintiff: 原告信息
- case_number: 案号（可选）
- defense_points: 答辩观点列表
- facts: 事实陈述
- evidence: 证据清单（可选）

返回：
- 完整的民事答辩状
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "defendant": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "address": {"type": "string"}
                        }
                    },
                    "plaintiff": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"}
                        }
                    },
                    "case_number": {
                        "type": "string",
                        "description": "案号"
                    },
                    "defense_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "答辩观点"
                    },
                    "facts": {
                        "type": "string",
                        "description": "事实陈述"
                    },
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "证据清单"
                    }
                },
                "required": ["defendant", "plaintiff", "defense_points", "facts"]
            }
        ),
        Tool(
            name="generate_legal_opinion",
            description="""生成法律意见书。

参数：
- client: 委托人信息
- matter: 委托事项
- facts: 事实概要
- analysis: 法律分析（可选，如不提供将根据facts自动分析）
- conclusion: 结论意见
- risks: 风险提示（可选）

返回：
- 完整的法律意见书
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "委托人名称"
                    },
                    "matter": {
                        "type": "string",
                        "description": "委托事项"
                    },
                    "facts": {
                        "type": "string",
                        "description": "事实概要"
                    },
                    "analysis": {
                        "type": "string",
                        "description": "法律分析"
                    },
                    "conclusion": {
                        "type": "string",
                        "description": "结论意见"
                    },
                    "risks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "风险提示"
                    }
                },
                "required": ["client", "matter", "facts", "conclusion"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """执行工具调用"""

    if name == "analyze_contract":
        contract_text = arguments.get("contract_text", "")
        contract_type = arguments.get("contract_type", "通用合同")

        # 返回分析提示（实际分析由AI完成）
        result = {
            "task": "contract_analysis",
            "contract_type": contract_type,
            "content_length": len(contract_text),
            "instructions": f"""请对以下{contract_type}进行专业分析：

1. 识别所有可能对一方不利的条款
2. 对每个风险条款标注风险等级（高/中/低）
3. 提供具体的修改建议
4. 检查是否缺少重要条款

合同内容：
{contract_text[:5000]}{"..." if len(contract_text) > 5000 else ""}"""
        }

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    elif name == "analyze_judgment":
        judgment_text = arguments.get("judgment_text", "")

        result = {
            "task": "judgment_analysis",
            "content_length": len(judgment_text),
            "instructions": f"""请对以下判决书进行专业分析，提取关键信息：

1. 案件基本信息（案号、法院、审判人员）
2. 当事人信息（原告、被告、第三人）
3. 争议焦点
4. 事实认定
5. 裁判要旨
6. 适用法条
7. 判决结果

判决书内容：
{judgment_text[:8000]}{"..." if len(judgment_text) > 8000 else ""}"""
        }

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    elif name == "extract_facts":
        materials_text = arguments.get("materials_text", "")

        result = {
            "task": "fact_extraction",
            "content_length": len(materials_text),
            "instructions": f"""请从以下案件材料中提取关键信息：

1. 时间线（按时间顺序列出重要事件）
2. 关键人物及其关系
3. 争议焦点
4. 证据清单
5. 对己方有利的事实
6. 对己方不利的事实

材料内容：
{materials_text[:8000]}{"..." if len(materials_text) > 8000 else ""}"""
        }

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    elif name == "generate_complaint":
        plaintiff = arguments.get("plaintiff", {})
        defendant = arguments.get("defendant", {})
        cause = arguments.get("cause", "")
        facts = arguments.get("facts", "")
        claims = arguments.get("claims", [])
        evidence = arguments.get("evidence", [])

        # 生成起诉状
        complaint = f"""民事起诉状

原告：{plaintiff.get('name', '（姓名）')}
身份证号：{plaintiff.get('id_number', '（身份证号）')}
住所地：{plaintiff.get('address', '（地址）')}
联系电话：{plaintiff.get('phone', '（电话）')}

被告：{defendant.get('name', '（姓名/名称）')}
住所地：{defendant.get('address', '（地址）')}

案由：{cause}

诉讼请求：
"""
        for i, claim in enumerate(claims, 1):
            complaint += f"{i}. {claim}\n"

        complaint += f"""
事实与理由：
{facts}
"""
        if evidence:
            complaint += "\n证据清单：\n"
            for i, ev in enumerate(evidence, 1):
                complaint += f"{i}. {ev}\n"

        complaint += """
此致
        人民法院

                                    起诉人：

                                    年    月    日

附：
1. 本起诉状副本    份
2. 证据材料    份
"""

        return [TextContent(type="text", text=complaint)]

    elif name == "generate_defense":
        defendant_info = arguments.get("defendant", {})
        plaintiff = arguments.get("plaintiff", {})
        case_number = arguments.get("case_number", "")
        defense_points = arguments.get("defense_points", [])
        facts = arguments.get("facts", "")
        evidence = arguments.get("evidence", [])

        defense_doc = f"""民事答辩状

答辩人：{defendant_info.get('name', '（姓名）')}
住所地：{defendant_info.get('address', '（地址）')}

被答辩人（原告）：{plaintiff.get('name', '（姓名）')}

"""
        if case_number:
            defense_doc += f"案号：{case_number}\n"

        defense_doc += """
答辩人因与被答辩人        纠纷一案，现提出答辩意见如下：

"""
        for i, point in enumerate(defense_points, 1):
            defense_doc += f"{i}. {point}\n"

        defense_doc += f"""
事实与理由：
{facts}
"""
        if evidence:
            defense_doc += "\n证据清单：\n"
            for i, ev in enumerate(evidence, 1):
                defense_doc += f"{i}. {ev}\n"

        defense_doc += """
综上所述，答辩人认为：

此致
        人民法院

                                    答辩人：

                                    年    月    日

附：
1. 本答辩状副本    份
2. 证据材料    份
"""

        return [TextContent(type="text", text=defense_doc)]

    elif name == "generate_legal_opinion":
        client = arguments.get("client", "")
        matter = arguments.get("matter", "")
        facts = arguments.get("facts", "")
        analysis = arguments.get("analysis", "")
        conclusion = arguments.get("conclusion", "")
        risks = arguments.get("risks", [])

        from datetime import datetime

        opinion = f"""法律意见书

致：{client}

关于：{matter}

一、事实概要
{facts}

"""
        if analysis:
            opinion += f"""二、法律分析
{analysis}

"""
        else:
            opinion += """二、法律分析
（请根据上述事实进行法律分析）

"""

        opinion += f"""三、结论意见
{conclusion}

"""
        if risks:
            opinion += """四、风险提示
"""
            for i, risk in enumerate(risks, 1):
                opinion += f"{i}. {risk}\n"

        opinion += f"""

本法律意见书仅供委托人参考，不作为正式法律文件使用。

                                    法律顾问：

                                    {datetime.now().strftime('%Y年%m月%d日')}
"""

        return [TextContent(type="text", text=opinion)]

    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


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
