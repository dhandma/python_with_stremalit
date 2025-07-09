#!/bin/bash
# Simple script to run the Hello MCP Server

echo "Starting Hello MCP Server..."
echo "Press Ctrl+C to stop the server."
echo "=========================================="

# Check if dependencies are installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "Installing MCP dependencies..."
    pip install -r requirements.txt
fi

# Run the server
python3 main.py