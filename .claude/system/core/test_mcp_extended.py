#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extended MCP Configuration Tests
Phase 3: Test postgres, redis, filesystem MCP integration

TDD Implementation:
RED -> GREEN -> REFACTOR for MCP server extensions
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from mcp_config_extended import MCPConfigManager, ExtendedMCPSetup, MCPServerConfig, create_extended_mcp_config


class TestMCPConfigManager(unittest.TestCase):
    """Test MCP configuration management"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / ".mcp.json"
        self.manager = MCPConfigManager(str(self.config_file))
    
    def test_load_existing_config(self):
        """Test loading existing MCP configuration"""
        # Create test config
        test_config = {
            "mcpServers": {
                "gemini-cli": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["@choplin/mcp-gemini-cli", "--allow-npx"],
                    "env": {}
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Load config
        manager = MCPConfigManager(str(self.config_file))
        
        self.assertIn("gemini-cli", manager.servers)
        gemini_config = manager.servers["gemini-cli"]
        self.assertEqual(gemini_config.command, "npx")
        self.assertEqual(gemini_config.type, "stdio")
    
    def test_add_new_server(self):
        """Test adding new MCP server configuration"""
        server_config = MCPServerConfig(
            name="test-server",
            type="stdio",
            command="test-command",
            args=["--test"],
            env={"TEST_VAR": "test_value"},
            description="Test server"
        )
        
        success = self.manager.add_server(server_config)
        
        self.assertTrue(success)
        self.assertIn("test-server", self.manager.servers)
        self.assertEqual(self.manager.servers["test-server"].command, "test-command")
    
    def test_remove_server(self):
        """Test removing MCP server configuration"""
        # Add a server first
        server_config = MCPServerConfig(
            name="temp-server",
            type="stdio",
            command="temp",
            args=[],
            env={},
            description="Temporary server"
        )
        self.manager.add_server(server_config)
        
        # Remove it
        success = self.manager.remove_server("temp-server")
        
        self.assertTrue(success)
        self.assertNotIn("temp-server", self.manager.servers)
        
        # Try to remove non-existent server
        success = self.manager.remove_server("non-existent")
        self.assertFalse(success)
    
    def test_save_config(self):
        """Test saving configuration to file"""
        # Add test server
        server_config = MCPServerConfig(
            name="save-test",
            type="stdio",
            command="save-command",
            args=["--save"],
            env={"SAVE": "true"},
            description="Save test server"
        )
        self.manager.add_server(server_config)
        
        # Save config
        success = self.manager.save_config()
        self.assertTrue(success)
        self.assertTrue(self.config_file.exists())
        
        # Verify saved content
        with open(self.config_file, 'r') as f:
            saved_config = json.load(f)
        
        self.assertIn("mcpServers", saved_config)
        self.assertIn("save-test", saved_config["mcpServers"])
        
        saved_server = saved_config["mcpServers"]["save-test"]
        self.assertEqual(saved_server["command"], "save-command")
        self.assertEqual(saved_server["args"], ["--save"])
    
    def test_list_servers(self):
        """Test listing configured servers"""
        # Initially should have no servers (or just existing ones)
        initial_count = len(self.manager.list_servers())
        
        # Add some servers
        for i in range(3):
            server_config = MCPServerConfig(
                name=f"test-server-{i}",
                type="stdio",
                command=f"command-{i}",
                args=[],
                env={},
                description=f"Test server {i}"
            )
            self.manager.add_server(server_config)
        
        servers = self.manager.list_servers()
        self.assertEqual(len(servers), initial_count + 3)
        self.assertIn("test-server-0", servers)
        self.assertIn("test-server-1", servers)
        self.assertIn("test-server-2", servers)


class TestExtendedMCPSetup(unittest.TestCase):
    """Test extended MCP server setup"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / ".mcp.json"
        
        # Patch the config manager to use our temp file
        with patch('mcp_config_extended.MCPConfigManager') as mock_manager:
            mock_instance = MagicMock()
            mock_manager.return_value = mock_instance
            self.setup = ExtendedMCPSetup()
            self.setup.config_manager = MCPConfigManager(str(self.config_file))
    
    def test_postgres_server_setup(self):
        """Test PostgreSQL MCP server setup"""
        with patch.object(self.setup, '_check_command_available', return_value=True):
            server_config = self.setup._setup_postgres_commands()
            
            self.assertEqual(server_config.name, "postgres")
            self.assertEqual(server_config.type, "stdio")
            self.assertEqual(server_config.command, "npx")
            self.assertIn("@modelcontextprotocol/server-postgres", server_config.args)
            self.assertIn("POSTGRES_HOST", server_config.env)
            self.assertIn("POSTGRES_PORT", server_config.env)
    
    def test_redis_server_setup(self):
        """Test Redis MCP server setup"""
        with patch.object(self.setup, '_check_command_available', return_value=True):
            server_config = self.setup._setup_redis_commands()
            
            self.assertEqual(server_config.name, "redis")
            self.assertEqual(server_config.type, "stdio")
            self.assertEqual(server_config.command, "npx")
            self.assertIn("@modelcontextprotocol/server-redis", server_config.args)
            self.assertIn("REDIS_HOST", server_config.env)
            self.assertIn("REDIS_PORT", server_config.env)
    
    def test_filesystem_server_setup(self):
        """Test Filesystem MCP server setup"""
        server_config = self.setup._setup_filesystem_commands()
        
        self.assertEqual(server_config.name, "filesystem")
        self.assertEqual(server_config.type, "stdio")
        self.assertEqual(server_config.command, "npx")
        self.assertIn("@modelcontextprotocol/server-filesystem", server_config.args)
        self.assertIn("FILESYSTEM_ROOT", server_config.env)
        self.assertIn("FILESYSTEM_ALLOWED_EXTENSIONS", server_config.env)
    
    def test_setup_all_servers(self):
        """Test setting up all extended MCP servers"""
        with patch.object(self.setup, '_check_command_available', return_value=True):
            with patch.object(self.setup.config_manager, 'add_server', return_value=True) as mock_add:
                with patch.object(self.setup.config_manager, 'save_config', return_value=True):
                    results = self.setup.setup_all_servers()
                    
                    # Should attempt to setup 3 servers
                    self.assertEqual(len(results), 3)
                    self.assertIn("postgres", results)
                    self.assertIn("redis", results)
                    self.assertIn("filesystem", results)
                    
                    # All should succeed
                    self.assertTrue(all(results.values()))
                    
                    # Should have called add_server 3 times
                    self.assertEqual(mock_add.call_count, 3)
    
    def test_setup_server_fallback(self):
        """Test server setup with fallback when commands not available"""
        with patch.object(self.setup, '_check_command_available', return_value=False):
            postgres_config = self.setup._setup_postgres_commands()
            
            # Should fallback to Python implementation
            self.assertEqual(postgres_config.command, "python")
            self.assertIn("-m", postgres_config.args)
            self.assertIn("mcp_postgres_server", postgres_config.args)
    
    def test_command_availability_check(self):
        """Test command availability checking"""
        # Test with a command that should exist
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            result = self.setup._check_command_available('python')
            mock_run.assert_called_once()
            self.assertTrue(result)
        
        # Test with a command that doesn't exist
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            result = self.setup._check_command_available('non_existent_command')
            self.assertFalse(result)
    
    def test_installation_guide_generation(self):
        """Test installation guide generation"""
        guide = self.setup.generate_installation_guide()
        
        self.assertIsInstance(guide, str)
        self.assertIn("PostgreSQL MCP Server", guide)
        self.assertIn("Redis MCP Server", guide)
        self.assertIn("Filesystem MCP Server", guide)
        self.assertIn("npm install", guide)
        self.assertIn("Environment Variables", guide)


