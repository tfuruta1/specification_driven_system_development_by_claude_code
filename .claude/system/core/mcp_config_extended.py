#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extended MCP Configuration System
Phase 3: Add postgres, redis, filesystem support to existing o3 integration

Features:
- PostgreSQL database integration
- Redis caching and session management
- Filesystem operations and monitoring
- Unified MCP server management
- TDD-based implementation with comprehensive testing
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from logger import logger


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server"""
    name: str
    type: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    enabled: bool = True
    connection_timeout: int = 30
    retry_count: int = 3


class MCPConfigManager:
    """Manage extended MCP server configurations"""
    
    def __init__(self, config_file: str = ".mcp.json"):
        self.config_file = Path(config_file)
        self.servers = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load existing MCP configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Convert existing config to new format
                if 'mcpServers' in config_data:
                    for name, server_config in config_data['mcpServers'].items():
                        self.servers[name] = MCPServerConfig(
                            name=name,
                            type=server_config.get('type', 'stdio'),
                            command=server_config.get('command', ''),
                            args=server_config.get('args', []),
                            env=server_config.get('env', {}),
                            description=f"Existing {name} server",
                            enabled=True
                        )
                
                logger.info(f"Loaded {len(self.servers)} MCP servers from config", "MCP")
                
            except Exception as e:
                logger.warning(f"Failed to load MCP config: {e}", "MCP")
                self.servers = {}
        else:
            logger.info("No existing MCP config found, creating new one", "MCP")
    
    def add_server(self, server_config: MCPServerConfig) -> bool:
        """Add a new MCP server configuration"""
        try:
            self.servers[server_config.name] = server_config
            logger.info(f"Added MCP server: {server_config.name}", "MCP")
            return True
        except Exception as e:
            logger.warning(f"Failed to add MCP server {server_config.name}: {e}", "MCP")
            return False
    
    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server configuration"""
        if server_name in self.servers:
            del self.servers[server_name]
            logger.info(f"Removed MCP server: {server_name}", "MCP")
            return True
        return False
    
    def get_server(self, server_name: str) -> Optional[MCPServerConfig]:
        """Get a specific server configuration"""
        return self.servers.get(server_name)
    
    def list_servers(self) -> List[str]:
        """List all configured server names"""
        return list(self.servers.keys())
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Convert to standard MCP format
            config_data = {
                "mcpServers": {}
            }
            
            for name, server in self.servers.items():
                if server.enabled:
                    config_data["mcpServers"][name] = {
                        "type": server.type,
                        "command": server.command,
                        "args": server.args,
                        "env": server.env
                    }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved MCP configuration with {len(config_data['mcpServers'])} active servers", "MCP")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to save MCP config: {e}", "MCP")
            return False
    
    def test_server_connection(self, server_name: str) -> bool:
        """Test connection to an MCP server"""
        server = self.servers.get(server_name)
        if not server:
            return False
        
        try:
            # Test server connectivity
            cmd = [server.command] + server.args
            env = {**os.environ, **server.env}
            
            # Short test connection
            process = subprocess.Popen(
                cmd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=server.connection_timeout
            )
            
            # Send basic test request
            test_msg = json.dumps({"jsonrpc": "2.0", "method": "initialize", "id": 1})
            try:
                stdout, stderr = process.communicate(input=test_msg.encode(), timeout=5)
                return process.returncode == 0
            except subprocess.TimeoutExpired:
                process.kill()
                return False
                
        except Exception as e:
            logger.warning(f"Server connection test failed for {server_name}: {e}", "MCP")
            return False


