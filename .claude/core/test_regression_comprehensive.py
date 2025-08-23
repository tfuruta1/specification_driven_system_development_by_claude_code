#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Regression TDD Tests
包括的リグレッションTDDテスト

循環依存解決後の既存機能の完全性を検証
パフォーマンス回帰、API互換性、機能回帰を重点的にテスト

テストエンジニア: Claude Code TDD Specialist
作成日: 2025-08-23
"""

import unittest
import time
import threading
import concurrent.futures
import gc
import importlib
import inspect
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# テスト対象のモジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))


class TestAPICompatibilityRegression(unittest.TestCase):
    """
    API互換性リグレッションテスト
    
    TDD Phase: GREEN - 既存APIの継続動作確認
    """
    
    def setUp(self):
        """API互換性テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_service_factory_api_compatibility(self):
        """
        ServiceFactory APIの互換性テスト
        
        GREEN: 既存のAPIが引き続き利用可能
        """
        # 旧来のサービス取得方法が動作することを確認
        from .service_factory import (
            get_config_service, get_state_service, clear_services,
            ServiceFactory
        )
        
        # 関数形式のAPI
        config = get_config_service()
        state = get_state_service()
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
        # クラス形式のAPI
        config_class = ServiceFactory.get_config_service()
        state_class = ServiceFactory.get_state_service()
        
        # 同じインスタンスを返すことを確認
        self.assertIs(config, config_class)
        self.assertIs(state, state_class)
        
        # クリア関数の互換性
        clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_auto_mode_config_api_compatibility(self):
        """
        AutoModeConfig APIの互換性テスト
        
        GREEN: 設定管理APIの既存機能
        """
        from .service_factory import get_config_service
        
        config = get_config_service()
        
        # 既存のプロパティアクセス
        self.assertIsInstance(config.is_enabled, bool)
        self.assertIsInstance(config.mode, str)
        self.assertIsInstance(config.flows, list)
        self.assertIsNotNone(config.current_flow)  # None or string
        
        # 既存のメソッド
        self.assertTrue(hasattr(config, 'enable'))
        self.assertTrue(hasattr(config, 'disable'))
        self.assertTrue(hasattr(config, 'set_flow'))
        self.assertTrue(hasattr(config, 'get_config_summary'))
        
        # メソッドが実行可能
        original_state = config.is_enabled
        config.enable()
        self.assertTrue(config.is_enabled)
        config.disable()
        self.assertFalse(config.is_enabled)
        
        # 設定要約が取得可能
        summary = config.get_config_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('is_enabled', summary)
        
    def test_auto_mode_state_api_compatibility(self):
        """
        AutoModeState APIの互換性テスト
        
        GREEN: 状態管理APIの既存機能
        """
        from .service_factory import get_state_service
        
        state = get_state_service()
        
        # 既存のプロパティアクセス
        self.assertIsInstance(state.is_active, bool)
        self.assertIsInstance(state.session_count, int)
        self.assertIsInstance(state.session_data, dict)
        
        # 既存のメソッド
        self.assertTrue(hasattr(state, 'start'))
        self.assertTrue(hasattr(state, 'stop'))
        self.assertTrue(hasattr(state, 'get_status'))
        self.assertTrue(hasattr(state, 'get_session_summary'))
        
        # セッション管理機能の動作確認
        self.assertFalse(state.is_active)
        session_id = state.start()
        self.assertIsNotNone(session_id)
        self.assertTrue(state.is_active)
        
        status = state.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn('active', status)
        
        state.stop()
        self.assertFalse(state.is_active)
        
    def test_auto_mode_core_api_compatibility(self):
        """
        AutoModeCore APIの互換性テスト
        
        GREEN: コアシステムAPIの既存機能
        """
        from .auto_mode_core import create_auto_mode, AutoMode
        
        # ファクトリー関数の動作確認
        auto_mode = create_auto_mode()
        self.assertIsInstance(auto_mode, AutoMode)
        
        # 既存のメソッド
        self.assertTrue(hasattr(auto_mode, 'execute_command'))
        self.assertTrue(hasattr(auto_mode, 'is_active'))
        
        # コマンド実行
        status = auto_mode.execute_command("status")
        self.assertIsInstance(status, dict)
        
        # 無効なコマンドのハンドリング
        invalid_result = auto_mode.execute_command("invalid")
        self.assertFalse(invalid_result)
        
    def tearDown(self):
        """API互換性テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestFunctionalRegression(unittest.TestCase):
    """
    機能リグレッションテスト
    
    TDD Phase: GREEN - 既存機能の継続動作
    """
    
    def setUp(self):
        """機能リグレッションテスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_config_persistence_regression(self):
        """
        設定永続化機能のリグレッションテスト
        
        GREEN: 設定保存・読み込み機能の継続動作
        """
        from .service_factory import get_config_service
        
        config = get_config_service()
        
        # 設定変更
        original_flow = config.current_flow
        config.enable()
        config.set_flow("バグ修正")
        
        # 設定要約での確認
        summary = config.get_config_summary()
        self.assertTrue(summary['is_enabled'])
        self.assertEqual(summary['current_flow'], "バグ修正")
        
        # 統合テスト設定の更新
        config.update_integration_settings(
            integration_tests_enabled=True,
            circular_import_detection=True
        )
        
        updated_summary = config.get_config_summary()
        integration_settings = updated_summary['integration_tests']
        self.assertTrue(integration_settings['enabled'])
        self.assertTrue(integration_settings['circular_import_detection'])
        
    def test_session_management_regression(self):
        """
        セッション管理機能のリグレッションテスト
        
        GREEN: セッション機能の完全な動作
        """
        from .service_factory import get_state_service
        
        state = get_state_service()
        
        # セッション開始
        session_id = state.start()
        self.assertIsNotNone(session_id)
        self.assertTrue(state.is_session_active())
        
        # セッションデータ追加
        test_result = {'test': 'regression_test', 'status': 'passed'}
        state.add_test_result(test_result)
        state.add_warning("Deprecation warning")
        state.add_error("Minor error occurred")
        
        # セッション状況確認
        status = state.get_status()
        self.assertEqual(status['test_results_count'], 1)
        self.assertEqual(status['warnings_count'], 1)
        self.assertEqual(status['errors_count'], 1)
        
        # セッション要約
        summary = state.get_session_summary()
        self.assertEqual(summary['test_results'], 1)
        self.assertEqual(summary['warnings'], 1)
        self.assertEqual(summary['errors'], 1)
        
        # セッション停止
        state.stop()
        self.assertFalse(state.is_session_active())
        
        # 停止後もデータが保持されることを確認
        final_summary = state.get_session_summary(session_id)
        self.assertIsNotNone(final_summary)
        
    def test_interface_implementation_regression(self):
        """
        インターフェース実装のリグレッションテスト
        
        GREEN: インターフェース準拠の継続確認
        """
        from .service_factory import get_config_service, get_state_service
        from .auto_mode_interfaces import ConfigInterface, StateInterface
        
        config = get_config_service()
        state = get_state_service()
        
        # インターフェース実装確認
        self.assertIsInstance(config, ConfigInterface)
        self.assertIsInstance(state, StateInterface)
        
        # ConfigInterface必須メソッド
        self.assertTrue(hasattr(config, 'is_enabled'))
        self.assertTrue(hasattr(config, 'current_flow'))
        self.assertTrue(hasattr(config, 'mode'))
        self.assertTrue(hasattr(config, 'flows'))
        self.assertTrue(hasattr(config, 'enable'))
        self.assertTrue(hasattr(config, 'disable'))
        self.assertTrue(hasattr(config, 'set_flow'))
        
        # StateInterface必須メソッド
        self.assertTrue(hasattr(state, 'is_active'))
        self.assertTrue(hasattr(state, 'current_session'))
        self.assertTrue(hasattr(state, 'start_time'))
        self.assertTrue(hasattr(state, 'session_data'))
        self.assertTrue(hasattr(state, 'start'))
        self.assertTrue(hasattr(state, 'stop'))
        self.assertTrue(hasattr(state, 'get_status'))
        
    def tearDown(self):
        """機能リグレッションテストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestPerformanceRegression(unittest.TestCase):
    """
    パフォーマンスリグレッションテスト
    
    TDD Phase: REFACTOR - パフォーマンスの非劣化確認
    """
    
    def setUp(self):
        """パフォーマンスリグレッションテスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_service_initialization_performance_regression(self):
        """
        サービス初期化パフォーマンスのリグレッションテスト
        
        REFACTOR: 初期化時間の非劣化確認
        """
        from .service_factory import ServiceFactory
        
        # 複数回の初期化時間測定
        initialization_times = []
        
        for _ in range(20):
            ServiceFactory.clear_services()
            
            start_time = time.time()
            ServiceFactory.initialize_services()
            end_time = time.time()
            
            initialization_times.append(end_time - start_time)
        
        # 統計計算
        avg_time = sum(initialization_times) / len(initialization_times)
        max_time = max(initialization_times)
        
        # パフォーマンス基準
        self.assertLess(avg_time, 0.1,
                       f"Average initialization time regressed: {avg_time:.4f}s")
        self.assertLess(max_time, 0.2,
                       f"Max initialization time regressed: {max_time:.4f}s")
        
    def test_service_access_performance_regression(self):
        """
        サービスアクセスパフォーマンスのリグレッションテスト
        
        REFACTOR: アクセス時間の非劣化確認
        """
        from .service_factory import get_config_service, get_state_service
        
        # 初期化
        config = get_config_service()
        state = get_state_service()
        
        # 大量アクセスの時間測定
        start_time = time.time()
        
        for _ in range(10000):
            config_access = get_config_service()
            state_access = get_state_service()
            
            # 簡単なプロパティアクセス
            _ = config_access.is_enabled
            _ = state_access.is_active
        
        end_time = time.time()
        duration = end_time - start_time
        
        # パフォーマンス基準（10,000回のアクセスが0.5秒以内）
        self.assertLess(duration, 0.5,
                       f"Service access performance regressed: {duration:.3f}s for 10,000 accesses")
        
        # 平均アクセス時間
        avg_access_time = duration / 20000  # config + state で 20,000回
        self.assertLess(avg_access_time, 0.000025,
                       f"Average access time regressed: {avg_access_time:.6f}s per access")
        
    def test_concurrent_access_performance_regression(self):
        """
        並行アクセスパフォーマンスのリグレッションテスト
        
        REFACTOR: 並行処理パフォーマンスの非劣化確認
        """
        from .service_factory import get_config_service, get_state_service
        
        def concurrent_access_load(thread_id):
            start_time = time.time()
            
            for _ in range(1000):
                config = get_config_service()
                state = get_state_service()
                _ = config.is_enabled
                _ = state.is_active
            
            end_time = time.time()
            return end_time - start_time
        
        # 5つのスレッドで並行アクセス
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_access_load, i) for i in range(5)]
            thread_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        avg_thread_time = sum(thread_times) / len(thread_times)
        
        # 並行処理による効率性確認
        self.assertLess(total_time, 2.0,
                       f"Concurrent access performance regressed: {total_time:.3f}s total")
        self.assertLess(avg_thread_time, 1.5,
                       f"Average thread performance regressed: {avg_thread_time:.3f}s per thread")
        
    def test_memory_usage_regression(self):
        """
        メモリ使用量リグレッションテスト
        
        REFACTOR: メモリ効率の非劣化確認
        """
        from .service_factory import ServiceFactory
        import gc
        
        # ベースラインメモリ測定
        gc.collect()
        baseline_objects = len(gc.get_objects())
        
        # サービス作成・削除を繰り返す
        for cycle in range(10):
            ServiceFactory.initialize_services()
            
            # サービス使用
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            
            # 設定・状態変更
            config.enable()
            session_id = state.start()
            state.add_test_result({'test': f'memory_test_{cycle}'})
            state.stop()
            config.disable()
            
            # クリア
            ServiceFactory.clear_services()
            gc.collect()
        
        # 最終メモリ測定
        final_objects = len(gc.get_objects())
        memory_growth = final_objects - baseline_objects
        
        # メモリリーク検出
        self.assertLess(memory_growth, 50,
                       f"Memory usage regressed: {memory_growth} objects leaked")
        
    def tearDown(self):
        """パフォーマンスリグレッションテストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        gc.collect()


class TestInterfaceStabilityRegression(unittest.TestCase):
    """
    インターフェース安定性リグレッションテスト
    
    TDD Phase: GREEN - インターフェース仕様の継続性
    """
    
    def setUp(self):
        """インターフェース安定性テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_service_locator_interface_stability(self):
        """
        ServiceLocatorインターフェース安定性テスト
        
        GREEN: ServiceLocatorの既存インターフェース維持
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 必須メソッドの存在確認
        required_methods = ['register', 'get', 'clear', 'has']
        
        for method_name in required_methods:
            self.assertTrue(hasattr(ServiceLocator, method_name),
                          f"ServiceLocator.{method_name} method is missing")
            method = getattr(ServiceLocator, method_name)
            self.assertTrue(callable(method),
                          f"ServiceLocator.{method_name} is not callable")
        
        # クラスメソッドとして動作することを確認
        test_service = Mock()
        ServiceLocator.register('test', test_service)
        self.assertTrue(ServiceLocator.has('test'))
        retrieved = ServiceLocator.get('test')
        self.assertIs(retrieved, test_service)
        ServiceLocator.clear()
        
    def test_config_interface_stability(self):
        """
        ConfigInterfaceの安定性テスト
        
        GREEN: 設定インターフェースの継続性
        """
        from .auto_mode_interfaces import ConfigInterface
        from .service_factory import get_config_service
        
        config = get_config_service()
        
        # ConfigInterface必須属性・メソッド
        required_properties = [
            'is_enabled', 'current_flow', 'mode', 'flows',
            'integration_tests_enabled', 'circular_import_detection',
            'component_connectivity_test', 'initialization_test'
        ]
        
        required_methods = ['enable', 'disable', 'set_flow', 'update_integration_settings']
        
        for prop_name in required_properties:
            self.assertTrue(hasattr(config, prop_name),
                          f"ConfigInterface.{prop_name} property is missing")
        
        for method_name in required_methods:
            self.assertTrue(hasattr(config, method_name),
                          f"ConfigInterface.{method_name} method is missing")
            method = getattr(config, method_name)
            self.assertTrue(callable(method),
                          f"ConfigInterface.{method_name} is not callable")
        
    def test_state_interface_stability(self):
        """
        StateInterfaceの安定性テスト
        
        GREEN: 状態インターフェースの継続性
        """
        from .auto_mode_interfaces import StateInterface
        from .service_factory import get_state_service
        
        state = get_state_service()
        
        # StateInterface必須属性・メソッド
        required_properties = [
            'is_active', 'current_session', 'start_time', 'session_data'
        ]
        
        required_methods = ['start', 'stop', 'get_status']
        
        for prop_name in required_properties:
            self.assertTrue(hasattr(state, prop_name),
                          f"StateInterface.{prop_name} property is missing")
        
        for method_name in required_methods:
            self.assertTrue(hasattr(state, method_name),
                          f"StateInterface.{method_name} method is missing")
            method = getattr(state, method_name)
            self.assertTrue(callable(method),
                          f"StateInterface.{method_name} is not callable")
        
    def test_service_factory_interface_stability(self):
        """
        ServiceFactoryインターフェース安定性テスト
        
        GREEN: ServiceFactoryの既存インターフェース維持
        """
        from .service_factory import ServiceFactory
        
        # 必須クラスメソッド
        required_class_methods = [
            'initialize_services', 'get_config_service', 'get_state_service',
            'clear_services', 'is_initialized'
        ]
        
        for method_name in required_class_methods:
            self.assertTrue(hasattr(ServiceFactory, method_name),
                          f"ServiceFactory.{method_name} method is missing")
            method = getattr(ServiceFactory, method_name)
            self.assertTrue(callable(method),
                          f"ServiceFactory.{method_name} is not callable")
        
        # 互換性関数の存在確認
        from . import service_factory
        
        compatibility_functions = [
            'get_config_service', 'get_state_service', 'clear_services'
        ]
        
        for func_name in compatibility_functions:
            self.assertTrue(hasattr(service_factory, func_name),
                          f"Compatibility function {func_name} is missing")
            func = getattr(service_factory, func_name)
            self.assertTrue(callable(func),
                          f"Compatibility function {func_name} is not callable")
        
    def tearDown(self):
        """インターフェース安定性テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestErrorHandlingRegression(unittest.TestCase):
    """
    エラーハンドリングリグレッションテスト
    
    TDD Phase: RED-GREEN - エラー処理の継続性確認
    """
    
    def setUp(self):
        """エラーハンドリングリグレッションテスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_service_locator_error_handling_regression(self):
        """
        ServiceLocatorエラーハンドリングのリグレッションテスト
        
        RED-GREEN: 既存のエラーハンドリング動作
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 未登録サービス取得エラー
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get('nonexistent_service')
        
        error_message = str(context.exception)
        self.assertIn('not registered', error_message)
        self.assertIn('nonexistent_service', error_message)
        
        # hasメソッドは例外を発生させない
        self.assertFalse(ServiceLocator.has('nonexistent_service'))
        
    def test_config_service_error_handling_regression(self):
        """
        設定サービスエラーハンドリングのリグレッションテスト
        
        GREEN: 設定エラーの適切な処理
        """
        from .service_factory import get_config_service
        
        config = get_config_service()
        
        # 無効なフロー設定
        result = config.set_flow('無効なフロー名')
        self.assertFalse(result)  # 失敗を示すFalse
        
        # 現在のフローは変更されない
        self.assertNotEqual(config.current_flow, '無効なフロー名')
        
        # 無効な統合テスト設定
        original_timeout = config.integration_test_timeout
        config.update_integration_settings(integration_test_timeout=-1)
        
        # 無効な値は設定されない
        self.assertEqual(config.integration_test_timeout, original_timeout)
        
    def test_auto_mode_error_handling_regression(self):
        """
        AutoModeエラーハンドリングのリグレッションテスト
        
        RED-GREEN: コアシステムのエラー処理
        """
        from .auto_mode_core import create_auto_mode
        
        auto_mode = create_auto_mode()
        
        # 無効なコマンド
        result = auto_mode.execute_command('invalid_command')
        self.assertFalse(result)
        
        # システムは正常状態を維持
        status = auto_mode.execute_command('status')
        self.assertIsInstance(status, dict)
        
    def tearDown(self):
        """エラーハンドリングリグレッションテストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


def run_comprehensive_regression_tests():
    """
    包括的リグレッションテストの実行
    
    Returns:
        テスト結果の詳細レポート
    """
    # テストスイート構築
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
    test_classes = [
        TestAPICompatibilityRegression,
        TestFunctionalRegression,
        TestPerformanceRegression,
        TestInterfaceStabilityRegression,
        TestErrorHandlingRegression
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
        'api_compatibility_tests': 4,
        'functional_regression_tests': 3,
        'performance_regression_tests': 4,
        'interface_stability_tests': 4,
        'error_handling_tests': 3
    }
    
    return report


if __name__ == '__main__':
    print("=== Comprehensive Regression TDD Tests ===")
    print("Testing regression prevention after circular dependency resolution...")
    print("Focus: API compatibility, functional regression, performance regression, interface stability")
    
    # 包括的リグレッションテスト実行
    report = run_comprehensive_regression_tests()
    
    print(f"\n=== Comprehensive Regression Test Report ===")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"API Compatibility Tests: {report['api_compatibility_tests']}")
    print(f"Functional Regression Tests: {report['functional_regression_tests']}")
    print(f"Performance Regression Tests: {report['performance_regression_tests']}")
    print(f"Interface Stability Tests: {report['interface_stability_tests']}")
    print(f"Error Handling Tests: {report['error_handling_tests']}")
    
    if report['success_rate'] == 100.0:
        print("\n✅ All comprehensive regression tests passed!")
        print("No regression detected after circular dependency resolution.")
    else:
        print(f"\n⚠️  Some regression tests failed. Review the output above for details.")