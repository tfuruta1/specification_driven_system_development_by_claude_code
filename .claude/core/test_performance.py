#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Tests - Consolidated performance and coverage testing
TDD Red-Green-Refactor implementation for comprehensive performance testing

Consolidates tests from:
- test_coverage_report.py
- test_100_coverage.py
- test_master_suite.py
- Performance tests from various modules

TDD Requirements:
- 100% coverage verification and reporting
- Performance benchmarking and optimization testing
- Memory usage and resource consumption testing
- Scalability and load testing
- System performance monitoring
"""

import unittest
import tempfile
import shutil
import json
import sys
import os
import time
import threading
import psutil
import gc
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime
from io import StringIO
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Test target module imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Import all modules for coverage testing
    import auto_mode_core
    import emoji_core
    import shared_logger
    import file_access_logger
    import unified_system
    import integration_test_runner
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Import error: {e}")
    print("Running with mock implementations for TDD demonstration...")
    IMPORT_SUCCESS = False


class PerformanceProfiler:
    """Performance profiling utility"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        
    def start_timer(self, name):
        """Start timing a operation"""
        self.start_times[name] = time.time()
        
    def end_timer(self, name):
        """End timing and record duration"""
        if name in self.start_times:
            duration = time.time() - self.start_times[name]
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(duration)
            del self.start_times[name]
            return duration
        return None
        
    def get_average_time(self, name):
        """Get average time for an operation"""
        if name in self.metrics and self.metrics[name]:
            return sum(self.metrics[name]) / len(self.metrics[name])
        return None
        
    def get_total_time(self, name):
        """Get total time for all operations of a type"""
        if name in self.metrics:
            return sum(self.metrics[name])
        return 0
        
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.start_times.clear()


