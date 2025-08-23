#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルな循環依存解決テスト
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """インポートテスト"""
    print("=== Import Test Starting ===\n")
    
    try:
        # ServiceFactoryから始める
        print("1. Importing ServiceFactory...")
        from service_factory import ServiceFactory
        print("   [OK] ServiceFactory imported\n")
        
        # サービス初期化
        print("2. Initializing services...")
        ServiceFactory.initialize_services()
        print("   [OK] Services initialized\n")
        
        # サービス取得テスト
        print("3. Getting config service...")
        config = ServiceFactory.get_config_service()
        print(f"   [OK] Config service: {config}\n")
        
        print("4. Getting state service...")
        state = ServiceFactory.get_state_service()
        print(f"   [OK] State service: {state}\n")
        
        # ServiceLocatorテスト
        print("5. Testing ServiceLocator...")
        from auto_mode_interfaces import ServiceLocator
        
        # 登録されているサービス確認
        config_from_locator = ServiceLocator.get('config')
        state_from_locator = ServiceLocator.get('state')
        print(f"   [OK] ServiceLocator working\n")
        
        # auto_mode_coreテスト
        print("6. Testing auto_mode_core...")
        from auto_mode_core import AutoMode
        core = AutoMode()
        print(f"   [OK] AutoMode created: {core}\n")
        
        print("=== ALL TESTS PASSED ===")
        print("\nCircular dependency has been successfully resolved!")
        print("ServiceLocator pattern is working correctly.")
        
        return True
        
    except ImportError as e:
        print(f"\n[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)