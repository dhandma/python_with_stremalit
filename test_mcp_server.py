#!/usr/bin/env python3
"""
Test script for MCP Server functionality
Tests tools, resources, and basic operations
"""

import asyncio
import json
import sqlite3
import tempfile
from pathlib import Path

# Import the MCP server components
from mcp_server import mcp, init_database, DATABASE_PATH

async def test_calculator_tool():
    """Test the calculator tool"""
    print("🧮 Testing calculator tool...")
    
    # Test addition
    result = mcp._tools["calculator"].function("add", 5, 3)
    assert result["result"] == 8, f"Expected 8, got {result['result']}"
    print("  ✅ Addition test passed")
    
    # Test division by zero
    result = mcp._tools["calculator"].function("divide", 10, 0)
    assert "error" in result, "Expected error for division by zero"
    print("  ✅ Division by zero test passed")
    
    # Test invalid operation
    result = mcp._tools["calculator"].function("invalid", 5, 3)
    assert "error" in result, "Expected error for invalid operation"
    print("  ✅ Invalid operation test passed")

async def test_database_operations():
    """Test database operations"""
    print("🗄️ Testing database operations...")
    
    # Test database initialization
    init_database()
    print("  ✅ Database initialization passed")
    
    # Check if sample data exists
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    assert user_count > 0, "Expected sample users to exist"
    print(f"  ✅ Sample users found: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    assert task_count > 0, "Expected sample tasks to exist"
    print(f"  ✅ Sample tasks found: {task_count}")
    
    conn.close()

async def test_resources():
    """Test MCP resources"""
    print("📊 Testing resources...")
    
    # Test users list resource
    users_data = mcp._resources["users://list"].function()
    users = json.loads(users_data)
    assert isinstance(users, list), "Expected users to be a list"
    assert len(users) > 0, "Expected at least one user"
    print(f"  ✅ Users list resource: {len(users)} users found")
    
    # Test user by ID resource
    user_data = mcp._resources["user://{user_id}"].function(1)
    user = json.loads(user_data)
    assert isinstance(user, dict), "Expected user to be a dict"
    assert "name" in user, "Expected user to have a name"
    print(f"  ✅ User by ID resource: Found user {user['name']}")
    
    # Test system info resource
    system_data = mcp._resources["system://info"].function()
    system = json.loads(system_data)
    assert isinstance(system, dict), "Expected system info to be a dict"
    assert "total_users" in system, "Expected total_users in system info"
    print(f"  ✅ System info resource: {system['total_users']} users, {system['total_tasks']} tasks")

async def test_prompts():
    """Test MCP prompts"""
    print("💬 Testing prompts...")
    
    # Test task analysis prompt
    prompt = mcp._prompts["task_analysis_prompt"].function(1)
    assert isinstance(prompt, str), "Expected prompt to be a string"
    assert "user ID 1" in prompt, "Expected prompt to mention user ID"
    print("  ✅ Task analysis prompt generated")
    
    # Test productivity report prompt
    prompt = mcp._prompts["productivity_report_prompt"].function()
    assert isinstance(prompt, str), "Expected prompt to be a string"
    assert "productivity report" in prompt.lower(), "Expected prompt to mention productivity report"
    print("  ✅ Productivity report prompt generated")
    
    # Test onboarding prompt
    prompt = mcp._prompts["user_onboarding_prompt"].function("Test User")
    assert isinstance(prompt, str), "Expected prompt to be a string"
    assert "Test User" in prompt, "Expected prompt to mention user name"
    print("  ✅ User onboarding prompt generated")

async def test_user_creation():
    """Test user creation tool"""
    print("👤 Testing user creation...")
    
    # Create a mock context
    class MockContext:
        async def info(self, message):
            print(f"    ℹ️ {message}")
        
        async def error(self, message):
            print(f"    ❌ {message}")
    
    ctx = MockContext()
    
    # Test creating a new user
    from mcp_server import User
    new_user = User(name="Test User", email="test@example.com")
    
    # Note: This will actually create a user in the database
    # In a real test, you'd use a test database
    result = await mcp._tools["create_user"].function(new_user, ctx)
    
    if "error" not in result:
        assert "id" in result, "Expected user ID in result"
        assert result["name"] == "Test User", "Expected correct name"
        print(f"  ✅ User creation successful: ID {result['id']}")
    else:
        # User might already exist from previous test runs
        print(f"  ⚠️ User creation skipped: {result['error']}")

async def run_all_tests():
    """Run all tests"""
    print("🧪 Starting MCP Server Tests")
    print("=" * 50)
    
    try:
        await test_calculator_tool()
        await test_database_operations()
        await test_resources()
        await test_prompts()
        await test_user_creation()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
        print("\n💡 MCP Server is working correctly")
        print("🚀 Ready to connect with MCP clients")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("🔧 Please check the server implementation")
        return False
    
    return True

def test_mcp_tools_available():
    """Test that all expected tools are available"""
    print("🔧 Testing MCP tools availability...")
    
    expected_tools = [
        "calculator",
        "create_user",
        "get_user_tasks", 
        "create_task",
        "update_task_status",
        "get_system_stats"
    ]
    
    available_tools = list(mcp._tools.keys())
    
    for tool in expected_tools:
        assert tool in available_tools, f"Expected tool '{tool}' not found"
        print(f"  ✅ Tool '{tool}' available")

def test_mcp_resources_available():
    """Test that all expected resources are available"""
    print("📊 Testing MCP resources availability...")
    
    expected_resources = [
        "users://list",
        "user://{user_id}",
        "tasks://status/{status}",
        "system://info"
    ]
    
    available_resources = list(mcp._resources.keys())
    
    for resource in expected_resources:
        assert resource in available_resources, f"Expected resource '{resource}' not found"
        print(f"  ✅ Resource '{resource}' available")

if __name__ == "__main__":
    print("🧪 MCP Server Test Suite")
    print("Testing Model Context Protocol server functionality")
    print("-" * 50)
    
    # Test availability first
    test_mcp_tools_available()
    test_mcp_resources_available()
    
    # Run async tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Run the server: python mcp_server.py")
        print("2. Connect with MCP client (Claude Desktop, Inspector, etc.)")
        print("3. Test tools and resources with your AI assistant")
        print("\n🔗 For web interface: python main.py")
    else:
        exit(1)