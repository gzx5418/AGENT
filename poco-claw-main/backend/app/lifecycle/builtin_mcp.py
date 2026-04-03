import logging
import os

from sqlalchemy.orm import Session

from app.models.mcp_server import McpServer

logger = logging.getLogger(__name__)

# 系统级用户 ID，用于内置 MCP 服务器
SYSTEM_USER_ID = "system"


class McpServerBootstrapService:
    """Bootstrap service for built-in MCP servers."""

    # 内置 MCP 服务器配置
    BUILTIN_SERVERS = [
        {
            "name": "legal-search",
            "description": "法律检索服务 - 提供法规检索(search_law)和案例检索(search_case)功能",
            "scope": "system",
            "server_config": {
                "mcpServers": {
                    "legal-search": {
                        "type": "http",
                        "url": os.environ.get("LEGAL_MCP_URL", "http://legal-mcp:8765/mcp"),
                        "headers": {
                            "Content-Type": "application/json"
                        }
                    }
                }
            },
        }
    ]

    @classmethod
    def bootstrap_builtin_servers(cls, db: Session) -> None:
        """Bootstrap built-in MCP servers.

        Creates system-level MCP servers that are available to all users.
        """
        for server_config in cls.BUILTIN_SERVERS:
            # 检查是否已存在
            existing = (
                db.query(McpServer)
                .filter(
                    McpServer.name == server_config["name"],
                    McpServer.owner_user_id == SYSTEM_USER_ID,
                )
                .first()
            )

            if existing:
                logger.debug(
                    f"Built-in MCP server '{server_config['name']}' already exists, skipping"
                )
                continue

            # 创建新的 MCP 服务器
            server = McpServer(
                name=server_config["name"],
                description=server_config["description"],
                scope=server_config["scope"],
                owner_user_id=SYSTEM_USER_ID,
                server_config=server_config["server_config"],
            )
            db.add(server)
            logger.info(f"Created built-in MCP server: {server_config['name']}")

        db.commit()
