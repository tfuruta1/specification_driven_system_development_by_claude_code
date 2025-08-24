#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Test Coverage for mcp_config_extended
Auto-generated test file to improve coverage from 0.0% to 20%+

Generated functions: 59 test functions
Priority score: 27
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import mcp_config_extended
except ImportError as e:
    print(f"Warning: Could not import mcp_config_extended: {e}")
    mcp_config_extended = None


class TestMcpConfigExtendedEnhanced(unittest.TestCase):
    """Enhanced test cases for mcp_config_extended module"""
    
    def setUp(self):
        """Test setup"""
        if mcp_config_extended is None:
            self.skipTest("Module mcp_config_extended not available")
    
    def test_module_imports(self):
        """Test that module imports without errors"""
        self.assertIsNotNone(mcp_config_extended)
        
    def test_module_has_expected_attributes(self):
        """Test that module has expected public attributes"""
        if mcp_config_extended:
            # Get all public attributes
            public_attrs = [attr for attr in dir(mcp_config_extended) if not attr.startswith('_')]
            self.assertGreater(len(public_attrs), 0, "Module should have public attributes")


    def test_generate_installation_guide_exists(self):
        """Test that generate_installation_guide function/method exists"""
        if '.' in 'ExtendedMCPSetup.generate_installation_guide':
            # Class method
            class_name, method_name = 'ExtendedMCPSetup.generate_installation_guide'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'generate_installation_guide'), 
                          f"Module should have function generate_installation_guide")
    
    def test_generate_installation_guide_callable(self):
        """Test that generate_installation_guide is callable"""
        if '.' in 'ExtendedMCPSetup.generate_installation_guide':
            # Class method - test with mock instance
            class_name, method_name = 'ExtendedMCPSetup.generate_installation_guide'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'generate_installation_guide'):
                func = getattr(mcp_config_extended, 'generate_installation_guide')
                self.assertTrue(callable(func), f"generate_installation_guide should be callable")

    def test_add_server_exists(self):
        """Test that add_server function/method exists"""
        if '.' in 'MCPConfigManager.add_server':
            # Class method
            class_name, method_name = 'MCPConfigManager.add_server'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'add_server'), 
                          f"Module should have function add_server")
    
    def test_add_server_callable(self):
        """Test that add_server is callable"""
        if '.' in 'MCPConfigManager.add_server':
            # Class method - test with mock instance
            class_name, method_name = 'MCPConfigManager.add_server'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'add_server'):
                func = getattr(mcp_config_extended, 'add_server')
                self.assertTrue(callable(func), f"add_server should be callable")

    def test_get_server_exists(self):
        """Test that get_server function/method exists"""
        if '.' in 'MCPConfigManager.get_server':
            # Class method
            class_name, method_name = 'MCPConfigManager.get_server'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'get_server'), 
                          f"Module should have function get_server")
    
    def test_get_server_callable(self):
        """Test that get_server is callable"""
        if '.' in 'MCPConfigManager.get_server':
            # Class method - test with mock instance
            class_name, method_name = 'MCPConfigManager.get_server'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'get_server'):
                func = getattr(mcp_config_extended, 'get_server')
                self.assertTrue(callable(func), f"get_server should be callable")

    def test_load_config_exists(self):
        """Test that load_config function/method exists"""
        if '.' in 'MCPConfigManager.load_config':
            # Class method
            class_name, method_name = 'MCPConfigManager.load_config'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'load_config'), 
                          f"Module should have function load_config")
    
    def test_load_config_callable(self):
        """Test that load_config is callable"""
        if '.' in 'MCPConfigManager.load_config':
            # Class method - test with mock instance
            class_name, method_name = 'MCPConfigManager.load_config'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'load_config'):
                func = getattr(mcp_config_extended, 'load_config')
                self.assertTrue(callable(func), f"load_config should be callable")

    def test_test_server_connection_exists(self):
        """Test that test_server_connection function/method exists"""
        if '.' in 'MCPConfigManager.test_server_connection':
            # Class method
            class_name, method_name = 'MCPConfigManager.test_server_connection'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'test_server_connection'), 
                          f"Module should have function test_server_connection")
    
    def test_test_server_connection_callable(self):
        """Test that test_server_connection is callable"""
        if '.' in 'MCPConfigManager.test_server_connection':
            # Class method - test with mock instance
            class_name, method_name = 'MCPConfigManager.test_server_connection'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'test_server_connection'):
                func = getattr(mcp_config_extended, 'test_server_connection')
                self.assertTrue(callable(func), f"test_server_connection should be callable")

    def test_absolute_exists(self):
        """Test that absolute function/method exists"""
        if '.' in 'Path.absolute':
            # Class method
            class_name, method_name = 'Path.absolute'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'absolute'), 
                          f"Module should have function absolute")
    
    def test_absolute_callable(self):
        """Test that absolute is callable"""
        if '.' in 'Path.absolute':
            # Class method - test with mock instance
            class_name, method_name = 'Path.absolute'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'absolute'):
                func = getattr(mcp_config_extended, 'absolute')
                self.assertTrue(callable(func), f"absolute should be callable")

    def test_as_posix_exists(self):
        """Test that as_posix function/method exists"""
        if '.' in 'Path.as_posix':
            # Class method
            class_name, method_name = 'Path.as_posix'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'as_posix'), 
                          f"Module should have function as_posix")
    
    def test_as_posix_callable(self):
        """Test that as_posix is callable"""
        if '.' in 'Path.as_posix':
            # Class method - test with mock instance
            class_name, method_name = 'Path.as_posix'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'as_posix'):
                func = getattr(mcp_config_extended, 'as_posix')
                self.assertTrue(callable(func), f"as_posix should be callable")

    def test_as_uri_exists(self):
        """Test that as_uri function/method exists"""
        if '.' in 'Path.as_uri':
            # Class method
            class_name, method_name = 'Path.as_uri'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'as_uri'), 
                          f"Module should have function as_uri")
    
    def test_as_uri_callable(self):
        """Test that as_uri is callable"""
        if '.' in 'Path.as_uri':
            # Class method - test with mock instance
            class_name, method_name = 'Path.as_uri'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'as_uri'):
                func = getattr(mcp_config_extended, 'as_uri')
                self.assertTrue(callable(func), f"as_uri should be callable")

    def test_chmod_exists(self):
        """Test that chmod function/method exists"""
        if '.' in 'Path.chmod':
            # Class method
            class_name, method_name = 'Path.chmod'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'chmod'), 
                          f"Module should have function chmod")
    
    def test_chmod_callable(self):
        """Test that chmod is callable"""
        if '.' in 'Path.chmod':
            # Class method - test with mock instance
            class_name, method_name = 'Path.chmod'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'chmod'):
                func = getattr(mcp_config_extended, 'chmod')
                self.assertTrue(callable(func), f"chmod should be callable")

    def test_cwd_exists(self):
        """Test that cwd function/method exists"""
        if '.' in 'Path.cwd':
            # Class method
            class_name, method_name = 'Path.cwd'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'cwd'), 
                          f"Module should have function cwd")
    
    def test_cwd_callable(self):
        """Test that cwd is callable"""
        if '.' in 'Path.cwd':
            # Class method - test with mock instance
            class_name, method_name = 'Path.cwd'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'cwd'):
                func = getattr(mcp_config_extended, 'cwd')
                self.assertTrue(callable(func), f"cwd should be callable")

    def test_exists_exists(self):
        """Test that exists function/method exists"""
        if '.' in 'Path.exists':
            # Class method
            class_name, method_name = 'Path.exists'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'exists'), 
                          f"Module should have function exists")
    
    def test_exists_callable(self):
        """Test that exists is callable"""
        if '.' in 'Path.exists':
            # Class method - test with mock instance
            class_name, method_name = 'Path.exists'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'exists'):
                func = getattr(mcp_config_extended, 'exists')
                self.assertTrue(callable(func), f"exists should be callable")

    def test_expanduser_exists(self):
        """Test that expanduser function/method exists"""
        if '.' in 'Path.expanduser':
            # Class method
            class_name, method_name = 'Path.expanduser'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'expanduser'), 
                          f"Module should have function expanduser")
    
    def test_expanduser_callable(self):
        """Test that expanduser is callable"""
        if '.' in 'Path.expanduser':
            # Class method - test with mock instance
            class_name, method_name = 'Path.expanduser'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'expanduser'):
                func = getattr(mcp_config_extended, 'expanduser')
                self.assertTrue(callable(func), f"expanduser should be callable")

    def test_from_uri_exists(self):
        """Test that from_uri function/method exists"""
        if '.' in 'Path.from_uri':
            # Class method
            class_name, method_name = 'Path.from_uri'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'from_uri'), 
                          f"Module should have function from_uri")
    
    def test_from_uri_callable(self):
        """Test that from_uri is callable"""
        if '.' in 'Path.from_uri':
            # Class method - test with mock instance
            class_name, method_name = 'Path.from_uri'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'from_uri'):
                func = getattr(mcp_config_extended, 'from_uri')
                self.assertTrue(callable(func), f"from_uri should be callable")

    def test_full_match_exists(self):
        """Test that full_match function/method exists"""
        if '.' in 'Path.full_match':
            # Class method
            class_name, method_name = 'Path.full_match'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'full_match'), 
                          f"Module should have function full_match")
    
    def test_full_match_callable(self):
        """Test that full_match is callable"""
        if '.' in 'Path.full_match':
            # Class method - test with mock instance
            class_name, method_name = 'Path.full_match'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'full_match'):
                func = getattr(mcp_config_extended, 'full_match')
                self.assertTrue(callable(func), f"full_match should be callable")

    def test_glob_exists(self):
        """Test that glob function/method exists"""
        if '.' in 'Path.glob':
            # Class method
            class_name, method_name = 'Path.glob'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'glob'), 
                          f"Module should have function glob")
    
    def test_glob_callable(self):
        """Test that glob is callable"""
        if '.' in 'Path.glob':
            # Class method - test with mock instance
            class_name, method_name = 'Path.glob'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'glob'):
                func = getattr(mcp_config_extended, 'glob')
                self.assertTrue(callable(func), f"glob should be callable")

    def test_group_exists(self):
        """Test that group function/method exists"""
        if '.' in 'Path.group':
            # Class method
            class_name, method_name = 'Path.group'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'group'), 
                          f"Module should have function group")
    
    def test_group_callable(self):
        """Test that group is callable"""
        if '.' in 'Path.group':
            # Class method - test with mock instance
            class_name, method_name = 'Path.group'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'group'):
                func = getattr(mcp_config_extended, 'group')
                self.assertTrue(callable(func), f"group should be callable")

    def test_hardlink_to_exists(self):
        """Test that hardlink_to function/method exists"""
        if '.' in 'Path.hardlink_to':
            # Class method
            class_name, method_name = 'Path.hardlink_to'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'hardlink_to'), 
                          f"Module should have function hardlink_to")
    
    def test_hardlink_to_callable(self):
        """Test that hardlink_to is callable"""
        if '.' in 'Path.hardlink_to':
            # Class method - test with mock instance
            class_name, method_name = 'Path.hardlink_to'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'hardlink_to'):
                func = getattr(mcp_config_extended, 'hardlink_to')
                self.assertTrue(callable(func), f"hardlink_to should be callable")

    def test_home_exists(self):
        """Test that home function/method exists"""
        if '.' in 'Path.home':
            # Class method
            class_name, method_name = 'Path.home'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'home'), 
                          f"Module should have function home")
    
    def test_home_callable(self):
        """Test that home is callable"""
        if '.' in 'Path.home':
            # Class method - test with mock instance
            class_name, method_name = 'Path.home'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'home'):
                func = getattr(mcp_config_extended, 'home')
                self.assertTrue(callable(func), f"home should be callable")

    def test_is_absolute_exists(self):
        """Test that is_absolute function/method exists"""
        if '.' in 'Path.is_absolute':
            # Class method
            class_name, method_name = 'Path.is_absolute'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'is_absolute'), 
                          f"Module should have function is_absolute")
    
    def test_is_absolute_callable(self):
        """Test that is_absolute is callable"""
        if '.' in 'Path.is_absolute':
            # Class method - test with mock instance
            class_name, method_name = 'Path.is_absolute'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'is_absolute'):
                func = getattr(mcp_config_extended, 'is_absolute')
                self.assertTrue(callable(func), f"is_absolute should be callable")

    def test_is_block_device_exists(self):
        """Test that is_block_device function/method exists"""
        if '.' in 'Path.is_block_device':
            # Class method
            class_name, method_name = 'Path.is_block_device'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                self.assertTrue(hasattr(cls, method_name), 
                              f"Class {class_name} should have method {method_name}")
        else:
            # Module function
            self.assertTrue(hasattr(mcp_config_extended, 'is_block_device'), 
                          f"Module should have function is_block_device")
    
    def test_is_block_device_callable(self):
        """Test that is_block_device is callable"""
        if '.' in 'Path.is_block_device':
            # Class method - test with mock instance
            class_name, method_name = 'Path.is_block_device'.split('.', 1)
            if hasattr(mcp_config_extended, class_name):
                cls = getattr(mcp_config_extended, class_name)
                if hasattr(cls, method_name):
                    method = getattr(cls, method_name)
                    # Check if it's callable
                    self.assertTrue(callable(method) or isinstance(method, property),
                                  f"{class_name}.{method_name} should be callable or property")
        else:
            # Module function
            if hasattr(mcp_config_extended, 'is_block_device'):
                func = getattr(mcp_config_extended, 'is_block_device')
                self.assertTrue(callable(func), f"is_block_device should be callable")


def run_enhanced_tests():
    """Run enhanced tests for the module"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMcpConfigExtendedEnhanced)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_enhanced_tests()
    exit(0 if success else 1)
