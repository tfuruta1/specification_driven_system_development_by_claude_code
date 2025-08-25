#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for path_utils module
Achieving 100% test coverage
"""

import os
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Setup relative imports from .claude folder
import sys
from pathlib import Path

# Find .claude root using relative path
current_file = Path(__file__).resolve()
current = current_file.parent

# Navigate up to find .claude folder (not subfolder)
claude_root = None
for _ in range(10):  # Limit iterations
    if current.name == '.claude':
        claude_root = current
        break
    if current.parent == current:  # Reached root
        break
    current = current.parent

# If not found, check for .claude in parent directories
if claude_root is None:
    current = current_file.parent
    for _ in range(10):
        if (current / '.claude').exists() and (current / '.claude' / 'system').exists():
            claude_root = current / '.claude'
            break
        if current.parent == current:
            break
        current = current.parent

# Final fallback
if claude_root is None:
    # Assume we're in .claude/project/tests
    claude_root = current_file.parent.parent.parent

# Add system path
system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

# Now import the modules to test
from core.path_utils import (
    get_claude_root, get_relative_path, setup_import_path,
    ClaudePaths, paths
)


class TestGetClaudeRoot(unittest.TestCase):
    """Tests for get_claude_root function"""
    
    def test_get_claude_root_from_inside_claude(self):
        """Test finding .claude root from inside .claude directory"""
        root = get_claude_root()
        self.assertTrue(root.exists())
        self.assertTrue(root.name == '.claude' or (root / '.claude').exists())
    
    def test_get_claude_root_with_nested_structure(self):
        """Test finding .claude root from deeply nested directory"""
        # Create temporary structure
        with tempfile.TemporaryDirectory() as tmpdir:
            claude_dir = Path(tmpdir) / ".claude" / "system" / "core"
            claude_dir.mkdir(parents=True)
            
            # Create a test file deep in structure
            test_file = claude_dir / "test.py"
            test_file.write_text("")
            
            # Mock __file__ to be in the temp structure
            with patch('core.path_utils.__file__', str(test_file)):
                root = get_claude_root()
                self.assertEqual(root.name, '.claude')
    
    def test_get_claude_root_from_cwd(self):
        """Test finding .claude root from current working directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claude_dir = Path(tmpdir) / ".claude"
            claude_dir.mkdir()
            
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Mock __file__ to be outside .claude
                with patch('core.path_utils.__file__', str(Path(tmpdir) / "other.py")):
                    root = get_claude_root()
                    self.assertEqual(root, claude_dir)
            finally:
                os.chdir(original_cwd)
    
    def test_get_claude_root_fallback(self):
        """Test fallback when .claude cannot be found"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file without .claude in path
            test_file = Path(tmpdir) / "a" / "b" / "c" / "test.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("")
            
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                with patch('core.path_utils.__file__', str(test_file)):
                    root = get_claude_root()
                    # Should return 3 levels up as fallback
                    self.assertEqual(root, test_file.parent.parent.parent)
            finally:
                os.chdir(original_cwd)


class TestGetRelativePath(unittest.TestCase):
    """Tests for get_relative_path function"""
    
    def test_get_relative_path_without_base(self):
        """Test getting relative path without base"""
        with patch('core.path_utils.get_claude_root') as mock_root:
            mock_root.return_value = Path("/test/.claude")
            
            result = get_relative_path("system/core")
            self.assertEqual(result, Path("/test/.claude/system/core"))
    
    def test_get_relative_path_with_base(self):
        """Test getting relative path with base"""
        with patch('core.path_utils.get_claude_root') as mock_root:
            mock_root.return_value = Path("/test/.claude")
            
            result = get_relative_path("module.py", "system/core")
            self.assertEqual(result, Path("/test/.claude/system/core/module.py"))
    
    def test_get_relative_path_empty_target(self):
        """Test getting relative path with empty target"""
        with patch('core.path_utils.get_claude_root') as mock_root:
            mock_root.return_value = Path("/test/.claude")
            
            result = get_relative_path("")
            self.assertEqual(result, Path("/test/.claude"))


class TestSetupImportPath(unittest.TestCase):
    """Tests for setup_import_path function"""
    
    def test_setup_import_path_adds_paths(self):
        """Test that setup_import_path adds correct paths to sys.path"""
        original_path = sys.path.copy()
        
        with patch('core.path_utils.get_claude_root') as mock_root:
            mock_root.return_value = Path("/test/.claude")
            
            # Clear sys.path for test
            sys.path = []
            
            setup_import_path()
            
            self.assertIn("/test/.claude/system", sys.path)
            self.assertIn("/test/.claude", sys.path)
        
        # Restore original path
        sys.path = original_path
    
    def test_setup_import_path_avoids_duplicates(self):
        """Test that setup_import_path doesn't add duplicate paths"""
        with patch('core.path_utils.get_claude_root') as mock_root:
            mock_root.return_value = Path("/test/.claude")
            
            # Add paths first time
            setup_import_path()
            initial_count = sys.path.count("/test/.claude/system")
            
            # Add paths second time
            setup_import_path()
            final_count = sys.path.count("/test/.claude/system")
            
            self.assertEqual(initial_count, final_count)


