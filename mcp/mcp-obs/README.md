# mcp-obs

MCP server for observability tools (VictoriaLogs and VictoriaTraces).

## Tools

### logs_search
Search logs in VictoriaLogs using a LogsQL query.

### logs_error_count
Count errors for a specific service over a time window.

### traces_list
List recent traces for a service from VictoriaTraces.

### traces_get
Fetch a specific trace by ID from VictoriaTraces.

## Usage

```bash
python -m mcp_obs
```
