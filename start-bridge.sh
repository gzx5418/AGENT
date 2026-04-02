#!/bin/bash

# 法律AI专家系统 - 快速启动脚本

echo "================================"
echo "法律AI专家系统 - 启动中..."
echo "================================"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "创建.env配置文件..."
    cat > .env << EOF
# 智谱AI配置
ZHIPU_API_KEY=你的智谱API密钥

# Poco安全配置
BACKEND_SECRET_KEY=legal-ai-secret-key-$(date +%s)
INTERNAL_API_TOKEN=internal-token-$(date +%s)
CALLBACK_TOKEN=callback-token-$(date +%s)

# 模型配置
DEFAULT_MODEL=claude-3-5-sonnet-20241022
MODEL_LIST=["claude-3-5-sonnet-20241022","claude-3-opus-20240229","claude-3-haiku-20240307"]
EOF
    echo "已创建 .env 文件，请编辑并填入你的智谱API密钥"
    echo "然后重新运行此脚本"
    exit 1
fi

# 启动API转换桥
echo "启动智谱API转换桥..."
cd api-bridge
pip install -r requirements.txt -q
python zhipu_bridge.py &
BRIDGE_PID=$!
cd ..

# 等待桥启动
sleep 3

# 启动Poco
echo "启动Poco框架..."
cd poco-claw-main

# 设置环境变量指向本地桥
export ANTHROPIC_API_KEY="${ZHIPU_API_KEY}"
export ANTHROPIC_BASE_URL="http://localhost:8080/v1"

# 启动Docker服务
docker compose up -d

echo ""
echo "================================"
echo "启动完成！"
echo "================================"
echo ""
echo "访问地址："
echo "  前端: http://localhost:3000"
echo "  API桥: http://localhost:8080"
echo ""
echo "停止服务："
echo "  cd poco-claw-main && docker compose down"
echo "  kill $BRIDGE_PID"
echo ""
