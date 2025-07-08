# FastAPI MCP Server

A comprehensive Model Context Protocol (MCP) server built with Python FastAPI and FastMCP, demonstrating the full capabilities of MCP including tools, resources, prompts, and web interface integration.

## 🚀 Features

- **MCP Tools**: Interactive functions that AI models can execute
- **MCP Resources**: Data sources that AI models can access
- **MCP Prompts**: Reusable templates for AI interactions
- **Web Dashboard**: FastAPI-powered web interface for monitoring
- **Database Integration**: SQLite database for persistent data
- **Comprehensive Logging**: Context-aware logging with MCP
- **Type Safety**: Full Pydantic validation for all inputs

## 🛠️ What is MCP?

The Model Context Protocol (MCP) is an open standard that enables AI models to securely connect with external data sources and tools. Think of it as a "USB-C for AI" - providing a standardized way to:

- **Expose Tools**: Let AI models execute functions and perform actions
- **Share Resources**: Provide AI models with access to data and information
- **Define Prompts**: Create reusable templates for AI interactions
- **Enable Sampling**: Allow two-way communication between servers and AI models

## 📁 Project Structure

```
mcp-fastapi-server/
├── main.py              # Combined MCP + FastAPI server
├── mcp_server.py        # Standalone MCP server
├── requirements.txt     # Python dependencies
├── templates/
│   └── dashboard.html   # Web dashboard template
├── static/             # Static assets (CSS, JS, images)
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip or uv package manager

### Installation

1. **Clone or create the project:**
```bash
git clone <repository-url>
cd mcp-fastapi-server
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the standalone MCP server:**
```bash
python mcp_server.py
```

4. **Or run the combined FastAPI + MCP server:**
```bash
python main.py
```

## 🔧 MCP Tools

The server provides several tools that AI models can use:

### `calculator`
Perform basic arithmetic operations (add, subtract, multiply, divide).

**Example usage:**
```json
{
  "operation": "add",
  "a": 15,
  "b": 27
}
```

### `create_user`
Create a new user in the database.

**Example usage:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### `create_task`
Create a new task for a user.

**Example usage:**
```json
{
  "user_id": 1,
  "title": "Complete project",
  "description": "Finish the MCP server implementation",
  "status": "pending"
}
```

### `get_user_tasks`
Get all tasks for a specific user.

### `update_task_status`
Update the status of a task (pending, in_progress, completed).

### `get_system_stats`
Get system statistics and overview.

## 📊 MCP Resources

Resources provide read-only access to data:

### `users://list`
Returns a JSON list of all users in the system.

### `user://{user_id}`
Returns detailed information about a specific user, including their tasks.

### `tasks://status/{status}`
Returns all tasks with a specific status (pending, in_progress, completed).

### `system://info`
Returns system information and statistics.

## 💬 MCP Prompts

Pre-defined prompt templates for common scenarios:

### `task_analysis_prompt`
Generate a prompt for analyzing a user's task patterns and productivity.

### `productivity_report_prompt`
Create a comprehensive productivity report based on system data.

### `user_onboarding_prompt`
Generate a personalized onboarding guide for new users.

## 🌐 Web Interface

When running `main.py`, you can access the web dashboard at:

- **Dashboard**: http://localhost:8000
- **API Users**: http://localhost:8000/api/users
- **API Tasks**: http://localhost:8000/api/tasks
- **MCP Info**: http://localhost:8000/mcp-info

## 🔗 Connecting MCP Clients

### Using Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "fastapi-mcp": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

### Using MCP Inspector

For testing and development:

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

### Using FastMCP CLI

```bash
fastmcp dev mcp_server.py
```

## 💾 Database

The server uses SQLite for persistent storage with two main tables:

- **users**: Store user information (id, name, email, created_at)
- **tasks**: Store tasks (id, user_id, title, description, status, created_at)

Sample data is automatically created on first run.

## 🧪 Example Interactions

Here are some example ways an AI model might interact with this server:

### Creating and Managing Tasks

```
AI: I'll help you create a new task. First, let me check the existing users.

[Uses users://list resource]

AI: I can see we have users Alice, Bob, and Carol. Let me create a task for Alice.

[Uses create_task tool with user_id=1, title="Review quarterly report"]

AI: Task created successfully! Now let me update its status to in_progress.

[Uses update_task_status tool with task_id=5, status="in_progress"]
```

### Generating Reports

```
AI: I'll generate a productivity report. Let me gather the system statistics first.

[Uses system://info resource]
[Uses tasks://status/completed resource]
[Uses tasks://status/pending resource]

AI: Based on the data, here's your productivity report...
```

### Data Analysis

```
AI: Let me analyze Alice's task patterns.

[Uses user://1 resource to get Alice's profile and tasks]
[Uses task_analysis_prompt to generate analysis framework]

AI: Alice has 3 tasks total: 1 pending, 1 in progress, and 1 completed...
```

## 🛡️ Security Considerations

- The server uses SQLite with proper SQL parameterization to prevent injection
- Input validation via Pydantic models
- Error handling with proper logging
- Context-aware operations with MCP logging

## 🎯 Use Cases

This MCP server is perfect for:

- **Task Management Systems**: AI assistants that help with project management
- **Data Analysis**: AI models that need to query and analyze task/user data
- **Productivity Tools**: AI assistants that provide insights and recommendations
- **Learning MCP**: Understanding how to build comprehensive MCP servers

## 🔧 Customization

### Adding New Tools

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int, ctx: Context) -> Dict[str, Any]:
    """Description of what this tool does"""
    await ctx.info(f"Executing my_new_tool with {param1}")
    # Your logic here
    return {"result": "success"}
```

### Adding New Resources

```python
@mcp.resource("my_resource://{param}")
def my_resource(param: str) -> str:
    """Description of this resource"""
    # Your logic here
    return json.dumps({"data": f"Resource for {param}"})
```

### Adding New Prompts

```python
@mcp.prompt()
def my_prompt(context: str) -> str:
    """Description of this prompt"""
    return f"Please analyze the following context: {context}"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Related Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 🆘 Support

If you run into issues:

1. Check the logs in the console
2. Verify your Python version (3.10+ required)
3. Ensure all dependencies are installed
4. Try the MCP Inspector for debugging

For questions or contributions, please open an issue or submit a pull request!

---

🤖 **Built with FastMCP & FastAPI** | Demonstrating the power of Model Context Protocol