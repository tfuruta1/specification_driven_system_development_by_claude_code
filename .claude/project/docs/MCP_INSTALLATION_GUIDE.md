
# Extended MCP Server Installation Guide

## Prerequisites

1. Node.js and npm installed
2. Python with required packages

## Installation Commands

### PostgreSQL MCP Server
```bash
npm install -g @modelcontextprotocol/server-postgres
# OR create custom Python implementation
pip install psycopg2-binary
```

### Redis MCP Server
```bash
npm install -g @modelcontextprotocol/server-redis
# OR create custom Python implementation
pip install redis
```

### Filesystem MCP Server
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

## Environment Variables

Create a .env file with:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=claude_code
POSTGRES_USER=claude_user
POSTGRES_PASSWORD=your_password

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## Testing

After setup, test connections:
```python
from mcp_config_extended import ExtendedMCPSetup
setup = ExtendedMCPSetup()
results = setup.setup_all_servers()
print(results)
```
