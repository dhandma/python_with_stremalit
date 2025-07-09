#!/usr/bin/env python3
"""
Simple test script for the Hello MCP Server
This script demonstrates basic interaction with the MCP server.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict


async def test_mcp_server():
    """Test the MCP server with sample requests."""
    print("Testing Hello MCP Server...")
    print("=" * 40)
    
    # Test data
    test_requests = [
        {
            "description": "Test hello tool without name",
            "request": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "hello",
                    "arguments": {}
                }
            }
        },
        {
            "description": "Test hello tool with name",
            "request": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "hello",
                    "arguments": {"name": "Alice"}
                }
            }
        },
        {
            "description": "Test echo tool",
            "request": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "echo",
                    "arguments": {"message": "Hello from the test script!"}
                }
            }
        }
    ]
    
    print("Note: This is a basic test structure.")
    print("To fully test the MCP server, you would need an MCP client.")
    print("\nTest requests that could be sent to the server:")
    
    for i, test in enumerate(test_requests, 1):
        print(f"\n{i}. {test['description']}")
        print("Request:")
        print(json.dumps(test['request'], indent=2))
    
    print("\n" + "=" * 40)
    print("To run the actual server, use: python main.py")
    print("The server will wait for MCP protocol messages on stdin.")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())