class ExtendedMCPSetup:
    """Setup extended MCP servers: postgres, redis, filesystem"""
    
    def __init__(self):
        self.config_manager = MCPConfigManager()
        self.setup_commands = {
            'postgres': self._setup_postgres_commands,
            'redis': self._setup_redis_commands,
            'filesystem': self._setup_filesystem_commands
        }
    
    def setup_all_servers(self) -> Dict[str, bool]:
        """Setup all extended MCP servers"""
        results = {}
        
        for server_type in ['postgres', 'redis', 'filesystem']:
            try:
                success = self.setup_server(server_type)
                results[server_type] = success
                logger.info(f"MCP {server_type} setup: {'SUCCESS' if success else 'FAILED'}", "MCP")
            except Exception as e:
                results[server_type] = False
                logger.warning(f"MCP {server_type} setup error: {e}", "MCP")
        
        # Save configuration
        self.config_manager.save_config()
        
        return results
    
    def setup_server(self, server_type: str) -> bool:
        """Setup a specific MCP server type"""
        if server_type not in self.setup_commands:
            logger.warning(f"Unknown MCP server type: {server_type}", "MCP")
            return False
        
        try:
            server_config = self.setup_commands[server_type]()
            return self.config_manager.add_server(server_config)
        except Exception as e:
            logger.warning(f"Failed to setup {server_type} MCP server: {e}", "MCP")
            return False
    
    def _setup_postgres_commands(self) -> MCPServerConfig:
        """Setup PostgreSQL MCP server configuration"""
        # Check if PostgreSQL tools are available
        postgres_available = self._check_command_available('psql')
        
        if postgres_available:
            command = "npx"
            args = ["@modelcontextprotocol/server-postgres"]
        else:
            # Fallback to mock or alternative
            command = "python"
            args = ["-m", "mcp_postgres_server"]  # Custom implementation
        
        return MCPServerConfig(
            name="postgres",
            type="stdio",
            command=command,
            args=args,
            env={
                "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
                "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
                "POSTGRES_DB": os.getenv("POSTGRES_DB", "claude_code"),
                "POSTGRES_USER": os.getenv("POSTGRES_USER", "claude_user"),
                "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "")
            },
            description="PostgreSQL database integration for data persistence and querying",
            connection_timeout=30
        )
    
    def _setup_redis_commands(self) -> MCPServerConfig:
        """Setup Redis MCP server configuration"""
        # Check if Redis tools are available
        redis_available = self._check_command_available('redis-cli')
        
        if redis_available:
            command = "npx"
            args = ["@modelcontextprotocol/server-redis"]
        else:
            # Fallback to mock or alternative
            command = "python"
            args = ["-m", "mcp_redis_server"]  # Custom implementation
        
        return MCPServerConfig(
            name="redis",
            type="stdio",
            command=command,
            args=args,
            env={
                "REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
                "REDIS_PORT": os.getenv("REDIS_PORT", "6379"),
                "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", ""),
                "REDIS_DB": os.getenv("REDIS_DB", "0")
            },
            description="Redis caching and session management for high-performance data access",
            connection_timeout=15
        )
    
    def _setup_filesystem_commands(self) -> MCPServerConfig:
        """Setup Filesystem MCP server configuration"""
        return MCPServerConfig(
            name="filesystem",
            type="stdio",
            command="npx",
            args=["@modelcontextprotocol/server-filesystem", str(Path.cwd())],
            env={
                "FILESYSTEM_ROOT": str(Path.cwd()),
                "FILESYSTEM_ALLOWED_EXTENSIONS": ".py,.js,.vue,.ts,.tsx,.json,.md,.txt",
                "FILESYSTEM_MAX_FILE_SIZE": "10485760",  # 10MB
                "FILESYSTEM_WATCH_CHANGES": "true"
            },
            description="Filesystem operations and file monitoring for project management",
            connection_timeout=10
        )
    
    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            subprocess.run([command, "--version"], 
                         capture_output=True, 
                         timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def generate_installation_guide(self) -> str:
        """Generate installation guide for MCP servers"""
        guide = """
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
"""
        return guide


def create_extended_mcp_config() -> bool:
    """Create extended MCP configuration with postgres, redis, filesystem"""
    try:
        setup = ExtendedMCPSetup()
        results = setup.setup_all_servers()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info(f"MCP setup complete: {success_count}/{total_count} servers configured", "MCP")
        
        # Generate installation guide
        guide = setup.generate_installation_guide()
        guide_file = Path(".claude/core/MCP_INSTALLATION_GUIDE.md")
        guide_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        logger.info(f"Installation guide created: {guide_file}", "MCP")
        
        return success_count == total_count
        
    except Exception as e:
        logger.warning(f"Extended MCP setup failed: {e}", "MCP")
        return False


# For testing and direct execution
if __name__ == "__main__":
    print("=== Extended MCP Configuration Setup ===")
    success = create_extended_mcp_config()
    
    if success:
        print("✅ All MCP servers configured successfully")
    else:
        print("⚠️  Some MCP servers may need manual configuration")
        print("See MCP_INSTALLATION_GUIDE.md for details")