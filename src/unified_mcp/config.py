import json
import os
from typing import Dict, List

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class MCPServerConfig(BaseModel):
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}
    disabled: bool = False

class UnifiedMCPConfig(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    name: str = "Unified MCP Server"
    version: str = "1.0.0"
    host: str = "localhost"
    port: int = 8929
    debug: bool = False

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
                args=["@playwright/mcp@latest"],
                env={
                    "PLAYWRIGHT_HEADLESS": os.getenv("PLAYWRIGHT_HEADLESS", "true"),
                    "PLAYWRIGHT_TIMEOUT": os.getenv("PLAYWRIGHT_TIMEOUT", "30000")
                }
            ))

        if os.getenv("ENABLE_CONTEXT7", "true").lower() == "true":
            servers.append(MCPServerConfig(
                name="context7",
                command="npx",
                args=["@upstash/context7-mcp"],
                env={
                    "CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", "")
                }
            ))

        return servers

config = UnifiedMCPConfig()