class TestMCPIntegration(unittest.TestCase):
    """Test full MCP integration"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up integration test environment"""
        os.chdir(self.original_cwd)
    
    @patch('mcp_config_extended.ExtendedMCPSetup')
    def test_create_extended_mcp_config_success(self, mock_setup_class):
        """Test successful extended MCP configuration creation"""
        # Mock successful setup
        mock_setup = MagicMock()
        mock_setup.setup_all_servers.return_value = {
            'postgres': True,
            'redis': True,
            'filesystem': True
        }
        mock_setup.generate_installation_guide.return_value = "Test guide"
        mock_setup_class.return_value = mock_setup
        
        result = create_extended_mcp_config()
        
        self.assertTrue(result)
        mock_setup.setup_all_servers.assert_called_once()
        mock_setup.generate_installation_guide.assert_called_once()
    
    @patch('mcp_config_extended.ExtendedMCPSetup')
    def test_create_extended_mcp_config_partial_failure(self, mock_setup_class):
        """Test partial failure in extended MCP configuration creation"""
        # Mock partial failure
        mock_setup = MagicMock()
        mock_setup.setup_all_servers.return_value = {
            'postgres': True,
            'redis': False,  # Failed
            'filesystem': True
        }
        mock_setup.generate_installation_guide.return_value = "Test guide"
        mock_setup_class.return_value = mock_setup
        
        result = create_extended_mcp_config()
        
        self.assertFalse(result)  # Should fail if any server setup fails
    
    def test_mcp_config_file_format(self):
        """Test that generated MCP config file follows correct format"""
        manager = MCPConfigManager(".mcp.json")
        
        # Add test servers
        test_servers = [
            MCPServerConfig("postgres", "stdio", "npx", ["@modelcontextprotocol/server-postgres"], {}, "PostgreSQL"),
            MCPServerConfig("redis", "stdio", "npx", ["@modelcontextprotocol/server-redis"], {}, "Redis"),
            MCPServerConfig("filesystem", "stdio", "npx", ["@modelcontextprotocol/server-filesystem"], {}, "Filesystem")
        ]
        
        for server in test_servers:
            manager.add_server(server)
        
        manager.save_config()
        
        # Verify file format
        config_file = Path(".mcp.json")
        self.assertTrue(config_file.exists())
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        self.assertIn("mcpServers", config_data)
        self.assertEqual(len(config_data["mcpServers"]), 3)
        
        # Verify each server has required fields
        for server_name in ["postgres", "redis", "filesystem"]:
            self.assertIn(server_name, config_data["mcpServers"])
            server_config = config_data["mcpServers"][server_name]
            
            self.assertIn("type", server_config)
            self.assertIn("command", server_config)
            self.assertIn("args", server_config)
            self.assertIn("env", server_config)


def run_mcp_tests():
    """Run all MCP extension tests"""
    test_classes = [
        TestMCPConfigManager,
        TestExtendedMCPSetup,
        TestMCPIntegration
    ]
    
    for test_class in test_classes:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            return False
    
    return True


if __name__ == '__main__':
    print("=== Extended MCP Configuration Tests ===")
    success = run_mcp_tests()
    
    if success:
        print("\n✅ All MCP tests passed - ready for implementation")
    else:
        print("\n❌ Some MCP tests failed - check implementation")
    
    exit(0 if success else 1)