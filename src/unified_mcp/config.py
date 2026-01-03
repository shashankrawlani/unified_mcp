import json
import os
from typing import Dict, List

from pydantic import BaseModel


class MCPServerConfig(BaseModel):
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}
    disabled: bool = False

class UnifiedMCPConfig(BaseModel):
    name: str = "Unified MCP Server"
    version: str = "1.0.0"
    host: str = os.getenv("HOST", "localhost")
    port: int = int(os.getenv("PORT", "3000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    def load_mcp_config(self) -> List[MCPServerConfig]:
        """Load MCP servers from mcp.json file"""
        try:
            with open("mcp.json", "r") as f:
                data = json.load(f)

            servers = []
            for name, config in data.get("mcpServers", {}).items():
                if config.get("disabled", False):
                    continue

                # Merge environment variables
                env = {**config.get("env", {}), **os.environ}

                servers.append(MCPServerConfig(
                    name=name,
                    command=config["command"],
                    args=config.get("args", []),
                    env=env
                ))

            return servers
        except FileNotFoundError:
            print("mcp.json not found, using default configuration")
            return self._default_servers()
        except Exception as e:
            print(f"Error loading mcp.json: {e}")
            return self._default_servers()

    def _default_servers(self) -> List[MCPServerConfig]:
        """Fallback to environment-based configuration"""
        servers = []

        if os.getenv("ENABLE_PLAYWRIGHT", "true").lower() == "true":
            servers.append(MCPServerConfig(
                name="playwright",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-playwright"],
                env={
                    "PLAYWRIGHT_HEADLESS": os.getenv("PLAYWRIGHT_HEADLESS", "true"),
                    "PLAYWRIGHT_TIMEOUT": os.getenv("PLAYWRIGHT_TIMEOUT", "30000")
                }
            ))

        return servers

config = UnifiedMCPConfig()
