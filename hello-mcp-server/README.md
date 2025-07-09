# Hello MCP Server

A basic "Hello World" implementation of a Model Context Protocol (MCP) server. This project provides a simple foundation for building MCP servers and demonstrates basic tool functionality.

## About this Project

This project was created as a starting point for MCP server development. It includes two simple tools:
- `hello`: A greeting tool that says hello (optionally with a name)
- `echo`: An echo tool that repeats back messages

## LLM Model Information

This project was created using **Claude Sonnet 4** as the development assistant. Claude Sonnet 4 is Anthropic's latest large language model, designed for coding tasks, reasoning, and complex problem-solving.

## Features

- ✅ Basic MCP server implementation
- ✅ Two simple tools (hello and echo)
- ✅ Proper error handling
- ✅ Async/await support
- ✅ Standard input/output communication
- ✅ JSON schema validation for tool inputs

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the MCP server:
```bash
python main.py
```

## Usage

The server runs over standard input/output (stdio) and follows the MCP protocol. It can be integrated with any MCP-compatible client.

### Available Tools

#### `hello`
Greets the user with an optional name parameter.

**Parameters:**
- `name` (optional): The name to greet

**Example:**
```json
{
  "name": "hello",
  "arguments": {
    "name": "Alice"
  }
}
```

#### `echo`
Echoes back the provided message.

**Parameters:**
- `message` (required): The message to echo back

**Example:**
```json
{
  "name": "echo",
  "arguments": {
    "message": "Hello, World!"
  }
}
```

## Development

This is a basic template that you can extend with additional tools and functionality. The server uses the official MCP Python SDK for implementation.

### Adding New Tools

To add a new tool:

1. Add the tool definition to the `list_tools()` function
2. Add the tool handler to the `call_tool()` function
3. Implement your tool logic

### Architecture

- `main.py`: Core server implementation
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation

## License

This project is provided as-is for educational and development purposes.

## Next Steps

You can extend this basic server by:
- Adding more sophisticated tools
- Implementing resource management
- Adding configuration options
- Integrating with external APIs
- Adding logging and monitoring
- Implementing authentication if needed

Happy coding! 🚀