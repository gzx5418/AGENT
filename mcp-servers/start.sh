#!/bin/bash
# 法律MCP服务启动脚本

SERVICE=${1:-"delilegal-api"}

case $SERVICE in
    "delilegal-api")
        echo "Starting Delilegal API MCP Server..."
        python /app/delilegal-api/server.py
        ;;
    "doc-tools")
        echo "Starting Document Tools MCP Server..."
        python /app/doc-tools/server.py
        ;;
    "all")
        echo "Starting all MCP servers..."
        # 启动所有服务（需要进程管理器）
        python /app/delilegal-api/server.py &
        python /app/doc-tools/server.py &
        wait
        ;;
    *)
        echo "Usage: $0 [delilegal-api|doc-tools|all]"
        exit 1
        ;;
esac
