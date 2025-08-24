import copy
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced ServiceLocator Pattern TDD Tests
TESTServiceLocatorTESTTDDTEST

ServiceLocatorTEST
TEST

TEST: Claude Code TDD Specialist
TEST: 2025-08-23
"""

import unittest
import threading
import time
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# TEST
sys.path.insert(0, str(Path(__file__).parent))


class TestServiceLocatorCore(unittest.TestCase):
    """
    ServiceLocatorTEST
    
    TDD Phase: RED-GREEN-REFACTOR
    """
    
    def setUp(self):
        """CONFIG"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_service_registration(self):
        """
        TEST
        
        RED: TEST
        GREEN: 
        REFACTOR: 
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # RED: TEST
        self.assertFalse(ServiceLocator.has('test_service'))
        
        # GREEN: TEST
        test_service = Mock(name='test_service')
        ServiceLocator.register('test_service', test_service)
        self.assertTrue(ServiceLocator.has('test_service'))
        
        # REFACTOR: TEST
        retrieved = ServiceLocator.get('test_service')
        self.assertIs(retrieved, test_service)
        
    def test_service_registration_overwrite(self):
        """
        TEST
        
        GREEN: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # TEST
        service1 = Mock(name='service1')
        ServiceLocator.register('overwrite_test', service1)
        
        # TEST
        service2 = Mock(name='service2')
        ServiceLocator.register('overwrite_test', service2)
        
        # TEST
        retrieved = ServiceLocator.get('overwrite_test')
        self.assertIs(retrieved, service2)
        self.assertIsNot(retrieved, service1)
        
    def test_multiple_service_registration(self):
        """
        TEST
        
        GREEN: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        
        services = {}
        for i in range(10):
            service_name = f'service_{i}'
            service_instance = Mock(name=service_name)
            service_instance.id = i
            
            services[service_name] = service_instance
            ServiceLocator.register(service_name, service_instance)
        
        # 
        for service_name, original_service in services.items():
            self.assertTrue(ServiceLocator.has(service_name))
            retrieved = ServiceLocator.get(service_name)
            self.assertIs(retrieved, original_service)
            self.assertEqual(retrieved.id, original_service.id)
            
    def tearDown(self):
        """"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


