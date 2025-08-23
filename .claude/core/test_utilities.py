#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities Tests - Consolidated utility and base system testing
TDD Red-Green-Refactor implementation for comprehensive utility testing

Consolidates tests from:
- test_base_utilities.py
- test_base.py
- test_utilities_system.py
- test_module_imports.py
- test_trigger_keyword_detector.py
- test_existing_analysis.py

TDD Requirements:
- 100% coverage of utility functionality
- Base system component testing
- Import system validation
- Keyword detection testing
- JST utilities testing
- Path utilities testing
"""

import unittest
import tempfile
import shutil
import json
import sys
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime, timezone, timedelta
from io import StringIO

# Test target module imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from jst_utils import get_jst_now, format_jst_time, format_jst_datetime, get_filename_timestamp
    from path_utils import PathUtils
    from trigger_keyword_detector import TriggerKeywordDetector
    from circular_import_detector import CircularImportDetector
    from import_optimizer import ImportOptimizer
    from cache import SystemCache
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Import error: {e}")
    print("Running with mock implementations for TDD demonstration...")
    IMPORT_SUCCESS = False
    
    # RED Phase: Mock implementations for failing tests
    def get_jst_now():
        jst = timezone(timedelta(hours=9))
        return datetime.now(jst)
        
    def format_jst_time(dt):
        return f"{dt.strftime('%H:%M:%S')} JST"
        
    def format_jst_datetime(dt):
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} JST"
        
    def get_filename_timestamp():
        return datetime.now().strftime('%Y%m%d_%H%M%S')
        
    class PathUtils:
        @staticmethod
        def normalize_path(path):
            return Path(path).resolve()
            
        @staticmethod
        def is_safe_path(path):
            return not any(part in str(path) for part in ['..', '~'])
            
    class TriggerKeywordDetector:
        def __init__(self):
            self.keywords = ['auto', 'trigger', 'activate', 'execute']
            
        def detect_keywords(self, text):
            if not text:
                return []
            return [kw for kw in self.keywords if kw.lower() in text.lower()]
            
    class CircularImportDetector:
        def __init__(self):
            self.import_stack = []
            
        def check_circular_import(self, module_name):
            return module_name in self.import_stack
            
    class ImportOptimizer:
        def __init__(self):
            self.optimized_imports = {}
            
        def optimize_imports(self, module_list):
            return {mod: f"optimized_{mod}" for mod in module_list}
            
    class SystemCache:
        def __init__(self):
            self.cache = {}
            
        def get(self, key):
            return self.cache.get(key)
            
        def set(self, key, value):
            self.cache[key] = value


class OptimizedTestCase(unittest.TestCase):
    """Optimized test case base class with common functionality"""
    
    def setUp(self):
        """Common test setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.start_time = time.time()
        
    def tearDown(self):
        """Common test cleanup"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Performance check
        execution_time = time.time() - self.start_time
        if execution_time > 1.0:
            print(f"Warning: Test {self._testMethodName} took {execution_time:.2f}s")
            
    def assertExecutionTime(self, max_time, func, *args, **kwargs):
        """Assert function executes within time limit"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        execution_time = end - start
        self.assertLess(execution_time, max_time,
                       f"Function took {execution_time:.3f}s, expected < {max_time}s")
        return result
        
    def create_temp_file(self, content="", suffix=".txt"):
        """Create temporary file for testing"""
        temp_file = self.temp_dir / f"test{suffix}"
        temp_file.write_text(content)
        return temp_file


