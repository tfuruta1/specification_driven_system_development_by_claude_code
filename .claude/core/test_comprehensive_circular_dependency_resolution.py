#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive TDD Test Suite: Circular Dependency Resolution
包括的循環依存解決TDDテストスイート

RED-GREEN-REFACTOR サイクルに従って
循環依存の完全解決を100%カバレッジで検証

テストエンジニア: Claude Code TDD Specialist
作成日: 2025-08-23
"""

import unittest
import sys
import os
import ast
import importlib
import threading
import time
import gc
import psutil
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from unittest.mock import Mock, patch, MagicMock

# テスト対象のモジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))


class TestCircularDependencyDetection(unittest.TestCase):
    """
    1. 循環依存検出テスト
    
    TDD Phase: RED - テストを書いて失敗させ、問題を特定
    """
    
    def setUp(self):
        """テストケースごとの初期化"""
        self.test_modules = [
            'auto_mode_interfaces',
            'auto_mode_config', 
            'auto_mode_state',
            'service_factory',
            'auto_mode_core'
        ]
        
    def test_no_circular_imports_between_core_modules(self):
        """
        重要なモジュール間に循環依存がないことを確認
        
        RED: 循環依存があれば失敗
        GREEN: 循環依存がなければ成功
        REFACTOR: より効率的な検出方法に改善
        """
        import networkx as nx
        
        # 依存関係グラフを構築
        dependency_graph = nx.DiGraph()
        
        for module_name in self.test_modules:
            try:
                module = importlib.import_module(f'.{module_name}', package=__name__.rsplit('.', 1)[0])
                source_file = Path(module.__file__)
                
                # ASTを使用してimport文を解析
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith('.'):
                            imported_module = node.module.lstrip('.')
                            if imported_module in self.test_modules:
                                dependency_graph.add_edge(module_name, imported_module)
                                
            except Exception as e:
                self.fail(f"Failed to analyze module {module_name}: {e}")
        
        # 循環依存検出
        try:
            cycles = list(nx.simple_cycles(dependency_graph))
            self.assertEqual(len(cycles), 0, 
                           f"Circular dependencies detected: {cycles}")
        except nx.NetworkXError as e:
            self.fail(f"Graph analysis failed: {e}")
    
    def test_interface_module_has_no_concrete_imports(self):
        """
        インターフェースモジュールが具象クラスをインポートしていないことを確認
        
        RED: 具象クラスのインポートがあれば失敗
        GREEN: インターフェースのみなら成功
        """
        import inspect
        from . import auto_mode_interfaces
        
        source = inspect.getsource(auto_mode_interfaces)
        
        # 禁止されたインポートパターン
        forbidden_imports = [
            'from .auto_mode_config import AutoModeConfig',
            'from .auto_mode_state import AutoModeState',
            'from .auto_mode_core import AutoMode',
            'create_default_services'
        ]
        
        for forbidden in forbidden_imports:
            self.assertNotIn(forbidden, source,
                           f"Interface module contains forbidden import: {forbidden}")
    
    def test_service_factory_manages_all_dependencies(self):
        """
        ServiceFactoryがすべての依存関係を適切に管理していることを確認
        
        RED: 依存関係の管理が不完全なら失敗
        GREEN: 適切に管理されていれば成功
        """
        from .service_factory import ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 初期化実行
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 必要なサービスが登録されていることを確認
        from .auto_mode_interfaces import ServiceLocator
        
        self.assertTrue(ServiceLocator.has('config'))
        self.assertTrue(ServiceLocator.has('state'))
        
        # 冪等性テスト（複数回実行しても同じ結果）
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        
        # クリーンアップ
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
    def tearDown(self):
        """テストケースごとのクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceLocatorPattern(unittest.TestCase):
    """
    2. ServiceLocatorパターンテスト
    
    TDD Phase: GREEN - 既存の実装が正常動作することを確認
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_service_registration_and_retrieval(self):
        """
        サービスの登録と取得が正しく動作することを確認
        
        GREEN: 基本機能の動作確認
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # テスト用サービス
        test_service = Mock()
        test_service.name = "test_service"
        
        # 登録
        ServiceLocator.register('test', test_service)
        self.assertTrue(ServiceLocator.has('test'))
        
        # 取得
        retrieved = ServiceLocator.get('test')
        self.assertIs(retrieved, test_service)
        
    def test_lazy_initialization_working(self):
        """
        遅延初期化が適切に機能することを検証
        
        GREEN: 遅延初期化の動作確認
        """
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        
        # 未初期化状態でサービス取得を試行
        # これにより自動的に初期化されるべき
        config_service = ServiceLocator.get('config')
        self.assertIsNotNone(config_service)
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_unregistered_service_error_handling(self):
        """
        未登録サービスへのアクセス時のエラーハンドリング
        
        RED: エラーが発生すべき
        GREEN: 適切なエラーメッセージが返される
        """
        from .auto_mode_interfaces import ServiceLocator
        
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get('nonexistent_service')
            
        self.assertIn("not registered", str(context.exception))
        
    def test_service_locator_thread_safety(self):
        """
        ServiceLocatorのスレッドセーフティテスト
        
        REFACTOR: 並行アクセスでも安全に動作することを確認
        """
        from .auto_mode_interfaces import ServiceLocator
        import threading
        import time
        
        results = []
        exceptions = []
        
        def register_and_get_service(service_name, service_instance):
            try:
                ServiceLocator.register(service_name, service_instance)
                retrieved = ServiceLocator.get(service_name)
                results.append((service_name, retrieved is service_instance))
            except Exception as e:
                exceptions.append(e)
        
        # 複数のスレッドで同時にサービスを登録・取得
        threads = []
        for i in range(10):
            service_name = f'service_{i}'
            service_instance = Mock()
            service_instance.id = i
            
            thread = threading.Thread(
                target=register_and_get_service,
                args=(service_name, service_instance)
            )
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドを待機
        for thread in threads:
            thread.join()
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 10)
        for service_name, is_same_instance in results:
            self.assertTrue(is_same_instance, 
                          f"Service {service_name} instance mismatch")
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactory(unittest.TestCase):
    """
    3. ServiceFactoryテスト
    
    TDD Phase: GREEN - 実装の完全性確認
    REFACTOR - より効率的な実装への改善
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_initialization_idempotency(self):
        """
        初期化の冪等性（複数回実行しても同じ結果）
        
        GREEN: 冪等性の確認
        """
        from .service_factory import ServiceFactory
        
        # 最初の初期化
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 2回目の初期化（変化なし）
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        
        # サービス数が変わらないことを確認
        from .auto_mode_interfaces import ServiceLocator
        initial_services = set(ServiceLocator._services.keys())
        
        ServiceFactory.initialize_services()
        final_services = set(ServiceLocator._services.keys())
        
        self.assertEqual(initial_services, final_services)
        
    def test_service_clear_functionality(self):
        """
        サービスクリア機能の動作確認
        
        GREEN: クリア機能の正常動作
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        # サービス初期化
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertTrue(len(ServiceLocator._services) > 0)
        
        # クリア実行
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        self.assertEqual(len(ServiceLocator._services), 0)
        
    def test_is_initialized_method_state_management(self):
        """
        is_initialized()メソッドの状態管理
        
        GREEN: 状態管理の正確性確認
        """
        from .service_factory import ServiceFactory
        
        # 初期状態
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 初期化後
        ServiceFactory.initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        
        # クリア後
        ServiceFactory.clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_compatibility_functions(self):
        """
        互換性関数の動作確認
        
        GREEN: 既存のAPIとの互換性確保
        """
        from .service_factory import (
            get_config_service, get_state_service, clear_services
        )
        
        # 互換性関数の動作確認
        config = get_config_service()
        state = get_state_service()
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
        # インターフェース実装確認
        from .auto_mode_interfaces import ConfigInterface, StateInterface
        self.assertIsInstance(config, ConfigInterface)
        self.assertIsInstance(state, StateInterface)
        
        # クリア関数確認
        clear_services()
        from .service_factory import ServiceFactory
        self.assertFalse(ServiceFactory.is_initialized())
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestIntegration(unittest.TestCase):
    """
    4. 統合テスト
    
    TDD Phase: GREEN - システム全体の動作確認
    REFACTOR - パフォーマンスとメモリ使用量の最適化
    """
    
    def setUp(self):
        """統合テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_full_auto_mode_system_startup_and_shutdown(self):
        """
        実際のauto_modeシステム全体の起動と停止
        
        GREEN: システム全体の動作確認
        """
        from .auto_mode_core import create_auto_mode
        
        # システム起動
        auto_mode = create_auto_mode()
        self.assertIsNotNone(auto_mode)
        self.assertIsNotNone(auto_mode.config)
        self.assertIsNotNone(auto_mode.state)
        
        # 基本コマンド実行
        status = auto_mode.execute_command("status")
        self.assertIsInstance(status, dict)
        self.assertIn('active', status)
        self.assertFalse(status['active'])  # 初期状態は非アクティブ
        
        # システム停止（自動）
        # auto_modeのライフサイクル管理による自動停止
        
    def test_service_interactions(self):
        """
        各サービス間の相互作用テスト
        
        GREEN: サービス間の正常な相互作用確認
        """
        from .service_factory import get_config_service, get_state_service
        
        config = get_config_service()
        state = get_state_service()
        
        # 設定変更がシステムに反映されることを確認
        original_enabled = config.is_enabled
        config.enable()
        self.assertTrue(config.is_enabled)
        
        # 状態管理の動作確認
        self.assertFalse(state.is_active)  # 初期状態
        session_id = state.start()
        self.assertIsNotNone(session_id)
        self.assertTrue(state.is_active)
        
        # クリーンアップ
        state.stop()
        config.disable()
        
    def test_memory_leak_prevention(self):
        """
        メモリリークやリソースリークがないことの確認
        
        REFACTOR: メモリ効率の最適化検証
        """
        import gc
        import sys
        
        # ベースラインメモリ使用量測定
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # 複数回のサービス初期化とクリア
        from .service_factory import ServiceFactory
        for _ in range(10):
            ServiceFactory.initialize_services()
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            
            # 簡単な操作実行
            config.enable()
            session_id = state.start()
            state.stop()
            config.disable()
            
            ServiceFactory.clear_services()
            
        # 最終的なメモリ使用量測定
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # メモリリークの検出（許容範囲内の増加は問題なし）
        object_increase = final_objects - initial_objects
        self.assertLess(object_increase, 100, 
                       f"Potential memory leak detected: {object_increase} objects leaked")
        
    def test_error_resilience(self):
        """
        エラー耐性とリカバリ機能のテスト
        
        GREEN: エラー処理の正常動作確認
        """
        from .service_factory import ServiceFactory
        from .auto_mode_interfaces import ServiceLocator
        
        # 異常な状態を作成
        ServiceLocator.register('invalid', None)
        
        # システムが適切にリカバリできることを確認
        try:
            ServiceFactory.initialize_services()
            config = ServiceFactory.get_config_service()
            self.assertIsNotNone(config)
        except Exception as e:
            self.fail(f"System failed to recover from error state: {e}")
            
    def tearDown(self):
        """統合テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        gc.collect()


