#!/usr/bin/env python3
"""
Enterprise MCP Server with ServiceNow and Splunk Integration
Handles incident management, monitoring, and correlation
"""

import asyncio
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import base64

import httpx
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# Configuration from environment variables
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE", "your-instance.service-now.com")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", "")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "")
SPLUNK_HOST = os.getenv("SPLUNK_HOST", "your-splunk.com")
SPLUNK_PORT = os.getenv("SPLUNK_PORT", "8089")
SPLUNK_USERNAME = os.getenv("SPLUNK_USERNAME", "")
SPLUNK_PASSWORD = os.getenv("SPLUNK_PASSWORD", "")

# Initialize MCP server
mcp = FastMCP("Enterprise-ServiceNow-Splunk-MCP")

# Pydantic models
class IncidentFilter(BaseModel):
    assigned_to: Optional[str] = None
    state: Optional[str] = None
    priority: Optional[int] = None
    category: Optional[str] = None
    limit: int = 10

class SplunkSearch(BaseModel):
    query: str
    earliest_time: str = "-24h"
    latest_time: str = "now"
    max_results: int = 100

class IncidentUpdate(BaseModel):
    incident_number: str
    work_notes: Optional[str] = None
    state: Optional[str] = None
    assigned_to: Optional[str] = None

# ServiceNow API Helper Functions
async def servicenow_request(endpoint: str, method: str = "GET", data: Dict = None, ctx: Context = None) -> Dict:
    """Make authenticated request to ServiceNow API"""
    if not SERVICENOW_USERNAME or not SERVICENOW_PASSWORD:
        raise ValueError("ServiceNow credentials not configured")
    
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/{endpoint}"
    
    # Basic authentication
    auth_str = f"{SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if ctx:
        await ctx.info(f"ServiceNow API: {method} {endpoint}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data)
        
        response.raise_for_status()
        return response.json()

# Splunk API Helper Functions
async def splunk_request(endpoint: str, method: str = "GET", data: Dict = None, ctx: Context = None) -> Dict:
    """Make authenticated request to Splunk API"""
    if not SPLUNK_USERNAME or not SPLUNK_PASSWORD:
        raise ValueError("Splunk credentials not configured")
    
    url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/{endpoint}"
    
    # Basic authentication
    auth_str = f"{SPLUNK_USERNAME}:{SPLUNK_PASSWORD}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    if ctx:
        await ctx.info(f"Splunk API: {method} {endpoint}")
    
    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:  # Note: verify=False for demo, use proper certs in production
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, data=data)
        
        response.raise_for_status()
        return response.json()

