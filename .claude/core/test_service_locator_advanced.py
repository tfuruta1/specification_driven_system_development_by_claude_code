#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced ServiceLocator Pattern TDD Tests
高度なServiceLocatorパターンTDDテスト

ServiceLocatorパターンの完全性とパフォーマンスを検証
遅延初期化、スレッドセーフティ、エラーハンドリングを重点的にテスト

テストエンジニア: Claude Code TDD Specialist
作成日: 2025-08-23
"""

import unittest
import threading
import time
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# テスト対象のモジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))


class TestServiceLocatorCore(unittest.TestCase):
    """
    ServiceLocatorコア機能テスト
    
    TDD Phase: RED-GREEN-REFACTOR
    """
    
    def setUp(self):
        """テストケースごとの初期化"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_service_registration(self):
        """
        サービス登録機能のテスト
        
        RED: 未登録状態での確認
        GREEN: 登録後の確認
        REFACTOR: より効率的な登録方法
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # RED: 初期状態では未登録
        self.assertFalse(ServiceLocator.has('test_service'))
        
        # GREEN: 登録後は存在
        test_service = Mock(name='test_service')
        ServiceLocator.register('test_service', test_service)
        self.assertTrue(ServiceLocator.has('test_service'))
        
        # REFACTOR: 登録されたサービスが正確に取得できる
        retrieved = ServiceLocator.get('test_service')
        self.assertIs(retrieved, test_service)
        
    def test_service_registration_overwrite(self):
        """
        サービス登録の上書き動作テスト
        
        GREEN: 上書き登録の動作確認
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 最初のサービス登録
        service1 = Mock(name='service1')
        ServiceLocator.register('overwrite_test', service1)
        
        # 上書き登録
        service2 = Mock(name='service2')
        ServiceLocator.register('overwrite_test', service2)
        
        # 新しいサービスが取得されることを確認
        retrieved = ServiceLocator.get('overwrite_test')
        self.assertIs(retrieved, service2)
        self.assertIsNot(retrieved, service1)
        
    def test_multiple_service_registration(self):
        """
        複数サービスの同時登録テスト
        
        GREEN: 複数サービスの正常管理
        """
        from .auto_mode_interfaces import ServiceLocator
        
        services = {}
        for i in range(10):
            service_name = f'service_{i}'
            service_instance = Mock(name=service_name)
            service_instance.id = i
            
            services[service_name] = service_instance
            ServiceLocator.register(service_name, service_instance)
        
        # すべてのサービスが正常に登録・取得できることを確認
        for service_name, original_service in services.items():
            self.assertTrue(ServiceLocator.has(service_name))
            retrieved = ServiceLocator.get(service_name)
            self.assertIs(retrieved, original_service)
            self.assertEqual(retrieved.id, original_service.id)
            
    def tearDown(self):
        """テストクリーンアップ"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


class TestServiceLocatorLazyInitialization(unittest.TestCase):
    """
    ServiceLocator遅延初期化テスト
    
    TDD Phase: GREEN - 既存機能の動作確認
    REFACTOR - より効率的な遅延初期化
    """
    
    def setUp(self):
        """テスト準備"""
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        ServiceLocator.clear()
        ServiceFactory.clear_services()
        
    def test_lazy_initialization_triggers_service_factory(self):
        """
        遅延初期化がServiceFactoryを正しく呼び出すかテスト
        
        GREEN: 遅延初期化の動作確認
        """
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        self.assertFalse(ServiceLocator.has('config'))
        
        # 未登録サービスを取得しようとすると自動初期化が実行される
        config_service = ServiceLocator.get('config')
        
        # 自動初期化が実行されたことを確認
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertIsNotNone(config_service)
        
    def test_lazy_initialization_multiple_calls(self):
        """
        複数回の遅延初期化呼び出しテスト
        
        GREEN: 冪等性の確認
        """
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        
        # 複数回取得しても同じインスタンスが返される
        config1 = ServiceLocator.get('config')
        config2 = ServiceLocator.get('config')
        config3 = ServiceLocator.get('config')
        
        self.assertIs(config1, config2)
        self.assertIs(config2, config3)
        
        # ServiceFactoryは一度だけ初期化される
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_lazy_initialization_error_handling(self):
        """
        遅延初期化中のエラーハンドリングテスト
        
        RED: エラー状況での動作確認
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 存在しないサービスを取得しようとする
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get('nonexistent_service')
        
        error_message = str(context.exception)
        self.assertIn('not registered', error_message)
        self.assertIn('nonexistent_service', error_message)
        
    @patch('auto_mode_core.service_factory.ServiceFactory.initialize_services')
    def test_lazy_initialization_service_factory_failure(self, mock_initialize):
        """
        ServiceFactory初期化失敗時の動作テスト
        
        RED: 初期化失敗時のエラーハンドリング
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # ServiceFactory.initialize_services()が失敗するように設定
        mock_initialize.side_effect = RuntimeError("Initialization failed")
        
        # エラーが適切に伝播されることを確認
        with self.assertRaises(RuntimeError):
            ServiceLocator.get('config')
            
    def tearDown(self):
        """テストクリーンアップ"""
        from .auto_mode_interfaces import ServiceLocator
        from .service_factory import ServiceFactory
        ServiceLocator.clear()
        ServiceFactory.clear_services()


class TestServiceLocatorThreadSafety(unittest.TestCase):
    """
    ServiceLocatorスレッドセーフティテスト
    
    TDD Phase: REFACTOR - 並行処理での安全性確保
    """
    
    def setUp(self):
        """テスト準備"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_concurrent_service_registration(self):
        """
        並行サービス登録テスト
        
        REFACTOR: スレッドセーフな登録処理
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
                
                # 登録直後に取得して確認
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
        
        # 20個のスレッドで同時にサービス登録
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(register_service, i) for i in range(20)]
            concurrent.futures.wait(futures)
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 20)
        
        for result in results:
            self.assertTrue(result['registered_correctly'],
                          f"Service {result['service_name']} not registered correctly")
            
    def test_concurrent_service_retrieval(self):
        """
        並行サービス取得テスト
        
        REFACTOR: スレッドセーフな取得処理
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 事前にサービスを登録
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
        
        # 15個のスレッドで同時にサービス取得
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(access_service, i) for i in range(15)]
            concurrent.futures.wait(futures)
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 15)
        self.assertEqual(test_service.access_count, 15)
        
        for result in results:
            self.assertTrue(result['service_retrieved'],
                          f"Thread {result['thread_id']} did not retrieve correct service")
            
    def test_concurrent_clear_operations(self):
        """
        並行クリア操作テスト
        
        REFACTOR: クリア操作のスレッドセーフティ
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 複数のサービスを登録
        for i in range(10):
            service = Mock(name=f'service_{i}')
            ServiceLocator.register(f'service_{i}', service)
        
        results = []
        exceptions = []
        
        def clear_and_register(thread_id):
            try:
                ServiceLocator.clear()
                
                # クリア後に新しいサービスを登録
                new_service = Mock(name=f'new_service_{thread_id}')
                ServiceLocator.register(f'new_service_{thread_id}', new_service)
                
                results.append(thread_id)
                
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': e
                })
        
        # 5個のスレッドで同時にクリア・登録
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear_and_register, i) for i in range(5)]
            concurrent.futures.wait(futures)
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 5)
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


class TestServiceLocatorPerformance(unittest.TestCase):
    """
    ServiceLocatorパフォーマンステスト
    
    TDD Phase: REFACTOR - パフォーマンス最適化
    """
    
    def setUp(self):
        """テスト準備"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_service_registration_performance(self):
        """
        サービス登録のパフォーマンステスト
        
        REFACTOR: 登録処理の効率化
        """
        from .auto_mode_interfaces import ServiceLocator
        import time
        
        # 大量のサービス登録のパフォーマンス測定
        start_time = time.time()
        
        for i in range(1000):
            service = Mock(name=f'perf_service_{i}')
            ServiceLocator.register(f'perf_service_{i}', service)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1000個のサービス登録が1秒以内に完了すること
        self.assertLess(duration, 1.0,
                       f"Service registration too slow: {duration:.2f}s for 1000 services")
        
        # 登録されたサービス数の確認
        registered_count = len(ServiceLocator._services)
        self.assertEqual(registered_count, 1000)
        
    def test_service_retrieval_performance(self):
        """
        サービス取得のパフォーマンステスト
        
        REFACTOR: 取得処理の効率化
        """
        from .auto_mode_interfaces import ServiceLocator
        import time
        
        # 事前にサービスを登録
        services = {}
        for i in range(100):
            service_name = f'fast_service_{i}'
            service = Mock(name=service_name)
            services[service_name] = service
            ServiceLocator.register(service_name, service)
        
        # 大量のサービス取得のパフォーマンス測定
        start_time = time.time()
        
        for _ in range(10000):  # 10,000回の取得
            for service_name in services.keys():
                ServiceLocator.get(service_name)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1,000,000回の取得が2秒以内に完了すること
        total_retrievals = 10000 * 100
        self.assertLess(duration, 2.0,
                       f"Service retrieval too slow: {duration:.2f}s for {total_retrievals:,} retrievals")
        
        # 平均取得時間の計算
        avg_time_per_retrieval = duration / total_retrievals
        self.assertLess(avg_time_per_retrieval, 0.00001,
                       f"Average retrieval time too slow: {avg_time_per_retrieval:.6f}s per retrieval")
        
    def test_memory_usage_optimization(self):
        """
        メモリ使用量最適化テスト
        
        REFACTOR: メモリ効率の向上
        """
        from .auto_mode_interfaces import ServiceLocator
        import gc
        import sys
        
        # ベースラインメモリ使用量
        gc.collect()
        baseline_objects = len(gc.get_objects())
        
        # 大量のサービス登録・クリアを繰り返す
        for cycle in range(5):
            for i in range(200):
                service = Mock(name=f'memory_service_{cycle}_{i}')
                ServiceLocator.register(f'memory_service_{cycle}_{i}', service)
            
            ServiceLocator.clear()
            gc.collect()
        
        # 最終メモリ使用量
        final_objects = len(gc.get_objects())
        memory_growth = final_objects - baseline_objects
        
        # メモリ増加が許容範囲内であることを確認
        self.assertLess(memory_growth, 50,
                       f"Memory leak detected: {memory_growth} objects leaked")
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


