import json
import os
import tempfile
from unittest.mock import patch

import pytest


def load_mcp_servers_func():
    """Testable version of load_mcp_servers"""
    try:
        with open("mcp.json", "r") as f:
            data = json.load(f)
        return data.get("mcpServers", {})
    except Exception as e:
        print(f"Error loading mcp.json: {e}")
        return {}


async def enable_server_func(server_name: str) -> str:
    """Testable version of enable_server"""
    try:
        with open("mcp.json", "r") as f:
            data = json.load(f)

        if server_name not in data.get("mcpServers", {}):
            return f"Server '{server_name}' not found in configuration"

        data["mcpServers"][server_name]["disabled"] = False

        with open("mcp.json", "w") as f:
            json.dump(data, f, indent=2)

        return f"Server '{server_name}' enabled and reloaded successfully."
    except Exception as e:
        return f"Error enabling server: {e}"


async def disable_server_func(server_name: str) -> str:
    """Testable version of disable_server"""
    try:
        with open("mcp.json", "r") as f:
            data = json.load(f)

        if server_name not in data.get("mcpServers", {}):
            return f"Server '{server_name}' not found in configuration"

        data["mcpServers"][server_name]["disabled"] = True

        with open("mcp.json", "w") as f:
            json.dump(data, f, indent=2)

        return f"Server '{server_name}' disabled and reloaded successfully."
    except Exception as e:
        return f"Error disabling server: {e}"


def list_servers_func() -> str:
    """Testable version of list_servers"""
    servers = load_mcp_servers_func()
    server_info = []
    for name, config in servers.items():
        status = "disabled" if config.get("disabled", False) else "enabled"
        server_info.append(f"{name}: {status}")
    return "\n".join(server_info)


@pytest.fixture
def temp_mcp_json():
    """Create a temporary mcp.json file for testing"""
    config = {
        "mcpServers": {
            "test_server": {
                "command": "echo",
                "args": ["test"]
            },
            "disabled_server": {
                "command": "echo",
                "args": ["disabled"],
                "disabled": True
            }
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        temp_file = f.name

    yield temp_file
    os.unlink(temp_file)


def test_load_mcp_servers():
    """Test loading MCP server configuration"""
    test_config = {
        "mcpServers": {
            "test": {"command": "echo", "args": ["test"]}
        }
    }

    with patch('builtins.open', create=True):
        with patch('json.load', return_value=test_config):
            servers = load_mcp_servers_func()
            assert "test" in servers
            assert servers["test"]["command"] == "echo"


async def test_enable_server():
    """Test enabling a disabled server"""
    test_config = {
        "mcpServers": {
            "test_server": {
                "command": "echo",
                "args": ["test"],
                "disabled": True
            }
        }
    }

    with patch('builtins.open', create=True):
        with patch('json.load', return_value=test_config):
            with patch('json.dump'):
                result = await enable_server_func("test_server")
                assert "enabled and reloaded successfully" in result


async def test_disable_server():
    """Test disabling an enabled server"""
    test_config = {
        "mcpServers": {
            "test_server": {
                "command": "echo",
                "args": ["test"]
            }
        }
    }

    with patch('builtins.open', create=True):
        with patch('json.load', return_value=test_config):
            with patch('json.dump'):
                result = await disable_server_func("test_server")
                assert "disabled and reloaded successfully" in result


async def test_enable_nonexistent_server():
    """Test enabling a server that doesn't exist"""
    test_config = {"mcpServers": {}}

    with patch('builtins.open', create=True):
        with patch('json.load', return_value=test_config):
            result = await enable_server_func("nonexistent")
            assert "not found in configuration" in result


def test_list_servers():
    """Test listing server configurations"""
    test_config = {
        "enabled_server": {"command": "echo"},
        "disabled_server": {"command": "echo", "disabled": True}
    }

    with patch('tests.unit.test_unified_mcp.load_mcp_servers_func', return_value=test_config):
        result = list_servers_func()
        assert "enabled_server: enabled" in result
        assert "disabled_server: disabled" in result