# ServiceNow MCP Tools
@mcp.tool()
async def get_my_incidents(filter_options: IncidentFilter, ctx: Context) -> Dict[str, Any]:
    """
    Get incidents from ServiceNow based on filter criteria.
    Useful for checking your incident queue.
    
    Args:
        filter_options: Filter criteria including assigned_to, state, priority, etc.
        ctx: MCP context for logging
    
    Returns:
        List of incidents with details
    """
    await ctx.info("Fetching incidents from ServiceNow")
    
    try:
        # Build query parameters
        params = []
        if filter_options.assigned_to:
            params.append(f"assigned_to.name={filter_options.assigned_to}")
        if filter_options.state:
            params.append(f"state={filter_options.state}")
        if filter_options.priority:
            params.append(f"priority={filter_options.priority}")
        if filter_options.category:
            params.append(f"category={filter_options.category}")
        
        query = "^".join(params) if params else ""
        endpoint = f"incident?sysparm_query={query}&sysparm_limit={filter_options.limit}&sysparm_fields=number,short_description,description,state,priority,assigned_to,created_on,updated_on,work_notes"
        
        result = await servicenow_request(endpoint, ctx=ctx)
        incidents = result.get("result", [])
        
        await ctx.info(f"Found {len(incidents)} incidents")
        
        return {
            "total_incidents": len(incidents),
            "incidents": incidents,
            "query_used": query,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        await ctx.error(f"ServiceNow API error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_incident_details(incident_number: str, ctx: Context) -> Dict[str, Any]:
    """
    Get detailed information about a specific incident including summary, notes, and history.
    
    Args:
        incident_number: ServiceNow incident number (e.g., INC0001234)
        ctx: MCP context for logging
    
    Returns:
        Detailed incident information
    """
    await ctx.info(f"Fetching details for incident {incident_number}")
    
    try:
        # Get main incident details
        endpoint = f"incident?sysparm_query=number={incident_number}&sysparm_fields=number,short_description,description,state,priority,assigned_to,created_on,updated_on,work_notes,close_notes,resolution_code,resolved_by,closed_by"
        result = await servicenow_request(endpoint, ctx=ctx)
        
        incidents = result.get("result", [])
        if not incidents:
            return {"error": f"Incident {incident_number} not found"}
        
        incident = incidents[0]
        
        # Get work notes/journal entries
        try:
            notes_endpoint = f"sys_journal_field?sysparm_query=element_id={incident['sys_id']}&sysparm_fields=value,created_on,created_by&sysparm_order_by=created_on"
            notes_result = await servicenow_request(notes_endpoint, ctx=ctx)
            work_notes = notes_result.get("result", [])
        except Exception:
            work_notes = []
        
        await ctx.info(f"Retrieved incident details with {len(work_notes)} work notes")
        
        return {
            "incident": incident,
            "work_notes": work_notes,
            "notes_count": len(work_notes),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        await ctx.error(f"ServiceNow API error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def update_incident(update_data: IncidentUpdate, ctx: Context) -> Dict[str, Any]:
    """
    Update a ServiceNow incident with work notes, state changes, or reassignment.
    
    Args:
        update_data: Incident update information
        ctx: MCP context for logging
    
    Returns:
        Update confirmation
    """
    await ctx.info(f"Updating incident {update_data.incident_number}")
    
    try:
        # First, get the incident sys_id
        search_endpoint = f"incident?sysparm_query=number={update_data.incident_number}&sysparm_fields=sys_id"
        search_result = await servicenow_request(search_endpoint, ctx=ctx)
        
        incidents = search_result.get("result", [])
        if not incidents:
            return {"error": f"Incident {update_data.incident_number} not found"}
        
        sys_id = incidents[0]["sys_id"]
        
        # Build update data
        update_payload = {}
        if update_data.work_notes:
            update_payload["work_notes"] = update_data.work_notes
        if update_data.state:
            update_payload["state"] = update_data.state
        if update_data.assigned_to:
            update_payload["assigned_to"] = update_data.assigned_to
        
        # Update the incident
        endpoint = f"incident/{sys_id}"
        result = await servicenow_request(endpoint, method="PATCH", data=update_payload, ctx=ctx)
        
        await ctx.info(f"Successfully updated incident {update_data.incident_number}")
        
        return {
            "success": True,
            "incident_number": update_data.incident_number,
            "updates_applied": update_payload,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        await ctx.error(f"ServiceNow update error: {str(e)}")
        return {"error": str(e)}

# Splunk MCP Tools
@mcp.tool()
async def splunk_search(search_params: SplunkSearch, ctx: Context) -> Dict[str, Any]:
    """
    Execute a Splunk search query to correlate incident data with logs/metrics.
    
    Args:
        search_params: Splunk search parameters including query and time range
        ctx: MCP context for logging
    
    Returns:
        Search results from Splunk
    """
    await ctx.info(f"Executing Splunk search: {search_params.query}")
    
    try:
        # Create search job
        search_data = {
            "search": f"search {search_params.query}",
            "earliest_time": search_params.earliest_time,
            "latest_time": search_params.latest_time,
            "max_count": search_params.max_results,
            "output_mode": "json"
        }
        
        # Start the search
        job_result = await splunk_request("search/jobs", method="POST", data=search_data, ctx=ctx)
        
        # Note: In a real implementation, you'd poll for job completion
        # For this demo, we'll use a oneshot search for immediate results
        oneshot_data = {
            "search": f"search {search_params.query} | head {search_params.max_results}",
            "earliest_time": search_params.earliest_time,
            "latest_time": search_params.latest_time,
            "output_mode": "json"
        }
        
        result = await splunk_request("search/jobs/oneshot", method="POST", data=oneshot_data, ctx=ctx)
        
        events = result.get("results", [])
        await ctx.info(f"Splunk search returned {len(events)} events")
        
        return {
            "query": search_params.query,
            "events_count": len(events),
            "events": events,
            "time_range": f"{search_params.earliest_time} to {search_params.latest_time}",
            "executed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        await ctx.error(f"Splunk search error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def correlate_incident_with_logs(incident_number: str, search_keywords: List[str], ctx: Context) -> Dict[str, Any]:
    """
    Correlate a ServiceNow incident with Splunk logs by searching for related events.
    
    Args:
        incident_number: ServiceNow incident number
        search_keywords: Keywords to search for in Splunk (e.g., server names, error codes)
        ctx: MCP context for logging
    
    Returns:
        Correlation results combining ServiceNow and Splunk data
    """
    await ctx.info(f"Correlating incident {incident_number} with Splunk logs")
    
    try:
        # Get incident details first
        incident_details = await get_incident_details(incident_number, ctx)
        if "error" in incident_details:
            return incident_details
        
        # Build Splunk search query
        keyword_query = " OR ".join([f'"{keyword}"' for keyword in search_keywords])
        splunk_query = f"({keyword_query}) | head 20"
        
        # Search Splunk
        search_params = SplunkSearch(
            query=splunk_query,
            earliest_time="-24h",  # Search last 24 hours
            latest_time="now",
            max_results=20
        )
        
        splunk_results = await splunk_search(search_params, ctx)
        
        # Analyze correlation
        correlation_score = 0
        if "events" in splunk_results:
            correlation_score = min(len(splunk_results["events"]) * 10, 100)  # Simple scoring
        
        await ctx.info(f"Correlation analysis complete. Score: {correlation_score}")
        
        return {
            "incident_number": incident_number,
            "incident_summary": incident_details["incident"].get("short_description", ""),
            "search_keywords": search_keywords,
            "splunk_events_found": splunk_results.get("events_count", 0),
            "correlation_score": correlation_score,
            "splunk_events": splunk_results.get("events", []),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        await ctx.error(f"Correlation error: {str(e)}")
        return {"error": str(e)}

# Combined workflow tools
@mcp.tool()
async def incident_investigation_workflow(incident_number: str, ctx: Context) -> Dict[str, Any]:
    """
    Complete incident investigation workflow combining ServiceNow and Splunk data.
    
    Args:
        incident_number: ServiceNow incident number to investigate
        ctx: MCP context for logging
    
    Returns:
        Comprehensive investigation report
    """
    await ctx.info(f"Starting investigation workflow for {incident_number}")
    
    try:
        # Step 1: Get incident details
        await ctx.info("Step 1: Retrieving incident details from ServiceNow")
        incident_details = await get_incident_details(incident_number, ctx)
        
        if "error" in incident_details:
            return incident_details
        
        # Step 2: Extract keywords for Splunk search
        incident = incident_details["incident"]
        description = incident.get("description", "")
        short_desc = incident.get("short_description", "")
        
        # Simple keyword extraction (in production, use NLP)
        keywords = []
        text_to_analyze = f"{short_desc} {description}".lower()
        
        # Look for common IT terms
        common_terms = ["server", "database", "network", "application", "service", "error", "timeout", "failed", "down"]
        for term in common_terms:
            if term in text_to_analyze:
                keywords.append(term)
        
        # Step 3: Search Splunk if keywords found
        splunk_results = {}
        if keywords:
            await ctx.info(f"Step 2: Searching Splunk for keywords: {keywords}")
            correlation = await correlate_incident_with_logs(incident_number, keywords, ctx)
            splunk_results = correlation
        
        # Step 4: Generate investigation summary
        await ctx.info("Step 3: Generating investigation summary")
        
        investigation_summary = {
            "incident_number": incident_number,
            "priority": incident.get("priority", "Unknown"),
            "state": incident.get("state", "Unknown"),
            "created_on": incident.get("created_on", ""),
            "summary": incident.get("short_description", ""),
            "description": incident.get("description", ""),
            "work_notes_count": len(incident_details.get("work_notes", [])),
            "keywords_extracted": keywords,
            "splunk_correlation": splunk_results,
            "investigation_completed_at": datetime.now().isoformat()
        }
        
        await ctx.info("Investigation workflow completed")
        
        return investigation_summary
        
    except Exception as e:
        await ctx.error(f"Investigation workflow error: {str(e)}")
        return {"error": str(e)}

# MCP Resources
@mcp.resource("incidents://my_queue")
def get_my_incident_queue() -> str:
    """Get current user's incident queue from ServiceNow"""
    # This would typically use the current user's credentials
    # For demo, return a static example
    queue_data = {
        "user": SERVICENOW_USERNAME or "current_user",
        "total_incidents": 5,
        "by_priority": {
            "1 - Critical": 1,
            "2 - High": 2,
            "3 - Moderate": 2,
            "4 - Low": 0
        },
        "by_state": {
            "New": 2,
            "In Progress": 2,
            "On Hold": 1,
            "Resolved": 0
        },
        "last_updated": datetime.now().isoformat()
    }
    return json.dumps(queue_data, indent=2)

@mcp.resource("splunk://recent_alerts")
def get_recent_splunk_alerts() -> str:
    """Get recent alerts from Splunk"""
    # This would make an actual Splunk API call
    # For demo, return static data
    alerts_data = {
        "alerts": [
            {
                "title": "High CPU Usage Alert",
                "severity": "Medium",
                "time": "2024-01-15T10:30:00Z",
                "source": "server-01"
            },
            {
                "title": "Database Connection Timeout",
                "severity": "High", 
                "time": "2024-01-15T09:45:00Z",
                "source": "db-cluster-prod"
            }
        ],
        "total_alerts": 2,
        "generated_at": datetime.now().isoformat()
    }
    return json.dumps(alerts_data, indent=2)

@mcp.resource("correlation://incident_log_patterns")
def get_incident_log_patterns() -> str:
    """Get common patterns found when correlating incidents with logs"""
    patterns_data = {
        "common_patterns": [
            {
                "pattern": "Database timeout incidents often correlate with high connection pool usage",
                "frequency": "Daily",
                "confidence": 0.85
            },
            {
                "pattern": "Network incidents peak during backup windows",
                "frequency": "Weekly",
                "confidence": 0.92
            },
            {
                "pattern": "Application errors increase before scheduled maintenance",
                "frequency": "Monthly",
                "confidence": 0.78
            }
        ],
        "last_analysis": datetime.now().isoformat()
    }
    return json.dumps(patterns_data, indent=2)

# MCP Prompts
@mcp.prompt()
def incident_analysis_prompt(incident_number: str) -> str:
    """Generate a comprehensive incident analysis prompt"""
    return f"""
    Please perform a comprehensive analysis of incident {incident_number}:
    
    1. **Incident Overview**: Use get_incident_details to retrieve the incident summary, description, and current state
    
    2. **Historical Context**: Review work notes and timeline to understand what has been tried
    
    3. **Log Correlation**: Use correlate_incident_with_logs to search for related events in Splunk
    
    4. **Impact Assessment**: Analyze the priority and affected systems
    
    5. **Next Steps**: Based on the analysis, recommend specific actions:
       - Immediate actions to resolve the issue
       - Escalation recommendations if needed
       - Preventive measures for the future
    
    6. **Documentation**: Suggest work notes to add to the incident
    
    Focus on actionable insights and clear recommendations for the incident handler.
    """

@mcp.prompt()
def splunk_investigation_prompt(keywords: List[str]) -> str:
    """Generate a Splunk investigation prompt for incident correlation"""
    keyword_list = ", ".join(keywords)
    return f"""
    Investigate the following keywords in Splunk logs: {keyword_list}
    
    Please execute Splunk searches to:
    
    1. **Error Pattern Analysis**: Search for error patterns related to these keywords in the last 24 hours
    
    2. **Timeline Analysis**: Look for event clusters or spikes around the incident time
    
    3. **System Correlation**: Identify which systems/services are mentioned alongside these keywords
    
    4. **Impact Scope**: Determine how widespread the issue might be based on log volume
    
    5. **Root Cause Indicators**: Look for events that might indicate the root cause
    
    Use the splunk_search tool with appropriate queries for each analysis area.
    Provide a summary of findings and their relevance to the incident investigation.
    """

if __name__ == "__main__":
    print("🚀 Starting Enterprise ServiceNow + Splunk MCP Server...")
    print("🔧 Available integrations:")
    print("  • ServiceNow API - Incident management")
    print("  • Splunk API - Log analysis and correlation")
    print("  • Combined workflows - Investigation automation")
    print("\n💡 Configure credentials in environment variables:")
    print("  • SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD")
    print("  • SPLUNK_HOST, SPLUNK_PORT, SPLUNK_USERNAME, SPLUNK_PASSWORD")
    print("\n📡 Server ready for MCP connections...")
    
    # Run the MCP server
    mcp.run()