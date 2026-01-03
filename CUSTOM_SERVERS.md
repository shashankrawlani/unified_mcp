# Adding Custom MCP Servers

To add a custom MCP server to the unified server, add it to the `mcp.json` configuration file.

## Configuration Format

Add your server to `mcp.json`:

```json
{
  "mcpServers": {
    "my_custom_server": {
      "command": "python",
      "args": ["/path/to/my_server.py"],
      "env": {
        "MY_API_KEY": "your_api_key",
        "MY_CONFIG": "custom_value"
      },
      "disabled": false
    }
  }
}
```

## NPM Package Servers

```json
{
  "mcpServers": {
    "my_npm_server": {
      "command": "npx",
      "args": ["my-mcp-server-package@latest"]
    }
  }
}
```

## Available Official Servers

- `@playwright/mcp@latest` - Web automation (22 tools)
- `@upstash/context7-mcp` - Documentation queries (2 tools)
- `@modelcontextprotocol/server-filesystem` - File operations
- `@modelcontextprotocol/server-brave-search` - Web search
- `@modelcontextprotocol/server-sqlite` - SQLite database
- `@modelcontextprotocol/server-github` - GitHub integration

## Server Management

- **Enable/Disable**: Set `"disabled": true` to disable a server
- **Environment Variables**: Use the `env` object to pass environment variables
- **Tool Prefixing**: All tools are automatically prefixed with server name (e.g., `playwright_navigate`)
- **Endpoints**: Each server is available at `http://localhost:3000/{server_name}/mcp`

## Built-in Tools

- `list_servers` - Show all configured servers and their status
- `list_tools` - Show all available tools from all mounted servers

## Testing

Use the MCP Inspector to test your configuration:

```bash
npx @modelcontextprotocol/inspector \
  --transport http \
  --url http://localhost:3000/mcp
```