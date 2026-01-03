FROM python:3.11-slim

# Install Node.js for official MCP servers
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application code first
COPY . .

# Install Python dependencies and the package
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Pre-install MCP servers to avoid runtime issues
RUN npm install -g @playwright/mcp@latest @upstash/context7-mcp

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

EXPOSE 8929

CMD ["python", "src/unified_mcp/main.py"]