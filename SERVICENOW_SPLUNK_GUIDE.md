# ServiceNow + Splunk MCP Integration Guide

This guide shows how to use the enterprise MCP server for incident management with ServiceNow and Splunk integration.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install fastmcp httpx pydantic python-dotenv
```

### 2. Configure Credentials

Copy the environment template:
```bash
cp .env.servicenow_splunk .env
```

Edit `.env` with your actual credentials:
```bash
# ServiceNow Configuration
SERVICENOW_INSTANCE=your-company.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password

# Splunk Configuration
SPLUNK_HOST=splunk.your-company.com
SPLUNK_PORT=8089
SPLUNK_USERNAME=your_splunk_user
SPLUNK_PASSWORD=your_splunk_password
```

### 3. Run the Server

```bash
python3 servicenow_mcp_server.py
```

### 4. Connect with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "enterprise-incidents": {
      "command": "python3",
      "args": ["/absolute/path/to/servicenow_mcp_server.py"],
      "env": {
        "SERVICENOW_INSTANCE": "your-company.service-now.com",
        "SERVICENOW_USERNAME": "your_username", 
        "SERVICENOW_PASSWORD": "your_password",
        "SPLUNK_HOST": "splunk.your-company.com",
        "SPLUNK_USERNAME": "your_splunk_user",
        "SPLUNK_PASSWORD": "your_splunk_password"
      }
    }
  }
}
```

## 🔧 Available Tools

### ServiceNow Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `get_my_incidents` | Check your incident queue | Filter by priority, state, assignment |
| `get_incident_details` | Get full incident info | Retrieve summary, notes, history |
| `update_incident` | Update incident status | Add work notes, change state |
| `incident_investigation_workflow` | Full investigation | Automated analysis workflow |

### Splunk Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `splunk_search` | Execute Splunk queries | Search logs, metrics, events |
| `correlate_incident_with_logs` | Cross-reference data | Find related log events |

### Combined Workflows

| Tool | Purpose | Result |
|------|---------|--------|
| `incident_investigation_workflow` | Complete investigation | ServiceNow + Splunk analysis |

## 💬 Real-World Usage Examples

### Example 1: Check Your Incident Queue

```
You: "Check what incidents are currently assigned to me"

AI: I'll check your ServiceNow incident queue right now.

[Uses get_my_incidents tool with assigned_to filter]

You currently have 3 incidents assigned:

📋 **INC0001234** - Database Connection Issues (Priority: High)
- State: In Progress  
- Created: 2024-01-15 09:30

📋 **INC0001235** - Web Application Slow Response (Priority: Medium)
- State: New
- Created: 2024-01-15 11:15

📋 **INC0001236** - Email Service Intermittent (Priority: Low) 
- State: On Hold
- Created: 2024-01-14 16:20

Would you like me to investigate any of these incidents in detail?
```

### Example 2: Investigate a Specific Incident

```
You: "Investigate incident INC0001234 and check for related log events"

AI: I'll perform a comprehensive investigation of INC0001234, including correlation with Splunk logs.

[Uses incident_investigation_workflow tool]

## 🔍 Investigation Report for INC0001234

**Incident Summary:**
- Title: Database Connection Issues
- Priority: High
- State: In Progress  
- Created: 2024-01-15 09:30:15

**Description:**
Users reporting intermittent database connection timeouts affecting the customer portal application.

**Work Notes Analysis:**
- 3 work notes found
- Last update: DBA team investigating connection pool settings

**Splunk Correlation:**
- Keywords extracted: ["database", "connection", "timeout", "application"]
- 15 related events found in last 24 hours
- Correlation score: 80%

**Key Findings from Logs:**
1. Connection pool exhaustion detected at 09:25
2. Database server CPU spike at 09:28  
3. Application errors increased 400% from 09:30-10:00

**Recommendations:**
1. **Immediate**: Restart database connection pool
2. **Short-term**: Increase connection pool size
3. **Long-term**: Implement connection pooling monitoring

Would you like me to add these findings as work notes to the incident?
```

### Example 3: Update Incident with Findings

```
You: "Add the investigation findings as work notes to INC0001234"

AI: I'll update the incident with the investigation findings.

[Uses update_incident tool]

✅ Successfully updated INC0001234

**Work Notes Added:**
```
Investigation completed using automated correlation with Splunk logs:

FINDINGS:
- Connection pool exhaustion detected at 09:25 (5 minutes before user reports)
- Database server CPU spike correlates with incident start time
- 15 related log events found with 80% correlation confidence

IMMEDIATE ACTIONS TAKEN:
- Database connection pool restarted
- Monitoring connection pool metrics

RECOMMENDATIONS:
- Increase connection pool size from 50 to 100 connections
- Implement proactive monitoring for connection pool usage
- Schedule maintenance window for database performance tuning

Log correlation analysis available in Splunk search: 
(database OR connection OR timeout) earliest=-24h
```

**Incident Status:** Updated with investigation findings
**Next Steps:** Awaiting DBA team response on connection pool changes
```

### Example 4: Search Splunk for Specific Patterns