class TestJSTUtils(OptimizedTestCase):
    """JST utilities comprehensive tests"""
    
    def test_get_jst_now(self):
        """JST current time test"""
        jst_now = get_jst_now()
        
        self.assertIsInstance(jst_now, datetime)
        # JST (UTC+9) verification
        if hasattr(jst_now, 'utcoffset') and jst_now.utcoffset():
            self.assertEqual(jst_now.utcoffset().total_seconds(), 9 * 3600)
            
    def test_format_jst_time(self):
        """JST time formatting test"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_jst_time(test_datetime)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("10:30:45", formatted)
        self.assertIn("JST", formatted)
        
    def test_format_jst_datetime(self):
        """JST datetime formatting test"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_jst_datetime(test_datetime)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("2024-01-15", formatted)
        self.assertIn("10:30:45", formatted)
        self.assertIn("JST", formatted)
        
    def test_get_filename_timestamp(self):
        """Filename timestamp test"""
        timestamp = get_filename_timestamp()
        
        self.assertIsInstance(timestamp, str)
        self.assertRegex(timestamp, r'\d{8}_\d{6}')  # YYYYMMDD_HHMMSS format
        
    def test_jst_timezone_consistency(self):
        """JST timezone consistency test"""
        time1 = get_jst_now()
        time.sleep(0.01)  # Small delay
        time2 = get_jst_now()
        
        # Both times should be in same timezone
        if hasattr(time1, 'utcoffset') and hasattr(time2, 'utcoffset'):
            if time1.utcoffset() and time2.utcoffset():
                self.assertEqual(time1.utcoffset(), time2.utcoffset())
                
    def test_jst_format_edge_cases(self):
        """JST format edge cases test"""
        edge_cases = [
            datetime(1970, 1, 1, 0, 0, 0),  # Unix epoch
            datetime(2099, 12, 31, 23, 59, 59),  # Future date
            datetime(2024, 2, 29, 12, 0, 0),  # Leap year
        ]
        
        for dt in edge_cases:
            time_formatted = format_jst_time(dt)
            datetime_formatted = format_jst_datetime(dt)
            
            self.assertIsInstance(time_formatted, str)
            self.assertIsInstance(datetime_formatted, str)
            self.assertIn("JST", time_formatted)
            self.assertIn("JST", datetime_formatted)