class TestServiceLocatorLazyInitialization(unittest.TestCase):
    """
    ServiceLocatorTEST
    
    TDD Phase: GREEN - TEST
    REFACTOR - TEST
    """
    
    def setUp(self):
        """CONFIG"""
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        ServiceLocator.clear()
        ServiceFactory.clear_services()
        
    def test_lazy_initialization_triggers_service_factory(self):
        """
        TESTServiceFactoryTEST
        
        GREEN: 
        """
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        
        # 
        self.assertFalse(ServiceFactory.is_initialized())
        self.assertFalse(ServiceLocator.has('config'))
        
        # CONFIG
        config_service = ServiceLocator.get('config')
        
        # CONFIG
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertIsNotNone(config_service)
        
    def test_lazy_initialization_multiple_calls(self):
        """
        TEST
        
        GREEN: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        
        # CONFIG
        config1 = ServiceLocator.get('config')
        config2 = ServiceLocator.get('config')
        config3 = ServiceLocator.get('config')
        
        self.assertIs(config1, config2)
        self.assertIs(config2, config3)
        
        # ServiceFactoryTEST
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_lazy_initialization_error_handling(self):
        """
        ERROR
        
        RED: ERROR
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # ERROR
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get('nonexistent_service')
        
        error_message = str(context.exception)
        self.assertIn('not registered', error_message)
        self.assertIn('nonexistent_service', error_message)
        
    @patch('auto_mode_core.service_factory.ServiceFactory.initialize_services')
    def test_lazy_initialization_service_factory_failure(self, mock_initialize):
        """
        ServiceFactoryERROR
        
        RED: ERROR
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # ServiceFactory.initialize_services()ERROR
        mock_initialize.side_effect = RuntimeError("Initialization failed")
        
        # ERROR
        with self.assertRaises(RuntimeError):
            ServiceLocator.get('config')
            
    def tearDown(self):
        """ERROR"""
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        ServiceLocator.clear()
        ServiceFactory.clear_services()


class TestServiceLocatorThreadSafety(unittest.TestCase):
    """
    ServiceLocatorTEST
    
    TDD Phase: REFACTOR - TEST
    """
    
    def setUp(self):
        """CONFIG"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_concurrent_service_registration(self):
        """
        TEST
        
        REFACTOR: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        
        results = []
        exceptions = []
        
        def register_service(service_id):
            try:
                service_name = f'concurrent_service_{service_id}'
                service_instance = Mock(name=service_name)
                service_instance.id = service_id
                
                ServiceLocator.register(service_name, service_instance)
                
                # REPORT
                retrieved = ServiceLocator.get(service_name)
                results.append({
                    'service_id': service_id,
                    'service_name': service_name,
                    'registered_correctly': retrieved is service_instance
                })
                
            except Exception as e:
                exceptions.append({
                    'service_id': service_id,
                    'exception': e
                })
        
        # 20ERROR
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(register_service, i) for i in range(20)]
            concurrent.futures.wait(futures)
        
        # ERROR
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 20)
        
        for result in results:
            self.assertTrue(result['registered_correctly'],
                          f"Service {result['service_name']} not registered correctly")
            
    def test_concurrent_service_retrieval(self):
        """
        TEST
        
        REFACTOR: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # TEST
        test_service = Mock(name='shared_service')
        test_service.access_count = 0
        test_service.access_lock = threading.Lock()
        
        def increment_access():
            with test_service.access_lock:
                test_service.access_count += 1
        
        test_service.increment = increment_access
        ServiceLocator.register('shared_service', test_service)
        
        results = []
        exceptions = []
        
        def access_service(thread_id):
            try:
                retrieved = ServiceLocator.get('shared_service')
                retrieved.increment()
                results.append({
                    'thread_id': thread_id,
                    'service_retrieved': retrieved is test_service
                })
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': e
                })
        
        # 15ERROR
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(access_service, i) for i in range(15)]
            concurrent.futures.wait(futures)
        
        # ERROR
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 15)
        self.assertEqual(test_service.access_count, 15)
        
        for result in results:
            self.assertTrue(result['service_retrieved'],
                          f"Thread {result['thread_id']} did not retrieve correct service")
            
    def test_concurrent_clear_operations(self):
        """
        TEST
        
        REFACTOR: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 
        for i in range(10):
            service = Mock(name=f'service_{i}')
            ServiceLocator.register(f'service_{i}', service)
        
        results = []
        exceptions = []
        
        def clear_and_register(thread_id):
            try:
                ServiceLocator.clear()
                
                # 
                new_service = Mock(name=f'new_service_{thread_id}')
                ServiceLocator.register(f'new_service_{thread_id}', new_service)
                
                results.append(thread_id)
                
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': e
                })
        
        # 5ERROR
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear_and_register, i) for i in range(5)]
            concurrent.futures.wait(futures)
        
        # ERROR
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 5)
        
    def tearDown(self):
        """ERROR"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