```
You: "Search Splunk for any application errors in the last 4 hours related to the customer portal"

AI: I'll search Splunk for customer portal application errors.

[Uses splunk_search tool]

## 🔍 Splunk Search Results

**Query:** `"customer portal" AND (error OR exception OR failed)`  
**Time Range:** Last 4 hours  
**Events Found:** 23

**Top Error Patterns:**
1. **Database Connection Timeout** (12 events)
   - Peak: 09:30-10:00 (matches INC0001234)
   - Affected servers: app-01, app-02, app-03

2. **Session Management Errors** (7 events)  
   - Pattern: User session cleanup failures
   - Servers: app-01, app-04

3. **Authentication Service Timeouts** (4 events)
   - Pattern: LDAP connection delays
   - Server: auth-01

**Trend Analysis:**
- Error volume 300% higher than baseline
- Concentrated in 30-minute window (09:30-10:00)
- Multiple application tiers affected

This data supports the database connection issue theory for INC0001234 and suggests potential cascading effects.
```

### Example 5: Proactive Monitoring

```
You: "Check for any new high-priority incidents and correlate with recent Splunk alerts"

AI: I'll check for new high-priority incidents and cross-reference with Splunk monitoring.

[Uses get_my_incidents with priority filter and splunk_search]

## 🚨 High-Priority Incident Analysis

**New High-Priority Incidents:**
1. **INC0001237** - Email Service Down (Critical)
   - Created: 13:45 (15 minutes ago)
   - Assigned: John Smith

**Splunk Alert Correlation:**
- **Email server disk space alert** triggered at 13:42
- **Exchange service stopped** logged at 13:43  
- **User authentication failures** spiking since 13:44

**Automated Analysis:**
✅ **Root Cause Identified:** Disk space exhaustion on email server
✅ **Impact Scope:** All email services affected
✅ **Resolution Path:** Clear disk space, restart Exchange services

**Recommended Actions:**
1. **Immediate:** Contact infrastructure team for disk cleanup
2. **Communication:** Update incident with root cause findings
3. **Monitoring:** Set up disk space alerting to prevent recurrence

Would you like me to update INC0001237 with these findings and notify the assigned engineer?
```

## 🛠️ Advanced Workflows

### Custom Splunk Searches

You can create targeted Splunk searches for specific investigation needs:

```python
# Search for database performance issues
search_params = SplunkSearch(
    query='index=database_logs "slow query" OR "connection timeout" | stats count by host',
    earliest_time="-4h",
    max_results=50
)
```

### Incident Filtering

Filter incidents by various criteria:

```python
# Get critical incidents assigned to your team
filter_options = IncidentFilter(
    assigned_to="your_team_name",
    priority=1,  # Critical
    state="2",   # In Progress
    limit=20
)
```

### Automated Workflows

Combine multiple operations for complex investigations:

1. **Get incident details** from ServiceNow
2. **Extract keywords** from incident description
3. **Search Splunk** for related events
4. **Analyze correlation** patterns
5. **Generate recommendations** 
6. **Update incident** with findings

## 📊 Available Resources

Access read-only data through MCP resources:

- `incidents://my_queue` - Your current incident queue summary
- `splunk://recent_alerts` - Recent Splunk monitoring alerts  
- `correlation://incident_log_patterns` - Common correlation patterns

## 🔒 Security Best Practices

1. **Credential Management**
   - Use environment variables for credentials
   - Never commit credentials to version control
   - Rotate passwords regularly

2. **API Access**
   - Use service accounts with minimal required permissions
   - Enable API logging and monitoring
   - Implement rate limiting if needed

3. **Data Handling**
   - Log all API interactions for audit trails
   - Sanitize sensitive data in logs
   - Follow your organization's data handling policies

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Error: ServiceNow credentials not configured
   ```
   **Solution:** Check environment variables are set correctly

2. **Connection Timeouts**
   ```
   Error: Splunk search error: timeout
   ```
   **Solution:** Increase timeout settings or simplify search query

3. **Permission Denied**
   ```
   Error: 403 Forbidden
   ```
   **Solution:** Verify user has necessary permissions in ServiceNow/Splunk

### Debug Mode

Enable detailed logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

### Test Connectivity

Test your connections:
```bash
# Test ServiceNow connection
curl -u username:password https://your-instance.service-now.com/api/now/table/incident?sysparm_limit=1

# Test Splunk connection  
curl -k -u username:password https://your-splunk:8089/services/search/jobs/oneshot -d search="search index=* | head 1"
```

## 🎯 Next Steps

1. **Configure your environment** with actual credentials
2. **Test basic connectivity** with simple queries
3. **Customize workflows** for your organization's needs
4. **Train your team** on using AI-powered incident investigation
5. **Monitor usage** and optimize based on common patterns

## 🤝 Integration Benefits

**For IT Operations:**
- ⚡ Faster incident investigation (minutes vs hours)
- 🎯 Automated correlation between tickets and logs
- 📈 Better incident documentation and knowledge capture
- 🔄 Consistent investigation procedures

**For Engineers:**
- 🧠 AI-powered analysis and recommendations
- 📊 Immediate access to relevant log data
- ⏱️ Reduced context switching between tools
- 📝 Automated work note generation

**For Management:**
- 📈 Improved MTTR (Mean Time To Resolution)
- 👥 Better resource utilization
- 📋 Enhanced incident reporting and trends
- 🎓 Knowledge sharing and team learning

This MCP integration transforms incident management from a manual, time-consuming process into an intelligent, automated workflow that leverages the full power of your ServiceNow and Splunk investments.

---

🤖 **Powered by Model Context Protocol** | Bringing AI to Enterprise Operations