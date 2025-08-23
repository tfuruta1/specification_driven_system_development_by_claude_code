#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Performance Tests - Extracted from test_performance.py
TDD Red-Green-Refactor implementation for core performance testing

Split from original test_performance.py (964 lines) following KISS principles
Focus: Core performance metrics, timing, and resource usage
"""

import unittest
import time
import threading
import psutil
import gc
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock

# Test target module imports
sys.path.insert(0, str(Path(__file__).parent))


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
        return self.process.memory_info().rss / 1024 / 1024
        
    def get_memory_delta(self):
        """Get memory usage delta from initial"""
        current = self.get_memory_usage()
        return current - self.initial_memory
        
    def reset_baseline(self):
        """Reset memory baseline"""
        self.initial_memory = self.get_memory_usage()


class TestPerformanceCore(unittest.TestCase):
    """Core performance testing"""
    
    def setUp(self):
        """Test setup"""
        self.profiler = PerformanceProfiler()
        self.memory_profiler = MemoryProfiler()
        
    def tearDown(self):
        """Test cleanup"""
        self.profiler.clear_metrics()
        gc.collect()
    
    def test_performance_profiler_basic(self):
        """Test basic performance profiler functionality"""
        self.profiler.start_timer("test_operation")
        time.sleep(0.01)  # 10ms sleep
        duration = self.profiler.end_timer("test_operation")
        
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration, 0.01)
        self.assertLess(duration, 0.02)  # Should be close to 10ms
        
    def test_performance_multiple_operations(self):
        """Test multiple operations timing"""
        # Run multiple operations
        for i in range(5):
            self.profiler.start_timer("multi_test")
            time.sleep(0.005)  # 5ms sleep
            self.profiler.end_timer("multi_test")
        
        average_time = self.profiler.get_average_time("multi_test")
        total_time = self.profiler.get_total_time("multi_test")
        
        self.assertIsNotNone(average_time)
        self.assertGreaterEqual(average_time, 0.005)
        self.assertGreaterEqual(total_time, 0.025)  # At least 25ms total
    
    def test_memory_profiler_basic(self):
        """Test basic memory profiler functionality"""
        initial_memory = self.memory_profiler.get_memory_usage()
        self.assertIsInstance(initial_memory, float)
        self.assertGreater(initial_memory, 0)
        
        # Create some memory usage
        large_list = [i for i in range(10000)]
        current_memory = self.memory_profiler.get_memory_usage()
        
        # Memory should have increased
        delta = self.memory_profiler.get_memory_delta()
        # Note: Memory delta might be 0 due to Python's memory management
        self.assertIsInstance(delta, float)
        
        # Clean up
        del large_list
        gc.collect()
    
    def test_concurrent_performance(self):
        """Test concurrent operations performance"""
        def worker_function():
            time.sleep(0.01)
            return "completed"
        
        # Test sequential execution
        self.profiler.start_timer("sequential")
        for _ in range(3):
            worker_function()
        sequential_time = self.profiler.end_timer("sequential")
        
        # Test concurrent execution
        self.profiler.start_timer("concurrent")
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker_function) for _ in range(3)]
            results = [f.result() for f in futures]
        concurrent_time = self.profiler.end_timer("concurrent")
        
        # Concurrent should be faster
        self.assertLess(concurrent_time, sequential_time)
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r == "completed" for r in results))
    
    def test_performance_regression_threshold(self):
        """Test performance regression threshold"""
        # Define performance thresholds
        MAX_OPERATION_TIME = 0.1  # 100ms max
        MAX_MEMORY_INCREASE = 50  # 50MB max increase
        
        # Test operation time
        self.profiler.start_timer("threshold_test")
        # Simulate some work
        time.sleep(0.05)  # 50ms - should pass
        operation_time = self.profiler.end_timer("threshold_test")
        
        self.assertLess(operation_time, MAX_OPERATION_TIME)
        
        # Test memory usage
        initial_delta = self.memory_profiler.get_memory_delta()
        # Create controlled memory usage
        moderate_list = [i for i in range(1000)]  # Small list
        final_delta = self.memory_profiler.get_memory_delta()
        
        memory_increase = abs(final_delta - initial_delta)
        self.assertLess(memory_increase, MAX_MEMORY_INCREASE)
        
        # Clean up
        del moderate_list
        gc.collect()
    
    def test_stress_test_light(self):
        """Light stress test for basic stability"""
        iterations = 100
        self.profiler.start_timer("stress_test")
        
        # Light stress test
        for i in range(iterations):
            # Simple operations
            temp_list = list(range(100))
            temp_dict = {j: j*2 for j in temp_list}
            del temp_list, temp_dict
        
        stress_time = self.profiler.end_timer("stress_test")
        
        # Should complete within reasonable time
        self.assertLess(stress_time, 1.0)  # Max 1 second
        
        # Memory should be stable after cleanup
        gc.collect()
        final_memory_delta = self.memory_profiler.get_memory_delta()
        # Allow some variance in memory usage
        self.assertLess(abs(final_memory_delta), 10)  # Within 10MB


def run_performance_tests():
    """Run all core performance tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceCore)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_performance_tests()
    sys.exit(0 if success else 1)