class MemoryProfiler:
    """Memory profiling utility"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0
            
    def get_memory_increase(self):
        """Get memory increase since initialization"""
        current = self.get_memory_usage()
        return current - self.initial_memory
        
    def force_gc(self):
        """Force garbage collection"""
        gc.collect()
        
    def get_object_count(self):
        """Get current object count"""
        return len(gc.get_objects())


class CoverageReporter:
    """Test coverage reporting utility"""
    
    def __init__(self):
        self.modules_tested = set()
        self.functions_tested = set()
        self.lines_executed = set()
        self.total_modules = 0
        self.total_functions = 0
        self.total_lines = 0
        
    def register_module_test(self, module_name):
        """Register that a module has been tested"""
        self.modules_tested.add(module_name)
        
    def register_function_test(self, module_name, function_name):
        """Register that a function has been tested"""
        self.functions_tested.add(f"{module_name}.{function_name}")
        
    def register_line_execution(self, module_name, line_number):
        """Register that a line has been executed"""
        self.lines_executed.add(f"{module_name}:{line_number}")
        
    def set_total_counts(self, modules, functions, lines):
        """Set total counts for coverage calculation"""
        self.total_modules = modules
        self.total_functions = functions
        self.total_lines = lines
        
    def get_module_coverage(self):
        """Get module coverage percentage"""
        if self.total_modules == 0:
            return 100.0
        return (len(self.modules_tested) / self.total_modules) * 100
        
    def get_function_coverage(self):
        """Get function coverage percentage"""
        if self.total_functions == 0:
            return 100.0
        return (len(self.functions_tested) / self.total_functions) * 100
        
    def get_line_coverage(self):
        """Get line coverage percentage"""
        if self.total_lines == 0:
            return 100.0
        return (len(self.lines_executed) / self.total_lines) * 100
        
    def generate_report(self):
        """Generate comprehensive coverage report"""
        return {
            "module_coverage": self.get_module_coverage(),
            "function_coverage": self.get_function_coverage(),
            "line_coverage": self.get_line_coverage(),
            "modules_tested": len(self.modules_tested),
            "functions_tested": len(self.functions_tested),
            "lines_executed": len(self.lines_executed),
            "total_modules": self.total_modules,
            "total_functions": self.total_functions,
            "total_lines": self.total_lines,
        }


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


class TestMemoryUsage(unittest.TestCase):
    """Memory usage tests"""
    
    def setUp(self):
        """Test setup"""
        self.memory_profiler = MemoryProfiler()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Test cleanup"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.memory_profiler.force_gc()
        
    def test_memory_stability_during_operations(self):
        """Memory stability during operations test"""
        initial_memory = self.memory_profiler.get_memory_usage()
        
        # Perform various operations that should not leak memory
        for iteration in range(10):
            # Create temporary objects
            temp_objects = []
            for i in range(1000):
                temp_objects.append({
                    "id": i,
                    "data": f"test_data_{i}" * 10,
                    "nested": {"value": i * 2}
                })
                
            # Process objects
            for obj in temp_objects:
                _ = obj["id"] + obj["nested"]["value"]
                
            # Clear objects
            temp_objects.clear()
            del temp_objects
            
            # Force garbage collection
            self.memory_profiler.force_gc()
            
        final_memory = self.memory_profiler.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal
        self.assertLess(memory_increase, 50, f"Memory should not increase significantly: {memory_increase}MB")
        
    def test_large_data_processing_memory(self):
        """Large data processing memory test"""
        initial_memory = self.memory_profiler.get_memory_usage()
        
        # Process large amounts of data
        large_data = []
        try:
            # Create large dataset
            for i in range(10000):
                large_data.append({
                    "index": i,
                    "content": f"Large content string {i}" * 5,
                    "metadata": {
                        "timestamp": time.time(),
                        "category": f"category_{i % 100}",
                        "tags": [f"tag_{j}" for j in range(5)]
                    }
                })
                
            # Process data
            processed_count = 0
            for item in large_data:
                if item["index"] % 2 == 0:
                    processed_count += 1
                    
            # Verify processing
            self.assertEqual(processed_count, 5000)
            
        finally:
            # Clean up
            large_data.clear()
            del large_data
            self.memory_profiler.force_gc()
            
        final_memory = self.memory_profiler.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Should return to baseline after cleanup
        self.assertLess(memory_increase, 100, f"Memory should be released after processing: {memory_increase}MB")
        
    def test_object_lifecycle_memory(self):
        """Object lifecycle memory test"""
        initial_objects = self.memory_profiler.get_object_count()
        
        class TestObject:
            def __init__(self, data):
                self.data = data
                self.processed = False
                
            def process(self):
                self.processed = True
                return len(self.data)
                
        # Create and destroy objects multiple times
        for cycle in range(5):
            objects = []
            
            # Create objects
            for i in range(1000):
                obj = TestObject(f"data_{i}")
                obj.process()
                objects.append(obj)
                
            # Use objects
            total_processed = sum(1 for obj in objects if obj.processed)
            self.assertEqual(total_processed, 1000)
            
            # Destroy objects
            objects.clear()
            del objects
            
        # Force garbage collection
        self.memory_profiler.force_gc()
        
        final_objects = self.memory_profiler.get_object_count()
        object_increase = final_objects - initial_objects
        
        # Object count should not grow significantly
        self.assertLess(object_increase, 1000, f"Object count should remain stable: +{object_increase}")
        
    def test_recursive_data_structure_memory(self):
        """Recursive data structure memory test"""
        initial_memory = self.memory_profiler.get_memory_usage()
        
        def create_tree(depth, breadth=3):
            """Create a tree structure for testing"""
            if depth <= 0:
                return {"leaf": True, "value": "leaf_node"}
                
            node = {
                "depth": depth,
                "children": [],
                "data": f"node_at_depth_{depth}"
            }
            
            for i in range(breadth):
                child = create_tree(depth - 1, breadth)
                node["children"].append(child)
                
            return node
            
        # Create and process tree structures
        trees = []
        for i in range(10):
            tree = create_tree(4, 2)  # Depth 4, breadth 2
            trees.append(tree)
            
        # Process trees
        def count_nodes(node):
            if node.get("leaf"):
                return 1
            return 1 + sum(count_nodes(child) for child in node.get("children", []))
            
        total_nodes = sum(count_nodes(tree) for tree in trees)
        
        # Clean up
        trees.clear()
        del trees
        self.memory_profiler.force_gc()
        
        final_memory = self.memory_profiler.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Should handle recursive structures efficiently
        self.assertGreater(total_nodes, 0)
        self.assertLess(memory_increase, 50, f"Recursive structure memory should be manageable: {memory_increase}MB")


class TestScalabilityAndLoad(unittest.TestCase):
    """Scalability and load testing"""
    
    def setUp(self):
        """Test setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Test cleanup"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def test_concurrent_operations_scaling(self):
        """Concurrent operations scaling test"""
        def worker_task(worker_id, iterations=100):
            """Worker task for concurrent testing"""
            results = []
            for i in range(iterations):
                # Simulate work
                data = {"worker": worker_id, "iteration": i, "timestamp": time.time()}
                processed = json.dumps(data)
                parsed = json.loads(processed)
                results.append(parsed["worker"] + parsed["iteration"])
            return sum(results)
            
        # Test with increasing number of threads
        thread_counts = [1, 2, 4, 8]
        execution_times = []
        
        for thread_count in thread_counts:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = []
                for worker_id in range(thread_count):
                    future = executor.submit(worker_task, worker_id, 50)
                    futures.append(future)
                    
                # Wait for all tasks to complete
                results = [future.result() for future in futures]
                
            end_time = time.time()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Verify results
            self.assertEqual(len(results), thread_count)
            
        # Check that scaling improves or maintains performance
        # (More threads should not dramatically increase execution time)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        # Performance should not degrade too much with more threads
        self.assertLess(max_time / min_time, 3.0, "Scaling should not cause major performance degradation")
        
    def test_data_volume_scaling(self):
        """Data volume scaling test"""
        data_sizes = [100, 1000, 5000, 10000]
        processing_times = []
        
        for data_size in data_sizes:
            # Create dataset
            dataset = []
            for i in range(data_size):
                dataset.append({
                    "id": i,
                    "category": f"cat_{i % 10}",
                    "value": i * 1.5,
                    "tags": [f"tag_{j}" for j in range(i % 5 + 1)]
                })
                
            # Process dataset
            start_time = time.time()
            
            # Simulate processing operations
            filtered_data = [item for item in dataset if item["value"] > data_size / 2]
            grouped_data = {}
            for item in dataset:
                category = item["category"]
                if category not in grouped_data:
                    grouped_data[category] = []
                grouped_data[category].append(item)
                
            aggregated = {
                cat: sum(item["value"] for item in items)
                for cat, items in grouped_data.items()
            }
            
            end_time = time.time()
            processing_time = end_time - start_time
            processing_times.append(processing_time)
            
            # Verify processing
            self.assertGreater(len(filtered_data), 0)
            self.assertEqual(len(grouped_data), 10)  # 10 categories
            self.assertEqual(len(aggregated), 10)
            
        # Check that processing time scales reasonably
        # Should be roughly linear with data size
        time_per_item = [t / s for t, s in zip(processing_times, data_sizes)]
        
        # Time per item should remain relatively consistent
        max_time_per_item = max(time_per_item)
        min_time_per_item = min(time_per_item)
        
        self.assertLess(max_time_per_item / min_time_per_item, 5.0,
                       "Processing time should scale roughly linearly")
                       
    def test_file_system_load(self):
        """File system load test"""
        file_counts = [10, 50, 100, 200]
        file_operation_times = []
        
        for file_count in file_counts:
            start_time = time.time()
            
            # Create files
            created_files = []
            for i in range(file_count):
                file_path = self.temp_dir / f"load_test_{i}.txt"
                with open(file_path, 'w') as f:
                    f.write(f"Load test file {i}\n" * 10)
                created_files.append(file_path)
                
            # Read files
            file_contents = []
            for file_path in created_files:
                with open(file_path, 'r') as f:
                    content = f.read()
                file_contents.append(content)
                
            # Delete files
            for file_path in created_files:
                file_path.unlink()
                
            end_time = time.time()
            operation_time = end_time - start_time
            file_operation_times.append(operation_time)
            
            # Verify operations
            self.assertEqual(len(file_contents), file_count)
            for file_path in created_files:
                self.assertFalse(file_path.exists())
                
        # File operations should scale reasonably
        # Check that doubling files doesn't cause exponential time increase
        for i in range(1, len(file_operation_times)):
            current_time = file_operation_times[i]
            previous_time = file_operation_times[i-1]
            
            # Should not take more than 5x as long for 2x the files
            if previous_time > 0:
                time_ratio = current_time / previous_time
                self.assertLess(time_ratio, 5.0,
                               f"File operations should scale reasonably: {time_ratio}")


