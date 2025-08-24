import copy
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test: Circular Dependency Resolution
TESTTDDTEST

RED-GREEN-REFACTOR TEST
TEST
"""

import unittest
import sys
import os
from pathlib import Path

# TEST
sys.path.insert(0, str(Path(__file__).parent))

class TestCircularDependencyResolution(unittest.TestCase):
    """TEST"""
    
    def setUp(self):
        """TEST"""
        # ServiceFactoryCONFIG
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
    
    def test_service_factory_initialization(self):
        """
        TEST 1: ServiceFactoryTEST
        - TEST
        - TEST
        """
        from .service_factory import ServiceFactory, get_config_service, get_state_service
        
        # RED: CONFIG
        self.assertFalse(ServiceFactory.is_initialized())
        
        # GREEN: 
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        config = get_config_service()
        state = get_state_service()
        
        # REFACTOR: CONFIG
        from .auto_mode_interfaces import ConfigInterface, StateInterface
        self.assertIsInstance(config, ConfigInterface)
        self.assertIsInstance(state, StateInterface)
    
    def test_no_singleton_instances_in_modules(self):
        """
        TEST 2: TEST
        - auto_config, auto_stateTEST
        """
        # config ERROR
        try:
            from .auto_mode_config import auto_config
            self.fail("auto_config singleton should not exist")
        except ImportError:
            pass  # SUCCESS
        
        # state SUCCESS
        try:
            from .auto_mode_state import auto_state
            self.fail("auto_state singleton should not exist")
        except ImportError:
            pass  # SUCCESS
    
    def test_delayed_import_functions_removed(self):
        """
        TEST 3: TEST
        - _get_auto_config, _get_auto_stateTEST
        """
        from . import auto_mode_core
        
        # CONFIG
        self.assertFalse(hasattr(auto_mode_core, '_get_auto_config'))
        self.assertFalse(hasattr(auto_mode_core, '_get_auto_state'))
    
    def test_service_locator_pattern_working(self):
        """
        TEST 4: ServiceLocatorTEST
        - ServiceLocatorTEST
        - TEST
        """
        from .service_factory import initialize_services, get_config_service, get_state_service
        
        # CONFIG
        initialize_services()
        
        # CONFIG
        config1 = get_config_service()
        config2 = get_config_service()
        self.assertIs(config1, config2)
        
        state1 = get_state_service()
        state2 = get_state_service()
        self.assertIs(state1, state2)
    
    def test_auto_mode_creation_without_circular_dependency(self):
        """
        TEST 5: AutoModeTEST
        - create_auto_mode()TEST
        """
        from .service_factory import initialize_services
        from .auto_mode_core import create_auto_mode
        
        # SYSTEM
        initialize_services()
        
        # AutoMode
        auto_mode = create_auto_mode()
        self.assertIsNotNone(auto_mode)
        self.assertTrue(hasattr(auto_mode, 'config'))
        self.assertTrue(hasattr(auto_mode, 'state'))
    
    def test_complete_workflow_without_circular_imports(self):
        """
        TEST 6: SUCCESS
        - SUCCESS
        """
        from .service_factory import initialize_services, get_config_service, get_state_service
        from .auto_mode_core import create_auto_mode
        
        # CONFIG
        initialize_services()
        config = get_config_service()
        state = get_state_service()
        auto_mode = create_auto_mode()
        
        # CONFIG
        self.assertFalse(config.is_enabled)
        self.assertFalse(state.is_active)
        
        # CONFIG
        status = auto_mode.execute_command("status")
        self.assertIsInstance(status, dict)
        self.assertIn('active', status)
    
    def test_interfaces_not_importing_concrete_classes(self):
        """
        TEST 7: TEST
        - auto_mode_interfaces.pyTEST
        """
        import inspect
        from . import auto_mode_interfaces
        
        # 
        source = inspect.getsource(auto_mode_interfaces)
        
        # CONFIG
        self.assertNotIn('from .auto_mode_config import AutoModeConfig', source)
        self.assertNotIn('from .auto_mode_state import AutoModeState', source)
        self.assertNotIn('create_default_services', source)
    
    def test_kiss_principle_compliance(self):
        """
        TEST 8: KISSTEST
        - TEST
        - TEST
        """
        from .service_factory import initialize_services
        
        # 
        initialize_services()  # 
        
        # ServiceLocator
        from .auto_mode_interfaces import ServiceLocator
        services = ServiceLocator._services
        self.assertIn('config', services)
        self.assertIn('state', services)
        self.assertEqual(len(services), 2)  # TEST


class TestCircularImportDetection(unittest.TestCase):
    """TEST"""
    
    def test_no_circular_imports_detected(self):
        """
        TEST 9: TEST
        - TEST
        """
        from .circular_import_detector import CircularImportDetector
        
        detector = CircularImportDetector()
        current_dir = Path(__file__).parent
        circular_imports = detector.detect(str(current_dir))
        
        # auto_mode
        auto_mode_circulars = [
            circular for circular in circular_imports
            if 'auto_mode' in circular
        ]
        
        self.assertEqual(len(auto_mode_circulars), 0,
                        f"Circular imports detected: {auto_mode_circulars}")


if __name__ == '__main__':
    # TDD RED-GREEN-REFACTOR TEST
    print("=== TDD Test: Circular Dependency Resolution ===")
    print("Testing RED-GREEN-REFACTOR cycle compliance...")
    
    unittest.main(verbosity=2)