"""
MCP server for observability tools (VictoriaLogs and VictoriaTraces).
"""
import asyncio
from mcp.server.fastmcp import FastMCP
from .observability import get_logs_client, get_traces_client

mcp = FastMCP("mcp_obs")


@mcp.tool()
def logs_search(query: str, limit: int = 50) -> str:
    """
    Search logs in VictoriaLogs using a LogsQL query.
    
    Args:
        query: LogsQL query string (e.g., '_time:1h service.name:"Learning Management Service" severity:ERROR')
        limit: Maximum number of log entries to return (default: 50)
    
    Returns:
        JSON-formatted log entries
    """
    client = get_logs_client()
    results = client.search(query, limit)
    import json
    return json.dumps(results, indent=2)


@mcp.tool()
def logs_error_count(service: str, time_range: str = "1h") -> str:
    """
    Count errors for a specific service over a time window.
    
    Args:
        service: Service name to query (e.g., "Learning Management Service")
        time_range: Time range for the query (default: "1h", examples: "10m", "1h", "24h")
    
    Returns:
        JSON-formatted error count
    """
    client = get_logs_client()
    results = client.count_errors(service, time_range)
    import json
    return json.dumps(results, indent=2)


@mcp.tool()
def traces_list(service: str, limit: int = 20) -> str:
    """
    List recent traces for a service from VictoriaTraces.
    
    Args:
        service: Service name to query (e.g., "Learning Management Service")
        limit: Maximum number of traces to return (default: 20)
    
    Returns:
        JSON-formatted list of traces with trace IDs and span counts
    """
    client = get_traces_client()
    traces = client.list_traces(service, limit)
    # Simplify output - just show trace IDs and basic info
    simplified = []
    for trace in traces:
        simplified.append({
            "trace_id": trace.get("traceID"),
            "spans": len(trace.get("spans", [])),
            "service_name": trace.get("spans", [{}])[0].get("process", {}).get("serviceName", "unknown") if trace.get("spans") else "unknown"
        })
    import json
    return json.dumps(simplified, indent=2)


@mcp.tool()
def traces_get(trace_id: str) -> str:
    """
    Fetch a specific trace by ID from VictoriaTraces.
    
    Args:
        trace_id: The trace ID to fetch
    
    Returns:
        JSON-formatted trace with span hierarchy
    """
    client = get_traces_client()
    trace = client.get_trace(trace_id)
    if not trace:
        return f"Trace {trace_id} not found"
    
    # Simplify output - show span hierarchy
    spans = trace.get("spans", [])
    simplified_spans = []
    for span in spans:
        simplified_spans.append({
            "span_id": span.get("spanID"),
            "operation_name": span.get("operationName"),
            "service": span.get("process", {}).get("serviceName", "unknown"),
            "duration_ms": span.get("duration", 0) // 1000,  # Convert to ms
            "tags": {tag["key"]: tag["value"] for tag in span.get("tags", []) if tag.get("key") in ["error", "http.status_code", "db.statement"]}
        })
    
    result = {
        "trace_id": trace.get("traceID"),
        "spans": simplified_spans
    }
    import json
    return json.dumps(result, indent=2)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
