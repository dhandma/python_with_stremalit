#!/usr/bin/env python3
"""
Standalone MCP Server using FastMCP
This file contains only the MCP server functionality for use with MCP clients
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict

import httpx
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# Configuration
DATABASE_PATH = "mcp_server.db"

# Initialize FastMCP server
mcp = FastMCP("Standalone-MCP-Server")

# Pydantic models for validation
class User(BaseModel):
    name: str
    email: str

class Task(BaseModel):
    user_id: int
    title: str
    description: str = ""
    status: str = "pending"

# Database initialization
def init_database():
    """Initialize SQLite database with sample data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("Alice Johnson", "alice@example.com"),
            ("Bob Smith", "bob@example.com"),
            ("Carol Davis", "carol@example.com")
        ]
        cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", sample_users)
        
        sample_tasks = [
            (1, "Complete project proposal", "Write and submit the Q1 project proposal", "pending"),
            (1, "Review code changes", "Review pull requests from team members", "in_progress"),
            (2, "Update documentation", "Update API documentation with new endpoints", "completed"),
            (3, "Team meeting", "Attend weekly team sync meeting", "pending")
        ]
        cursor.executemany(
            "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)", 
            sample_tasks
        )
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# MCP Tools
@mcp.tool()
def calculator(operation: str, a: float, b: float) -> Dict[str, Any]:
    """
    Perform basic arithmetic operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    
    Returns:
        Result of the calculation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else None
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}"}
    
    result = operations[operation](a, b)
    if result is None:
        return {"error": "Division by zero"}
    
    return {
        "operation": operation,
        "operands": [a, b],
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
async def create_user(user_data: User, ctx: Context) -> Dict[str, Any]:
    """
    Create a new user in the database.
    
    Args:
        user_data: User information including name and email
        ctx: MCP context for logging
    
    Returns:
        Created user information
    """
    await ctx.info(f"Creating user: {user_data.name}")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user_data.name, user_data.email)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await ctx.info(f"User created successfully with ID: {user_id}")
        
        return {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
    except sqlite3.IntegrityError:
        await ctx.error(f"User with email {user_data.email} already exists")
        return {"error": "Email already exists"}
    except Exception as e:
        await ctx.error(f"Database error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_user_tasks(user_id: int, ctx: Context) -> Dict[str, Any]:
    """
    Get all tasks for a specific user.
    
    Args:
        user_id: ID of the user
        ctx: MCP context for logging
    
    Returns:
        List of user's tasks
    """
    await ctx.info(f"Fetching tasks for user ID: {user_id}")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return {"error": f"User with ID {user_id} not found"}
        
        # Get user's tasks
        cursor.execute(
            "SELECT id, title, description, status, created_at FROM tasks WHERE user_id = ?",
            (user_id,)
        )
        tasks = cursor.fetchall()
        conn.close()
        
        return {
            "user": {
                "id": user_id,
                "name": user[0],
                "email": user[1]
            },
            "tasks": [
                {
                    "id": task[0],
                    "title": task[1],
                    "description": task[2],
                    "status": task[3],
                    "created_at": task[4]
                }
                for task in tasks
            ],
            "total_tasks": len(tasks)
        }
        
    except Exception as e:
        await ctx.error(f"Database error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def create_task(task_data: Task, ctx: Context) -> Dict[str, Any]:
    """
    Create a new task for a user.
    
    Args:
        task_data: Task information
        ctx: MCP context for logging
    
    Returns:
        Created task information
    """
    await ctx.info(f"Creating task: {task_data.title}")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT name FROM users WHERE id = ?", (task_data.user_id,))
        user = cursor.fetchone()
        if not user:
            return {"error": f"User with ID {task_data.user_id} not found"}
        
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)",
            (task_data.user_id, task_data.title, task_data.description, task_data.status)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await ctx.info(f"Task created successfully with ID: {task_id}")
        
        return {
            "id": task_id,
            "user_id": task_data.user_id,
            "user_name": user[0],
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        await ctx.error(f"Database error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def update_task_status(task_id: int, status: str, ctx: Context) -> Dict[str, Any]:
    """
    Update the status of a task.
    
    Args:
        task_id: ID of the task to update
        status: New status (pending, in_progress, completed)
        ctx: MCP context for logging
    
    Returns:
        Updated task information
    """
    valid_statuses = ["pending", "in_progress", "completed"]
    if status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {valid_statuses}"}
    
    await ctx.info(f"Updating task {task_id} status to {status}")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get current task info
        cursor.execute(
            "SELECT t.title, t.status, u.name FROM tasks t JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (task_id,)
        )
        current_task = cursor.fetchone()
        
        if not current_task:
            return {"error": f"Task with ID {task_id} not found"}
        
        old_status = current_task[1]
        
        # Update task status
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )
        
        conn.commit()
        conn.close()
        
        await ctx.info(f"Task {task_id} status updated from '{old_status}' to '{status}'")
        
        return {
            "id": task_id,
            "title": current_task[0],
            "user_name": current_task[2],
            "old_status": old_status,
            "new_status": status,
            "updated_at": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        await ctx.error(f"Database error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_system_stats(ctx: Context) -> Dict[str, Any]:
    """
    Get system statistics and overview.
    
    Args:
        ctx: MCP context for logging
    
    Returns:
        System statistics
    """
    await ctx.info("Generating system statistics")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        task_stats = dict(cursor.fetchall())
        
        # Get recent activity
        cursor.execute("""
            SELECT t.title, t.status, u.name, t.created_at
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
            LIMIT 5
        """)
        recent_tasks = [
            {
                "title": task[0],
                "status": task[1],
                "user_name": task[2],
                "created_at": task[3]
            }
            for task in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "total_users": user_count,
            "total_tasks": task_count,
            "task_statistics": task_stats,
            "recent_tasks": recent_tasks,
            "generated_at": datetime.now().isoformat(),
            "server_name": "Standalone-MCP-Server"
        }
        
    except Exception as e:
        await ctx.error(f"Database error: {str(e)}")
        return {"error": str(e)}

# MCP Resources
@mcp.resource("users://list")
def get_all_users() -> str:
    """Get a list of all users in the system"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users")
        users = cursor.fetchall()
        conn.close()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "created_at": user[3]
            })
        
        return json.dumps(user_list, indent=2)
    except Exception as e:
        return f"Error retrieving users: {str(e)}"