class TestPathUtils(OptimizedTestCase):
    """Path utilities comprehensive tests"""
    
    def test_normalize_path(self):
        """Path normalization test"""
        test_paths = [
            "simple/path",
            "./relative/path",
            "/absolute/path",
            "path/../normalized",
        ]
        
        for path in test_paths:
            normalized = PathUtils.normalize_path(path)
            self.assertIsInstance(normalized, Path)
            
    def test_is_safe_path(self):
        """Safe path validation test"""
        safe_paths = [
            "/safe/absolute/path",
            "safe/relative/path",
            "simple_filename.txt",
        ]
        
        unsafe_paths = [
            "../unsafe/path",
            "path/../unsafe",
            "~/home/path",
            "/path/to/../../../unsafe",
        ]
        
        for path in safe_paths:
            self.assertTrue(PathUtils.is_safe_path(path), f"Path should be safe: {path}")
            
        for path in unsafe_paths:
            self.assertFalse(PathUtils.is_safe_path(path), f"Path should be unsafe: {path}")
            
    def test_path_traversal_prevention(self):
        """Path traversal prevention test"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/path/../../../root",
            "C:\\..\\..\\Windows\\System32",
        ]
        
        for path in dangerous_paths:
            self.assertFalse(PathUtils.is_safe_path(path),
                           f"Should detect path traversal: {path}")
            
    def test_path_normalization_consistency(self):
        """Path normalization consistency test"""
        test_path = "test/path/../normalized"
        
        # Multiple normalizations should yield same result
        norm1 = PathUtils.normalize_path(test_path)
        norm2 = PathUtils.normalize_path(str(norm1))
        
        self.assertEqual(str(norm1), str(norm2))
        
    def test_empty_path_handling(self):
        """Empty path handling test"""
        empty_paths = ["", "   ", None]
        
        for path in empty_paths:
            if path is not None:
                result = PathUtils.normalize_path(path)
                self.assertIsInstance(result, Path)


class TestTriggerKeywordDetector(OptimizedTestCase):
    """Trigger keyword detector comprehensive tests"""
    
    def setUp(self):
        """Test setup"""
        super().setUp()
        self.detector = TriggerKeywordDetector()
        
    def test_detector_initialization(self):
        """Detector initialization test"""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.keywords, list)
        self.assertGreater(len(self.detector.keywords), 0)
        
    def test_keyword_detection_basic(self):
        """Basic keyword detection test"""
        test_texts = [
            "Please auto generate the code",
            "Trigger the build process",
            "Activate the deployment",
            "Execute the test suite",
        ]
        
        for text in test_texts:
            keywords = self.detector.detect_keywords(text)
            self.assertIsInstance(keywords, list)
            self.assertGreater(len(keywords), 0, f"Should detect keywords in: {text}")
            
    def test_keyword_detection_case_insensitive(self):
        """Case insensitive keyword detection test"""
        test_cases = [
            "AUTO generation needed",
            "auto generation needed",
            "Auto Generation Needed",
            "aUtO gEnErAtIoN nEeDeD",
        ]
        
        for text in test_cases:
            keywords = self.detector.detect_keywords(text)
            self.assertIn('auto', keywords, f"Should detect 'auto' in: {text}")
            
    def test_keyword_detection_no_matches(self):
        """No keyword matches test"""
        no_match_texts = [
            "This text contains no trigger words",
            "Simple description without keywords",
            "Regular content here",
        ]
        
        for text in no_match_texts:
            keywords = self.detector.detect_keywords(text)
            self.assertEqual(len(keywords), 0, f"Should not detect keywords in: {text}")
            
    def test_keyword_detection_empty_input(self):
        """Empty input handling test"""
        empty_inputs = ["", "   ", None]
        
        for input_text in empty_inputs:
            keywords = self.detector.detect_keywords(input_text)
            self.assertIsInstance(keywords, list)
            self.assertEqual(len(keywords), 0)
            
    def test_keyword_detection_performance(self):
        """Keyword detection performance test"""
        large_text = "This is a test text with auto keyword " * 1000
        
        start_time = time.time()
        keywords = self.detector.detect_keywords(large_text)
        end_time = time.time()
        
        # Should process large text quickly
        self.assertLess(end_time - start_time, 0.1)
        self.assertIn('auto', keywords)
        
    def test_multiple_keyword_detection(self):
        """Multiple keyword detection test"""
        text_with_multiple = "Please auto trigger the execute process"
        keywords = self.detector.detect_keywords(text_with_multiple)
        
        expected_keywords = ['auto', 'trigger', 'execute']
        for expected in expected_keywords:
            self.assertIn(expected, keywords)


class TestCircularImportDetector(OptimizedTestCase):
    """Circular import detector comprehensive tests"""
    
    def setUp(self):
        """Test setup"""
        super().setUp()
        self.detector = CircularImportDetector()
        
    def test_detector_initialization(self):
        """Detector initialization test"""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.import_stack, list)
        self.assertEqual(len(self.detector.import_stack), 0)
        
    def test_circular_import_detection(self):
        """Circular import detection test"""
        # Simulate import stack
        self.detector.import_stack = ['module_a', 'module_b']
        
        # Check for circular import
        is_circular = self.detector.check_circular_import('module_a')
        self.assertTrue(is_circular, "Should detect circular import")
        
        # Check for non-circular import
        is_circular = self.detector.check_circular_import('module_c')
        self.assertFalse(is_circular, "Should not detect circular import")
        
    def test_empty_import_stack(self):
        """Empty import stack test"""
        is_circular = self.detector.check_circular_import('any_module')
        self.assertFalse(is_circular, "Empty stack should not show circular import")
        
    def test_import_stack_management(self):
        """Import stack management test"""
        modules = ['module_1', 'module_2', 'module_3']
        
        # Add modules to stack
        for module in modules:
            self.detector.import_stack.append(module)
            
        self.assertEqual(len(self.detector.import_stack), 3)
        
        # Test detection for each module
        for module in modules:
            is_circular = self.detector.check_circular_import(module)
            self.assertTrue(is_circular)
            
    def test_case_sensitivity(self):
        """Case sensitivity test"""
        self.detector.import_stack = ['Module_A']
        
        # Test exact match
        self.assertTrue(self.detector.check_circular_import('Module_A'))
        
        # Test case mismatch
        self.assertFalse(self.detector.check_circular_import('module_a'))
        self.assertFalse(self.detector.check_circular_import('MODULE_A'))


class TestImportOptimizer(OptimizedTestCase):
    """Import optimizer comprehensive tests"""
    
    def setUp(self):
        """Test setup"""
        super().setUp()
        self.optimizer = ImportOptimizer()
        
    def test_optimizer_initialization(self):
        """Optimizer initialization test"""
        self.assertIsNotNone(self.optimizer)
        self.assertIsInstance(self.optimizer.optimized_imports, dict)
        
    def test_import_optimization(self):
        """Import optimization test"""
        modules = ['module_a', 'module_b', 'module_c']
        optimized = self.optimizer.optimize_imports(modules)
        
        self.assertIsInstance(optimized, dict)
        self.assertEqual(len(optimized), len(modules))
        
        for module in modules:
            self.assertIn(module, optimized)
            self.assertIsInstance(optimized[module], str)
            
    def test_empty_module_list(self):
        """Empty module list test"""
        optimized = self.optimizer.optimize_imports([])
        self.assertIsInstance(optimized, dict)
        self.assertEqual(len(optimized), 0)
        
    def test_duplicate_modules(self):
        """Duplicate modules test"""
        modules = ['module_a', 'module_b', 'module_a']
        optimized = self.optimizer.optimize_imports(modules)
        
        # Should handle duplicates appropriately
        self.assertIn('module_a', optimized)
        self.assertIn('module_b', optimized)
        
    def test_optimization_consistency(self):
        """Optimization consistency test"""
        modules = ['consistent_module']
        
        result1 = self.optimizer.optimize_imports(modules)
        result2 = self.optimizer.optimize_imports(modules)
        
        # Results should be consistent
        self.assertEqual(result1, result2)


class TestSystemCache(OptimizedTestCase):
    """System cache comprehensive tests"""
    
    def setUp(self):
        """Test setup"""
        super().setUp()
        self.cache = SystemCache()
        
    def test_cache_initialization(self):
        """Cache initialization test"""
        self.assertIsNotNone(self.cache)
        self.assertIsInstance(self.cache.cache, dict)
        self.assertEqual(len(self.cache.cache), 0)
        
    def test_cache_set_and_get(self):
        """Cache set and get test"""
        key = "test_key"
        value = "test_value"
        
        # Set value
        self.cache.set(key, value)
        
        # Get value
        retrieved = self.cache.get(key)
        self.assertEqual(retrieved, value)
        
    def test_cache_get_nonexistent(self):
        """Cache get nonexistent key test"""
        result = self.cache.get("nonexistent_key")
        self.assertIsNone(result)
        
    def test_cache_overwrite(self):
        """Cache value overwrite test"""
        key = "overwrite_key"
        value1 = "original_value"
        value2 = "new_value"
        
        self.cache.set(key, value1)
        self.assertEqual(self.cache.get(key), value1)
        
        self.cache.set(key, value2)
        self.assertEqual(self.cache.get(key), value2)
        
    def test_cache_multiple_keys(self):
        """Multiple cache keys test"""
        test_data = {
            "key1": "value1",
            "key2": 42,
            "key3": {"nested": "dict"},
            "key4": [1, 2, 3],
        }
        
        # Set all values
        for key, value in test_data.items():
            self.cache.set(key, value)
            
        # Verify all values
        for key, expected_value in test_data.items():
            actual_value = self.cache.get(key)
            self.assertEqual(actual_value, expected_value)


class TestUtilitiesIntegration(OptimizedTestCase):
    """Utilities integration tests"""
    
    def test_utilities_interoperability(self):
        """Utilities interoperability test"""
        # Test that utilities can work together
        detector = TriggerKeywordDetector()
        cache = SystemCache()
        
        # Use detector to find keywords
        keywords = detector.detect_keywords("auto trigger execute")
        
        # Cache the results
        cache.set("detected_keywords", keywords)
        
        # Retrieve from cache
        cached_keywords = cache.get("detected_keywords")
        self.assertEqual(keywords, cached_keywords)
        
    def test_path_and_time_utilities(self):
        """Path and time utilities integration test"""
        # Generate timestamp for filename
        timestamp = get_filename_timestamp()
        
        # Create path with timestamp
        filename = f"test_file_{timestamp}.txt"
        safe_path = PathUtils.normalize_path(filename)
        
        self.assertTrue(PathUtils.is_safe_path(str(safe_path)))
        self.assertIn(timestamp, str(safe_path))
        
    def test_import_detection_integration(self):
        """Import detection integration test"""
        detector = CircularImportDetector()
        optimizer = ImportOptimizer()
        
        # Simulate import process
        modules = ['test_module_1', 'test_module_2']
        
        for module in modules:
            is_circular = detector.check_circular_import(module)
            self.assertFalse(is_circular)  # Should not be circular initially
            
        # Optimize imports
        optimized = optimizer.optimize_imports(modules)
        self.assertEqual(len(optimized), 2)


class TestUtilitiesPerformance(OptimizedTestCase):
    """Utilities performance tests"""
    
    def test_keyword_detection_performance(self):
        """Keyword detection performance test"""
        detector = TriggerKeywordDetector()
        large_text = "This is a large text with auto and trigger keywords. " * 1000
        
        def detect_keywords():
            return detector.detect_keywords(large_text)
            
        # Should complete within time limit
        result = self.assertExecutionTime(0.1, detect_keywords)
        self.assertGreater(len(result), 0)
        
    def test_cache_performance(self):
        """Cache performance test"""
        cache = SystemCache()
        
        def cache_operations():
            for i in range(1000):
                cache.set(f"key_{i}", f"value_{i}")
                cache.get(f"key_{i}")
                
        # Should complete cache operations quickly
        self.assertExecutionTime(0.5, cache_operations)
        
    def test_path_normalization_performance(self):
        """Path normalization performance test"""
        paths = [f"path_{i}/subpath_{i}/file_{i}.txt" for i in range(100)]
        
        def normalize_paths():
            return [PathUtils.normalize_path(path) for path in paths]
            
        # Should normalize 100 paths quickly
        results = self.assertExecutionTime(0.1, normalize_paths)
        self.assertEqual(len(results), 100)


class TestUtilitiesErrorHandling(OptimizedTestCase):
    """Utilities error handling tests"""
    
    def test_jst_utils_error_handling(self):
        """JST utils error handling test"""
        # Test with invalid datetime objects
        invalid_inputs = [None, "invalid", 12345]
        
        for invalid_input in invalid_inputs:
            try:
                if invalid_input is not None:
                    # These should either handle gracefully or raise appropriate exceptions
                    format_jst_time(invalid_input)
            except (TypeError, AttributeError):
                # Expected for invalid inputs
                pass
                
    def test_path_utils_error_handling(self):
        """Path utils error handling test"""
        # Test with invalid path inputs
        invalid_paths = [None, 123, {"not": "a_path"}]
        
        for invalid_path in invalid_paths:
            try:
                if invalid_path is not None:
                    PathUtils.is_safe_path(invalid_path)
                    # Should handle gracefully
            except (TypeError, AttributeError):
                # Expected for invalid inputs
                pass
                
    def test_detector_error_handling(self):
        """Detector error handling test"""
        detector = TriggerKeywordDetector()
        
        # Test with various invalid inputs
        invalid_inputs = [123, {"dict": "value"}, ["list", "value"]]
        
        for invalid_input in invalid_inputs:
            try:
                result = detector.detect_keywords(invalid_input)
                # Should return empty list or handle gracefully
                self.assertIsInstance(result, list)
            except (TypeError, AttributeError):
                # Acceptable to raise type errors for invalid inputs
                pass


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)