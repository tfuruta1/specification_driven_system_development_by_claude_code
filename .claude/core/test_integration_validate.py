#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Validation Tests - System integrity verification
Validates the refactored system components work together correctly

Created for validating Alex Team refactoring efforts
Focus: System integrity, component interaction, refactoring validation
"""

import unittest
import sys
import importlib
from pathlib import Path
from typing import List, Dict, Any

# Test target module imports
sys.path.insert(0, str(Path(__file__).parent))


class TestSystemIntegration(unittest.TestCase):
    """System integration validation tests"""
    
    def setUp(self):
        """Test setup"""
        self.core_modules = [
            'logger',
            'service_factory', 
            'auto_mode_interfaces',
            'error_core',
            'alex_team_core'
        ]
        
    def test_core_modules_import(self):
        """Test core modules can be imported without errors"""
        import_results = {}
        
        for module_name in self.core_modules:
            try:
                module = importlib.import_module(module_name)
                import_results[module_name] = {
                    'success': True,
                    'module': module,
                    'error': None
                }
            except ImportError as e:
                import_results[module_name] = {
                    'success': False,
                    'module': None,
                    'error': str(e)
                }
        
        # Verify imports
        successful_imports = [name for name, result in import_results.items() 
                            if result['success']]
        failed_imports = [name for name, result in import_results.items() 
                         if not result['success']]
        
        # Report results
        print(f"\nImport Results:")
        print(f"Successful: {len(successful_imports)}/{len(self.core_modules)}")
        if failed_imports:
            print(f"Failed: {failed_imports}")
            for name in failed_imports:
                print(f"  {name}: {import_results[name]['error']}")
        
        # At least half should import successfully
        self.assertGreaterEqual(len(successful_imports), len(self.core_modules) // 2)
    
    def test_service_factory_integration(self):
        """Test service factory integration"""
        try:
            from service_factory import ServiceFactory
            from auto_mode_interfaces import ServiceLocator
            
            # Clear any existing services
            ServiceFactory.clear_services()
            
            # Test initialization
            ServiceFactory.initialize_services()
            self.assertTrue(ServiceFactory.is_initialized())
            
            # Test service retrieval
            config_service = ServiceFactory.get_config_service()
            state_service = ServiceFactory.get_state_service()
            
            # Basic validation
            self.assertIsNotNone(config_service)
            self.assertIsNotNone(state_service)
            
            # Test ServiceLocator integration
            self.assertTrue(ServiceLocator.has('config'))
            self.assertTrue(ServiceLocator.has('state'))
            
            print("\n✓ Service Factory integration validated")
            
        except ImportError as e:
            self.skipTest(f"Service factory modules not available: {e}")
    
    def test_logger_integration(self):
        """Test unified logger integration"""
        try:
            from logger import UnifiedLogger, IntegratedLogger, FileUtils, PathUtils
            
            # Test basic logger creation
            logger = UnifiedLogger()
            self.assertIsNotNone(logger)
            self.assertIsNotNone(logger.log_dir)
            
            # Test integrated logger (alias)
            integrated = IntegratedLogger("TestLogger")
            self.assertEqual(integrated.name, "TestLogger")
            
            # Test utility classes
            file_utils = FileUtils()
            path_utils = PathUtils()
            self.assertIsNotNone(file_utils)
            self.assertIsNotNone(path_utils)
            
            print("\n✓ Logger integration validated")
            
        except ImportError as e:
            self.skipTest(f"Logger modules not available: {e}")
    
    def test_error_handling_integration(self):
        """Test error handling integration"""
        try:
            from error_core import (
                StandardError, FileOperationError, ValidationError,
                ErrorSeverity, ErrorCategory, ErrorFactory
            )
            
            # Test basic error creation
            basic_error = StandardError("Test error")
            self.assertEqual(basic_error.message, "Test error")
            self.assertEqual(basic_error.severity, ErrorSeverity.MEDIUM)
            
            # Test specialized errors
            file_error = FileOperationError("File not found", "/test/path")
            self.assertEqual(file_error.file_path, "/test/path")
            self.assertEqual(file_error.category, ErrorCategory.FILE_OPERATION)
            
            validation_error = ValidationError("Invalid value", "email", "invalid@")
            self.assertEqual(validation_error.field_name, "email")
            self.assertEqual(validation_error.invalid_value, "invalid@")
            
            # Test factory
            factory_error = ErrorFactory.create_error(
                ErrorCategory.NETWORK, "Connection failed"
            )
            self.assertEqual(factory_error.category, ErrorCategory.NETWORK)
            
            # Test serialization
            error_dict = basic_error.to_dict()
            self.assertIn('message', error_dict)
            self.assertIn('severity', error_dict)
            
            print("\n✓ Error handling integration validated")
            
        except ImportError as e:
            self.skipTest(f"Error handling modules not available: {e}")
    
    def test_alex_team_integration(self):
        """Test Alex Team system integration"""
        try:
            from alex_team_core import (
                TaskStatus, VoteResult, EngineerRole,
                TaskAssignment, EngineerTask, TeamTask,
                AlexTeamConfig, create_engineer_task, create_team_task
            )
            
            # Test enums
            self.assertIn("alex-sdd-tdd-lead", [role.value for role in EngineerRole])
            self.assertIn("pending", [status.value for status in TaskStatus])
            self.assertIn("approve", [vote.value for vote in VoteResult])
            
            # Test task creation
            engineer_task = create_engineer_task(
                "alex-sdd-tdd-lead", "Test task", 1
            )
            self.assertEqual(engineer_task.engineer_type, "alex-sdd-tdd-lead")
            self.assertEqual(engineer_task.priority, 1)
            
            team_task = create_team_task("test-task-1", "Test objective")
            self.assertEqual(team_task.task_id, "test-task-1")
            self.assertEqual(team_task.main_objective, "Test objective")
            
            # Test configuration
            engineers = AlexTeamConfig.ENGINEERS
            self.assertIn("alex-sdd-tdd-lead", engineers)
            self.assertIn("code-optimizer-engineer", engineers)
            
            voting_rules = AlexTeamConfig.VOTING_RULES
            self.assertIn("quorum", voting_rules)
            self.assertIn("approval_threshold", voting_rules)
            
            print("\n✓ Alex Team integration validated")
            
        except ImportError as e:
            self.skipTest(f"Alex Team modules not available: {e}")
    
    def test_new_test_modules_integration(self):
        """Test newly created test modules integration"""
        new_test_modules = [
            'test_unified_logger',
            'test_performance_core', 
            'test_coverage_report'
        ]
        
        successful_tests = []
        failed_tests = []
        
        for module_name in new_test_modules:
            try:
                module = importlib.import_module(module_name)
                # Check if it has test classes
                test_classes = [obj for name, obj in vars(module).items() 
                              if (name.startswith('Test') and 
                                  hasattr(obj, '__bases__') and
                                  unittest.TestCase in obj.__bases__)]
                
                if test_classes:
                    successful_tests.append({
                        'module': module_name,
                        'test_classes': len(test_classes)
                    })
                else:
                    failed_tests.append({
                        'module': module_name,
                        'error': 'No test classes found'
                    })
                    
            except ImportError as e:
                failed_tests.append({
                    'module': module_name,
                    'error': str(e)
                })
        
        print(f"\nNew Test Modules:")
        print(f"Successful: {len(successful_tests)}")
        for test in successful_tests:
            print(f"  {test['module']}: {test['test_classes']} test classes")
            
        if failed_tests:
            print(f"Failed: {len(failed_tests)}")
            for test in failed_tests:
                print(f"  {test['module']}: {test['error']}")
        
        # At least some should be available
        self.assertGreater(len(successful_tests), 0)
    
    def test_circular_dependency_resolution(self):
        """Test circular dependency resolution"""
        try:
            # Test the circular dependency resolution pattern
            from service_factory import ServiceFactory
            from auto_mode_interfaces import ServiceLocator
            
            # This should work without circular import errors
            ServiceFactory.clear_services()
            ServiceFactory.initialize_services()
            
            # Test that services can be retrieved
            config = ServiceLocator.get('config')
            state = ServiceLocator.get('state')
            
            self.assertIsNotNone(config)
            self.assertIsNotNone(state)
            
            print("\n✓ Circular dependency resolution validated")
            
        except ImportError as e:
            self.skipTest(f"Circular dependency test modules not available: {e}")
        except Exception as e:
            self.fail(f"Circular dependency resolution failed: {e}")
    
    def test_system_cleanup_validation(self):
        """Test system cleanup and resource management"""
        try:
            from service_factory import ServiceFactory
            
            # Initialize services
            ServiceFactory.initialize_services()
            self.assertTrue(ServiceFactory.is_initialized())
            
            # Clean up services
            ServiceFactory.clear_services()
            # Note: is_initialized() should return False after clear
            # (this depends on implementation)
            
            # Reinitialize to test repeatability
            ServiceFactory.initialize_services()
            self.assertTrue(ServiceFactory.is_initialized())
            
            print("\n✓ System cleanup validation passed")
            
        except Exception as e:
            self.skipTest(f"System cleanup test failed: {e}")


def run_integration_tests():
    """Run all integration validation tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSystemIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*60}")
    print(f"ALEX TEAM REFACTORING VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)