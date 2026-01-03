import asyncio
import json
import os
import signal

from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import StdioTransport

from .config import config

# Create unified MCP server
mcp = FastMCP("unified-mcp")
mounted_servers = {}
shutdown_event = asyncio.Event()

def load_mcp_servers():
    try:
        with open("mcp.json", "r") as f:
            data = json.load(f)
        return data.get("mcpServers", {})
    except Exception as e:
        print(f"Error loading mcp.json: {e}")
        return {}

async def cleanup_servers():
    """Cleanup mounted servers"""
    for name, client in mounted_servers.items():
        try:
            await client.close()
            print(f"Closed server: {name}")
        except Exception:
            pass
    mounted_servers.clear()

async def reload_servers():
    """Hot reload servers by unmounting and remounting"""
    print("Reloading servers...")
    await cleanup_servers()
    await setup_proxy_servers()
    print("Server reload complete")

async def setup_proxy_servers():
    """Setup and mount child MCP servers as proxies"""
    server_configs = load_mcp_servers()

    for name, server_config in server_configs.items():
        if server_config.get("disabled", False):
            print(f"Skipping disabled server: {name}")
            continue

        try:
            print(f"Setting up server: {name}")

            transport = StdioTransport(
                command=server_config["command"],
                args=server_config.get("args", []),
                env={**os.environ, **server_config.get("env", {})}
            )

            client = Client(transport)
            proxy_server = FastMCP.as_proxy(client, name=name)

            # Wait a moment for initialization
            await asyncio.sleep(1)

            mcp.mount(proxy_server, prefix=name)
            mounted_servers[name] = client

            print(f"Mounted server '{name}' at /{name}/mcp")

        except Exception as e:
            print(f"Failed to mount server '{name}': {e}")
            import traceback
            traceback.print_exc()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown_event.set()

@mcp.tool()
async def enable_server(server_name: str) -> str:
    """Enable a disabled MCP server with hot reload"""
    try:
        with open("mcp.json", "r") as f:
            data = json.load(f)

        if server_name not in data.get("mcpServers", {}):
            return f"Server '{server_name}' not found in configuration"

        data["mcpServers"][server_name]["disabled"] = False

        with open("mcp.json", "w") as f:
            json.dump(data, f, indent=2)

        await reload_servers()
        return f"Server '{server_name}' enabled and reloaded successfully."
    except Exception as e:
        return f"Error enabling server: {e}"

@mcp.tool()
async def disable_server(server_name: str) -> str:
    """Disable an enabled MCP server with hot reload"""
    try:
        with open("mcp.json", "r") as f:
            data = json.load(f)

        if server_name not in data.get("mcpServers", {}):
            return f"Server '{server_name}' not found in configuration"

        data["mcpServers"][server_name]["disabled"] = True

        with open("mcp.json", "w") as f:
            json.dump(data, f, indent=2)

        await reload_servers()
        return f"Server '{server_name}' disabled and reloaded successfully."
    except Exception as e:
        return f"Error disabling server: {e}"

@mcp.tool()
async def list_tools() -> str:
    """List all available tools from mounted servers"""
    try:
        tools = await mcp.get_tools()
        tool_list = []
        for name, tool in tools.items():
            tool_list.append(f"{name}: {tool.description or 'No description'}")
        return f"Total tools: {len(tools)}\n" + "\n".join(sorted(tool_list))
    except Exception as e:
        return f"Error listing tools: {e}"

@mcp.tool()
def list_servers() -> str:
    """List all configured MCP servers"""
    servers = load_mcp_servers()
    server_info = []
    for name, server_config in servers.items():
        status = "disabled" if server_config.get("disabled", False) else "enabled"
        endpoint = f"http://localhost:3000/{name}/mcp" if status == "enabled" else "N/A"
        server_info.append(f"{name}: {status} - {endpoint}")
    return "\n".join(server_info)

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    async def main():
        try:
            print("Setting up proxy servers...")
            await setup_proxy_servers()
            print(f"Starting unified MCP server on {config.host}:{config.port}")

            # Run server with shutdown handling
            server_task = asyncio.create_task(
                mcp.run_async(transport="streamable-http", host=config.host, port=config.port)
            )

            # Wait for shutdown signal
            await shutdown_event.wait()

            print("Shutting down server...")
            server_task.cancel()
            await cleanup_servers()
            print("Shutdown complete")

        except KeyboardInterrupt:
            print("\nReceived interrupt, shutting down...")
            await cleanup_servers()
        except Exception as e:
            print(f"Server error: {e}")
            await cleanup_servers()

    asyncio.run(main())


async def main():
    """Main entry point for the unified MCP server."""
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        print("Setting up proxy servers...")
        await setup_proxy_servers()
        print(f"Starting unified MCP server on {config.host}:{config.port}")

        # Run server with shutdown handling
        server_task = asyncio.create_task(
            mcp.run_async(transport="streamable-http", host=config.host, port=config.port)
        )

        # Wait for shutdown signal
        await shutdown_event.wait()

        print("Shutting down server...")
        server_task.cancel()
        await cleanup_servers()
        print("Shutdown complete")

    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
        await cleanup_servers()
    except Exception as e:
        print(f"Server error: {e}")
        await cleanup_servers()
