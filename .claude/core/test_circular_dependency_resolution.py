#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test: Circular Dependency Resolution
循環依存解決のTDD検証テスト

RED-GREEN-REFACTOR サイクルに従って
循環依存の完全解決を検証
"""

import unittest
import sys
import os
from pathlib import Path

# テスト対象のモジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))

class TestCircularDependencyResolution(unittest.TestCase):
    """循環依存解決テストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        # ServiceFactoryのクリア
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
    
    def test_service_factory_initialization(self):
        """
        TEST 1: ServiceFactory初期化テスト
        - サービスファクトリーが正常に初期化できること
        - 循環依存なしでサービス作成できること
        """
        from .service_factory import ServiceFactory, get_config_service, get_state_service
        
        # RED: まず初期化前の状態確認（失敗すべき）
        self.assertFalse(ServiceFactory.is_initialized())
        
        # GREEN: 初期化後の成功確認
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        config = get_config_service()
        state = get_state_service()
        
        # REFACTOR: インターフェース実装確認
        from .auto_mode_interfaces import ConfigInterface, StateInterface
        self.assertIsInstance(config, ConfigInterface)
        self.assertIsInstance(state, StateInterface)
    
    def test_no_singleton_instances_in_modules(self):
        """
        TEST 2: シングルトンインスタンス除去テスト
        - auto_config, auto_stateシングルトンが存在しないこと
        """
        # config モジュールにシングルトンがないことを確認
        try:
            from .auto_mode_config import auto_config
            self.fail("auto_config singleton should not exist")
        except ImportError:
            pass  # 期待される動作
        
        # state モジュールにシングルトンがないことを確認
        try:
            from .auto_mode_state import auto_state
            self.fail("auto_state singleton should not exist")
        except ImportError:
            pass  # 期待される動作
    
    def test_delayed_import_functions_removed(self):
        """
        TEST 3: 遅延インポート関数除去テスト
        - _get_auto_config, _get_auto_state関数が除去されていること
        """
        from . import auto_mode_core
        
        # 遅延インポート関数が存在しないことを確認
        self.assertFalse(hasattr(auto_mode_core, '_get_auto_config'))
        self.assertFalse(hasattr(auto_mode_core, '_get_auto_state'))
    
    def test_service_locator_pattern_working(self):
        """
        TEST 4: ServiceLocatorパターン動作テスト
        - ServiceLocatorが正常に動作すること
        - 複数回取得しても同じインスタンスが返されること
        """
        from .service_factory import initialize_services, get_config_service, get_state_service
        
        # サービス初期化
        initialize_services()
        
        # 同じインスタンスが返されることを確認
        config1 = get_config_service()
        config2 = get_config_service()
        self.assertIs(config1, config2)
        
        state1 = get_state_service()
        state2 = get_state_service()
        self.assertIs(state1, state2)
    
    def test_auto_mode_creation_without_circular_dependency(self):
        """
        TEST 5: AutoMode作成テスト（循環依存なし）
        - create_auto_mode()が循環依存なしで動作すること
        """
        from .service_factory import initialize_services
        from .auto_mode_core import create_auto_mode
        
        # サービス初期化
        initialize_services()
        
        # AutoMode作成（循環依存があれば失敗）
        auto_mode = create_auto_mode()
        self.assertIsNotNone(auto_mode)
        self.assertTrue(hasattr(auto_mode, 'config'))
        self.assertTrue(hasattr(auto_mode, 'state'))
    
    def test_complete_workflow_without_circular_imports(self):
        """
        TEST 6: 完全ワークフローテスト
        - モジュール全体が循環依存なしで動作すること
        """
        from .service_factory import initialize_services, get_config_service, get_state_service
        from .auto_mode_core import create_auto_mode
        
        # ワークフロー実行
        initialize_services()
        config = get_config_service()
        state = get_state_service()
        auto_mode = create_auto_mode()
        
        # 基本機能テスト
        self.assertFalse(config.is_enabled)
        self.assertFalse(state.is_active)
        
        # コマンド実行テスト（循環依存があれば失敗）
        status = auto_mode.execute_command("status")
        self.assertIsInstance(status, dict)
        self.assertIn('active', status)
    
    def test_interfaces_not_importing_concrete_classes(self):
        """
        TEST 7: インターフェースファイルの循環依存除去テスト
        - auto_mode_interfaces.pyが具象クラスをインポートしていないこと
        """
        import inspect
        from . import auto_mode_interfaces
        
        # インターフェースファイルのソースコード取得
        source = inspect.getsource(auto_mode_interfaces)
        
        # 循環依存の原因となるインポートがないことを確認
        self.assertNotIn('from .auto_mode_config import AutoModeConfig', source)
        self.assertNotIn('from .auto_mode_state import AutoModeState', source)
        self.assertNotIn('create_default_services', source)
    
    def test_kiss_principle_compliance(self):
        """
        TEST 8: KISS原則準拠テスト
        - コードがシンプルであること
        - 不要な複雑性がないこと
        """
        from .service_factory import initialize_services
        
        # サービスファクトリーのシンプルさを検証
        initialize_services()  # 複雑であれば例外が発生
        
        # ServiceLocatorの使用が簡潔であることを確認
        from .auto_mode_interfaces import ServiceLocator
        services = ServiceLocator._services
        self.assertIn('config', services)
        self.assertIn('state', services)
        self.assertEqual(len(services), 2)  # 必要最小限


class TestCircularImportDetection(unittest.TestCase):
    """循環インポート検出テストクラス"""
    
    def test_no_circular_imports_detected(self):
        """
        TEST 9: 循環インポート検出なしテスト
        - 循環インポート検出器で循環が検出されないこと
        """
        from .circular_import_detector import CircularImportDetector
        
        detector = CircularImportDetector()
        current_dir = Path(__file__).parent
        circular_imports = detector.detect(str(current_dir))
        
        # auto_mode関連の循環インポートがないことを確認
        auto_mode_circulars = [
            circular for circular in circular_imports
            if 'auto_mode' in circular
        ]
        
        self.assertEqual(len(auto_mode_circulars), 0,
                        f"Circular imports detected: {auto_mode_circulars}")


if __name__ == '__main__':
    # TDD RED-GREEN-REFACTOR サイクルでテスト実行
    print("=== TDD Test: Circular Dependency Resolution ===")
    print("Testing RED-GREEN-REFACTOR cycle compliance...")
    
    unittest.main(verbosity=2)