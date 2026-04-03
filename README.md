# 法律 AI Agent

基于 `poco-claw` 工作流改造的法律智能体项目。当前版本已经完成：

- Web 聊天界面与后端运行链路打通
- Lite / Browser 两类 executor 权限问题修复
- `legal-search` 法律检索 MCP 标准化接入
- 对话会话内自动暴露 `search_law` / `search_case` 工具

## 目录结构

```text
法律agent/
├─ poco-claw-main/          # 主应用，包含 frontend / backend / executor / docker compose
├─ legal-mcp-server/        # 法律检索 MCP 服务
├─ src/                     # 额外的本地 Python 脚本
├─ web/                     # 独立静态页面原型
├─ mcp-servers/             # 其它 MCP 相关材料
└─ skills/                  # 自定义技能
```

## 核心能力

- 法律检索 MCP：
  - `search_law(query)`：检索法律法规
  - `search_case(keywords)`：检索案例
- Agent 执行环境：
  - 普通会话
  - 浏览器会话
  - 文件与工作区操作
- Poco Claw 原生能力：
  - Skills
  - MCP
  - 会话状态
  - Docker 沙箱执行

## 运行要求

- Docker Desktop
- 可用的大模型兼容接口
- 德理法律 API 凭证

需要配置的关键环境变量位于 [poco-claw-main/.env](/C:/Users/32212/Desktop/法律agent/poco-claw-main/.env)：

```env
ANTHROPIC_API_KEY=...
ANTHROPIC_BASE_URL=...
DEFAULT_MODEL=claude-sonnet-4-20250514

DELILEGAL_APPID=...
DELILEGAL_SECRET=...

BACKEND_SECRET_KEY=...
INTERNAL_API_TOKEN=...
CALLBACK_TOKEN=...
```

## 启动方式

在 [poco-claw-main](/C:/Users/32212/Desktop/法律agent/poco-claw-main) 目录执行：

```powershell
docker compose up -d
```

常用地址：

- 前端：`http://localhost:3000/zh`
- 后端文档：`http://localhost:8000/docs`
- 法律 MCP 健康检查：`http://localhost:8765/health`

## 当前接入状态

`legal-search` 已经接入到聊天执行链路，并在新会话中验证通过。

会话初始化时可以看到：

- `legal-search` 状态为 `connected`
- MCP 工具包含：
  - `mcp__legal-search__search_law`
  - `mcp__legal-search__search_case`

## 使用示例

可以直接在网页里问：

- “帮我检索和劳动合同解除有关的中国法律法规”
- “帮我找几个和民间借贷纠纷有关的判例”
- “先查法条，再总结相关裁判思路”

模型会在需要时自动调用法律 MCP。

## 这次关键改动

- 修复 executor 在 Docker 挂载工作区中的写权限问题
- 将 `legal-mcp-server` 改为标准 Streamable HTTP MCP 服务
- 修正 executor 访问法律 MCP 的地址与 Host 校验
- 验证浏览器模式和普通模式都能正常完成对话

## 开发说明

本仓库当前会产生一些运行时目录，例如：

- `poco-claw-main/oss_data/`
- `poco-claw-main/tmp_workspace/`

这些目录属于运行产物，不建议直接提交到 Git。