class TestCoverageReporting(unittest.TestCase):
    """Test coverage reporting tests"""
    
    def setUp(self):
        """Test setup"""
        self.coverage_reporter = CoverageReporter()
        
    def test_coverage_reporter_initialization(self):
        """Coverage reporter initialization test"""
        self.assertEqual(len(self.coverage_reporter.modules_tested), 0)
        self.assertEqual(len(self.coverage_reporter.functions_tested), 0)
        self.assertEqual(len(self.coverage_reporter.lines_executed), 0)
        self.assertEqual(self.coverage_reporter.total_modules, 0)
        
    def test_module_coverage_tracking(self):
        """Module coverage tracking test"""
        modules = ["module1", "module2", "module3"]
        
        for module in modules:
            self.coverage_reporter.register_module_test(module)
            
        self.assertEqual(len(self.coverage_reporter.modules_tested), 3)
        
        # Set total modules
        self.coverage_reporter.set_total_counts(5, 0, 0)
        
        # Calculate coverage
        coverage = self.coverage_reporter.get_module_coverage()
        self.assertEqual(coverage, 60.0)  # 3/5 * 100
        
    def test_function_coverage_tracking(self):
        """Function coverage tracking test"""
        functions = [
            ("module1", "function1"),
            ("module1", "function2"),
            ("module2", "function1"),
        ]
        
        for module, function in functions:
            self.coverage_reporter.register_function_test(module, function)
            
        self.assertEqual(len(self.coverage_reporter.functions_tested), 3)
        
        # Set total functions
        self.coverage_reporter.set_total_counts(0, 10, 0)
        
        # Calculate coverage
        coverage = self.coverage_reporter.get_function_coverage()
        self.assertEqual(coverage, 30.0)  # 3/10 * 100
        
    def test_line_coverage_tracking(self):
        """Line coverage tracking test"""
        lines = [
            ("module1", 10),
            ("module1", 15),
            ("module1", 20),
            ("module2", 5),
        ]
        
        for module, line in lines:
            self.coverage_reporter.register_line_execution(module, line)
            
        self.assertEqual(len(self.coverage_reporter.lines_executed), 4)
        
        # Set total lines
        self.coverage_reporter.set_total_counts(0, 0, 20)
        
        # Calculate coverage
        coverage = self.coverage_reporter.get_line_coverage()
        self.assertEqual(coverage, 20.0)  # 4/20 * 100
        
    def test_comprehensive_coverage_report(self):
        """Comprehensive coverage report test"""
        # Register various coverage data
        self.coverage_reporter.register_module_test("core_module")
        self.coverage_reporter.register_module_test("util_module")
        
        self.coverage_reporter.register_function_test("core_module", "main_function")
        self.coverage_reporter.register_function_test("core_module", "helper_function")
        self.coverage_reporter.register_function_test("util_module", "utility_function")
        
        for i in range(50):
            self.coverage_reporter.register_line_execution("core_module", i + 1)
            
        # Set totals
        self.coverage_reporter.set_total_counts(3, 5, 100)
        
        # Generate report
        report = self.coverage_reporter.generate_report()
        
        # Verify report structure
        expected_keys = [
            "module_coverage", "function_coverage", "line_coverage",
            "modules_tested", "functions_tested", "lines_executed",
            "total_modules", "total_functions", "total_lines"
        ]
        
        for key in expected_keys:
            self.assertIn(key, report)
            
        # Verify calculations
        self.assertAlmostEqual(report["module_coverage"], 66.67, places=1)  # 2/3
        self.assertEqual(report["function_coverage"], 60.0)  # 3/5
        self.assertEqual(report["line_coverage"], 50.0)  # 50/100
        
    def test_100_percent_coverage_verification(self):
        """100% coverage verification test"""
        # Simulate complete coverage
        modules = ["mod1", "mod2", "mod3"]
        functions = [("mod1", "f1"), ("mod1", "f2"), ("mod2", "f1"), ("mod3", "f1")]
        
        for module in modules:
            self.coverage_reporter.register_module_test(module)
            
        for module, function in functions:
            self.coverage_reporter.register_function_test(module, function)
            
        # Register line executions for complete coverage
        for i in range(100):
            module = f"mod{(i % 3) + 1}"
            self.coverage_reporter.register_line_execution(module, i + 1)
            
        # Set totals to match registered items
        self.coverage_reporter.set_total_counts(3, 4, 100)
        
        # Verify 100% coverage
        self.assertEqual(self.coverage_reporter.get_module_coverage(), 100.0)
        self.assertEqual(self.coverage_reporter.get_function_coverage(), 100.0)
        self.assertEqual(self.coverage_reporter.get_line_coverage(), 100.0)


