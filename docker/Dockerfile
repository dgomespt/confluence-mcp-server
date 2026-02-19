# Use a slim Python image for security and speed
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
# We use --no-cache-dir to keep the image lean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY src/ ./src/

# Create a wrapper script that handles both transport modes
RUN echo '#!/bin/bash\npython -m src.main' > /usr/local/bin/mcp-server && chmod +x /usr/local/bin/mcp-server

# Ensure the app runs as a non-privileged user
RUN useradd -m mcpuser
USER mcpuser

# Default command runs in stdio mode
# Set MCP_TRANSPORT=sse to run in SSE mode
CMD ["python", "-m", "src.main"]
