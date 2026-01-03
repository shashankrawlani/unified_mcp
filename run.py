#!/usr/bin/env python3
"""Entry point for unified MCP server."""

import asyncio

from src.unified_mcp.main import main

if __name__ == "__main__":
    asyncio.run(main())
