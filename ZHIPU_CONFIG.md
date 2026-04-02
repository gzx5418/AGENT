# 智谱AI + Poco 配置指南

## 问题说明

Poco使用Claude Agent SDK，需要Anthropic兼容的API格式。智谱AI使用OpenAI兼容格式，需要通过转换层对接。

## 解决方案

### 方案一：使用 one-api 转换（推荐）

[one-api](https://github.com/songquanpeng/one-api) 是一个OpenAI API管理工具，支持将多种模型转换为统一格式。

#### 1. 部署one-api

```bash
# Docker部署
docker run -d --name one-api \
  -p 3001:3000 \
  -v /path/to/one-api:/data \
  justsong/one-api:latest

# 访问 http://localhost:3001
# 默认账号: root / 123456
```

#### 2. 配置智谱AI渠道

在one-api管理界面：
1. 进入 **渠道管理**
2. 添加渠道：
   - 类型：智谱AI
   - 名称：zhipu
   - Base URL：https://open.bigmodel.cn/api/paas/v4
   - API Key：你的智谱API Key
   - 模型：glm-4, glm-4-plus, glm-4-flash

#### 3. 创建令牌

1. 进入 **令牌管理**
2. 创建令牌（勾选允许的模型）
3. 复制生成的令牌

#### 4. 配置Poco

编辑 `poco-claw-main/.env`：

```bash
# Anthropic兼容配置（通过one-api）
ANTHROPIC_API_KEY=sk-xxx  # one-api生成的令牌
ANTHROPIC_BASE_URL=http://localhost:3001/v1

# 默认模型（必须是Anthropic格式）
DEFAULT_MODEL=claude-3-5-sonnet-20241022

# 模型列表（one-api会自动映射）
MODEL_LIST=["claude-3-5-sonnet-20241022","claude-3-opus-20240229"]
```

---

### 方案二：使用 OpenRouter

[OpenRouter](https://openrouter.ai/) 提供统一的API接口，支持智谱模型。

#### 1. 注册OpenRouter

访问 https://openrouter.ai/ 注册并获取API Key

#### 2. 配置Poco

```bash
ANTHROPIC_API_KEY=sk-or-xxx  # OpenRouter API Key
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=zhipu/glm-4-plus
MODEL_LIST=["zhipu/glm-4-plus","zhipu/glm-4"]
```

---

### 方案三：使用 SiliconFlow

[SiliconFlow](https://siliconflow.cn/) 提供国内模型API，部分支持Anthropic格式。

```bash
SILICONFLOW_API_KEY=xxx
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

---

### 方案四：直接修改Poco支持OpenAI（高级）

修改 `executor/app/core/engine.py`，将Claude Agent SDK替换为OpenAI SDK。

这个方案较复杂，需要：
1. 替换SDK依赖
2. 修改消息格式转换
3. 调整工具调用格式

---

## 推荐配置

**最简单方案**：使用 one-api + 智谱AI

```bash
# .env 配置
ANTHROPIC_API_KEY=sk-one-api-token
ANTHROPIC_BASE_URL=http://localhost:3001/v1
DEFAULT_MODEL=claude-3-5-sonnet-20241022

# 安全配置
BACKEND_SECRET_KEY=your-secret-key
INTERNAL_API_TOKEN=your-internal-token
CALLBACK_TOKEN=your-callback-token
```

## 启动Poco

```bash
cd poco-claw-main

# 复制配置
cp .env.example .env

# 编辑.env，填入上述配置
# 然后启动
docker compose up -d

# 访问
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```

## 测试

1. 访问 http://localhost:3000
2. 创建新任务
3. 选择MCP服务（法律检索）
4. 输入测试问题

## 注意事项

1. one-api需要和Poco在同一个Docker网络中
2. 确保API Key有足够余额
3. 智谱模型名称会被one-api自动映射
