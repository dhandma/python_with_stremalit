#!/usr/bin/env python3
"""
MCP Server Launcher
Provides different ways to run the MCP server
"""

import argparse
import sys
import subprocess
from pathlib import Path

def run_standalone_mcp():
    """Run the standalone MCP server (STDIO only)"""
    print("🚀 Starting Standalone MCP Server...")
    print("📡 Server will communicate via STDIO")
    print("🔗 Connect using any MCP client")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "mcp_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 MCP Server stopped")
    except FileNotFoundError:
        print("❌ Error: mcp_server.py not found")
        sys.exit(1)

def run_fastapi_web():
    """Run the FastAPI web server with MCP integration"""
    print("🚀 Starting FastAPI + MCP Server...")
    print("🌐 Web dashboard: http://localhost:8000")
    print("📡 MCP Server available via STDIO")
    print("🔗 API endpoints: /api/users, /api/tasks, /mcp-info")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 FastAPI + MCP Server stopped")
    except FileNotFoundError:
        print("❌ Error: main.py not found")
        sys.exit(1)

def run_with_inspector():
    """Run with MCP Inspector for development"""
    print("🚀 Starting MCP Server with Inspector...")
    print("🔍 Inspector will be available at http://localhost:5173")
    print("🧪 Perfect for testing and debugging")
    print("-" * 50)
    
    try:
        # Try to run with MCP inspector
        subprocess.run(["npx", "@modelcontextprotocol/inspector", "python", "mcp_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 MCP Inspector stopped")
    except FileNotFoundError:
        print("❌ Error: npx not found. Please install Node.js")
        print("💡 Falling back to standalone MCP server...")
        run_standalone_mcp()

def run_with_fastmcp_dev():
    """Run with FastMCP dev command"""
    print("🚀 Starting with FastMCP dev mode...")
    print("🔧 Development mode with hot reload")
    print("-" * 50)
    
    try:
        subprocess.run(["fastmcp", "dev", "mcp_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 FastMCP dev stopped")
    except FileNotFoundError:
        print("❌ Error: fastmcp not found. Please install fastmcp")
        print("💡 Run: pip install fastmcp")
        print("🔄 Falling back to standalone MCP server...")
        run_standalone_mcp()

def show_info():
    """Show information about the MCP server"""
    print("📋 MCP Server Information")
    print("=" * 50)
    print("🔧 Available Tools:")
    print("  • calculator - Perform arithmetic operations")
    print("  • create_user - Create new users")
    print("  • create_task - Create new tasks")
    print("  • get_user_tasks - Get user's tasks")
    print("  • update_task_status - Update task status")
    print("  • get_system_stats - Get system statistics")
    print("")
    print("📊 Available Resources:")
    print("  • users://list - List all users")
    print("  • user://{user_id} - Get user details")
    print("  • tasks://status/{status} - Get tasks by status")
    print("  • system://info - System information")
    print("")
    print("💬 Available Prompts:")
    print("  • task_analysis_prompt - Analyze user tasks")
    print("  • productivity_report_prompt - Generate productivity report")
    print("  • user_onboarding_prompt - User onboarding guide")
    print("")
    print("🔗 Connection Methods:")
    print("  • STDIO - Direct process communication")
    print("  • FastAPI - Web interface + MCP")
    print("  • MCP Inspector - Development testing")
    print("  • FastMCP Dev - Hot reload development")

def main():
    parser = argparse.ArgumentParser(
        description="MCP Server Launcher - Run the Model Context Protocol server in different modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_mcp_server.py                    # Run standalone MCP server
  python run_mcp_server.py --web              # Run with web interface
  python run_mcp_server.py --inspector        # Run with MCP Inspector
  python run_mcp_server.py --dev              # Run with FastMCP dev mode
  python run_mcp_server.py --info             # Show server information
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--web",
        action="store_true",
        help="Run FastAPI web server with MCP integration"
    )
    group.add_argument(
        "--inspector",
        action="store_true",
        help="Run with MCP Inspector for development/testing"
    )
    group.add_argument(
        "--dev",
        action="store_true",
        help="Run with FastMCP dev mode (hot reload)"
    )
    group.add_argument(
        "--info",
        action="store_true",
        help="Show information about the MCP server"
    )
    
    args = parser.parse_args()
    
    # Check if required files exist
    required_files = ["mcp_server.py"]
    if args.web:
        required_files.append("main.py")
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: {file} not found")
            print("💡 Make sure you're in the correct directory")
            sys.exit(1)
    
    # Run based on arguments
    if args.web:
        run_fastapi_web()
    elif args.inspector:
        run_with_inspector()
    elif args.dev:
        run_with_fastmcp_dev()
    elif args.info:
        show_info()
    else:
        # Default: run standalone MCP server
        run_standalone_mcp()

if __name__ == "__main__":
    main()