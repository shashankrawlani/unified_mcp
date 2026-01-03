import asyncio
import subprocess
import time
from pathlib import Path

import httpx
import pytest


@pytest.fixture(scope="module")
def mcp_server():
    """Start the unified MCP server for integration testing."""
    # Start server in background
    process = subprocess.Popen(
        ["uv", "run", "python", "src/unified_mcp/main.py"],
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(8)

    yield process

    # Cleanup
    process.terminate()
    process.wait()


@pytest.mark.asyncio
async def test_list_servers_tool(mcp_server):
    """Test our custom list_servers tool."""
    async with httpx.AsyncClient() as client:
        session_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Session-ID": "test-session"
        }

        # Initialize session
        await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
        )

        # Call our custom list_servers tool
        response = await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "list_servers",
                    "arguments": {}
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        result_text = data["result"]["content"][0]["text"]
        assert "playwright: enabled" in result_text
        assert "context7: enabled" in result_text


@pytest.mark.asyncio
async def test_list_tools_custom(mcp_server):
    """Test our custom list_tools tool."""
    async with httpx.AsyncClient() as client:
        session_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Session-ID": "test-session-2"
        }

        # Initialize session
        await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
        )

        # Call our custom list_tools tool
        response = await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "list_tools",
                    "arguments": {}
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        result_text = data["result"]["content"][0]["text"]

        # Check our custom tools are present
        assert "list_servers:" in result_text
        assert "list_tools:" in result_text
        assert "enable_server:" in result_text
        assert "disable_server:" in result_text
        assert "Total tools:" in result_text


@pytest.mark.asyncio
async def test_disable_enable_server_workflow(mcp_server):
    """Test our custom enable/disable server workflow."""
    async with httpx.AsyncClient() as client:
        session_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Session-ID": "test-session-3"
        }

        # Initialize session
        await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
        )

        # Disable context7 server
        disable_response = await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "disable_server",
                    "arguments": {"server_name": "context7"}
                }
            }
        )

        assert disable_response.status_code == 200
        data = disable_response.json()
        result_text = data["result"]["content"][0]["text"]
        assert "disabled and reloaded successfully" in result_text

        # Wait for hot reload
        await asyncio.sleep(3)

        # Verify server is disabled
        list_response = await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "list_servers",
                    "arguments": {}
                }
            }
        )

        assert list_response.status_code == 200
        data = list_response.json()
        result_text = data["result"]["content"][0]["text"]
        assert "context7: disabled" in result_text

        # Re-enable context7 server
        enable_response = await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "enable_server",
                    "arguments": {"server_name": "context7"}
                }
            }
        )

        assert enable_response.status_code == 200
        data = enable_response.json()
        result_text = data["result"]["content"][0]["text"]
        assert "enabled and reloaded successfully" in result_text


@pytest.mark.asyncio
async def test_enable_nonexistent_server(mcp_server):
    """Test enabling a server that doesn't exist."""
    async with httpx.AsyncClient() as client:
        session_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Session-ID": "test-session-4"
        }

        # Initialize session
        await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
        )

        # Try to enable non-existent server
        response = await client.post(
            "http://localhost:8929/mcp",
            headers=session_headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "enable_server",
                    "arguments": {"server_name": "nonexistent"}
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        result_text = data["result"]["content"][0]["text"]
        assert "not found in configuration" in result_text