class TestClaudePaths(unittest.TestCase):
    """Tests for ClaudePaths class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_root = Path("/test/.claude")
        self.patcher = patch('core.path_utils.get_claude_root')
        self.mock_get_root = self.patcher.start()
        self.mock_get_root.return_value = self.mock_root
        
        self.paths = ClaudePaths()
    
    def tearDown(self):
        """Clean up"""
        self.patcher.stop()
    
    def test_root_property(self):
        """Test root property"""
        self.assertEqual(self.paths.root, self.mock_root)
    
    def test_system_property(self):
        """Test system property"""
        self.assertEqual(self.paths.system, self.mock_root / "system")
    
    def test_core_property(self):
        """Test core property"""
        self.assertEqual(self.paths.core, self.mock_root / "system/core")
    
    def test_config_property(self):
        """Test config property"""
        self.assertEqual(self.paths.config, self.mock_root / "system/config")
    
    def test_project_property(self):
        """Test project property"""
        self.assertEqual(self.paths.project, self.mock_root / "project")
    
    def test_tests_property(self):
        """Test tests property"""
        self.assertEqual(self.paths.tests, self.mock_root / "project/tests")
    
    def test_temp_property(self):
        """Test temp property"""
        self.assertEqual(self.paths.temp, self.mock_root / "temp")
    
    def test_cache_property(self):
        """Test cache property"""
        self.assertEqual(self.paths.cache, self.mock_root / "temp/cache")
    
    def test_logs_property(self):
        """Test logs property"""
        self.assertEqual(self.paths.logs, self.mock_root / "temp/logs")
    
    def test_reports_property(self):
        """Test reports property"""
        self.assertEqual(self.paths.reports, self.mock_root / "temp/reports")


class TestModuleLevelPaths(unittest.TestCase):
    """Test module-level paths singleton"""
    
    def test_paths_singleton(self):
        """Test that paths is a ClaudePaths instance"""
        self.assertIsInstance(paths, ClaudePaths)
    
    def test_paths_properties_accessible(self):
        """Test that all paths properties are accessible"""
        # Just check they don't raise errors
        _ = paths.root
        _ = paths.system
        _ = paths.core
        _ = paths.config
        _ = paths.project
        _ = paths.tests
        _ = paths.temp
        _ = paths.cache
        _ = paths.logs
        _ = paths.reports


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_get_claude_root_max_iterations(self):
        """Test that get_claude_root stops after max iterations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create very deep structure without .claude
            deep_path = Path(tmpdir)
            for i in range(15):
                deep_path = deep_path / f"level{i}"
            deep_path.mkdir(parents=True)
            
            test_file = deep_path / "test.py"
            test_file.write_text("")
            
            original_cwd = os.getcwd()
            try:
                # Change to a directory without .claude
                os.chdir(tmpdir)
                
                with patch('core.path_utils.__file__', str(test_file)):
                    # Should not hang, should return fallback
                    root = get_claude_root()
                    self.assertIsInstance(root, Path)
            finally:
                os.chdir(original_cwd)
    
    def test_get_relative_path_with_pathlib_path(self):
        """Test get_relative_path with Path object as input"""
        with patch('core.path_utils.get_claude_root') as mock_root:
            mock_root.return_value = Path("/test/.claude")
            
            # Pass Path object instead of string
            result = get_relative_path(Path("system/core"))
            self.assertEqual(result, Path("/test/.claude/system/core"))
    
    def test_setup_import_path_with_non_existent_paths(self):
        """Test setup_import_path with non-existent paths"""
        with patch('core.path_utils.get_claude_root') as mock_root:
            # Return non-existent path
            mock_root.return_value = Path("/non/existent/.claude")
            
            # Should not raise error
            setup_import_path()
            
            # Paths should still be added to sys.path
            self.assertIn("/non/existent/.claude/system", sys.path)


if __name__ == '__main__':
    unittest.main(verbosity=2)