#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for cache module
Achieving 100% test coverage
"""

import os
import json
import pickle
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch, MagicMock, mock_open

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
from core.cache import (
    FileInfo, CacheEntry, AnalysisCache, CachedAnalyzer,
    cache_system, analyzer,
    calculate_file_hash, calculate_project_hash, get_cache_key,
    load_cache, save_cache, cleanup_old_cache, get_statistics,
    clear_all_cache, analyze_project
)


class TestFileInfo(unittest.TestCase):
    """Tests for FileInfo dataclass"""
    
    def test_file_info_creation(self):
        """Test FileInfo creation"""
        info = FileInfo(
            path="test.py",
            size=1024,
            modified=1234567890.0,
            hash="abc123"
        )
        
        self.assertEqual(info.path, "test.py")
        self.assertEqual(info.size, 1024)
        self.assertEqual(info.modified, 1234567890.0)
        self.assertEqual(info.hash, "abc123")


class TestCacheEntry(unittest.TestCase):
    """Tests for CacheEntry dataclass"""
    
    def test_cache_entry_creation(self):
        """Test CacheEntry creation"""
        entry = CacheEntry(
            project_hash="hash123",
            timestamp="2024-01-01 12:00:00 JST",
            files={},
            analysis_result={"test": "data"},
            execution_time=1.5
        )
        
        self.assertEqual(entry.project_hash, "hash123")
        self.assertEqual(entry.timestamp, "2024-01-01 12:00:00 JST")
        self.assertEqual(entry.files, {})
        self.assertEqual(entry.analysis_result, {"test": "data"})
        self.assertEqual(entry.execution_time, 1.5)


class TestAnalysisCache(unittest.TestCase):
    """Tests for AnalysisCache class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        with patch('core.cache.paths') as mock_paths:
            mock_paths.cache = Path(self.temp_dir)
            self.cache = AnalysisCache()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directories(self):
        """Test that initialization creates necessary directories"""
        self.assertTrue(self.cache.cache_dir.exists())
        self.assertTrue(self.cache.detailed_cache_dir.exists())
    
    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        hash_result = self.cache.calculate_file_hash(test_file)
        
        # Should produce consistent hash
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
    
    def test_calculate_file_hash_error(self):
        """Test file hash calculation with error"""
        with patch('core.cache.logger') as mock_logger:
            result = self.cache.calculate_file_hash(Path("/nonexistent/file"))
            self.assertEqual(result, "")
            mock_logger.warn.assert_called()
    
    def test_calculate_project_hash(self):
        """Test project hash calculation"""
        # Create test project structure
        project_dir = Path(self.temp_dir) / "project"
        project_dir.mkdir()
        (project_dir / "test.py").write_text("python code")
        (project_dir / "test.js").write_text("js code")
        
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [
                project_dir / "test.py",
                project_dir / "test.js"
            ]
            
            hash_result = self.cache.calculate_project_hash(project_dir)
            
            self.assertIsInstance(hash_result, str)
            self.assertEqual(len(hash_result), 16)  # Truncated to 16 chars
    
    def test_calculate_project_hash_excludes_patterns(self):
        """Test that project hash excludes certain directories"""
        project_dir = Path(self.temp_dir) / "project"
        project_dir.mkdir()
        
        # Create files in excluded directories
        (project_dir / ".git").mkdir()
        (project_dir / ".git" / "config").touch()
        (project_dir / "node_modules").mkdir()
        (project_dir / "node_modules" / "package.json").touch()
        (project_dir / "__pycache__").mkdir()
        (project_dir / "__pycache__" / "test.pyc").touch()
        
        # Create included file
        (project_dir / "main.py").write_text("code")
        
        # Mock rglob to return all files
        with patch.object(Path, 'rglob') as mock_rglob:
            mock_rglob.return_value = [
                project_dir / ".git" / "config",
                project_dir / "node_modules" / "package.json",
                project_dir / "__pycache__" / "test.pyc",
                project_dir / "main.py"
            ]
            
            # Calculate hash - should only include main.py
            with patch.object(self.cache, 'calculate_file_hash', return_value="hash"):
                self.cache.calculate_project_hash(project_dir)
                
                # Should only hash main.py
                self.cache.calculate_file_hash.assert_called_once()
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        with patch.object(self.cache, 'calculate_project_hash', return_value="project_hash"):
            # Without params
            key1 = self.cache.get_cache_key("operation")
            self.assertEqual(key1, "project_hash_operation")
            
            # With params
            key2 = self.cache.get_cache_key("operation", {"param": "value"})
            self.assertTrue(key2.startswith("project_hash_operation_"))
    
    def test_load_cache_not_found(self):
        """Test loading cache when file doesn't exist"""
        result = self.cache.load_cache("nonexistent_op")
        self.assertIsNone(result)
        self.assertFalse(self.cache.cache_hit_rate[-1])
    
    def test_load_cache_success(self):
        """Test successful cache load"""
        # Create cache file
        cache_key = "test_key"
        cache_file = self.cache.detailed_cache_dir / f"{cache_key}.pkl"
        
        cache_data = {
            'project_hash': 'hash123',
            'timestamp': '2024-01-01 12:00:00',
            'analysis_result': {'data': 'test'},
            'execution_time': 1.5
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        with patch.object(self.cache, 'get_cache_key', return_value=cache_key):
            with patch.object(self.cache, 'calculate_project_hash', return_value='hash123'):
                with patch('core.cache.get_jst_now') as mock_now:
                    mock_now.return_value = datetime(2024, 1, 1, 12, 30, 0)
                    
                    result = self.cache.load_cache("test_op")
                    
                    self.assertEqual(result, {'data': 'test'})
                    self.assertTrue(self.cache.cache_hit_rate[-1])
    
    def test_load_cache_expired(self):
        """Test loading expired cache"""
        cache_key = "test_key"
        cache_file = self.cache.detailed_cache_dir / f"{cache_key}.pkl"
        
        cache_data = {
            'project_hash': 'hash123',
            'timestamp': '2024-01-01 12:00:00',
            'analysis_result': {'data': 'test'},
            'execution_time': 1.5
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        with patch.object(self.cache, 'get_cache_key', return_value=cache_key):
            with patch('core.cache.get_jst_now') as mock_now:
                # Set current time to 31 days later
                mock_now.return_value = datetime(2024, 2, 2, 12, 0, 0)
                
                result = self.cache.load_cache("test_op")
                
                self.assertIsNone(result)
                self.assertFalse(cache_file.exists())
    
    def test_load_cache_with_jst_suffix(self):
        """Test loading cache with JST suffix in timestamp"""
        cache_key = "test_key"
        cache_file = self.cache.detailed_cache_dir / f"{cache_key}.pkl"
        
        cache_data = {
            'project_hash': 'hash123',
            'timestamp': '2024-01-01 12:00:00 JST',  # With JST suffix
            'analysis_result': {'data': 'test'},
            'execution_time': 1.5
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        with patch.object(self.cache, 'get_cache_key', return_value=cache_key):
            with patch.object(self.cache, 'calculate_project_hash', return_value='hash123'):
                with patch('core.cache.get_jst_now') as mock_now:
                    mock_now.return_value = datetime(2024, 1, 1, 12, 30, 0)
                    
                    result = self.cache.load_cache("test_op")
                    self.assertEqual(result, {'data': 'test'})
    
    def test_load_cache_project_changed(self):
        """Test loading cache when project has changed"""
        cache_key = "test_key"
        cache_file = self.cache.detailed_cache_dir / f"{cache_key}.pkl"
        
        cache_data = {
            'project_hash': 'old_hash',
            'timestamp': '2024-01-01 12:00:00',
            'analysis_result': {'data': 'test'},
            'execution_time': 1.5
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        with patch.object(self.cache, 'get_cache_key', return_value=cache_key):
            with patch.object(self.cache, 'calculate_project_hash', return_value='new_hash'):
                with patch('core.cache.get_jst_now') as mock_now:
                    mock_now.return_value = datetime(2024, 1, 1, 12, 30, 0)
                    
                    result = self.cache.load_cache("test_op")
                    
                    # Should return differential analysis
                    self.assertEqual(result['_cache_mode'], 'differential')
                    self.assertEqual(result['_old_hash'], 'old_hash')
                    self.assertEqual(result['_new_hash'], 'new_hash')
    
    def test_load_cache_corrupted(self):
        """Test loading corrupted cache file"""
        cache_key = "test_key"
        cache_file = self.cache.detailed_cache_dir / f"{cache_key}.pkl"
        cache_file.write_text("corrupted data")
        
        with patch.object(self.cache, 'get_cache_key', return_value=cache_key):
            with patch('core.cache.logger') as mock_logger:
                result = self.cache.load_cache("test_op")
                
                self.assertIsNone(result)
                mock_logger.warn.assert_called()
    
    def test_save_cache(self):
        """Test saving cache"""
        with patch.object(self.cache, 'get_cache_key', return_value="test_key"):
            with patch.object(self.cache, 'calculate_project_hash', return_value="hash123"):
                with patch('core.cache.format_jst_time', return_value="2024-01-01 12:00:00"):
                    with patch('core.cache.logger') as mock_logger:
                        self.cache.save_cache("test_op", {"result": "data"}, 1.5, {"param": "value"})
                        
                        # Check file was created
                        cache_file = self.cache.detailed_cache_dir / "test_key.pkl"
                        self.assertTrue(cache_file.exists())
                        
                        # Check content
                        with open(cache_file, 'rb') as f:
                            saved_data = pickle.load(f)
                        
                        self.assertEqual(saved_data['project_hash'], "hash123")
                        self.assertEqual(saved_data['analysis_result'], {"result": "data"})
                        self.assertEqual(saved_data['execution_time'], 1.5)
                        
                        mock_logger.info.assert_called()
    
    def test_save_cache_error(self):
        """Test save cache with error"""
        with patch.object(self.cache, 'get_cache_key', return_value="test_key"):
            with patch('builtins.open', side_effect=Exception("Write error")):
                with patch('core.cache.logger') as mock_logger:
                    self.cache.save_cache("test_op", {"result": "data"}, 1.5)
                    mock_logger.warn.assert_called()
    
    def test_differential_analysis(self):
        """Test differential analysis"""
        old_cache = {
            'project_hash': 'old_hash',
            'analysis_result': {'original': 'data', 'count': 5}
        }
        
        with patch('core.cache.logger') as mock_logger:
            result = self.cache._differential_analysis(old_cache, 'new_hash')
            
            self.assertEqual(result['_cache_mode'], 'differential')
            self.assertEqual(result['_old_hash'], 'old_hash')
            self.assertEqual(result['_new_hash'], 'new_hash')
            self.assertEqual(result['original'], 'data')
            self.assertEqual(result['count'], 5)
            
            mock_logger.info.assert_called()
    
    def test_update_cache_index(self):
        """Test updating cache index"""
        with patch('core.cache.format_jst_time', return_value="2024-01-01 12:00:00"):
            self.cache._update_cache_index("key1", "operation1", 1.5)
            
            # Check index file
            self.assertTrue(self.cache.cache_file.exists())
            
            with open(self.cache.cache_file, 'r') as f:
                index = json.load(f)
            
            self.assertIn("key1", index)
            self.assertEqual(index["key1"]["operation"], "operation1")
            self.assertEqual(index["key1"]["execution_time"], 1.5)
    
    def test_update_cache_index_existing(self):
        """Test updating existing cache index"""
        # Create existing index
        existing_index = {
            "old_key": {"operation": "old_op", "timestamp": "old_time", "execution_time": 1.0}
        }
        
        with open(self.cache.cache_file, 'w') as f:
            json.dump(existing_index, f)
        
        with patch('core.cache.format_jst_time', return_value="2024-01-01 12:00:00"):
            self.cache._update_cache_index("new_key", "new_op", 2.0)
            
            with open(self.cache.cache_file, 'r') as f:
                index = json.load(f)
            
            # Old entry should still exist
            self.assertIn("old_key", index)
            # New entry should be added
            self.assertIn("new_key", index)
    
    def test_update_cache_index_corrupted(self):
        """Test updating cache index with corrupted file"""
        # Create corrupted index file
        self.cache.cache_file.write_text("corrupted json")
        
        with patch('core.cache.format_jst_time', return_value="2024-01-01 12:00:00"):
            # Should not raise exception
            self.cache._update_cache_index("key1", "op1", 1.5)
            
            # Should create new valid index
            with open(self.cache.cache_file, 'r') as f:
                index = json.load(f)
            self.assertIn("key1", index)
    
    def test_cleanup_old_cache(self):
        """Test cleanup of old cache files"""
        # Create old cache file
        old_file = self.cache.detailed_cache_dir / "old.pkl"
        old_file.touch()
        
        # Set modification time to old
        old_time = time.time() - (31 * 24 * 3600)  # 31 days ago
        os.utime(old_file, (old_time, old_time))
        
        # Create recent file
        recent_file = self.cache.detailed_cache_dir / "recent.pkl"
        recent_file.touch()
        
        with patch('core.cache.get_jst_now') as mock_now:
            mock_now.return_value = datetime.now()
            with patch('core.cache.logger') as mock_logger:
                self.cache.cleanup_old_cache()
                
                self.assertFalse(old_file.exists())
                self.assertTrue(recent_file.exists())
                mock_logger.info.assert_called()
    
    def test_cleanup_old_cache_error(self):
        """Test cleanup with error"""
        problem_file = self.cache.detailed_cache_dir / "problem.pkl"
        problem_file.touch()
        
        with patch('pathlib.Path.unlink', side_effect=Exception("Permission denied")):
            with patch('core.cache.logger') as mock_logger:
                self.cache.cleanup_old_cache()
                mock_logger.warn.assert_called()
    
    def test_get_statistics_empty(self):
        """Test statistics with no cache operations"""
        stats = self.cache.get_statistics()
        
        self.assertEqual(stats['hit_rate'], 0)
        self.assertEqual(stats['total_requests'], 0)
        self.assertEqual(stats['cache_hits'], 0)
        self.assertEqual(stats['time_saved'], 0)
    
    def test_get_statistics_with_data(self):
        """Test statistics with cache operations"""
        # Generate hits and misses
        self.cache.cache_hit_rate = [True, True, False, True]
        
        # Create index file with time data
        index = {
            "key1": {"execution_time": 1.5},
            "key2": {"execution_time": 2.0}
        }
        with open(self.cache.cache_file, 'w') as f:
            json.dump(index, f)
        
        stats = self.cache.get_statistics()
        
        self.assertEqual(stats['total_requests'], 4)
        self.assertEqual(stats['cache_hits'], 3)
        self.assertEqual(stats['hit_rate'], 75.0)
        self.assertEqual(stats['time_saved'], 3.5)
    
    def test_get_statistics_index_error(self):
        """Test statistics when index file has error"""
        self.cache.cache_hit_rate = [True, False]
        
        # Create corrupted index
        self.cache.cache_file.write_text("corrupted")
        
        stats = self.cache.get_statistics()
        
        self.assertEqual(stats['total_requests'], 2)
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['time_saved'], 0)
    
    def test_clear_all_cache(self):
        """Test clearing all cache"""
        # Create cache files
        cache_file1 = self.cache.detailed_cache_dir / "cache1.pkl"
        cache_file2 = self.cache.detailed_cache_dir / "cache2.pkl"
        cache_file1.touch()
        cache_file2.touch()
        
        # Create index
        self.cache.cache_file.touch()
        
        # Add hit rate data
        self.cache.cache_hit_rate = [True, False]
        
        with patch('core.cache.logger') as mock_logger:
            self.cache.clear_all_cache()
            
            self.assertFalse(cache_file1.exists())
            self.assertFalse(cache_file2.exists())
            self.assertFalse(self.cache.cache_file.exists())
            self.assertEqual(self.cache.cache_hit_rate, [])
            mock_logger.info.assert_called()


class TestCachedAnalyzer(unittest.TestCase):
    """Tests for CachedAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CachedAnalyzer()
    
    def test_analyze_project_with_cache(self):
        """Test project analysis with cache hit"""
        cached_result = {"cached": True, "data": "test"}
        
        with patch.object(self.analyzer.cache, 'load_cache', return_value=cached_result):
            result = self.analyzer.analyze_project()
            self.assertEqual(result, cached_result)
    
    def test_analyze_project_without_cache(self):
        """Test project analysis with cache miss"""
        with patch.object(self.analyzer.cache, 'load_cache', return_value=None):
            with patch.object(self.analyzer.cache, 'save_cache') as mock_save:
                with patch('core.cache.logger') as mock_logger:
                    result = self.analyzer.analyze_project()
                    
                    # Should perform actual analysis
                    self.assertIn('project_type', result)
                    self.assertEqual(result['project_type'], 'vue_quality_management_system')
                    
                    # Should log
                    mock_logger.info.assert_called()
                    
                    # Should save to cache
                    mock_save.assert_called_once()
    
    def test_analyze_project_force_refresh(self):
        """Test forced refresh ignores cache"""
        cached_result = {"cached": True}
        
        with patch.object(self.analyzer.cache, 'load_cache', return_value=cached_result):
            with patch.object(self.analyzer.cache, 'save_cache'):
                result = self.analyzer.analyze_project(force_refresh=True)
                
                # Should not return cached result
                self.assertNotEqual(result, cached_result)
                self.assertIn('project_type', result)
    
    def test_perform_actual_analysis(self):
        """Test the actual analysis implementation"""
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [Path("file1.vue"), Path("file2.vue")]
            
            result = self.analyzer._perform_actual_analysis()
            
            self.assertEqual(result['project_type'], 'vue_quality_management_system')
            self.assertEqual(result['version'], 'v1.0')
            self.assertIn('components', result)
            self.assertIn('statistics', result)


class TestModuleLevelFunctions(unittest.TestCase):
    """Tests for module-level convenience functions"""
    
    def test_calculate_file_hash(self):
        """Test module-level calculate_file_hash"""
        test_file = Path(__file__)
        result = calculate_file_hash(test_file)
        self.assertIsInstance(result, str)
    
    def test_calculate_project_hash(self):
        """Test module-level calculate_project_hash"""
        result = calculate_project_hash()
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 16)
    
    def test_get_cache_key(self):
        """Test module-level get_cache_key"""
        key = get_cache_key("operation", {"param": "value"})
        self.assertIsInstance(key, str)
        self.assertIn("operation", key)
    
    def test_load_cache(self):
        """Test module-level load_cache"""
        with patch.object(cache_system, 'load_cache', return_value={"data": "test"}):
            result = load_cache("operation")
            self.assertEqual(result, {"data": "test"})
    
    def test_save_cache(self):
        """Test module-level save_cache"""
        with patch.object(cache_system, 'save_cache') as mock_save:
            save_cache("operation", {"result": "data"}, 1.5)
            mock_save.assert_called_once_with("operation", {"result": "data"}, 1.5, None)
    
    def test_cleanup_old_cache(self):
        """Test module-level cleanup_old_cache"""
        with patch.object(cache_system, 'cleanup_old_cache') as mock_cleanup:
            cleanup_old_cache()
            mock_cleanup.assert_called_once()
    
    def test_get_statistics(self):
        """Test module-level get_statistics"""
        with patch.object(cache_system, 'get_statistics', return_value={"hit_rate": 75}):
            stats = get_statistics()
            self.assertEqual(stats, {"hit_rate": 75})
    
    def test_clear_all_cache(self):
        """Test module-level clear_all_cache"""
        with patch.object(cache_system, 'clear_all_cache') as mock_clear:
            clear_all_cache()
            mock_clear.assert_called_once()
    
    def test_analyze_project(self):
        """Test module-level analyze_project"""
        with patch.object(analyzer, 'analyze_project', return_value={"analysis": "result"}):
            result = analyze_project()
            self.assertEqual(result, {"analysis": "result"})


class TestGlobalInstances(unittest.TestCase):
    """Tests for global instances"""
    
    def test_cache_system_instance(self):
        """Test cache_system is AnalysisCache instance"""
        self.assertIsInstance(cache_system, AnalysisCache)
    
    def test_analyzer_instance(self):
        """Test analyzer is CachedAnalyzer instance"""
        self.assertIsInstance(analyzer, CachedAnalyzer)


if __name__ == '__main__':
    unittest.main(verbosity=2)