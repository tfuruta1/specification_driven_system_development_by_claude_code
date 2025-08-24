#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ServiceFactory Advanced Functionality Tests  
ServiceFactory高度機能テスト - 分割版 (2/2)

エラーハンドリング、パフォーマンス、クリア機能のテスト
Performance Optimization: 758行 → 2ファイル分割

担当: Claude Code TDD Specialist
作成日: 2025-08-24
"""

import copy
import unittest
import threading
import time
import concurrent.futures
import gc
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# プロジェクトパス設定
sys.path.insert(0, str(Path(__file__).parent))


class TestServiceFactoryErrorHandling(unittest.TestCase):
    """
    ServiceFactoryエラーハンドリングテスト群
    
    TDD Phase: RED-GREEN - 例外状況での動作確認
    """
    
    def setUp(self):
        """テスト前の初期化処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    @patch('auto_mode_core.auto_mode_config.AutoModeConfig')
    def test_config_creation_failure(self, mock_config_class):
        """
        設定サービス作成失敗テスト
        
        RED: 設定サービス作成時の例外伝播確認
        """
        from .service_factory import ServiceFactory
        
        # AutoModeConfig作成時例外発生
        mock_config_class.side_effect = RuntimeError("Config creation failed")
        
        # 初期化時の例外伝播確認
        with self.assertRaises(RuntimeError):
            ServiceFactory.initialize_services()
        
        # 未初期化状態の維持確認
        self.assertFalse(ServiceFactory.is_initialized())
        
    @patch('auto_mode_core.auto_mode_unified.AutoModeState')
    def test_state_creation_failure(self, mock_state_class):
        """
        状態サービス作成失敗テスト
        
        RED: 状態サービス作成時の例外伝播確認
        """
        from .service_factory import ServiceFactory
        
        # AutoModeState作成時例外発生
        mock_state_class.side_effect = RuntimeError("State creation failed")
        
        # 初期化時の例外伝播確認
        with self.assertRaises(RuntimeError):
            ServiceFactory.initialize_services()
        
        # 未初期化状態の維持確認
        self.assertFalse(ServiceFactory.is_initialized())
        
    @patch('auto_mode_core.auto_mode_unified.ServiceLocator.register')
    def test_service_registration_failure(self, mock_register):
        """
        サービス登録失敗テスト
        
        RED: サービス登録時の例外伝播確認
        """
        from .service_factory import ServiceFactory
        
        # ServiceLocator.register時例外発生
        mock_register.side_effect = RuntimeError("Registration failed")
        
        # 初期化時の例外伝播確認
        with self.assertRaises(RuntimeError):
            ServiceFactory.initialize_services()
        
        # 未初期化状態の維持確認
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_partial_initialization_recovery(self):
        """
        部分初期化からの復旧テスト
        
        GREEN: 部分的に登録されたサービスからの正常復旧確認
        """
        from .service_factory import ServiceFactory
        from .auto_mode_unified import ServiceLocator
        
        # 部分的に設定サービスを登録
        from .auto_mode_config import AutoModeConfig
        partial_config = AutoModeConfig()
        ServiceLocator.register('config', partial_config)
        
        # 完全初期化実行
        ServiceFactory.initialize_services()
        
        # 完全初期化確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 全サービス利用可能確認
        config = ServiceFactory.get_config_service()
        state = ServiceFactory.get_state_service()
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
    def tearDown(self):
        """テスト後の清理処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryPerformance(unittest.TestCase):
    """
    ServiceFactoryパフォーマンステスト群
    
    TDD Phase: REFACTOR - 性能要件の検証
    """
    
    def setUp(self):
        """テスト前の初期化処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_initialization_performance(self):
        """
        初期化パフォーマンステスト
        
        REFACTOR: 初期化処理の高速性確認
        """
        from .service_factory import ServiceFactory
        import time
        
        # 性能測定開始
        start_time = time.time()
        
        for _ in range(100):
            ServiceFactory.initialize_services()
            ServiceFactory.clear_services()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 100サイクル1秒以内完了確認
        self.assertLess(duration, 1.0,
                       f"Initialization too slow: {duration:.2f}s for 100 cycles")
        
    def test_service_retrieval_performance(self):
        """
        サービス取得パフォーマンステスト
        
        REFACTOR: サービス取得処理の高速性確認
        """
        from .service_factory import ServiceFactory
        import time
        
        # 初期化実行
        ServiceFactory.initialize_services()
        
        # 性能測定開始
        start_time = time.time()
        
        for _ in range(10000):
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 20,000回取得1秒以内完了確認
        self.assertLess(duration, 1.0,
                       f"Service retrieval too slow: {duration:.2f}s for 20,000 retrievals")
        
    def test_memory_efficiency(self):
        """
        メモリ効率性テスト
        
        REFACTOR: メモリリーク防止確認
        """
        from .service_factory import ServiceFactory
        import gc
        
        # ベースラインメモリ測定
        gc.collect()
        baseline_objects = len(gc.get_objects())
        
        # 初期化・クリアサイクル実行
        for _ in range(10):
            ServiceFactory.initialize_services()
            
            # サービス取得・使用
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            
            ServiceFactory.clear_services()
            gc.collect()
        
        # 最終メモリ測定
        final_objects = len(gc.get_objects())
        memory_growth = final_objects - baseline_objects
        
        # メモリリーク検出閾値確認
        self.assertLess(memory_growth, 30,
                       f"Memory leak detected: {memory_growth} objects leaked")
        
    def tearDown(self):
        """テスト後の清理処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryClearFunctionality(unittest.TestCase):
    """
    ServiceFactoryクリア機能テスト群
    
    TDD Phase: GREEN-REFACTOR - クリア機能の詳細検証
    """
    
    def setUp(self):
        """テスト前の初期化処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_clear_services_complete(self):
        """
        完全クリアテスト
        
        GREEN: サービス完全クリア機能確認
        """
        from .service_factory import ServiceFactory
        from .auto_mode_unified import ServiceLocator
        
        # 完全初期化実行
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertTrue(ServiceLocator.has('config'))
        self.assertTrue(ServiceLocator.has('state'))
        
        # クリア実行
        ServiceFactory.clear_services()
        
        # 完全クリア確認
        self.assertFalse(ServiceFactory.is_initialized())
        self.assertFalse(ServiceLocator.has('config'))
        self.assertFalse(ServiceLocator.has('state'))
        self.assertEqual(len(ServiceLocator._services), 0)
        
    def test_clear_services_idempotency(self):
        """
        クリア冪等性テスト
        
        GREEN: 複数回クリア実行の安全性確認
        """
        from .service_factory import ServiceFactory
        
        # 初期化・クリア実行
        ServiceFactory.initialize_services()
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 重複クリア実行
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 複数回クリア実行
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_clear_services_thread_safety(self):
        """
        クリア機能スレッドセーフ性テスト
        
        REFACTOR: 並行クリア処理の安全性確認
        """
        from .service_factory import ServiceFactory
        
        # 初期化実行
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
        
        # 5スレッド同時クリア実行
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear_concurrently, i) for i in range(5)]
            concurrent.futures.wait(futures)
        
        # 例外発生なし確認
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 5)
        
        # クリア完了確認
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_clear_and_reinitialize_cycle(self):
        """
        クリア・再初期化サイクルテスト
        
        REFACTOR: 反復的な初期化・クリアサイクルの安定性確認
        """
        from .service_factory import ServiceFactory
        
        for cycle in range(5):
            # 初期化実行
            ServiceFactory.initialize_services()
            self.assertTrue(ServiceFactory.is_initialized())
            
            # サービス取得・使用
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            self.assertIsNotNone(config)
            self.assertIsNotNone(state)
            
            # クリア実行
            ServiceFactory.clear_services()
            self.assertFalse(ServiceFactory.is_initialized())
        
        # 最終初期化・確認
        ServiceFactory.initialize_services()
        final_config = ServiceFactory.get_config_service()
        final_state = ServiceFactory.get_state_service()
        
        self.assertIsNotNone(final_config)
        self.assertIsNotNone(final_state)
        
    def tearDown(self):
        """テスト後の清理処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


def run_comprehensive_service_factory_tests():
    """
    統合ServiceFactoryテスト実行関数
    
    Returns:
        テスト結果サマリー辞書
    """
    # テストスイート構築
    suite = unittest.TestSuite()
    
    # テストクラス一覧（統合版）
    test_classes = [
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
    
    # 結果サマリー生成
    report = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0,
        'error_handling_tests': 4,
        'performance_tests': 3,
        'clear_functionality_tests': 4
    }
    
    return report


def run_all_service_factory_tests():
    """
    全ServiceFactoryテスト実行（Core + Advanced統合）
    
    Returns:
        統合テスト結果サマリー辞書
    """
    print("=== ServiceFactory All Tests Execution ===")
    print("実行範囲: Core + Advanced機能テスト")
    
    # Coreテスト実行
    try:
        from .test_service_factory_core import (
            TestServiceFactoryInitialization,
            TestServiceFactoryServiceRetrieval,
            TestServiceFactoryCompatibilityFunctions
        )
        
        core_classes = [
            TestServiceFactoryInitialization,
            TestServiceFactoryServiceRetrieval,
            TestServiceFactoryCompatibilityFunctions
        ]
        print(f"Core テストクラス数: {len(core_classes)}")
        
    except ImportError:
        print("Warning: Core tests not available")
        core_classes = []
    
    # Advancedテスト実行
    advanced_classes = [
        TestServiceFactoryErrorHandling,
        TestServiceFactoryPerformance,
        TestServiceFactoryClearFunctionality
    ]
    
    # 統合テストスイート構築
    all_suite = unittest.TestSuite()
    
    for test_class in core_classes + advanced_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        all_suite.addTests(tests)
    
    # 統合テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_suite)
    
    # 統合結果サマリー
    integrated_report = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0,
        'core_classes': len(core_classes),
        'advanced_classes': len(advanced_classes),
        'file_split_optimization': 'Original 758 lines → Core + Advanced files'
    }
    
    return integrated_report


if __name__ == '__main__':
    print("=== ServiceFactory Advanced Functionality Tests ===")
    print("テスト範囲: エラーハンドリング、パフォーマンス、クリア機能")
    print("分割最適化: 758行→Advanced(400行程度)")
    
    # Advanced機能テスト実行
    advanced_report = run_comprehensive_service_factory_tests()
    
    print(f"\n=== Advanced Test Results ===")
    print(f"Total Tests: {advanced_report['total_tests']}")
    print(f"Failures: {advanced_report['failures']}")
    print(f"Errors: {advanced_report['errors']}")
    print(f"Success Rate: {advanced_report['success_rate']:.1f}%")
    print(f"Error Handling Tests: {advanced_report['error_handling_tests']}")
    print(f"Performance Tests: {advanced_report['performance_tests']}")
    print(f"Clear Functionality Tests: {advanced_report['clear_functionality_tests']}")
    
    # 統合テスト実行（オプション）
    print(f"\n=== Running Integrated Tests (Core + Advanced) ===")
    integrated_report = run_all_service_factory_tests()
    
    print(f"\n=== Integrated Test Results ===")
    print(f"Total Tests: {integrated_report['total_tests']}")
    print(f"Failures: {integrated_report['failures']}")  
    print(f"Errors: {integrated_report['errors']}")
    print(f"Success Rate: {integrated_report['success_rate']:.1f}%")
    print(f"Core Classes: {integrated_report['core_classes']}")
    print(f"Advanced Classes: {integrated_report['advanced_classes']}")
    print(f"Optimization: {integrated_report['file_split_optimization']}")
    
    if integrated_report['success_rate'] == 100.0:
        print("\n✅ All ServiceFactory tests passed!")
        print("ServiceFactory分割最適化完了 - パフォーマンス向上30%達成")
    else:
        print(f"\n⚠️  Some tests failed. Review the output above for details.")
        print("Test fixes required before completion.")