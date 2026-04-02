#!/bin/bash

# 法律AI专家系统 - 快速部署脚本

echo "================================"
echo "法律AI专家系统 - 快速部署"
echo "================================"

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_SERVERS_DIR="$PROJECT_DIR/mcp-servers"

echo -e "${YELLOW}项目目录: $PROJECT_DIR${NC}"

# 检查Python
echo -e "\n${YELLOW}[1/4] 检查Python环境...${NC}"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "${GREEN}✓ 已安装: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ 未找到Python，请先安装Python 3.12+${NC}"
    exit 1
fi

# 安装MCP服务依赖
echo -e "\n${YELLOW}[2/4] 安装MCP服务依赖...${NC}"
pip install mcp httpx
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 配置API密钥
echo -e "\n${YELLOW}[3/4] 配置API密钥...${NC}"
read -p "请输入得理法律API的appid: " APPID
read -p "请输入得理法律API的secret: " SECRET

# 更新配置文件
CONFIG_FILE="$MCP_SERVERS_DIR/delilegal-api/config.py"
cat > "$CONFIG_FILE" << EOF
"""
得理法律API配置
"""

# API认证信息
APPID = "$APPID"
SECRET = "$SECRET"

# API基础URL
BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"

# 默认配置
DEFAULT_PAGE_SIZE = 5
DEFAULT_SORT_FIELD = "correlation"
DEFAULT_SORT_ORDER = "desc"
EOF

echo -e "${GREEN}✓ API配置已保存${NC}"

# 测试API连接
echo -e "\n${YELLOW}[4/4] 测试API连接...${NC}"
TEST_RESULT=$(curl -s -X POST 'https://openapi.delilegal.com/api/qa/v3/search/queryListLaw' \
    -H "Content-Type: application/json" \
    -H "appid: $APPID" \
    -H "secret: $SECRET" \
    -d '{"pageNo":1,"pageSize":1,"sortField":"correlation","sortOrder":"desc","condition":{"keywords":["测试"],"fieldName":"title"}}')

if echo "$TEST_RESULT" | grep -q '"success"'; then
    echo -e "${GREEN}✓ API连接成功${NC}"
else
    echo -e "${YELLOW}⚠ API返回异常，请检查密钥是否正确${NC}"
    echo "返回: $TEST_RESULT"
fi

# 完成
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "下一步操作："
echo ""
echo "1. 在Claude Desktop中使用:"
echo "   复制 claude_desktop_config.json 内容到:"
echo "   Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "2. 集成到Poco:"
echo "   参考 POCO_INTEGRATION.md 文档"
echo ""
echo "3. 直接测试MCP服务:"
echo "   cd $MCP_SERVERS_DIR/delilegal-api"
echo "   python server.py"
echo ""
