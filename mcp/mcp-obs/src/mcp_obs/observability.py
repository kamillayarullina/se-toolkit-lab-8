"""
Observability tools for querying VictoriaLogs and VictoriaTraces.
"""
import httpx
from typing import Optional
from pydantic import BaseModel


class VictoriaLogsClient:
    """Client for querying VictoriaLogs HTTP API."""
    
    def __init__(self, base_url: str = "http://victorialogs:9428"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def search(self, query: str, limit: int = 50) -> list[dict]:
        """Search logs using LogsQL query."""
        url = f"{self.base_url}/select/logsql/query"
        params = {"query": query, "limit": limit}
        response = self.client.get(url, params=params)
        response.raise_for_status()
        # VictoriaLogs returns newline-delimited JSON
        lines = response.text.strip().split('\n')
        results = []
        for line in lines:
            if line.strip():
                try:
                    results.append(httpx.Response.__class__)
                except:
                    pass
        # Parse JSON lines
        import json
        results = []
        for line in lines:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return results
    
    def count_errors(self, service: str, time_range: str = "1h") -> list[dict]:
        """Count errors per service over a time window."""
        query = f'_time:{time_range} service.name:"{service}" severity:ERROR'
        url = f"{self.base_url}/select/logsql/query"
        params = {"query": query, "limit": 1000}
        response = self.client.get(url, params=params)
        response.raise_for_status()
        import json
        lines = response.text.strip().split('\n')
        count = 0
        for line in lines:
            if line.strip():
                try:
                    json.loads(line)
                    count += 1
                except json.JSONDecodeError:
                    pass
        return [{"service": service, "error_count": count, "time_range": time_range}]


class VictoriaTracesClient:
    """Client for querying VictoriaTraces HTTP API (Jaeger-compatible)."""
    
    def __init__(self, base_url: str = "http://victoriatraces:10428"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def list_traces(self, service: str, limit: int = 20) -> list[dict]:
        """List recent traces for a service."""
        url = f"{self.base_url}/select/jaeger/api/traces"
        params = {"service": service, "limit": limit}
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # Jaeger API returns {"data": [...]}
        return data.get("data", [])
    
    def get_trace(self, trace_id: str) -> Optional[dict]:
        """Fetch a specific trace by ID."""
        url = f"{self.base_url}/select/jaeger/api/traces/{trace_id}"
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        traces = data.get("data", [])
        return traces[0] if traces else None


# Singleton instances
_logs_client: Optional[VictoriaLogsClient] = None
_traces_client: Optional[VictoriaTracesClient] = None


def get_logs_client() -> VictoriaLogsClient:
    global _logs_client
    if _logs_client is None:
        _logs_client = VictoriaLogsClient()
    return _logs_client


def get_traces_client() -> VictoriaTracesClient:
    global _traces_client
    if _traces_client is None:
        _traces_client = VictoriaTracesClient()
    return _traces_client
