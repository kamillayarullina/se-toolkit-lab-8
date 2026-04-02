---
name: observability
description: Use observability tools to query logs and traces when debugging issues
always: true
---

# Observability Skill

Use observability tools to query logs and traces when debugging issues or when the user asks about errors, failures, or system health.

## Available Tools

- `mcp_obs_logs_search` — Search logs in VictoriaLogs using LogsQL
- `mcp_obs_logs_error_count` — Count errors for a service over a time window
- `mcp_obs_traces_list` — List recent traces for a service
- `mcp_obs_traces_get` — Fetch a specific trace by ID

## When to Use

Use these tools when:
- The user asks about errors ("any errors?", "what went wrong?", "show me errors", "check system health")
- The user asks about system health from an observability perspective
- You need to debug a failure or understand what happened
- You see an error response (404, 500, etc.) and want to investigate the root cause
- An LMS tool call fails or returns an unexpected error

## Query Strategy

### For "What went wrong?" investigation:

1. **Start with error count** — Use `logs_error_count` to see if there are recent errors
   - Use a narrow time window like "10m" for recent issues
   - Specify the service name (e.g., "Learning Management Service")

2. **Search for details** — Use `logs_search` to get the actual log entries
   - Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
   - Extract any `trace_id` from error logs for deeper investigation

3. **Fetch the trace** — If you found a trace_id, use `traces_get` to see the full request flow
   - Look for spans with `error: true` tags
   - Identify which service/component failed

4. **Summarize findings** — Provide a concise summary citing both log AND trace evidence
   - What failed (from logs)
   - Where it failed (from trace span hierarchy)
   - Which service was affected
   - The root cause error message

### For error questions:

1. **Start with error count** — Use `logs_error_count` to see if there are recent errors
   - Use a narrow time window like "10m" or "1h" for recent issues
   - Specify the service name (e.g., "Learning Management Service")

2. **Search for details** — If errors exist, use `logs_search` to get the actual log entries
   - Include `severity:ERROR` in your query
   - Extract any `trace_id` from error logs for deeper investigation

3. **Fetch the trace** — If you found a trace_id, use `traces_get` to see the full request flow
   - Look for spans with `error: true` tags
   - Identify which service/component failed

4. **Summarize findings** — Provide a concise summary, not raw JSON
   - What failed
   - When it happened
   - Which service was affected
   - Any error messages

### Example Queries

For VictoriaLogs:
- `_time:10m service.name:"Learning Management Service" severity:ERROR`
- `_time:1h service.name:"Learning Management Service" event:request_completed status:500`
- `_time:1h trace_id:d2c2b9eddb97bb0ea0ca75fde26116d4`

For VictoriaTraces:
- Use `traces_list` to find recent traces for "Learning Management Service"
- Use `traces_get` with a specific trace_id from logs

## Response Style

- **Be concise** — Summarize findings in 2-4 sentences
- **Highlight the issue** — What failed, where, and why (if known)
- **Include trace context** — If you found a trace_id, mention it
- **Cite both log and trace evidence** — "Logs show X, trace Y confirms Z"
- **Don't dump raw JSON** — Extract the relevant information

## Example Interactions

**User:** "What went wrong?"

**Agent:** (thinks: I need to investigate the recent failure)
1. Calls `logs_error_count(service="Learning Management Service", time_range="10m")`
2. Finds errors, calls `logs_search(query='_time:10m service.name:"Learning Management Service" severity:ERROR', limit=5)`
3. Extracts trace_id from logs, calls `traces_get(trace_id="abc123...")`
4. Summarizes: "I found errors in the LMS backend logs from the last 10 minutes. Logs show 'connection refused' when querying PostgreSQL. Trace abc123... confirms the failure occurred in the db_query span. The backend is returning 404 'Items not found' but the root cause is actually a database connection failure."

**User:** "Any LMS backend errors in the last 10 minutes?"

**Agent:** (thinks: I should check for recent errors in the LMS backend)
1. Calls `logs_error_count(service="Learning Management Service", time_range="10m")`
2. If count > 0, calls `logs_search(query='_time:10m service.name:"Learning Management Service" severity:ERROR', limit=10)`
3. Summarizes: "Yes, I found 3 errors in the LMS backend in the last 10 minutes. The errors show database connection failures when querying the learners table. Trace ID: abc123..."

**User:** "Show me all recent traces for the backend"

**Agent:**
1. Calls `traces_list(service="Learning Management Service", limit=20)`
2. Presents a summary of trace count and any error traces