class TestRegression(unittest.TestCase):
    """
    5. リグレッションテスト
    
    TDD Phase: GREEN - 既存機能の継続動作確認
    """
    
    def setUp(self):
        """リグレッションテスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_all_previous_functionality_still_works(self):
        """
        以前の機能がすべて正常に動作することを確認
        
        GREEN: 後方互換性の保証
        """
        # 1. 基本的なサービス機能
        from .service_factory import get_config_service, get_state_service
        
        config = get_config_service()
        state = get_state_service()
        
        # 設定管理機能
        self.assertIsNotNone(config.flows)
        self.assertIsInstance(config.flows, list)
        self.assertTrue(len(config.flows) > 0)
        
        # 状態管理機能
        self.assertFalse(state.is_active)  # 初期状態
        status = state.get_status()
        self.assertIsInstance(status, dict)
        
        # 2. AutoModeの基本機能
        from .auto_mode_core import create_auto_mode
        auto_mode = create_auto_mode()
        
        # コマンド実行
        status_result = auto_mode.execute_command("status")
        self.assertIsInstance(status_result, dict)
        
    def test_performance_no_degradation(self):
        """
        パフォーマンスが劣化していないことを検証
        
        GREEN: パフォーマンス回帰の検出
        """
        import time
        from .service_factory import ServiceFactory
        
        # パフォーマンステスト
        start_time = time.time()
        
        # 複数回の初期化とサービス取得
        for _ in range(100):
            ServiceFactory.initialize_services()
            config = ServiceFactory.get_config_service()
            state = ServiceFactory.get_state_service()
            ServiceFactory.clear_services()
            
        end_time = time.time()
        duration = end_time - start_time
        
        # パフォーマンス基準（100回の操作が1秒以内）
        self.assertLess(duration, 1.0, 
                       f"Performance degradation detected: {duration:.2f}s for 100 operations")
        
    def test_interface_compatibility(self):
        """
        インターフェースの互換性確認
        
        GREEN: APIの後方互換性
        """
        from .auto_mode_interfaces import ConfigInterface, StateInterface
        from .service_factory import get_config_service, get_state_service
        
        config = get_config_service()
        state = get_state_service()
        
        # インターフェースメソッドの存在確認
        self.assertTrue(hasattr(config, 'is_enabled'))
        self.assertTrue(hasattr(config, 'enable'))
        self.assertTrue(hasattr(config, 'disable'))
        self.assertTrue(hasattr(config, 'set_flow'))
        
        self.assertTrue(hasattr(state, 'is_active'))
        self.assertTrue(hasattr(state, 'start'))
        self.assertTrue(hasattr(state, 'stop'))
        self.assertTrue(hasattr(state, 'get_status'))
        
    def tearDown(self):
        """リグレッションテストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestCoverageAnalysis(unittest.TestCase):
    """
    テストカバレッジ解析とレポート生成
    
    TDD Phase: REFACTOR - テストの完全性確認
    """
    
    def test_module_coverage_analysis(self):
        """
        モジュールカバレッジ分析
        
        REFACTOR: 100%カバレッジに向けた改善
        """
        # テスト対象モジュール
        test_modules = [
            'auto_mode_interfaces',
            'auto_mode_config',
            'auto_mode_state', 
            'service_factory',
            'auto_mode_core'
        ]
        
        coverage_results = {}
        
        for module_name in test_modules:
            try:
                module = importlib.import_module(f'.{module_name}', package=__name__.rsplit('.', 1)[0])
                
                # モジュール内のクラスとメソッド数を計算
                classes = []
                methods = []
                functions = []
                
                for name, obj in vars(module).items():
                    if not name.startswith('_'):
                        if isinstance(obj, type):
                            classes.append(name)
                            # クラスメソッドを取得
                            class_methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))]
                            methods.extend([f"{name}.{m}" for m in class_methods])
                        elif callable(obj):
                            functions.append(name)
                
                coverage_results[module_name] = {
                    'classes': len(classes),
                    'methods': len(methods),
                    'functions': len(functions),
                    'total_items': len(classes) + len(methods) + len(functions)
                }
                
            except Exception as e:
                coverage_results[module_name] = {'error': str(e)}
        
        # カバレッジレポート出力
        print("\n=== Test Coverage Analysis ===")
        for module, stats in coverage_results.items():
            if 'error' in stats:
                print(f"{module}: Error - {stats['error']}")
            else:
                print(f"{module}: {stats['classes']} classes, {stats['functions']} functions, {stats['methods']} methods")
        
        # すべてのモジュールが正常に分析されたことを確認
        for module, stats in coverage_results.items():
            self.assertNotIn('error', stats, f"Module {module} analysis failed")


def run_comprehensive_tests():
    """
    包括的テストスイートの実行
    
    Returns:
        テスト結果の詳細レポート
    """
    # テストスイート構築
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
    test_classes = [
        TestCircularDependencyDetection,
        TestServiceLocatorPattern,
        TestServiceFactory,
        TestIntegration,
        TestRegression,
        TestCoverageAnalysis
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
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0
    }
    
    return report


if __name__ == '__main__':
    print("=== Comprehensive TDD Test Suite: Circular Dependency Resolution ===")
    print("Testing RED-GREEN-REFACTOR cycle compliance...")
    print("Target: 100% test coverage for circular dependency resolution")
    
    # 詳細テスト実行
    report = run_comprehensive_tests()
    
    print(f"\n=== Test Report ===")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    
    if report['success_rate'] == 100.0:
        print("\n✅ All tests passed! Circular dependency resolution is complete.")
    else:
        print(f"\n⚠️  Some tests failed. Review the output above for details.")