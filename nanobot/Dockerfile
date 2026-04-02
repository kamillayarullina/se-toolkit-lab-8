# Runtime image for nanobot gateway
# The workspace directories are mounted from the host

FROM python:3.14-slim-bookworm AS runtime

WORKDIR /app

# Install nanobot base package
RUN pip install --no-cache-dir nanobot

# Create directories for mounted content
RUN mkdir -p /app/nanobot/workspace /app/mcp /app/nanobot-websocket-channel

# Default command runs the entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
