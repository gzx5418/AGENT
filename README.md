# 智能法律AI专家系统

基于 **poco-claw** 框架的真正法律智能体，具备任务规划、多工具协作、记忆系统等 Agent 能力。

## 🎯 项目特点

| 特性 | 说明 |
|------|------|
| 🧠 **智能规划** | 自动分解复杂法律任务 |
| 🔧 **多工具协作** | 法规检索 + 案例检索 + AI 分析 |
| 💾 **记忆系统** | 记住用户偏好和历史对话 |
| 🔄 **自主执行** | 循环执行直到任务完成 |
| 🌐 **Web 界面** | 统一对话模式，自动检索整合 |

## 📁 项目结构

```
法律agent/
├── poco-claw-main/              # poco-claw Agent 框架
│   ├── backend/                 # FastAPI 后端
│   ├── frontend/                # Next.js 前端
│   ├── executor/                # Agent 执行引擎
│   ├── executor_manager/        # 任务调度管理
│   ├── docker-compose.yml       # Docker 部署配置
│   └── .env                     # 环境配置
│
├── legal-mcp-server/            # 法律检索 MCP 服务
│   ├── server.py                # HTTP 服务（法规+案例检索）
│   ├── Dockerfile
│   └── requirements.txt
│
├── web/
│   └── legal-ai-chat.html       # 独立 Web 界面
│
├── mcp-servers/                 # MCP 服务（Claude Desktop）
│   ├── delilegal-api/           # 得理法律 API
│   └── doc-tools/               # 文档处理
│
├── src/                         # Python 源码
│   ├── legal_search.py
│   ├── legal_cli.py
│   └── legal_assistant.py
│
└── skills/legal-expert/         # 法律专家 Skill
    └── SKILL.md
```

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

1. **安装 Docker Desktop**

2. **配置环境变量**
   ```bash
   cd poco-claw-main
   # 编辑 .env 文件，填入你的 API Key
   ```

3. **启动服务**
   ```bash
   docker compose up -d
   ```

4. **访问界面**
   - poco-claw 前端: http://localhost:3000
   - 法律 MCP 服务: http://localhost:8765

### 方式二：独立 Web 界面

直接打开 `web/legal-ai-chat.html`，配置智谱 API Key 即可使用。

### 方式三：Claude Desktop

将 `claude_desktop_config.json` 复制到 Claude Desktop 配置目录。

## 🔧 环境配置

在 `poco-claw-main/.env` 中配置：

```bash
# 智谱 AI（Anthropic 兼容端点）
ANTHROPIC_API_KEY=你的智谱API_KEY
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
DEFAULT_MODEL=claude-sonnet-4-20250514

# 得理法律 API
DELILEGAL_APPID=你的appid
DELILEGAL_SECRET=你的secret

# 安全配置
BACKEND_SECRET_KEY=your-secret-key
INTERNAL_API_TOKEN=your-token
CALLBACK_TOKEN=your-token
```

## 🛠️ 功能模块

### 法律检索工具

| 工具 | 功能 | 参数 |
|------|------|------|
| `search_law` | 法规检索 | `query`: 关键词 |
| `search_case` | 案例检索 | `keywords`: 关键词数组 |

### Agent 能力

- ✅ **任务规划**: 自动分解复杂问题
- ✅ **工具选择**: 智能判断调用哪个工具
- ✅ **结果整合**: 综合多源信息生成回答
- ✅ **记忆系统**: 可启用 mem0 记忆

## 📖 使用示例

### 法律咨询
```
用户：上班途中发生车祸算工伤吗？

Agent 执行流程：
1. 理解问题 → 识别为工伤法律问题
2. 调用 search_law("工伤认定") → 检索法规
3. 调用 search_case(["工伤", "交通事故"]) → 检索案例
4. 整合分析 → 给出专业回答
```

### 合同审查
```
用户：帮我审查这份租房合同

Agent 执行流程：
1. 读取合同文件
2. 识别风险条款
3. 标注风险等级
4. 提供修改建议
```

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────┐
│                   用户界面                           │
│  ┌──────────────┐    ┌──────────────────────────┐  │
│  │ poco-claw    │    │  独立 Web 界面            │  │
│  │ (localhost:3000)│    │  (legal-ai-chat.html)    │  │
│  └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  Agent 核心                          │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ 任务规划     │ ←→ │ 工具调度     │              │
│  └──────────────┘    └──────────────┘              │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ 记忆系统     │    │ 结果整合     │              │
│  └──────────────┘    └──────────────┘              │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  MCP 工具层                          │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ 法规检索     │    │ 案例检索     │              │
│  │ search_law   │    │ search_case  │              │
│  └──────────────┘    └──────────────┘              │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  外部 API                            │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ 智谱 AI      │    │ 得理法律 API │              │
│  └──────────────┘    └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

## 📦 Docker 服务

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 3000 | Web 前端 |
| backend | 8000 | API 后端 |
| executor-manager | 8001 | 任务调度 |
| legal-mcp | 8765 | 法律检索服务 |
| postgres | 5432 | 数据库 |
| rustfs | 9000 | S3 存储 |

## 📝 API 说明

### 法律检索 API

**法规检索**：
```bash
curl -X POST http://localhost:8765/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "search_law", "arguments": {"query": "工伤认定"}}'
```

**案例检索**：
```bash
curl -X POST http://localhost:8765/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "search_case", "arguments": {"keywords": ["工伤", "赔偿"]}}'
```

## 🔐 安全说明

- ⚠️ 不要在代码中硬编码 API 密钥
- ✅ 使用 `.env` 文件管理敏感配置
- ✅ `.env` 文件已添加到 `.gitignore`

## 📄 License

MIT

## 🙏 致谢

- [poco-claw](https://github.com/poco-ai/poco-claw) - Agent 框架
- [得理法律](https://www.delilegal.com/) - 法律数据 API
- [智谱 AI](https://open.bigmodel.cn/) - 大模型服务
