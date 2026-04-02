# Poco 法律AI专家集成指南

本指南说明如何将法律AI专家MCP服务集成到Poco框架中。

## 前提条件

1. Poco已部署并运行（Docker Compose）
2. 已安装Python 3.12+
3. 得理法律API的appid和secret

## 集成步骤

### 步骤1: 构建MCP服务Docker镜像

Poco在容器中运行，因此MCP服务也需要在容器中可访问。

```bash
# 进入项目目录
cd c:\Users\32212\Desktop\法律agent

# 构建法律MCP服务镜像
docker build -t legal-mcp-server:latest -f Dockerfile.mcp mcp-servers/
```

### 步骤2: 修改Poco的docker-compose.yml

在 `poco-claw-main/docker-compose.yml` 中添加法律MCP服务：

```yaml
services:
  # 添加法律MCP服务
  legal-mcp:
    image: legal-mcp-server:latest
    container_name: legal-mcp
    restart: unless-stopped
    environment:
      - DELILEGAL_APPID=QthdBErlyaYvyXul
      - DELILEGAL_SECRET=EC5D455E6BD348CE8E18BE05926D2EBE
    networks:
      - poco-network

  # 修改executor配置，添加MCP服务依赖
  executor:
    # ... 现有配置 ...
    depends_on:
      - legal-mcp
```

### 步骤3: 通过Poco UI配置MCP服务

1. 启动Poco: `docker compose up -d`
2. 访问 `http://localhost:3000`
3. 进入 **Capabilities > MCP Servers**
4. 点击 **Add Server**，添加以下配置：

#### 得理法律API MCP

```json
{
  "name": "delilegal-api",
  "description": "得理法律API - 法规和案例检索",
  "command": "python",
  "args": ["/app/server.py"],
  "env": {
    "DELILEGAL_APPID": "QthdBErlyaYvyXul",
    "DELILEGAL_SECRET": "EC5D455E6BD348CE8E18BE05926D2EBE"
  }
}
```

#### 文档处理MCP

```json
{
  "name": "doc-tools",
  "description": "法律文档处理 - 合同审查、文书生成",
  "command": "python",
  "args": ["/app/server.py"],
  "env": {}
}
```

### 步骤4: 创建法律专家Skill

1. 进入 **Capabilities > Skills**
2. 点击 **Import Skill**
3. 上传 `skills/legal-expert/SKILL.md` 或手动创建

### 步骤5: 测试

1. 创建新任务
2. 在配置中选择法律相关的MCP服务
3. 输入测试问题：
   - "上班途中车祸算工伤吗？"
   - "帮我审查这份合同"
   - "搜索合同纠纷相关案例"

## 可用的MCP工具

### 得理法律API (delilegal-api)

| 工具 | 功能 |
|------|------|
| `search_law` | 搜索法律法规 |
| `search_case` | 搜索司法案例 |

### 文档处理 (doc-tools)

| 工具 | 功能 |
|------|------|
| `analyze_contract` | 合同风险审查 |
| `analyze_judgment` | 判决书分析 |
| `extract_facts` | 事实提取 |
| `generate_complaint` | 生成起诉状 |
| `generate_defense` | 生成答辩状 |
| `generate_legal_opinion` | 生成法律意见书 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DELILEGAL_APPID` | 得理法律API的AppID | - |
| `DELILEGAL_SECRET` | 得理法律API的Secret | - |

## 故障排除

### MCP服务无法启动
- 检查Python依赖是否安装: `pip install mcp httpx`
- 检查环境变量是否正确设置

### API调用失败
- 确认appid和secret是否有效
- 检查网络连接

### 工具不显示
- 确认MCP服务已正确注册
- 重启Poco服务

## 独立使用（不依赖Poco）

如果只想在Claude Desktop中使用：

1. 复制 `claude_desktop_config.json` 的内容到Claude Desktop配置文件
2. 修改路径为绝对路径
3. 重启Claude Desktop

Windows配置文件位置:
`%APPDATA%\Claude\claude_desktop_config.json`
