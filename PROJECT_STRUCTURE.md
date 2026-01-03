# Project Structure

## Unified MCP Server - Production Ready

```
unified_mcp/
├── src/unified_mcp/           # Main package
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   └── main.py               # Core server implementation
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests (mocked)
│   │   └── test_unified_mcp.py
│   └── integration/          # Integration tests (live server)
│       └── test_live_server.py
├── run.py                    # Entry point
├── mcp.json                  # Server configuration
├── pyproject.toml           # Project configuration
├── README.md                # Documentation
├── CUSTOM_SERVERS.md        # Server configuration guide
├── docker-compose.yml       # Docker setup
├── Dockerfile               # Container definition
└── requirements.txt         # Legacy requirements
```

## Key Features Implemented

### ✅ Core Functionality
- **Hot Reload**: Enable/disable servers without restart
- **Graceful Shutdown**: SIGTERM/SIGINT signal handling  
- **Server Management**: Custom tools for server control
- **Proxy Mounting**: Multiple MCP servers through single endpoint
- **Tool Prefixing**: All tools prefixed with server names

### ✅ Custom Tools
- `list_servers` - Show configured servers and status
- `list_tools` - Show all available tools from mounted servers
- `enable_server` - Enable disabled server with hot reload
- `disable_server` - Disable enabled server with hot reload

### ✅ Quality Assurance
- **Unit Tests**: Mocked tests for core functionality
- **Integration Tests**: Live server tests for custom tools only
- **Code Quality**: Ruff linting with zero issues
- **Type Safety**: Proper type annotations
- **Documentation**: Comprehensive README and guides

### ✅ Production Ready
- **Proper Package Structure**: src/ layout
- **Dependency Management**: uv with pyproject.toml
- **Docker Support**: Multi-stage builds
- **Error Handling**: Graceful error recovery
- **Logging**: Structured logging output

## Test Coverage

### Unit Tests (Mocked)
- Configuration loading
- Server enable/disable logic
- Error handling for non-existent servers
- Server listing functionality

### Integration Tests (Live Server)
- Custom tool functionality only
- Hot reload workflow testing
- Error scenarios with real server
- End-to-end server management

**Note**: Integration tests focus only on our custom tools, not third-party MCP server tools (playwright, context7, etc.)

## Usage

```bash
# Start server
uv run python run.py

# Run tests
uv run pytest tests/unit/     # Unit tests
uv run pytest tests/integration/  # Integration tests (requires running server)

# Code quality
uv run ruff check .
```