#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Benchmarks Test Module
Extracted from test_performance.py for better modularity

Performance benchmarking tests for various system components.
"""

import unittest
import tempfile
import shutil
import time
from pathlib import Path

# Import the extracted profiler classes
from .performance_profiler import PerformanceProfiler
from .memory_profiler import MemoryProfiler


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarking tests"""
    
    def setUp(self):
        """Test setup"""
        self.profiler = PerformanceProfiler()
        self.memory_profiler = MemoryProfiler()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Test cleanup"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def test_module_import_performance(self):
        """Module import performance test"""
        modules_to_test = [
            'json', 'os', 'sys', 'pathlib', 'unittest',
            'tempfile', 'shutil', 'time', 'datetime'
        ]
        
        import_times = []
        
        for module_name in modules_to_test:
            start_time = time.time()
            try:
                __import__(module_name)
            except ImportError:
                pass
            end_time = time.time()
            import_times.append(end_time - start_time)
            
        # All imports should complete quickly
        max_import_time = max(import_times) if import_times else 0
        avg_import_time = sum(import_times) / len(import_times) if import_times else 0
        
        self.assertLess(max_import_time, 0.1, "No single import should take > 0.1s")
        self.assertLess(avg_import_time, 0.01, "Average import time should be < 0.01s")
        
    def test_object_creation_performance(self):
        """Object creation performance test"""
        self.profiler.start_timer("object_creation")
        
        # Test various object creations
        objects = []
        for i in range(1000):
            objects.extend([
                {"key": f"value_{i}"},
                [i, i+1, i+2],
                f"string_{i}",
                (i, i+1),
                {i, i+1, i+2}
            ])
            
        creation_time = self.profiler.end_timer("object_creation")
        
        # Should create 5000 objects quickly
        self.assertLess(creation_time, 1.0, "Object creation should be fast")
        self.assertEqual(len(objects), 5000)
        
    def test_file_operations_performance(self):
        """File operations performance test"""
        self.profiler.start_timer("file_operations")
        
        # Create, write, read, and delete files
        for i in range(100):
            test_file = self.temp_dir / f"perf_test_{i}.txt"
            
            # Write file
            with open(test_file, 'w') as f:
                f.write(f"Performance test content {i}\n" * 10)
                
            # Read file
            with open(test_file, 'r') as f:
                content = f.read()
                
            # Verify content
            self.assertIn(f"Performance test content {i}", content)
            
            # Delete file
            test_file.unlink()
            
        file_ops_time = self.profiler.end_timer("file_operations")
        
        # Should complete file operations quickly
        self.assertLess(file_ops_time, 5.0, "100 file operations should complete in < 5s")
        
    def test_string_processing_performance(self):
        """String processing performance test"""
        large_text = "This is a test string for performance testing. " * 1000
        
        self.profiler.start_timer("string_processing")
        
        # Various string operations
        results = []
        for _ in range(100):
            # String manipulations
            upper_text = large_text.upper()
            lower_text = large_text.lower()
            split_text = large_text.split()
            joined_text = " ".join(split_text[:100])
            replaced_text = large_text.replace("test", "performance")
            
            results.extend([upper_text, lower_text, joined_text, replaced_text])
            
        processing_time = self.profiler.end_timer("string_processing")
        
        # String processing should be efficient
        self.assertLess(processing_time, 2.0, "String processing should complete in < 2s")
        self.assertEqual(len(results), 400)
        
    def test_data_structure_performance(self):
        """Data structure performance test"""
        # Test list operations
        self.profiler.start_timer("list_operations")
        
        test_list = []
        for i in range(10000):
            test_list.append(i)
            
        for i in range(1000):
            _ = test_list[i]
            
        for i in range(1000):
            test_list.remove(i)
            
        list_time = self.profiler.end_timer("list_operations")
        
        # Test dictionary operations
        self.profiler.start_timer("dict_operations")
        
        test_dict = {}
        for i in range(10000):
            test_dict[f"key_{i}"] = f"value_{i}"
            
        for i in range(1000):
            _ = test_dict[f"key_{i}"]
            
        for i in range(1000):
            del test_dict[f"key_{i}"]
            
        dict_time = self.profiler.end_timer("dict_operations")
        
        # Data structure operations should be fast
        self.assertLess(list_time, 1.0, "List operations should be fast")
        self.assertLess(dict_time, 1.0, "Dictionary operations should be fast")


if __name__ == '__main__':
    unittest.main()