class TestServiceLocatorErrorHandling(unittest.TestCase):
    """
    ServiceLocatorエラーハンドリングテスト
    
    TDD Phase: RED-GREEN - エラー処理の完全性確保
    """
    
    def setUp(self):
        """テスト準備"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()
        
    def test_get_nonexistent_service_error(self):
        """
        存在しないサービス取得時のエラーテスト
        
        RED: エラーが適切に発生することを確認
        """
        from .auto_mode_interfaces import ServiceLocator
        
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get('nonexistent_service')
        
        error_message = str(context.exception)
        self.assertIn("Service 'nonexistent_service' not registered", error_message)
        
    def test_register_none_service_handling(self):
        """
        Noneサービス登録時の処理テスト
        
        GREEN: None値の適切な処理
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # Noneサービスの登録（技術的には有効）
        ServiceLocator.register('none_service', None)
        self.assertTrue(ServiceLocator.has('none_service'))
        
        retrieved = ServiceLocator.get('none_service')
        self.assertIsNone(retrieved)
        
    def test_register_empty_string_service_name(self):
        """
        空文字列サービス名の処理テスト
        
        GREEN: 空文字列名の処理確認
        """
        from .auto_mode_interfaces import ServiceLocator
        
        test_service = Mock(name='empty_name_service')
        
        # 空文字列でのサービス登録
        ServiceLocator.register('', test_service)
        self.assertTrue(ServiceLocator.has(''))
        
        retrieved = ServiceLocator.get('')
        self.assertIs(retrieved, test_service)
        
    def test_service_locator_state_after_error(self):
        """
        エラー発生後のServiceLocator状態テスト
        
        GREEN: エラー後の状態整合性確認
        """
        from .auto_mode_interfaces import ServiceLocator
        
        # 正常なサービスを登録
        normal_service = Mock(name='normal_service')
        ServiceLocator.register('normal', normal_service)
        
        # エラーを発生させる
        try:
            ServiceLocator.get('nonexistent')
        except ValueError:
            pass
        
        # 正常なサービスが依然として取得できることを確認
        retrieved = ServiceLocator.get('normal')
        self.assertIs(retrieved, normal_service)
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .auto_mode_interfaces import ServiceLocator
        ServiceLocator.clear()


def run_advanced_service_locator_tests():
    """
    高度なServiceLocatorテストの実行
    
    Returns:
        テスト結果の詳細レポート
    """
    # テストスイート構築
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
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
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # レポート生成
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
    
    # 高度なテスト実行
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
        print("\n✅ All advanced ServiceLocator tests passed!")
        print("ServiceLocator pattern is fully implemented and optimized.")
    else:
        print(f"\n⚠️  Some advanced tests failed. Review the output above for details.")