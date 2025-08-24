import copy
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

ServiceLocator
"""

import sys
import os

# TEST
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_circular_dependency_resolution():
    """TEST"""
    print("=" * 60)
    print("SUCCESS - ServiceLocatorSUCCESS")
    print("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    # SUCCESS1: ServiceFactorySUCCESS
    print("\n[Test 1] ServiceFactoryTEST")
    try:
        from service_factory import ServiceFactory
        print("  [OK] ServiceFactorySUCCESS")
        success_count += 1
    except ImportError as e:
        print(f"  [FAIL] SUCCESS: {e}")
    
    # SUCCESS2: ERROR
    print("\n[Test 2] ERROR")
    try:
        ServiceFactory.initialize_services()
        print("  [OK] SUCCESS")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] SUCCESS: {e}")
    
    # SUCCESS3: ConfigServiceERROR
    print("\n[Test 3] ConfigServiceERROR")
    try:
        config = ServiceFactory.get_config_service()
        print(f"  [OK] ConfigServiceCONFIG")
        print(f"    - is_enabled: {config.is_enabled}")
        print(f"    - mode: {config.mode}")
        print(f"    - flows: {config.flows}")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] SUCCESS: {e}")
    
    # SUCCESS4: StateServiceERROR
    print("\n[Test 4] StateServiceERROR")
    try:
        state = ServiceFactory.get_state_service()
        print(f"  [OK] StateService")
        print(f"    - is_active: {state.is_active}")
        print(f"    - session_count: {state.session_count}")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] SUCCESS: {e}")
    
    # SUCCESS5: ServiceLocatorERROR
    print("\n[Test 5] ServiceLocatorERROR")
    try:
        from auto_mode_interfaces import ServiceLocator
        
        # ServiceLocatorCONFIG
        config_from_locator = ServiceLocator.get('config')
        state_from_locator = ServiceLocator.get('state')
        
        # CONFIG
        if config_from_locator is config and state_from_locator is state:
            print("  [OK] ServiceLocatorSUCCESS")
            print("    - SUCCESS")
            success_count += 1
        else:
            print("  [FAIL] SUCCESS")
    except Exception as e:
        print(f"  [FAIL] ServiceLocatorERROR: {e}")
    
    # SUCCESS
    print("\n" + "=" * 60)
    print("SUCCESS")
    print("=" * 60)
    print(f"SUCCESS: {success_count}/{total_tests}")
    print(f"SUCCESS: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n[SUCCESS] SUCCESS")
        print("ServiceLocatorSUCCESS")
        return True
    else:
        print("\n[WARNING] WARNING")
        return False

def main():
    """SUCCESS"""
    print("SUCCESS")
    print("ServiceFactorySUCCESSServiceLocatorSUCCESS\n")
    
    success = test_circular_dependency_resolution()
    
    print("\n" + "=" * 60)
    if success:
        print("[PASS] SUCCESS")
        print("SUCCESS")
    else:
        print("[FAIL] SUCCESS")
        print("SUCCESS")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())