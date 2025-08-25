#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for cache_optimized module
Achieving 100% test coverage
"""

import os
import time
import json
import pickle
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta

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
from core.cache_optimized import (
    CacheOptimized, AnalysisCache, OptimizedCachedAnalyzer,
    get_cache, get_analysis_cache
)


class TestCacheOptimized(unittest.TestCase):
    """Tests for CacheOptimized class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = CacheOptimized(cache_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_cache_dir(self):
        """Test that initialization creates cache directory"""
        test_dir = os.path.join(self.temp_dir, "test_cache")
        cache = CacheOptimized(cache_dir=test_dir)
        self.assertTrue(os.path.exists(test_dir))
    
    def test_init_with_default_dir(self):
        """Test initialization with default directory"""
        with patch('core.cache_optimized.paths') as mock_paths:
            mock_paths.cache = Path(self.temp_dir) / "default_cache"
            cache = CacheOptimized()
            self.assertEqual(cache.cache_dir, mock_paths.cache)
    
    def test_set_and_get_value(self):
        """Test setting and getting a value"""
        self.cache.set("test_key", {"data": "test_value"})
        result = self.cache.get("test_key")
        self.assertEqual(result, {"data": "test_value"})
    
    def test_get_nonexistent_key(self):
        """Test getting a nonexistent key"""
        result = self.cache.get("nonexistent", "default")
        self.assertEqual(result, "default")
    
    def test_memory_cache_hit(self):
        """Test memory cache hit statistics"""
        self.cache.set("test", "value")
        self.cache.get("test")  # Hit
        self.assertEqual(self.cache.stats['memory_hits'], 1)
        self.assertEqual(self.cache.stats['hits'], 1)
    
    def test_memory_cache_expiry(self):
        """Test memory cache expiry"""
        # Set with very short TTL
        self.cache.set("test", "value", ttl=0.001)
        time.sleep(0.002)
        result = self.cache.get("test")
        self.assertIsNone(result)
    
    def test_disk_cache_hit(self):
        """Test disk cache hit when not in memory"""
        # Set value
        self.cache.set("test", "value")
        
        # Clear memory cache
        self.cache.memory_cache.clear()
        
        # Get should hit disk cache
        result = self.cache.get("test")
        self.assertEqual(result, "value")
        self.assertEqual(self.cache.stats['disk_hits'], 1)
    
    def test_disk_cache_expiry(self):
        """Test disk cache expiry"""
        # Set with short TTL
        self.cache.set("test", "value", ttl=0.001)
        
        # Clear memory cache
        self.cache.memory_cache.clear()
        
        # Wait for expiry
        time.sleep(0.002)
        
        result = self.cache.get("test")
        self.assertIsNone(result)
    
    def test_disk_cache_corruption(self):
        """Test handling of corrupted disk cache"""
        key = "test"
        cache_file = self.cache._get_cache_file(key)
        
        # Write corrupted data
        cache_file.write_bytes(b"corrupted data")
        
        # Should return default
        result = self.cache.get(key, "default")
        self.assertEqual(result, "default")
        
        # File should be deleted
        self.assertFalse(cache_file.exists())
    
    def test_invalidate(self):
        """Test cache invalidation"""
        self.cache.set("test", "value")
        self.cache.invalidate("test")
        
        result = self.cache.get("test")
        self.assertIsNone(result)
        
        # Check disk cache is also removed
        cache_file = self.cache._get_cache_file("test")
        self.assertFalse(cache_file.exists())
    
    def test_clear_all(self):
        """Test clearing all cache"""
        # Set multiple values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear_all()
        
        # Memory cache should be empty
        self.assertEqual(len(self.cache.memory_cache), 0)
        
        # Disk cache should be empty
        cache_files = list(Path(self.temp_dir).glob("*.cache"))
        self.assertEqual(len(cache_files), 0)
        
        # Stats should be reset
        self.assertEqual(self.cache.stats['hits'], 0)
        self.assertEqual(self.cache.stats['misses'], 0)
    
    def test_get_stats(self):
        """Test getting cache statistics"""
        # Generate some statistics
        self.cache.set("hit_key", "value")
        self.cache.get("hit_key")  # Hit
        self.cache.get("miss_key")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_ratio'], 0.5)
        self.assertEqual(stats['memory_cache_size'], 1)
        self.assertIn('performance_improvement', stats)
    
    def test_cleanup_old_cache(self):
        """Test cleanup of old cache files"""
        # Create old cache file
        old_file = Path(self.temp_dir) / "old.cache"
        old_file.touch()
        
        # Modify time to be old
        old_time = time.time() - (self.cache.config['disk_cache_ttl'] + 1)
        os.utime(old_file, (old_time, old_time))
        
        # Run cleanup
        self.cache._cleanup_old_cache()
        
        # Old file should be deleted
        self.assertFalse(old_file.exists())
    
    def test_cleanup_old_cache_error_handling(self):
        """Test cleanup error handling"""
        # Create a file that can't be deleted
        problem_file = Path(self.temp_dir) / "problem.cache"
        problem_file.touch()
        
        with patch('pathlib.Path.unlink', side_effect=Exception("Permission denied")):
            # Should not raise exception
            self.cache._cleanup_old_cache()
    
    def test_is_valid_cache_with_custom_ttl(self):
        """Test cache validation with custom TTL in entry"""
        cache_entry = {
            'value': 'test',
            'timestamp': time.time() - 10,
            'ttl': 5  # Custom TTL
        }
        
        # Should be invalid (10 seconds old, 5 second TTL)
        self.assertFalse(self.cache._is_valid_cache(cache_entry, 3600))
    
    def test_set_with_write_error(self):
        """Test handling of write errors"""
        with patch('builtins.open', side_effect=Exception("Write error")):
            # Should not raise exception
            self.cache.set("test", "value")
            
            # Value should still be in memory cache
            self.assertEqual(self.cache.memory_cache["test"]['value'], "value")


class TestAnalysisCache(unittest.TestCase):
    """Tests for AnalysisCache class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        with patch('core.cache_optimized.paths') as mock_paths:
            mock_paths.cache = Path(self.temp_dir)
            self.cache = AnalysisCache()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directories(self):
        """Test that initialization creates necessary directories"""
        cache_dir = Path(self.temp_dir) / "core_analysis"
        self.assertTrue(cache_dir.exists())
    
    def test_cache_analysis(self):
        """Test caching analysis results"""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("test content")
        
        analysis_result = {"functions": 5, "classes": 2}
        self.cache.cache_analysis(str(test_file), analysis_result)
        
        # Retrieve cached analysis
        result = self.cache.get_analysis(str(test_file))
        self.assertEqual(result, analysis_result)
    
    def test_get_analysis_nonexistent_file(self):
        """Test getting analysis for nonexistent file"""
        result = self.cache.get_analysis("/nonexistent/file.py")
        self.assertIsNone(result)
    
    def test_get_analysis_modified_file(self):
        """Test that modified files invalidate cache"""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("original content")
        
        # Cache analysis
        self.cache.cache_analysis(str(test_file), {"version": 1})
        
        # Modify file
        time.sleep(0.01)  # Ensure different mtime
        test_file.write_text("modified content")
        
        # Should return None (cache invalidated)
        result = self.cache.get_analysis(str(test_file))
        self.assertIsNone(result)
    
    def test_save_and_load_cache(self):
        """Test save_cache and load_cache methods"""
        operation = "test_op"
        params = {"param1": "value1"}
        data = {"result": "data"}
        
        self.cache.save_cache(operation, data, 1.5, params)
        result = self.cache.load_cache(operation, params)
        
        self.assertEqual(result, data)
        self.assertTrue(self.cache.cache_hit_rate[-1])  # Last was a hit
    
    def test_load_cache_miss(self):
        """Test cache miss tracking"""
        result = self.cache.load_cache("nonexistent_op", {})
        self.assertIsNone(result)
        self.assertFalse(self.cache.cache_hit_rate[-1])  # Last was a miss
    
    def test_differential_analysis(self):
        """Test differential analysis for changed projects"""
        cache_entry = {
            'analysis_result': {'original': 'data'},
            'project_hash': 'old_hash'
        }
        
        result = self.cache._differential_analysis(cache_entry, 'new_hash')
        
        self.assertEqual(result['_cache_mode'], 'differential')
        self.assertEqual(result['_old_hash'], 'old_hash')
        self.assertEqual(result['_new_hash'], 'new_hash')
        self.assertEqual(result['original'], 'data')
    
    def test_get_statistics(self):
        """Test getting cache statistics"""
        # Generate some hits and misses
        self.cache.load_cache("op1", {})  # Miss
        self.cache.save_cache("op1", {"data": 1}, 1.0, {})
        self.cache.load_cache("op1", {})  # Hit
        
        stats = self.cache.get_statistics()
        
        self.assertEqual(stats['total_requests'], 2)
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['cache_misses'], 1)
        self.assertEqual(stats['hit_rate'], 50.0)
    
    def test_get_statistics_empty(self):
        """Test statistics with no cache operations"""
        stats = self.cache.get_statistics()
        
        self.assertEqual(stats['total_requests'], 0)
        self.assertEqual(stats['cache_hits'], 0)
        self.assertEqual(stats['hit_rate'], 0)
    
    def test_cleanup_old_cache_method(self):
        """Test cleanup_old_cache method"""
        # Inherits from parent class
        self.cache.cleanup_old_cache()
        # Should not raise exception
    
    def test_load_cached_module(self):
        """Test loading cached modules"""
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            
            # First call should import
            result1 = self.cache.load_cached_module("test_module")
            self.assertEqual(result1, mock_module)
            mock_import.assert_called_once()
            
            # Second call should use cache
            mock_import.reset_mock()
            result2 = self.cache.load_cached_module("test_module")
            self.assertEqual(result2, mock_module)
            mock_import.assert_not_called()
    
    def test_save_and_load_test_results(self):
        """Test saving and loading test results"""
        test_suite = "unit_tests"
        results = {"passed": 10, "failed": 0}
        
        self.cache.save_test_results(test_suite, results)
        loaded = self.cache.load_test_results(test_suite)
        
        self.assertEqual(loaded, results)
    
    def test_load_test_results_not_found(self):
        """Test loading non-existent test results"""
        result = self.cache.load_test_results("nonexistent_suite")
        self.assertIsNone(result)


class TestOptimizedCachedAnalyzer(unittest.TestCase):
    """Tests for OptimizedCachedAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = OptimizedCachedAnalyzer()
    
    def test_analyze_project_with_cache(self):
        """Test project analysis with cache hit"""
        cached_data = {"cached": True, "data": "test"}
        
        with patch.object(self.analyzer.cache, 'get', return_value=cached_data):
            result = self.analyzer.analyze_project()
            self.assertEqual(result, cached_data)
    
    def test_analyze_project_without_cache(self):
        """Test project analysis with cache miss"""
        with patch.object(self.analyzer.cache, 'get', return_value=None):
            with patch.object(self.analyzer.cache, 'set') as mock_set:
                result = self.analyzer.analyze_project()
                
                # Should perform actual analysis
                self.assertIn('analysis_type', result)
                self.assertIn('components', result)
                
                # Should cache result
                mock_set.assert_called_once()
    
    def test_analyze_project_force_refresh(self):
        """Test forced refresh ignores cache"""
        cached_data = {"cached": True}
        
        with patch.object(self.analyzer.cache, 'get', return_value=cached_data):
            with patch.object(self.analyzer.cache, 'set') as mock_set:
                result = self.analyzer.analyze_project(force_refresh=True)
                
                # Should not return cached data
                self.assertNotEqual(result, cached_data)
                
                # Should save new result
                mock_set.assert_called_once()
    
    def test_perform_actual_analysis(self):
        """Test the actual analysis method"""
        result = self.analyzer._perform_actual_analysis()
        
        self.assertEqual(result['analysis_type'], 'project_analysis')
        self.assertIn('frontend', result['components'])
        self.assertIn('backend', result['components'])
        self.assertIn('stats', result)


class TestGlobalInstances(unittest.TestCase):
    """Tests for global cache instances"""
    
    def test_get_cache_singleton(self):
        """Test that get_cache returns same instance"""
        cache1 = get_cache()
        cache2 = get_cache()
        self.assertIs(cache1, cache2)
    
    def test_get_analysis_cache_singleton(self):
        """Test that get_analysis_cache returns same instance"""
        cache1 = get_analysis_cache()
        cache2 = get_analysis_cache()
        self.assertIs(cache1, cache2)
    
    def test_cache_types(self):
        """Test that caches are correct types"""
        cache = get_cache()
        self.assertIsInstance(cache, CacheOptimized)
        
        analysis_cache = get_analysis_cache()
        self.assertIsInstance(analysis_cache, AnalysisCache)


class TestMainExecution(unittest.TestCase):
    """Test main execution block"""
    
    @patch('builtins.print')
    def test_main_demo(self, mock_print):
        """Test the demo in __main__ block"""
        # Import the module to run __main__
        import importlib
        import core.cache_optimized
        
        # Capture the __name__ attribute
        original_name = core.cache_optimized.__name__
        
        try:
            # Simulate running as main
            core.cache_optimized.__name__ = "__main__"
            
            # Reload to trigger __main__ block
            with patch('core.cache_optimized.get_cache') as mock_get_cache:
                with patch('core.cache_optimized.get_analysis_cache') as mock_get_analysis:
                    mock_cache = MagicMock()
                    mock_cache.get_stats.return_value = {
                        'hits': 1,
                        'misses': 0,
                        'hit_ratio': 1.0
                    }
                    mock_get_cache.return_value = mock_cache
                    
                    mock_analysis = MagicMock()
                    mock_analysis.get_analysis.return_value = {"test": "data"}
                    mock_get_analysis.return_value = mock_analysis
                    
                    # Execute the main block
                    exec(compile(open(core.cache_optimized.__file__).read(), 
                                 core.cache_optimized.__file__, 'exec'))
                    
                    # Verify demo was executed
                    mock_print.assert_called()
                    self.assertTrue(any("Cache System Demo" in str(call) 
                                       for call in mock_print.call_args_list))
        finally:
            # Restore original name
            core.cache_optimized.__name__ = original_name


if __name__ == '__main__':
    unittest.main(verbosity=2)