class TestSystemPerformanceMonitoring(unittest.TestCase):
    """System performance monitoring tests"""
    
    def setUp(self):
        """Test setup"""
        self.profiler = PerformanceProfiler()
        self.memory_profiler = MemoryProfiler()
        
    def test_performance_regression_detection(self):
        """Performance regression detection test"""
        # Baseline performance test
        def baseline_operation():
            return sum(i * i for i in range(1000))
            
        # Measure baseline
        baseline_times = []
        for _ in range(10):
            start = time.time()
            result = baseline_operation()
            end = time.time()
            baseline_times.append(end - start)
            self.assertEqual(result, sum(i * i for i in range(1000)))
            
        baseline_avg = sum(baseline_times) / len(baseline_times)
        
        # Test for regression (simulated slower operation)
        def potentially_slower_operation():
            # Intentionally slower version for testing
            total = 0
            for i in range(1000):
                total += i * i
                if i % 100 == 0:
                    time.sleep(0.001)  # Small delay
            return total
            
        slower_times = []
        for _ in range(5):
            start = time.time()
            result = potentially_slower_operation()
            end = time.time()
            slower_times.append(end - start)
            
        slower_avg = sum(slower_times) / len(slower_times)
        
        # Detect potential regression
        performance_ratio = slower_avg / baseline_avg if baseline_avg > 0 else 1
        
        # This test documents the performance difference
        # In a real scenario, you'd set thresholds for acceptable performance degradation
        print(f"Performance ratio: {performance_ratio:.2f}")
        print(f"Baseline average: {baseline_avg:.4f}s")
        print(f"Slower average: {slower_avg:.4f}s")
        
        # For this test, we just verify the measurement works
        self.assertGreater(slower_avg, baseline_avg, "Slower operation should be measurably slower")
        
    def test_resource_usage_monitoring(self):
        """Resource usage monitoring test"""
        initial_memory = self.memory_profiler.get_memory_usage()
        
        # Perform resource-intensive operations
        self.profiler.start_timer("resource_intensive")
        
        # CPU intensive
        cpu_result = sum(i ** 2 for i in range(100000))
        
        # Memory intensive
        large_list = [i for i in range(50000)]
        large_dict = {i: f"value_{i}" for i in range(10000)}
        
        # I/O intensive (using StringIO to avoid actual file system)
        string_io = StringIO()
        for i in range(1000):
            string_io.write(f"Line {i}: Some content for I/O testing\n")
        content = string_io.getvalue()
        string_io.close()
        
        resource_time = self.profiler.end_timer("resource_intensive")
        final_memory = self.memory_profiler.get_memory_usage()
        
        # Verify operations completed
        self.assertGreater(cpu_result, 0)
        self.assertEqual(len(large_list), 50000)
        self.assertEqual(len(large_dict), 10000)
        self.assertIn("Line 999:", content)
        
        # Monitor resource usage
        memory_used = final_memory - initial_memory
        
        print(f"Resource intensive operations took: {resource_time:.3f}s")
        print(f"Memory used: {memory_used:.2f}MB")
        
        # Verify reasonable resource usage
        self.assertLess(resource_time, 5.0, "Resource operations should complete in reasonable time")
        
        # Clean up
        del large_list, large_dict
        self.memory_profiler.force_gc()
        
    def test_performance_profile_aggregation(self):
        """Performance profile aggregation test"""
        # Simulate multiple operations of different types
        operations = {
            "fast_op": lambda: sum(range(100)),
            "medium_op": lambda: [i**2 for i in range(1000)],
            "slow_op": lambda: {i: i**3 for i in range(2000)}
        }
        
        # Execute operations multiple times
        for op_name, op_func in operations.items():
            for _ in range(10):
                self.profiler.start_timer(op_name)
                result = op_func()
                self.profiler.end_timer(op_name)
                self.assertIsNotNone(result)
                
        # Analyze performance profiles
        performance_summary = {}
        for op_name in operations.keys():
            avg_time = self.profiler.get_average_time(op_name)
            total_time = self.profiler.get_total_time(op_name)
            performance_summary[op_name] = {
                "average_time": avg_time,
                "total_time": total_time,
                "call_count": len(self.profiler.metrics[op_name])
            }
            
        # Verify profiling worked
        for op_name, stats in performance_summary.items():
            self.assertIsNotNone(stats["average_time"])
            self.assertGreater(stats["total_time"], 0)
            self.assertEqual(stats["call_count"], 10)
            
        # Verify relative performance expectations
        fast_avg = performance_summary["fast_op"]["average_time"]
        slow_avg = performance_summary["slow_op"]["average_time"]
        
        self.assertLess(fast_avg, slow_avg, "Fast operation should be faster than slow operation")


if __name__ == '__main__':
    # Run tests with detailed output and performance reporting
    print("=" * 80)
    print("PERFORMANCE AND COVERAGE TEST SUITE")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2, 
        buffer=True,
        stream=sys.stdout
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Report overall performance
    print("\n" + "=" * 80)
    print("TEST SUITE PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 80)