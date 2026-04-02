# 智能法律AI专家系统

基于 MCP (Model Context Protocol) 的智能法律AI专家系统，集成得理法律API，提供法规检索、案例检索和文档处理能力。

## 项目结构

```
法律agent/
├── src/                            # Python 源码
│   ├── legal_search.py             # 法律检索核心
│   ├── legal_cli.py                # 命令行工具
│   └── legal_assistant.py          # 对话式助手
├── mcp-servers/                    # MCP服务目录
│   ├── delilegal-api/              # 得理法律API服务
│   │   ├── server.py               # 主服务（法规+案例检索）
│   │   ├── config.py               # API配置
│   │   └── requirements.txt
│   ├── doc-tools/                  # 文档处理服务
│   │   ├── server.py               # 主服务（合同审查+文书生成）
│   │   ├── templates/              # 文书模板
│   │   └── requirements.txt
│   └── start.sh                    # 启动脚本
├── web/                            # Web 界面
│   └── legal-ai-chat.html          # 聊天界面
├── skills/
│   └── legal-expert/
│       └── SKILL.md                # 法律专家Skill定义
├── Dockerfile.mcp                  # MCP服务Docker镜像
├── setup.sh                        # 快速部署脚本
├── claude_desktop_config.json      # Claude Desktop配置
└── README.md
```

## 功能模块

### 🔍 法律法规检索 (`search_law`)
- 关键词搜索
- 语义搜索
- 返回相关法条

### 📋 案例检索 (`search_case`)
- 关键词搜索
- 长文本语义搜索
- 支持筛选：
  - 法院层级（最高/高级/中级/基层）
  - 裁判年份
  - 文书类型

### 📝 合同审查 (`analyze_contract`)
- 识别风险条款
- 标注风险等级（高/中/低）
- 提供修改建议

### 📄 判决书分析 (`analyze_judgment`)
- 提取当事人信息
- 识别争议焦点
- 总结裁判要旨

### ✍️ 法律文书生成
| 工具 | 文书类型 |
|------|----------|
| `generate_complaint` | 民事起诉状 |
| `generate_defense` | 民事答辩状 |
| `generate_legal_opinion` | 法律意见书 |

## 快速开始

### 方式一：Claude Desktop（推荐新手）

1. **安装依赖**
```bash
pip install mcp httpx
```

2. **配置API密钥**

设置环境变量（推荐）：

```bash
# Linux/macOS
export DELILEGAL_APPID="你的appid"
export DELILEGAL_SECRET="你的secret"

# Windows (PowerShell)
$env:DELILEGAL_APPID="你的appid"
$env:DELILEGAL_SECRET="你的secret"

# Windows (CMD)
set DELILEGAL_APPID=你的appid
set DELILEGAL_SECRET=你的secret
```

或者在 `.env` 文件中配置：
```
DELILEGAL_APPID=你的appid
DELILEGAL_SECRET=你的secret
```

3. **配置Claude Desktop**

将 `claude_desktop_config.json` 内容复制到：
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

4. **重启Claude Desktop**

### 方式二：直接运行MCP服务

```bash
cd mcp-servers/delilegal-api
python server.py
```

## 使用示例

### 法律咨询
```
用户：上班途中发生车祸算工伤吗？
AI：[自动检索相关法条和案例，给出专业分析]
```

### 合同审查
```
用户：帮我审查这份租房合同
[上传合同文件]
AI：[分析风险条款，标注风险等级，给出修改建议]
```

### 文书生成
```
用户：帮我写一份民间借贷纠纷的起诉状
AI：[收集必要信息，生成规范起诉状]
```

## API说明

### 得理法律API

| 接口 | 功能 |
|------|------|
| `queryListLaw` | 法规检索 |
| `queryListCase` | 案例检索 |

**认证方式**：Header中添加 `appid` 和 `secret`

### 请求示例

**法规检索**：
```bash
curl -X POST 'https://openapi.delilegal.com/api/qa/v3/search/queryListLaw' \
  -H "Content-Type: application/json" \
  -H "appid: YOUR_APPID" \
  -H "secret: YOUR_SECRET" \
  -d '{
    "pageNo": 1,
    "pageSize": 5,
    "sortField": "correlation",
    "sortOrder": "desc",
    "condition": {
      "keywords": ["合同法"],
      "fieldName": "title"
    }
  }'
```

**案例检索**：
```bash
curl -X POST 'https://openapi.delilegal.com/api/qa/v3/search/queryListCase' \
  -H "Content-Type: application/json" \
  -H "appid: YOUR_APPID" \
  -H "secret: YOUR_SECRET" \
  -d '{
    "pageNo": 1,
    "pageSize": 5,
    "sortField": "correlation",
    "sortOrder": "desc",
    "condition": {
      "keywordArr": ["工伤"]
    }
  }'
```

## 配置参数

### 法规检索参数

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `fieldName` | 检索方式 | `title`(关键词), `semantic`(语义) |
| `keywords` | 搜索关键词 | 字符串数组 |

### 案例检索参数

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `keywordArr` | 关键词数组 | 与`longText`二选一 |
| `longText` | 长文本检索 | 与`keywordArr`二选一 |
| `courtLevelArr` | 法院层级 | `0`最高,`1`高级,`2`中级,`3`基层 |
| `caseYearStart/End` | 裁判年份区间 | 如 2020-2024 |
| `judgementTypeArr` | 文书类型 | `30`判决书,`31`裁决书,`32`调解书 |
| `sortField` | 排序字段 | `correlation`(相关性),`time`(时间) |

## 文件清单

| 文件 | 用途 |
|------|------|
| `src/legal_search.py` | 法律检索核心模块 |
| `src/legal_cli.py` | 命令行工具 |
| `src/legal_assistant.py` | 对话式助手 |
| `mcp-servers/delilegal-api/server.py` | 得理法律MCP服务 |
| `mcp-servers/doc-tools/server.py` | 文档处理MCP服务 |
| `skills/legal-expert/SKILL.md` | 法律专家Skill |
| `web/legal-ai-chat.html` | Web聊天界面 |
| `claude_desktop_config.json` | Claude Desktop配置 |
| `setup.sh` | 快速部署脚本 |

## 免责声明

本系统提供的所有法律分析、建议和文书仅供参考，不构成正式法律意见。对于具体法律问题，请咨询专业律师。

## License

MIT