class TestServiceLocatorPerformance(unittest.TestCase):
    """
    ServiceLocatorTEST
    
    TDD Phase: REFACTOR - TEST
    """
    
    def setUp(self):
        """CONFIG"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_service_registration_performance(self):
        """
        TEST
        
        REFACTOR: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        import time
        
        # 
        start_time = time.time()
        
        for i in range(1000):
            service = Mock(name=f'perf_service_{i}')
            ServiceLocator.register(f'perf_service_{i}', service)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 10001
        self.assertLess(duration, 1.0,
                       f"Service registration too slow: {duration:.2f}s for 1000 services")
        
        # 
        registered_count = len(ServiceLocator._services)
        self.assertEqual(registered_count, 1000)
        
    def test_service_retrieval_performance(self):
        """
        TEST
        
        REFACTOR: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        import time
        
        # 
        services = {}
        for i in range(100):
            service_name = f'fast_service_{i}'
            service = Mock(name=service_name)
            services[service_name] = service
            ServiceLocator.register(service_name, service)
        
        # 
        start_time = time.time()
        
        for _ in range(10000):  # 10,000
            for service_name in services.keys():
                ServiceLocator.get(service_name)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1,000,0002
        total_retrievals = 10000 * 100
        self.assertLess(duration, 2.0,
                       f"Service retrieval too slow: {duration:.2f}s for {total_retrievals:,} retrievals")
        
        # 
        avg_time_per_retrieval = duration / total_retrievals
        self.assertLess(avg_time_per_retrieval, 0.00001,
                       f"Average retrieval time too slow: {avg_time_per_retrieval:.6f}s per retrieval")
        
    def test_memory_usage_optimization(self):
        """
        TEST
        
        REFACTOR: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        import gc
        import sys
        
        # 
        gc.collect()
        baseline_objects = len(gc.get_objects())
        
        # 
        for cycle in range(5):
            for i in range(200):
                service = Mock(name=f'memory_service_{cycle}_{i}')
                ServiceLocator.register(f'memory_service_{cycle}_{i}', service)
            
            ServiceLocator.clear()
            gc.collect()
        
        # 
        final_objects = len(gc.get_objects())
        memory_growth = final_objects - baseline_objects
        
        # 
        self.assertLess(memory_growth, 50,
                       f"Memory leak detected: {memory_growth} objects leaked")
        
    def tearDown(self):
        """"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


class TestServiceLocatorErrorHandling(unittest.TestCase):
    """
    ServiceLocatorERROR
    
    TDD Phase: RED-GREEN - ERROR
    """
    
    def setUp(self):
        """CONFIG"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_get_nonexistent_service_error(self):
        """
        ERROR
        
        RED: ERROR
        """
        from .auto_mode_interfaces import ServiceLocator
        
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get('nonexistent_service')
        
        error_message = str(context.exception)
        self.assertIn("Service 'nonexistent_service' not registered", error_message)
        
    def test_register_none_service_handling(self):
        """
        NoneERROR
        
        GREEN: None
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # None
        ServiceLocator.register('none_service', None)
        self.assertTrue(ServiceLocator.has('none_service'))
        
        retrieved = ServiceLocator.get('none_service')
        self.assertIsNone(retrieved)
        
    def test_register_empty_string_service_name(self):
        """
        TEST
        
        GREEN: TEST
        """
        from .auto_mode_interfaces import ServiceLocator
        
        test_service = Mock(name='empty_name_service')
        
        # TEST
        ServiceLocator.register('', test_service)
        self.assertTrue(ServiceLocator.has(''))
        
        retrieved = ServiceLocator.get('')
        self.assertIs(retrieved, test_service)
        
    def test_service_locator_state_after_error(self):
        """
        ERRORServiceLocatorERROR
        
        GREEN: ERROR
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 
        normal_service = Mock(name='normal_service')
        ServiceLocator.register('normal', normal_service)
        
        # ERROR
        try:
            ServiceLocator.get('nonexistent')
        except ValueError:
            pass
        
        # SUCCESS
        retrieved = ServiceLocator.get('normal')
        self.assertIs(retrieved, normal_service)
        
    def tearDown(self):
        """"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


def run_advanced_service_locator_tests():
    """
    TESTServiceLocatorTEST
    
    Returns:
        TEST
    """
    # TEST
    suite = unittest.TestSuite()
    
    # TEST
    test_classes = [
        TestServiceLocatorCore,
        TestServiceLocatorLazyInitialization,
        TestServiceLocatorThreadSafety,
        TestServiceLocatorPerformance,
        TestServiceLocatorErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # TEST
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # ERROR
    report = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0,
        'performance_tests': 2,
        'thread_safety_tests': 3,
        'error_handling_tests': 4
    }
    
    return report


if __name__ == '__main__':
    print("=== Advanced ServiceLocator Pattern TDD Tests ===")
    print("Testing ServiceLocator pattern implementation completeness...")
    print("Focus: Lazy initialization, thread safety, error handling, performance")
    
    # ERROR
    report = run_advanced_service_locator_tests()
    
    print(f"\n=== Advanced ServiceLocator Test Report ===")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Performance Tests: {report['performance_tests']}")
    print(f"Thread Safety Tests: {report['thread_safety_tests']}")
    print(f"Error Handling Tests: {report['error_handling_tests']}")
    
    if report['success_rate'] == 100.0:
        print("\n[OK] All advanced ServiceLocator tests passed!")
        print("ServiceLocator pattern is fully implemented and optimized.")
    else:
        print(f"\n[WARNING]  Some advanced tests failed. Review the output above for details.")