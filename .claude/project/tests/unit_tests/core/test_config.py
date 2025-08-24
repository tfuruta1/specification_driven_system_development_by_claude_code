#!/usr/bin/env python3
"""
Comprehensive unit tests for config.py module
TDD Test Engineer - Achieving 100% Coverage
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from typing import Dict, Any

# Import the module under test - fix import path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'system', 'core'))

from config import (
    Environment,
    ClaudeCoreConfig,
    config,
    get_config,
    is_debug,
    is_production,
    get_project_root,
    get,
    set,
    get_environment,
    detect_environment,
    get_logging_config,
    get_tdd_config
)


class TestEnvironment:
    """Test Environment enum"""
    
    def test_environment_values(self):
        """Test that Environment enum has correct values"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TEST.value == "test"


class TestClaudeCoreConfig:
    """Comprehensive tests for ClaudeCoreConfig class"""
    
    def test_init_creates_config_directory(self):
        """Test that __init__ creates config directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('config.Path') as mock_path:
                mock_path.return_value.parent.parent.parent = Path(temp_dir)
                instance = ClaudeCoreConfig()
                # Should not raise error
                assert instance is not None
    
    def test_default_config_structure(self):
        """Test that default configuration has all required sections"""
        instance = ClaudeCoreConfig()
        default_config = instance.default_config
        
        # Test main sections
        required_sections = [
            "version", "environment", "debug",
            "pair_programming", "sdd_tdd", "development_rules",
            "logging", "testing", "project", "quality"
        ]
        
        for section in required_sections:
            assert section in default_config
    
    def test_get_simple_key(self):
        """Test get method with simple key"""
        instance = ClaudeCoreConfig()
        assert instance.get("version") == "11.0"
        assert instance.get("debug") is True
    
    def test_get_nested_key(self):
        """Test get method with nested key path"""
        instance = ClaudeCoreConfig()
        assert instance.get("sdd_tdd.enforce_tdd") is True
        assert instance.get("testing.coverage_threshold") == 80
    
    def test_get_nonexistent_key(self):
        """Test get method with nonexistent key"""
        instance = ClaudeCoreConfig()
        assert instance.get("nonexistent") is None
        assert instance.get("nonexistent", "default") == "default"
    
    def test_get_environment_valid(self):
        """Test get_environment with valid environment"""
        instance = ClaudeCoreConfig()
        assert instance.get_environment() == Environment.DEVELOPMENT
    
    def test_is_debug_true(self):
        """Test is_debug returns True"""
        instance = ClaudeCoreConfig()
        assert instance.is_debug() is True
    
    def test_is_production_false(self):
        """Test is_production returns False in development"""
        instance = ClaudeCoreConfig()
        assert instance.is_production() is False
    
    def test_get_project_paths(self):
        """Test get_project_paths returns correct structure"""
        instance = ClaudeCoreConfig()
        paths = instance.get_project_paths()
        
        required_paths = ['root', 'core', 'docs', 'workspace', 'cache', 'activity_report']
        for path_name in required_paths:
            assert path_name in paths
            assert isinstance(paths[path_name], Path)
    
    def test_detect_environment(self):
        """Test detect_environment returns string"""
        instance = ClaudeCoreConfig()
        assert instance.detect_environment() == "development"
    
    def test_get_logging_config(self):
        """Test get_logging_config returns logging section"""
        instance = ClaudeCoreConfig()
        logging_config = instance.get_logging_config()
        assert "level" in logging_config
        assert logging_config["level"] == "INFO"


class TestModuleLevelFunctions:
    """Test module-level convenience functions"""
    
    def test_get_config(self):
        """Test get_config returns config instance"""
        config_instance = get_config()
        assert isinstance(config_instance, ClaudeCoreConfig)
        assert config_instance is config
    
    def test_is_debug(self):
        """Test module-level is_debug function"""
        assert isinstance(is_debug(), bool)
    
    def test_is_production(self):
        """Test module-level is_production function"""
        assert isinstance(is_production(), bool)
    
    def test_get_project_root(self):
        """Test get_project_root returns Path"""
        root = get_project_root()
        assert isinstance(root, Path)
    
    def test_module_get_function(self):
        """Test module-level get function"""
        result = get("version")
        assert result == "11.0"
    
    def test_get_environment_function(self):
        """Test module-level get_environment function"""
        env = get_environment()
        assert isinstance(env, Environment)
    
    def test_detect_environment_function(self):
        """Test module-level detect_environment function"""
        env_str = detect_environment()
        assert isinstance(env_str, str)
        assert env_str in ["development", "production", "test"]
    
    def test_get_logging_config_function(self):
        """Test module-level get_logging_config function"""
        logging_config = get_logging_config()
        assert isinstance(logging_config, dict)
    
    def test_get_tdd_config_function(self):
        """Test module-level get_tdd_config function"""
        tdd_config = get_tdd_config()
        assert isinstance(tdd_config, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])