@mcp.resource("user://{user_id}")
def get_user_by_id(user_id: int) -> str:
    """Get detailed information about a specific user"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return f"User with ID {user_id} not found"
        
        # Get user's tasks
        cursor.execute("SELECT id, title, description, status, created_at FROM tasks WHERE user_id = ?", (user_id,))
        tasks = cursor.fetchall()
        conn.close()
        
        user_data = {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "created_at": user[3],
            "tasks": [
                {
                    "id": task[0],
                    "title": task[1],
                    "description": task[2],
                    "status": task[3],
                    "created_at": task[4]
                }
                for task in tasks
            ],
            "task_count": len(tasks)
        }
        
        return json.dumps(user_data, indent=2)
    except Exception as e:
        return f"Error retrieving user: {str(e)}"

@mcp.resource("tasks://status/{status}")
def get_tasks_by_status(status: str) -> str:
    """Get all tasks with a specific status"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.title, t.description, t.status, t.created_at, u.name, u.email
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
        """, (status,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task[0],
                "title": task[1],
                "description": task[2],
                "status": task[3],
                "created_at": task[4],
                "user_name": task[5],
                "user_email": task[6]
            })
        
        return json.dumps({
            "status": status,
            "tasks": task_list,
            "count": len(task_list)
        }, indent=2)
    except Exception as e:
        return f"Error retrieving tasks: {str(e)}"

@mcp.resource("system://info")
def get_system_info() -> str:
    """Get system information and statistics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        task_stats = dict(cursor.fetchall())
        
        conn.close()
        
        system_info = {
            "server_name": "Standalone-MCP-Server",
            "version": "1.0.0",
            "total_users": user_count,
            "total_tasks": task_count,
            "task_statistics": task_stats,
            "database_path": DATABASE_PATH,
            "timestamp": datetime.now().isoformat(),
            "available_tools": [
                "calculator",
                "create_user", 
                "get_user_tasks",
                "create_task",
                "update_task_status",
                "get_system_stats"
            ],
            "available_resources": [
                "users://list",
                "user://{user_id}",
                "tasks://status/{status}",
                "system://info"
            ]
        }
        
        return json.dumps(system_info, indent=2)
    except Exception as e:
        return f"Error retrieving system info: {str(e)}"

# MCP Prompts
@mcp.prompt()
def task_analysis_prompt(user_id: int) -> str:
    """Generate a prompt for analyzing a user's tasks"""
    return f"""
    Please analyze the tasks for user ID {user_id}. 
    
    Steps to follow:
    1. First, use the user://{user_id} resource to get the user's complete profile and tasks
    2. Then analyze the task distribution by status
    3. Look at task complexity based on descriptions
    4. Identify potential bottlenecks or areas for improvement
    5. Provide recommendations for task prioritization
    
    Focus on:
    - Task completion patterns
    - Workload balance
    - Priority suggestions
    - Efficiency improvements
    """

@mcp.prompt()
def productivity_report_prompt() -> str:
    """Generate a prompt for creating a productivity report"""
    return """
    Create a comprehensive productivity report for the task management system.
    
    Please follow these steps:
    
    1. Use the system://info resource to get overall statistics
    2. Use the tasks://status/completed resource to analyze completed work
    3. Use the tasks://status/pending resource to identify upcoming work
    4. Use the tasks://status/in_progress resource to see current workload
    5. Use the users://list resource to understand team size
    
    Generate insights about:
    - Overall team productivity metrics
    - Task completion rates by status
    - Workload distribution across users
    - Bottlenecks and improvement opportunities
    - Trends and patterns in task management
    - Recommendations for optimizing workflow
    
    Present the findings in a structured, actionable format.
    """

@mcp.prompt()
def user_onboarding_prompt(user_name: str) -> str:
    """Generate a personalized onboarding prompt for new users"""
    return f"""
    Welcome {user_name} to our MCP-powered task management system!
    
    I'm here to help you get started. Here's what I can do for you:
    
    🔧 **Tools I can use:**
    - create_user: Create a new user account
    - create_task: Add tasks to your workflow
    - get_user_tasks: View all your tasks
    - update_task_status: Mark tasks as pending, in_progress, or completed
    - calculator: Perform calculations for you
    - get_system_stats: Show system overview
    
    📊 **Information I can access:**
    - users://list: View all system users
    - user://{{user_id}}: Get detailed user profiles
    - tasks://status/{{status}}: View tasks by status
    - system://info: Get system statistics
    
    💡 **What would you like to do first?**
    - Create your first task
    - View existing users and their tasks
    - Get an overview of the system
    - Learn about task management best practices
    
    Just let me know how I can help you get productive!
    """

if __name__ == "__main__":
    print("Starting Standalone MCP Server...")
    print("Server will communicate via STDIO using the MCP protocol")
    print("Connect using any MCP client to interact with tools and resources")
    
    # Run the MCP server
    mcp.run()