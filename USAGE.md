# MCP Server Usage Guide

This guide shows you how to get started with the FastAPI MCP Server.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or using a virtual environment (recommended)
python3 -m venv mcp_env
source mcp_env/bin/activate  # On Windows: mcp_env\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server

#### Option A: Standalone MCP Server (Recommended for AI clients)
```bash
python3 mcp_server.py
```

#### Option B: FastAPI Web Server + MCP
```bash
python3 main.py
```

#### Option C: Using the Launcher Script
```bash
# Default (standalone MCP)
python3 run_mcp_server.py

# With web interface
python3 run_mcp_server.py --web

# With MCP Inspector (for development)
python3 run_mcp_server.py --inspector

# Show server information
python3 run_mcp_server.py --info
```

### 3. Test the Server
```bash
python3 test_mcp_server.py
```

## 🔗 Connecting AI Clients

### Claude Desktop

Add this configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "fastapi-mcp": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

**Config file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### MCP Inspector (Development)

For testing and development:
```bash
npx @modelcontextprotocol/inspector python3 mcp_server.py
```

Then open http://localhost:5173 in your browser.

### FastMCP CLI

```bash
# Install FastMCP CLI
pip install fastmcp

# Run in development mode
fastmcp dev mcp_server.py
```

## 🛠️ Using the Tools

Once connected, you can ask your AI assistant to:

### Basic Operations
```
"Can you add 15 and 27 using the calculator?"
"What's 144 divided by 12?"
```

### User Management
```
"Create a new user named John Doe with email john@example.com"
"Show me all users in the system"
"Get details for user ID 1"
```

### Task Management
```
"Create a task for user 1: 'Review quarterly report'"
"Show me all pending tasks"
"Update task 2 status to completed"
"Get all tasks for user Alice"
```

### System Analysis
```
"Generate system statistics"
"Show me all completed tasks"
"Analyze user 1's task patterns"
"Create a productivity report"
```

### Weather Information
```
"Get weather for New York"
"What's the weather like in London?"
```

## 📊 Available Resources

Your AI can access these data sources:

- `users://list` - All users in the system
- `user://1` - Specific user details (replace 1 with user ID)
- `tasks://status/pending` - All pending tasks
- `tasks://status/completed` - All completed tasks
- `tasks://status/in_progress` - All in-progress tasks
- `system://info` - System statistics and information

## 💬 Example Conversations

### Task Management Scenario
```
You: "I need help managing my team's tasks. Can you show me what's currently in the system?"

AI: I'll help you get an overview of your task management system. Let me check the current state.

[AI uses system://info resource]

Based on the system data, you currently have:
- 3 users in the system
- 4 total tasks
- 2 pending tasks
- 1 in-progress task  
- 1 completed task

Would you like me to show you the details of any specific tasks or users?
```

### Productivity Analysis
```
You: "Can you analyze Alice's productivity and suggest improvements?"

AI: I'll analyze Alice's task patterns for you.

[AI uses user://1 resource to get Alice's profile]
[AI uses task_analysis_prompt to structure the analysis]

Based on Alice's current tasks:
- She has 2 tasks total
- 1 is in progress (Review code changes)
- 1 is pending (Complete project proposal)

Recommendations:
1. Focus on completing the in-progress task first
2. Break down the project proposal into smaller subtasks
3. Set specific deadlines for better time management
```

## 🌐 Web Interface

When running with `main.py`, visit:

- **Dashboard**: http://localhost:8000
- **Users API**: http://localhost:8000/api/users
- **Tasks API**: http://localhost:8000/api/tasks
- **MCP Info**: http://localhost:8000/mcp-info

## 🧪 Testing the Server

The project includes comprehensive tests:

```bash
python3 test_mcp_server.py
```

This will test:
- All MCP tools functionality
- Database operations
- Resource access
- Prompt generation
- Error handling

## 🔧 Customization

### Adding New Tools

Edit `mcp_server.py` and add:

```python
@mcp.tool()
async def my_custom_tool(param: str, ctx: Context) -> Dict[str, Any]:
    """Your custom tool description"""
    await ctx.info(f"Running custom tool with {param}")
    # Your logic here
    return {"result": "success", "param": param}
```

### Adding New Resources

```python
@mcp.resource("my_data://{id}")
def my_custom_resource(id: int) -> str:
    """Your custom resource description"""
    # Your logic here
    return json.dumps({"id": id, "data": "your_data"})
```

### Adding New Prompts

```python
@mcp.prompt()
def my_custom_prompt(context: str) -> str:
    """Your custom prompt description"""
    return f"Please analyze: {context}"
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**: Delete `mcp_server.db` and restart
   ```bash
   rm mcp_server.db
   python3 mcp_server.py
   ```

3. **Port Already in Use**: Change the port in `main.py`
   ```python
   uvicorn.run(web_app, host="0.0.0.0", port=8001)  # Changed from 8000
   ```

4. **MCP Client Connection Issues**: 
   - Use absolute paths in configuration
   - Ensure Python is in your PATH
   - Check that the server starts without errors

### Getting Help

1. Run the test suite: `python3 test_mcp_server.py`
2. Check server info: `python3 run_mcp_server.py --info`
3. Try the MCP Inspector for debugging
4. Review the logs in the terminal

## 🎯 Next Steps

1. **Connect your AI assistant** using the configuration above
2. **Experiment with the tools** by asking your AI to perform tasks
3. **Customize the server** by adding your own tools and resources
4. **Deploy in production** using Docker or cloud services

Happy building with MCP! 🚀