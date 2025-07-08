#!/usr/bin/env python3
"""
Comprehensive MCP Server using FastAPI and FastMCP
Demonstrates tools, resources, prompts, and web interface integration
"""

import asyncio
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# Configuration
DATABASE_PATH = "mcp_server.db"
API_BASE_URL = "https://jsonplaceholder.typicode.com"

# Initialize FastMCP server
mcp = FastMCP("FastAPI-MCP-Server", dependencies=["fastapi", "httpx", "aiosqlite"])

# Initialize FastAPI app for web interface
web_app = FastAPI(title="MCP Server Dashboard", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Database setup
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

# Initialize database on startup
init_database()

# Pydantic models for validation
class User(BaseModel):
    name: str
    email: str

class Task(BaseModel):
    user_id: int
    title: str
    description: str = ""
    status: str = "pending"

class WeatherRequest(BaseModel):
    city: str
    units: str = "metric"

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
        cursor.execute("SELECT id FROM users WHERE id = ?", (task_data.user_id,))
        if not cursor.fetchone():
            return {"error": f"User with ID {task_data.user_id} not found"}
        
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)",
            (task_data.user_id, task_data.title, task_data.description, task_data.status)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": task_id,
            "user_id": task_data.user_id,
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        await ctx.error(f"Database error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def fetch_weather(city: str, ctx: Context) -> Dict[str, Any]:
    """
    Fetch weather information for a city using a mock API.
    
    Args:
        city: Name of the city
        ctx: MCP context for logging
    
    Returns:
        Weather information
    """
    await ctx.info(f"Fetching weather for {city}")
    
    try:
        # Using a mock weather service since we don't have a real API key
        # In production, you would use a real weather API
        async with httpx.AsyncClient() as client:
            # Mock weather data for demonstration
            mock_weather = {
                "city": city,
                "temperature": 22,
                "condition": "sunny",
                "humidity": 65,
                "wind_speed": 10,
                "timestamp": datetime.now().isoformat()
            }
            
            await ctx.info(f"Weather data retrieved for {city}")
            return mock_weather
            
    except Exception as e:
        await ctx.error(f"Error fetching weather: {str(e)}")
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
        
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )
        
        if cursor.rowcount == 0:
            return {"error": f"Task with ID {task_id} not found"}
        
        # Get updated task
        cursor.execute(
            "SELECT t.*, u.name, u.email FROM tasks t JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (task_id,)
        )
        task = cursor.fetchone()
        conn.commit()
        conn.close()
        
        return {
            "id": task[0],
            "user_id": task[1],
            "title": task[2],
            "description": task[3],
            "status": task[4],
            "created_at": task[5],
            "user_name": task[6],
            "updated": True
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
            ]
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
        
        return json.dumps(task_list, indent=2)
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
            "total_users": user_count,
            "total_tasks": task_count,
            "task_statistics": task_stats,
            "database_path": DATABASE_PATH,
            "timestamp": datetime.now().isoformat(),
            "server_name": "FastAPI-MCP-Server",
            "version": "1.0.0"
        }
        
        return json.dumps(system_info, indent=2)
    except Exception as e:
        return f"Error retrieving system info: {str(e)}"

# MCP Prompts
@mcp.prompt()
def task_analysis_prompt(user_id: int) -> str:
    """Generate a prompt for analyzing a user's tasks"""
    return f"""
    Please analyze the tasks for user ID {user_id}. Consider the following aspects:
    
    1. Task distribution by status
    2. Task complexity based on descriptions
    3. Potential bottlenecks or areas for improvement
    4. Recommendations for task prioritization
    
    Use the user://{user_id} resource to get the user's task data.
    """

@mcp.prompt()
def productivity_report_prompt() -> str:
    """Generate a prompt for creating a productivity report"""
    return """
    Create a comprehensive productivity report based on the current system data:
    
    1. Use the system://info resource to get overall statistics
    2. Use the tasks://status/completed resource to analyze completed work
    3. Use the tasks://status/pending resource to identify upcoming work
    4. Use the tasks://status/in_progress resource to see current workload
    
    Generate insights about:
    - Team productivity trends
    - Task completion rates
    - Workload distribution
    - Recommendations for improvement
    """

@mcp.prompt()
def user_onboarding_prompt(user_name: str) -> str:
    """Generate a personalized onboarding prompt for new users"""
    return f"""
    Welcome {user_name} to our task management system!
    
    To get you started, I can help you:
    
    1. Create your first task using the create_task tool
    2. Show you existing users with the users://list resource
    3. Explain how to update task statuses using the update_task_status tool
    4. Generate weather information for your location using the fetch_weather tool
    5. Perform calculations using the calculator tool
    
    What would you like to explore first?
    """

# FastAPI Web Interface Routes
@web_app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard showing system overview"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        task_stats = dict(cursor.fetchall())
        
        # Get recent tasks
        cursor.execute("""
            SELECT t.title, t.status, u.name, t.created_at
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
            LIMIT 5
        """)
        recent_tasks = cursor.fetchall()
        
        conn.close()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user_count": user_count,
            "task_count": task_count,
            "task_stats": task_stats,
            "recent_tasks": recent_tasks
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/users")
async def api_get_users():
    """API endpoint to get all users"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "created_at": user[3]
        }
        for user in users
    ]

@web_app.get("/api/tasks")
async def api_get_tasks():
    """API endpoint to get all tasks"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.title, t.description, t.status, t.created_at, u.name
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    """)
    tasks = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "status": task[3],
            "created_at": task[4],
            "user_name": task[5]
        }
        for task in tasks
    ]

@web_app.get("/mcp-info")
async def mcp_info():
    """Get information about available MCP tools and resources"""
    return {
        "server_name": "FastAPI-MCP-Server",
        "version": "1.0.0",
        "tools": [
            {
                "name": "calculator",
                "description": "Perform basic arithmetic operations"
            },
            {
                "name": "create_user",
                "description": "Create a new user in the database"
            },
            {
                "name": "create_task",
                "description": "Create a new task for a user"
            },
            {
                "name": "fetch_weather",
                "description": "Fetch weather information for a city"
            },
            {
                "name": "update_task_status",
                "description": "Update the status of a task"
            }
        ],
        "resources": [
            {
                "uri": "users://list",
                "description": "Get a list of all users"
            },
            {
                "uri": "user://{user_id}",
                "description": "Get detailed information about a specific user"
            },
            {
                "uri": "tasks://status/{status}",
                "description": "Get all tasks with a specific status"
            },
            {
                "uri": "system://info",
                "description": "Get system information and statistics"
            }
        ],
        "prompts": [
            {
                "name": "task_analysis_prompt",
                "description": "Generate a prompt for analyzing a user's tasks"
            },
            {
                "name": "productivity_report_prompt",
                "description": "Generate a prompt for creating a productivity report"
            },
            {
                "name": "user_onboarding_prompt",
                "description": "Generate a personalized onboarding prompt"
            }
        ]
    }

# Mount the web app (optional - for demonstration)
if __name__ == "__main__":
    import uvicorn
    
    # For production, you would typically run the MCP server separately
    # This demonstrates both MCP and web capabilities in one process
    
    print("Starting FastAPI MCP Server...")
    print("MCP Server available via STDIO")
    print("Web interface available at http://localhost:8000")
    print("MCP info available at http://localhost:8000/mcp-info")
    
    # Run MCP server in background
    async def run_mcp():
        await mcp.run(transport="stdio")
    
    # For demo purposes, we'll just show how to run the web server
    # In production, you'd run these separately
    uvicorn.run(web_app, host="0.0.0.0", port=8000)