#!/usr/bin/env python3
"""
Entrypoint for nanobot gateway in Docker.

Resolves environment variables into the config at runtime,
installs required packages, then launches nanobot gateway.
"""
import json
import os
import socket
import subprocess
import sys

def resolve_host(hostname, max_retries=30, delay=1):
    """Resolve hostname to IP address with retries using Docker's internal DNS."""
    import time
    import struct
    
    # Try Docker's internal DNS server directly
    dns_server = "127.0.0.11"
    dns_port = 53
    
    for i in range(max_retries):
        try:
            # Try standard resolution first
            ip = socket.gethostbyname(hostname)
            print(f"Resolved {hostname} to {ip} (attempt {i+1}/{max_retries})", file=sys.stderr)
            return ip
        except socket.gaierror:
            # Try direct DNS query to Docker's internal DNS
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                # Build DNS query
                query_id = 0x1234
                flags = 0x0100  # Standard query
                questions = 1
                
                # DNS header
                header = struct.pack('>HHHHHH', query_id, flags, questions, 0, 0, 0)
                
                # DNS question
                question = b''
                for part in hostname.split('.'):
                    question += bytes([len(part)]) + part.encode()
                question += b'\x00'  # End of name
                question += struct.pack('>HH', 1, 1)  # Type A, Class IN
                
                sock.sendto(header + question, (dns_server, dns_port))
                response, _ = sock.recvfrom(512)
                
                # Parse response (simplified)
                if len(response) > 12:
                    # Skip header and question, look for answer
                    offset = 12
                    # Skip question name
                    while offset < len(response) and response[offset] != 0:
                        offset += response[offset] + 1
                    offset += 5  # Skip null terminator, type, class
                    
                    if offset + 16 <= len(response):
                        rtype = struct.unpack('>H', response[offset:offset+2])[0]
                        rdlength = struct.unpack('>H', response[offset+10:offset+12])[0]
                        if rtype == 1 and rdlength == 4:  # A record
                            ip_bytes = response[offset+12:offset+16]
                            ip = '.'.join(str(b) for b in ip_bytes)
                            sock.close()
                            print(f"Resolved {hostname} to {ip} via Docker DNS (attempt {i+1}/{max_retries})", file=sys.stderr)
                            return ip
                sock.close()
            except Exception as e:
                pass
            
            if i < max_retries - 1:
                print(f"DNS resolution failed for {hostname}, retrying in {delay}s... (attempt {i+1}/{max_retries})", file=sys.stderr)
                time.sleep(delay)
    
    print(f"Warning: Could not resolve {hostname} after {max_retries} attempts, using hostname directly", file=sys.stderr)
    return hostname

def main():
    # Install required packages from mounted directories
    print("Installing required packages...", file=sys.stderr)
    
    # Install nanobot-channel-protocol first (dependency for nanobot-webchat)
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "-e", "/app/nanobot-websocket-channel/nanobot-channel-protocol"
    ], check=True)
    
    # Install mcp-lms from mounted mcp directory
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "-e", "/app/mcp/mcp-lms"
    ], check=True)
    
    # Install nanobot-webchat from mounted nanobot-websocket-channel directory
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "-e", "/app/nanobot-websocket-channel/nanobot-webchat"
    ], check=True)
    
    # Install mcp-webchat from mounted nanobot-websocket-channel directory
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "-e", "/app/nanobot-websocket-channel/mcp-webchat"
    ], check=True)
    
    # Install mcp-obs from mounted mcp directory
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "-e", "/app/mcp/mcp-obs"
    ], check=True)
    
    print("Packages installed successfully.", file=sys.stderr)
    
    # Read the base config
    config_path = "/app/nanobot/config.json"
    workspace_path = "/app/nanobot/workspace"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Override provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")
    
    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base_url:
        # Resolve hostname in URL to IP address
        import re
        url_match = re.match(r'http://([^:/]+)(.*)', llm_api_base_url)
        if url_match:
            hostname = url_match.group(1)
            rest = url_match.group(2)
            resolved_host = resolve_host(hostname)
            config["providers"]["custom"]["apiBase"] = f"http://{resolved_host}{rest}"
        else:
            config["providers"]["custom"]["apiBase"] = llm_api_base_url
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model
    
    # Override gateway settings from env vars
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")
    
    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)
    
    # Override MCP server settings from env vars
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")
    
    if lms_backend_url:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key
    
    # Override webchat channel settings from env vars
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    
    if webchat_host:
        config["channels"]["webchat"]["host"] = webchat_host
    if webchat_port:
        config["channels"]["webchat"]["port"] = int(webchat_port)
    
    # Add mcp_webchat server config
    webchat_relay_url = os.environ.get("NANOBOT_WEBCHAT_RELAY_URL")
    webchat_token = os.environ.get("NANOBOT_ACCESS_KEY")
    
    if "mcp_webchat" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["mcp_webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {}
        }
    
    if webchat_relay_url:
        config["tools"]["mcpServers"]["mcp_webchat"]["env"]["NANOBOT_WEBCHAT_RELAY_URL"] = webchat_relay_url
    if webchat_token:
        config["tools"]["mcpServers"]["mcp_webchat"]["env"]["NANOBOT_WEBCHAT_TOKEN"] = webchat_token
    
    # Write the resolved config
    resolved_path = "/app/nanobot/config.resolved.json"
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Using config: {resolved_path}", file=sys.stderr)
    
    # Launch nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_path, "--workspace", workspace_path])

if __name__ == "__main__":
    main()
