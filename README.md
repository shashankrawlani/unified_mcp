# Unified MCP Server

A unified MCP server that mounts multiple MCP servers using a `mcp.json` configuration file, similar to Claude Desktop and Cursor.

## Quick Start

1. **Configure servers in `mcp.json`:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "context7": {
      "command": "npx",
      "args": ["@upstash/context7-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/tmp"],
      "disabled": true
    }
  }
}
```

2. **Run with Docker:**
```bash
docker-compose up --build
```

3. **Or run locally:**
```bash
uv run main.py
```

## Features

- **Single Endpoint**: Access all MCP servers through `http://localhost:3000/mcp`
- **Tool Prefixing**: All tools are prefixed with server name (e.g., `playwright_navigate`)
- **Dynamic Mounting**: Add/remove servers by editing `mcp.json` and restarting
- **Built-in Management**: Use `list_servers` and `list_tools` to inspect configuration
- **HTTP Streaming**: Full MCP-over-HTTP support with streaming protocol

## Configuration

### mcp.json Format

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "disabled": false
    }
  }
}
```

- `command`: Executable to run
- `args`: Command line arguments
- `env`: Environment variables (merged with system env)
- `disabled`: Set to `true` to disable the server

### Available Official Servers

- `@playwright/mcp@latest` - Web automation (22 tools)
- `@upstash/context7-mcp` - Documentation queries (2 tools)
- `@modelcontextprotocol/server-filesystem` - File operations
- `@modelcontextprotocol/server-brave-search` - Web search
- `@modelcontextprotocol/server-sqlite` - SQLite database
- `@modelcontextprotocol/server-github` - GitHub integration

## Tools

### Built-in Tools
- `list_servers` - Show all configured servers and their status
- `list_tools` - Show all available tools from mounted servers

### Mounted Server Tools
All tools from mounted servers are prefixed with the server name:
- `playwright_navigate` - Navigate to a URL
- `playwright_click` - Click on elements
- `context7_query-docs` - Query documentation
- `context7_resolve-library-id` - Resolve library IDs

## Testing

Use the MCP Inspector to test your server:

```bash
npx @modelcontextprotocol/inspector \
  --transport http \
  --url http://localhost:3000/mcp
```

## Environment Variables

- `HOST` - Server host (default: localhost)
- `PORT` - Server port (default: 3000)
- `DEBUG` - Enable debug logging (default: false)