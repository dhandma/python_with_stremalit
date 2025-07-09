#!/usr/bin/env python3
"""
Basic Hello World MCP Server
A simple Model Context Protocol server for demonstration purposes.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create the server instance
server = Server("hello-mcp-server")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="hello",
            description="A simple greeting tool that says hello",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name to greet (optional)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="echo",
            description="Echo back the provided message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    if name == "hello":
        name_arg = arguments.get("name", "World")
        return [
            TextContent(
                type="text",
                text=f"Hello, {name_arg}! This is a basic MCP server greeting."
            )
        ]
    elif name == "echo":
        message = arguments.get("message", "")
        return [
            TextContent(
                type="text",
                text=f"Echo: {message}"
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hello-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())