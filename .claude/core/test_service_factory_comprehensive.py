#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive ServiceFactory TDD Tests
包括的ServiceFactoryTDDテスト

ServiceFactoryの完全な動作検証とエッジケーステスト
初期化、冪等性、エラーハンドリング、パフォーマンスを重点的にテスト

テストエンジニア: Claude Code TDD Specialist
作成日: 2025-08-23
"""

import unittest
import threading
import time
import concurrent.futures
import gc
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# テスト対象のモジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))


class TestServiceFactoryInitialization(unittest.TestCase):
    """
    ServiceFactory初期化テスト
    
    TDD Phase: RED-GREEN-REFACTOR
    """
    
    def setUp(self):
        """テストケースごとの初期化"""
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        ServiceFactory.clear_services()
        ServiceLocator.clear()
        
    def test_initial_state(self):
        """
        初期状態テスト
        
        RED: 初期状態が未初期化であることを確認
        """
        from .service_factory import ServiceFactory
        
        # 初期状態では未初期化
        self.assertFalse(ServiceFactory.is_initialized())
        
        # サービスも未登録
        from .auto_mode_interfaces import ServiceLocator
        self.assertFalse(ServiceLocator.has('config'))
        self.assertFalse(ServiceLocator.has('state'))
        
    def test_first_initialization(self):
        """
        初回初期化テスト
        
        GREEN: 初期化が正常に実行されることを確認
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        # 初期化実行
        ServiceFactory.initialize_services()
        
        # 初期化状態確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 必要なサービスが登録されていることを確認
        self.assertTrue(ServiceLocator.has('config'))
        self.assertTrue(ServiceLocator.has('state'))
        
        # サービスが実際のインスタンスであることを確認
        config = ServiceLocator.get('config')
        state = ServiceLocator.get('state')
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
        # インターフェース実装確認
        from .auto_mode_interfaces import ConfigInterface, StateInterface
        self.assertIsInstance(config, ConfigInterface)
        self.assertIsInstance(state, StateInterface)
        
    def test_idempotent_initialization(self):
        """
        冪等性初期化テスト
        
        GREEN: 複数回実行しても同じ結果になることを確認
        REFACTOR: 効率的な冪等性実装
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        # 初回初期化
        ServiceFactory.initialize_services()
        first_config = ServiceLocator.get('config')
        first_state = ServiceLocator.get('state')
        
        # 2回目の初期化
        ServiceFactory.initialize_services()
        second_config = ServiceLocator.get('config')
        second_state = ServiceLocator.get('state')
        
        # 同じインスタンスが返されることを確認
        self.assertIs(first_config, second_config)
        self.assertIs(first_state, second_state)
        
        # 初期化状態は変わらない
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_initialization_thread_safety(self):
        """
        初期化のスレッドセーフティテスト
        
        REFACTOR: 並行初期化での安全性確保
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        results = []
        exceptions = []
        
        def initialize_concurrently(thread_id):
            try:
                ServiceFactory.initialize_services()
                config = ServiceLocator.get('config')
                state = ServiceLocator.get('state')
                
                results.append({
                    'thread_id': thread_id,
                    'config_id': id(config),
                    'state_id': id(state),
                    'initialized': ServiceFactory.is_initialized()
                })
                
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': str(e)
                })
        
        # 10個のスレッドで同時初期化
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(initialize_concurrently, i) for i in range(10)]
            concurrent.futures.wait(futures)
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 10)
        
        # すべてのスレッドが同じインスタンスを取得したことを確認
        config_ids = set(result['config_id'] for result in results)
        state_ids = set(result['state_id'] for result in results)
        
        self.assertEqual(len(config_ids), 1, "Multiple config instances created")
        self.assertEqual(len(state_ids), 1, "Multiple state instances created")
        
        # すべてのスレッドで初期化済み状態
        for result in results:
            self.assertTrue(result['initialized'])
            
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryServiceRetrieval(unittest.TestCase):
    """
    ServiceFactoryサービス取得テスト
    
    TDD Phase: GREEN - サービス取得機能の完全性確認
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_get_config_service_direct(self):
        """
        設定サービス直接取得テスト
        
        GREEN: get_config_service()の動作確認
        """
        from .service_factory import ServiceFactory
        
        config = ServiceFactory.get_config_service()
        
        # サービスが取得できることを確認
        self.assertIsNotNone(config)
        
        # 自動初期化が実行されたことを確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # インターフェース実装確認
        from .auto_mode_interfaces import ConfigInterface
        self.assertIsInstance(config, ConfigInterface)
        
    def test_get_state_service_direct(self):
        """
        状態サービス直接取得テスト
        
        GREEN: get_state_service()の動作確認
        """
        from .service_factory import ServiceFactory
        
        state = ServiceFactory.get_state_service()
        
        # サービスが取得できることを確認
        self.assertIsNotNone(state)
        
        # 自動初期化が実行されたことを確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # インターフェース実装確認
        from .auto_mode_interfaces import StateInterface
        self.assertIsInstance(state, StateInterface)
        
    def test_lazy_initialization_through_service_methods(self):
        """
        サービスメソッド経由の遅延初期化テスト
        
        GREEN: 遅延初期化の正常動作
        """
        from .service_factory import ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # サービス取得により自動初期化
        config = ServiceFactory.get_config_service()
        
        # 初期化が完了したことを確認
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertIsNotNone(config)
        
        # 状態サービスも取得可能
        state = ServiceFactory.get_state_service()
        self.assertIsNotNone(state)
        
    def test_service_consistency(self):
        """
        サービス一貫性テスト
        
        GREEN: 複数回取得でも同じインスタンス
        """
        from .service_factory import ServiceFactory
        
        # 複数回取得
        config1 = ServiceFactory.get_config_service()
        config2 = ServiceFactory.get_config_service()
        config3 = ServiceFactory.get_config_service()
        
        state1 = ServiceFactory.get_state_service()
        state2 = ServiceFactory.get_state_service()
        state3 = ServiceFactory.get_state_service()
        
        # 同じインスタンスであることを確認
        self.assertIs(config1, config2)
        self.assertIs(config2, config3)
        self.assertIs(state1, state2)
        self.assertIs(state2, state3)
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryCompatibilityFunctions(unittest.TestCase):
    """
    ServiceFactory互換性関数テスト
    
    TDD Phase: GREEN - 既存APIとの互換性確保
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_compatibility_get_config_service(self):
        """
        互換性関数get_config_service()テスト
        
        GREEN: 互換性関数の正常動作
        """
        from .service_factory import get_config_service, ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 互換性関数でサービス取得
        config = get_config_service()
        
        # 正常に取得できることを確認
        self.assertIsNotNone(config)
        self.assertTrue(ServiceFactory.is_initialized())
        
        # クラスメソッドと同じ結果
        config_direct = ServiceFactory.get_config_service()
        self.assertIs(config, config_direct)
        
    def test_compatibility_get_state_service(self):
        """
        互換性関数get_state_service()テスト
        
        GREEN: 互換性関数の正常動作
        """
        from .service_factory import get_state_service, ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 互換性関数でサービス取得
        state = get_state_service()
        
        # 正常に取得できることを確認
        self.assertIsNotNone(state)
        self.assertTrue(ServiceFactory.is_initialized())
        
        # クラスメソッドと同じ結果
        state_direct = ServiceFactory.get_state_service()
        self.assertIs(state, state_direct)
        
    def test_compatibility_clear_services(self):
        """
        互換性関数clear_services()テスト
        
        GREEN: 互換性関数の正常動作
        """
        from .service_factory import clear_services, ServiceFactory, get_config_service
        
        # 初期化
        config = get_config_service()
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 互換性関数でクリア
        clear_services()
        
        # クリア確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # クラスメソッドと同じ結果
        self.assertFalse(ServiceFactory.is_initialized())
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryErrorHandling(unittest.TestCase):
    """
    ServiceFactoryエラーハンドリングテスト
    
    TDD Phase: RED-GREEN - エラー処理の完全性
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    @patch('auto_mode_core.auto_mode_config.AutoModeConfig')
    def test_config_creation_failure(self, mock_config_class):
        """
        設定サービス作成失敗テスト
        
        RED: 作成失敗時のエラーハンドリング
        """
        from .service_factory import ServiceFactory
        
        # AutoModeConfigのコンストラクタで例外発生
        mock_config_class.side_effect = RuntimeError("Config creation failed")
        
        # エラーが適切に伝播されることを確認
        with self.assertRaises(RuntimeError):
            ServiceFactory.initialize_services()
        
        # 初期化状態は失敗のまま
        self.assertFalse(ServiceFactory.is_initialized())
        
    @patch('auto_mode_core.auto_mode_state.AutoModeState')
    def test_state_creation_failure(self, mock_state_class):
        """
        状態サービス作成失敗テスト
        
        RED: 作成失敗時のエラーハンドリング
        """
        from .service_factory import ServiceFactory
        
        # AutoModeStateのコンストラクタで例外発生
        mock_state_class.side_effect = RuntimeError("State creation failed")
        
        # エラーが適切に伝播されることを確認
        with self.assertRaises(RuntimeError):
            ServiceFactory.initialize_services()
        
        # 初期化状態は失敗のまま
        self.assertFalse(ServiceFactory.is_initialized())
        
    @patch('auto_mode_core.auto_mode_interfaces.ServiceLocator.register')
    def test_service_registration_failure(self, mock_register):
        """
        サービス登録失敗テスト
        
        RED: 登録失敗時のエラーハンドリング
        """
        from .service_factory import ServiceFactory
        
        # ServiceLocator.registerで例外発生
        mock_register.side_effect = RuntimeError("Registration failed")
        
        # エラーが適切に伝播されることを確認
        with self.assertRaises(RuntimeError):
            ServiceFactory.initialize_services()
        
        # 初期化状態は失敗のまま
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_partial_initialization_recovery(self):
        """
        部分初期化からの復旧テスト
        
        GREEN: 部分初期化状態からの適切な復旧
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        # 手動で部分的にサービス登録（異常な状態をシミュレート）
        from .auto_mode_config import AutoModeConfig
        partial_config = AutoModeConfig()
        ServiceLocator.register('config', partial_config)
        
        # 完全な初期化を実行
        ServiceFactory.initialize_services()
        
        # 正常に初期化が完了することを確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 両方のサービスが利用可能
        config = ServiceFactory.get_config_service()
        state = ServiceFactory.get_state_service()
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryPerformance(unittest.TestCase):
    """
    ServiceFactoryパフォーマンステスト
    
    TDD Phase: REFACTOR - パフォーマンス最適化検証
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_initialization_performance(self):
        """
        初期化パフォーマンステスト
        
        REFACTOR: 初期化時間の最適化
        """
        from .service_factory import ServiceFactory
        import time
        
        # 複数回の初期化・クリアのパフォーマンス測定
        start_time = time.time()
        
        for _ in range(100):
            ServiceFactory.initialize_services()
            ServiceFactory.clear_services()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 100回の初期化・クリアが1秒以内
        self.assertLess(duration, 1.0,
                       f"Initialization too slow: {duration:.2f}s for 100 cycles")
        
    def test_service_retrieval_performance(self):
        """
        サービス取得パフォーマンステスト
        
        REFACTOR: 取得処理の最適化
        """
        from .service_factory import ServiceFactory
        import time
        
        # 初期化
        ServiceFactory.initialize_services()
        
        # 大量のサービス取得のパフォーマンス測定
        start_time = time.time()
        
        for _ in range(10000):
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 20,000回の取得が1秒以内
        self.assertLess(duration, 1.0,
                       f"Service retrieval too slow: {duration:.2f}s for 20,000 retrievals")
        
    def test_memory_efficiency(self):
        """
        メモリ効率テスト
        
        REFACTOR: メモリ使用量の最適化
        """
        from .service_factory import ServiceFactory
        import gc
        
        # ベースラインメモリ使用量
        gc.collect()
        baseline_objects = len(gc.get_objects())
        
        # 初期化・クリアを繰り返す
        for _ in range(10):
            ServiceFactory.initialize_services()
            
            # サービス使用
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            
            ServiceFactory.clear_services()
            gc.collect()
        
        # 最終メモリ使用量
        final_objects = len(gc.get_objects())
        memory_growth = final_objects - baseline_objects
        
        # メモリ増加が許容範囲内
        self.assertLess(memory_growth, 30,
                       f"Memory leak detected: {memory_growth} objects leaked")
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryClearFunctionality(unittest.TestCase):
    """
    ServiceFactoryクリア機能テスト
    
    TDD Phase: GREEN-REFACTOR - クリア機能の完全性
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_clear_services_complete(self):
        """
        完全なサービスクリアテスト
        
        GREEN: クリア機能の正常動作
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        # サービス初期化
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertTrue(ServiceLocator.has('config'))
        self.assertTrue(ServiceLocator.has('state'))
        
        # クリア実行
        ServiceFactory.clear_services()
        
        # クリア確認
        self.assertFalse(ServiceFactory.is_initialized())
        self.assertFalse(ServiceLocator.has('config'))
        self.assertFalse(ServiceLocator.has('state'))
        self.assertEqual(len(ServiceLocator._services), 0)
        
    def test_clear_services_idempotency(self):
        """
        クリア機能の冪等性テスト
        
        GREEN: 複数回クリアしても安全
        """
        from .service_factory import ServiceFactory
        
        # 初期化後クリア
        ServiceFactory.initialize_services()
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 再度クリア（例外が発生しないことを確認）
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
        # さらにクリア
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_clear_services_thread_safety(self):
        """
        クリア機能のスレッドセーフティテスト
        
        REFACTOR: 並行クリアでの安全性
        """
        from .service_factory import ServiceFactory
        
        # 初期化
        ServiceFactory.initialize_services()
        
        results = []
        exceptions = []
        
        def clear_concurrently(thread_id):
            try:
                ServiceFactory.clear_services()
                results.append(thread_id)
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': str(e)
                })
        
        # 5個のスレッドで同時クリア
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear_concurrently, i) for i in range(5)]
            concurrent.futures.wait(futures)
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 5)
        
        # 最終的にクリア状態
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_clear_and_reinitialize_cycle(self):
        """
        クリア・再初期化サイクルテスト
        
        REFACTOR: 繰り返し使用での安定性
        """
        from .service_factory import ServiceFactory
        
        for cycle in range(5):
            # 初期化
            ServiceFactory.initialize_services()
            self.assertTrue(ServiceFactory.is_initialized())
            
            # サービス取得
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            self.assertIsNotNone(config)
            self.assertIsNotNone(state)
            
            # クリア
            ServiceFactory.clear_services()
            self.assertFalse(ServiceFactory.is_initialized())
        
        # 最終的に正常な状態
        ServiceFactory.initialize_services()
        final_config = ServiceFactory.get_config_service()
        final_state = ServiceFactory.get_state_service()
        
        self.assertIsNotNone(final_config)
        self.assertIsNotNone(final_state)
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


def run_comprehensive_service_factory_tests():
    """
    包括的ServiceFactoryテストの実行
    
    Returns:
        テスト結果の詳細レポート
    """
    # テストスイート構築
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
    test_classes = [
        TestServiceFactoryInitialization,
        TestServiceFactoryServiceRetrieval,
        TestServiceFactoryCompatibilityFunctions,
        TestServiceFactoryErrorHandling,
        TestServiceFactoryPerformance,
        TestServiceFactoryClearFunctionality
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # レポート生成
    report = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0,
        'initialization_tests': 4,
        'retrieval_tests': 4,
        'compatibility_tests': 3,
        'error_handling_tests': 4,
        'performance_tests': 3,
        'clear_functionality_tests': 4
    }
    
    return report


if __name__ == '__main__':
    print("=== Comprehensive ServiceFactory TDD Tests ===")
    print("Testing ServiceFactory implementation completeness...")
    print("Focus: Initialization, idempotency, error handling, performance, clear functionality")
    
    # 包括的テスト実行
    report = run_comprehensive_service_factory_tests()
    
    print(f"\n=== Comprehensive ServiceFactory Test Report ===")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Initialization Tests: {report['initialization_tests']}")
    print(f"Retrieval Tests: {report['retrieval_tests']}")
    print(f"Compatibility Tests: {report['compatibility_tests']}")
    print(f"Error Handling Tests: {report['error_handling_tests']}")
    print(f"Performance Tests: {report['performance_tests']}")
    print(f"Clear Functionality Tests: {report['clear_functionality_tests']}")
    
    if report['success_rate'] == 100.0:
        print("\n✅ All comprehensive ServiceFactory tests passed!")
        print("ServiceFactory implementation is complete and optimized.")
    else:
        print(f"\n⚠️  Some comprehensive tests failed. Review the output above for details.")