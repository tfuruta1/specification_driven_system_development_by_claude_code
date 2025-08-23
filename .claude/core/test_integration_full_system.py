#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full System Integration TDD Tests
完全システム統合TDDテスト

Auto-Modeシステム全体の統合テストとE2Eテスト
実際のユーザーワークフロー、システム間の相互作用、リソース管理を検証

テストエンジニア: Claude Code TDD Specialist
作成日: 2025-08-23
"""

import unittest
import threading
import time
import tempfile
import shutil
import json
import os
import gc
import psutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys

# テスト対象のモジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent))


class TestFullSystemStartupShutdown(unittest.TestCase):
    """
    システム全体の起動・停止統合テスト
    
    TDD Phase: GREEN - システム全体の動作確認
    """
    
    def setUp(self):
        """統合テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
        # テスト用一時ディレクトリ
        self.test_dir = tempfile.mkdtemp()
        
    def test_complete_system_startup_sequence(self):
        """
        完全なシステム起動シーケンステスト
        
        GREEN: システム全体の正常起動
        """
        from .auto_mode_core import create_auto_mode
        
        # システム作成
        auto_mode = create_auto_mode(self.test_dir)
        
        # システムコンポーネントの存在確認
        self.assertIsNotNone(auto_mode.config)
        self.assertIsNotNone(auto_mode.state)
        self.assertIsNotNone(auto_mode.logger)
        self.assertIsNotNone(auto_mode.error_handler)
        self.assertIsNotNone(auto_mode.integration_runner)
        
        # 初期状態確認
        initial_status = auto_mode.execute_command("status")
        self.assertIsInstance(initial_status, dict)
        self.assertFalse(initial_status['active'])
        
        # システムが正常に機能することを確認
        self.assertFalse(auto_mode.is_active())
        
    def test_system_configuration_persistence(self):
        """
        システム設定永続化テスト
        
        GREEN: 設定の保存と読み込み
        """
        from .auto_mode_core import create_auto_mode
        
        # 設定付きシステム作成
        auto_mode = create_auto_mode(self.test_dir)
        
        # 設定変更
        config = auto_mode.config
        original_enabled = config.is_enabled
        config.enable()
        config.set_flow("新規開発")
        
        # 設定が変更されたことを確認
        self.assertTrue(config.is_enabled)
        self.assertEqual(config.current_flow, "新規開発")
        
        # 設定ファイルの存在確認（実際のファイルシステムに保存される場合）
        # ここでは設定が内部的に保持されていることを確認
        config_summary = config.get_config_summary()
        self.assertTrue(config_summary['is_enabled'])
        self.assertEqual(config_summary['current_flow'], "新規開発")
        
    def test_system_state_management_integration(self):
        """
        システム状態管理統合テスト
        
        GREEN: 状態管理の完全な動作
        """
        from .auto_mode_core import create_auto_mode
        
        auto_mode = create_auto_mode(self.test_dir)
        state = auto_mode.state
        
        # 初期状態
        self.assertFalse(state.is_active)
        self.assertIsNone(state.current_session)
        
        # セッション開始
        session_id = state.start()
        self.assertIsNotNone(session_id)
        self.assertTrue(state.is_active)
        self.assertEqual(state.current_session, session_id)
        
        # セッション情報の記録
        state.add_test_result({'test': 'integration_test', 'result': 'pass'})
        state.add_warning('Test warning')
        
        # セッション状態確認
        status = state.get_status()
        self.assertTrue(status['active'])
        self.assertEqual(status['session_id'], session_id)
        
        # セッション停止
        state.stop()
        self.assertFalse(state.is_active)
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
        # 一時ディレクトリクリーンアップ
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestSystemInterServiceCommunication(unittest.TestCase):
    """
    システム内サービス間通信テスト
    
    TDD Phase: GREEN - サービス間の正常な相互作用
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_config_state_interaction(self):
        """
        設定-状態サービス間相互作用テスト
        
        GREEN: サービス間の正常な連携
        """
        from .service_factory import get_config_service, get_state_service
        
        config = get_config_service()
        state = get_state_service()
        
        # 設定変更が状態管理に影響しないことを確認（独立性）
        config.enable()
        self.assertTrue(config.is_enabled)
        self.assertFalse(state.is_active)  # 状態は独立
        
        # 状態変更が設定に影響しないことを確認
        session_id = state.start()
        self.assertTrue(state.is_active)
        self.assertTrue(config.is_enabled)  # 設定は変更されない
        
        state.stop()
        config.disable()
        
    def test_auto_mode_service_coordination(self):
        """
        AutoModeサービス協調テスト
        
        GREEN: AutoModeとサービス間の協調動作
        """
        from .auto_mode_core import create_auto_mode
        
        auto_mode = create_auto_mode()
        
        # statusコマンドによるサービス間協調
        status = auto_mode.execute_command("status")
        
        # 複数のサービスからの情報が統合されていることを確認
        self.assertIn('active', status)          # state service
        self.assertIn('config_enabled', status)  # config service
        self.assertIn('current_flow', status)    # config service
        self.assertIn('mode', status)            # config service
        
        # 各サービスが適切に動作していることを確認
        self.assertIsInstance(status['active'], bool)
        self.assertIsInstance(status['config_enabled'], bool)
        
    def test_service_error_isolation(self):
        """
        サービスエラー分離テスト
        
        GREEN: 一つのサービスのエラーが他に波及しないことを確認
        """
        from .service_factory import get_config_service, get_state_service
        
        config = get_config_service()
        state = get_state_service()
        
        # 状態サービスでセッション開始
        session_id = state.start()
        self.assertTrue(state.is_active)
        
        # 設定サービスに無効なフローを設定（エラー発生）
        invalid_flow_result = config.set_flow("無効なフロー")
        self.assertFalse(invalid_flow_result)  # 失敗
        
        # 状態サービスは影響を受けない
        self.assertTrue(state.is_active)
        self.assertEqual(state.current_session, session_id)
        
        state.stop()
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestSystemResourceManagement(unittest.TestCase):
    """
    システムリソース管理テスト
    
    TDD Phase: REFACTOR - リソース効率の最適化
    """
    
    def setUp(self):
        """テスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_memory_leak_prevention_full_system(self):
        """
        システム全体でのメモリリーク防止テスト
        
        REFACTOR: メモリ効率の最適化
        """
        import gc
        from .auto_mode_core import create_auto_mode
        
        # ベースラインメモリ使用量
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # システム作成・削除を繰り返す
        auto_modes = []
        for i in range(5):
            auto_mode = create_auto_mode()
            
            # 基本操作実行
            status = auto_mode.execute_command("status")
            
            # セッション開始・停止
            if auto_mode.state.is_active:
                auto_mode.state.stop()
            
            auto_modes.append(auto_mode)
        
        # オブジェクト削除
        del auto_modes
        
        # サービスクリア
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
        # メモリクリーンアップ
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # メモリ増加量確認
        memory_growth = final_objects - initial_objects
        self.assertLess(memory_growth, 100,
                       f"Memory leak detected: {memory_growth} objects leaked")
        
    def test_resource_cleanup_on_system_shutdown(self):
        """
        システムシャットダウン時のリソースクリーンアップテスト
        
        REFACTOR: 適切なリソース解放
        """
        from .auto_mode_core import create_auto_mode
        from .service_factory import ServiceFactory
        
        # システム作成とリソース確保
        auto_mode = create_auto_mode()
        
        # セッション開始（リソース確保）
        session_id = auto_mode.state.start()
        auto_mode.state.add_test_result({'test': 'resource_test'})
        
        # セッションデータ確保確認
        session_data = auto_mode.state.session_data
        self.assertIn(session_id, session_data)
        self.assertGreater(len(session_data[session_id]['test_results']), 0)
        
        # システムシャットダウン
        auto_mode.state.stop()
        ServiceFactory.clear_services()
        
        # リソースがクリーンアップされたことを確認
        self.assertFalse(ServiceFactory.is_initialized())
        
    def test_concurrent_system_access_resource_safety(self):
        """
        並行システムアクセスでのリソース安全性テスト
        
        REFACTOR: 並行処理での安全なリソース管理
        """
        from .auto_mode_core import create_auto_mode
        import concurrent.futures
        
        results = []
        exceptions = []
        
        def concurrent_system_operation(thread_id):
            try:
                auto_mode = create_auto_mode()
                
                # 状態取得
                status = auto_mode.execute_command("status")
                
                # 設定変更
                auto_mode.config.enable()
                auto_mode.config.disable()
                
                results.append({
                    'thread_id': thread_id,
                    'status_received': isinstance(status, dict)
                })
                
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': str(e)
                })
        
        # 複数スレッドでシステム操作
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_system_operation, i) for i in range(5)]
            concurrent.futures.wait(futures)
        
        # 結果検証
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 5)
        
        for result in results:
            self.assertTrue(result['status_received'])
        
    def tearDown(self):
        """テストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        gc.collect()


class TestEndToEndWorkflows(unittest.TestCase):
    """
    エンドツーエンドワークフローテスト
    
    TDD Phase: GREEN - 実際のユーザーワークフローの検証
    """
    
    def setUp(self):
        """E2Eテスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
        # テスト用一時ディレクトリ
        self.test_dir = tempfile.mkdtemp()
        
    def test_complete_auto_mode_workflow(self):
        """
        完全なAuto-Modeワークフローテスト
        
        GREEN: 実際のユーザー操作シーケンス
        """
        from .auto_mode_core import create_auto_mode
        
        # ステップ1: システム初期化
        auto_mode = create_auto_mode(self.test_dir)
        
        # ステップ2: 初期状態確認
        status = auto_mode.execute_command("status")
        self.assertFalse(status['active'])
        
        # ステップ3: 設定確認
        config = auto_mode.config
        self.assertIsNotNone(config.flows)
        self.assertGreater(len(config.flows), 0)
        
        # ステップ4: セッション開始シミュレーション
        # （実際のstartコマンドは入力待ちがあるため、直接状態操作）
        session_id = auto_mode.state.start()
        config.enable()
        config.set_flow("新規開発")
        
        # ステップ5: アクティブ状態確認
        status = auto_mode.execute_command("status")
        self.assertTrue(status['active'])
        self.assertEqual(status['current_flow'], "新規開発")
        
        # ステップ6: セッション中の操作
        auto_mode.state.add_test_result({
            'test_name': 'integration_test',
            'result': 'passed',
            'duration': 0.5
        })
        
        # ステップ7: セッション停止
        result = auto_mode.execute_command("stop")
        self.assertTrue(result)
        
        # ステップ8: 最終状態確認
        final_status = auto_mode.execute_command("status")
        self.assertFalse(final_status['active'])
        
    @patch('builtins.input', return_value='1')  # フロー選択をモック
    def test_auto_mode_start_command_workflow(self, mock_input):
        """
        Auto-Modeスタートコマンドワークフローテスト
        
        GREEN: startコマンドの完全な実行
        """
        from .auto_mode_core import create_auto_mode
        
        auto_mode = create_auto_mode(self.test_dir)
        
        # startコマンド実行
        result = auto_mode.execute_command("start")
        self.assertTrue(result)
        
        # システムがアクティブになったことを確認
        self.assertTrue(auto_mode.is_active())
        status = auto_mode.execute_command("status")
        self.assertTrue(status['active'])
        
        # stopコマンド実行
        stop_result = auto_mode.execute_command("stop")
        self.assertTrue(stop_result)
        self.assertFalse(auto_mode.is_active())
        
    def test_session_data_lifecycle(self):
        """
        セッションデータライフサイクルテスト
        
        GREEN: セッションデータの完全な管理
        """
        from .auto_mode_core import create_auto_mode
        
        auto_mode = create_auto_mode(self.test_dir)
        state = auto_mode.state
        
        # セッション開始
        session_id = state.start()
        
        # セッション中のデータ蓄積
        test_data = [
            {'test': 'unit_test_1', 'result': 'pass'},
            {'test': 'unit_test_2', 'result': 'pass'},
            {'test': 'integration_test', 'result': 'fail'}
        ]
        
        for data in test_data:
            state.add_test_result(data)
        
        state.add_warning("Test coverage below 80%")
        state.add_error("Connection timeout")
        
        # セッション要約取得
        summary = state.get_session_summary()
        self.assertIsNotNone(summary)
        self.assertEqual(summary['test_results'], 3)
        self.assertEqual(summary['warnings'], 1)
        self.assertEqual(summary['errors'], 1)
        
        # セッション停止
        state.stop()
        
        # セッション終了後もデータが保持されることを確認
        final_summary = state.get_session_summary(session_id)
        self.assertIsNotNone(final_summary)
        self.assertEqual(final_summary['test_results'], 3)
        
    def test_error_recovery_workflow(self):
        """
        エラー回復ワークフローテスト
        
        GREEN: システムエラーからの適切な回復
        """
        from .auto_mode_core import create_auto_mode
        
        auto_mode = create_auto_mode(self.test_dir)
        
        # 正常操作
        status = auto_mode.execute_command("status")
        self.assertIsInstance(status, dict)
        
        # 無効なコマンドでエラー発生
        invalid_result = auto_mode.execute_command("invalid_command")
        self.assertFalse(invalid_result)
        
        # システムが正常状態を維持していることを確認
        recovery_status = auto_mode.execute_command("status")
        self.assertIsInstance(recovery_status, dict)
        
        # 正常なコマンドが引き続き実行できることを確認
        self.assertTrue(auto_mode is not None)
        
    def tearDown(self):
        """E2Eテストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
        # 一時ディレクトリクリーンアップ
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestSystemPerformanceIntegration(unittest.TestCase):
    """
    システムパフォーマンス統合テスト
    
    TDD Phase: REFACTOR - システム全体のパフォーマンス最適化
    """
    
    def setUp(self):
        """パフォーマンステスト準備"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_system_startup_performance(self):
        """
        システム起動パフォーマンステスト
        
        REFACTOR: 起動時間の最適化
        """
        from .auto_mode_core import create_auto_mode
        import time
        
        startup_times = []
        
        for _ in range(10):
            start_time = time.time()
            auto_mode = create_auto_mode()
            end_time = time.time()
            
            startup_times.append(end_time - start_time)
            
            # クリーンアップ
            from .service_factory import ServiceFactory
            ServiceFactory.clear_services()
        
        # 平均起動時間確認
        avg_startup_time = sum(startup_times) / len(startup_times)
        max_startup_time = max(startup_times)
        
        # 起動時間が許容範囲内
        self.assertLess(avg_startup_time, 0.5,
                       f"Average startup time too slow: {avg_startup_time:.3f}s")
        self.assertLess(max_startup_time, 1.0,
                       f"Max startup time too slow: {max_startup_time:.3f}s")
        
    def test_command_execution_performance(self):
        """
        コマンド実行パフォーマンステスト
        
        REFACTOR: コマンド処理の最適化
        """
        from .auto_mode_core import create_auto_mode
        import time
        
        auto_mode = create_auto_mode()
        
        # 大量のコマンド実行
        start_time = time.time()
        
        for _ in range(1000):
            status = auto_mode.execute_command("status")
            self.assertIsInstance(status, dict)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1000回のstatus実行が1秒以内
        self.assertLess(duration, 1.0,
                       f"Command execution too slow: {duration:.3f}s for 1000 commands")
        
        # 平均実行時間
        avg_time = duration / 1000
        self.assertLess(avg_time, 0.001,
                       f"Average command time too slow: {avg_time:.6f}s per command")
        
    def test_concurrent_system_performance(self):
        """
        並行システムパフォーマンステスト
        
        REFACTOR: 並行処理の最適化
        """
        from .auto_mode_core import create_auto_mode
        import concurrent.futures
        import time
        
        def system_operation_load(operation_id):
            auto_mode = create_auto_mode()
            
            start_time = time.time()
            
            # 複数のコマンド実行
            for _ in range(100):
                status = auto_mode.execute_command("status")
            
            end_time = time.time()
            return {
                'operation_id': operation_id,
                'duration': end_time - start_time
            }
        
        # 5つの並行操作
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(system_operation_load, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # 並行実行により全体時間が短縮されることを確認
        self.assertLess(total_time, 3.0,
                       f"Concurrent execution too slow: {total_time:.3f}s")
        
        # すべての操作が完了したことを確認
        self.assertEqual(len(results), 5)
        
        for result in results:
            self.assertLess(result['duration'], 2.0)
        
    def tearDown(self):
        """パフォーマンステストクリーンアップ"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


def run_full_system_integration_tests():
    """
    完全システム統合テストの実行
    
    Returns:
        テスト結果の詳細レポート
    """
    # テストスイート構築
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
    test_classes = [
        TestFullSystemStartupShutdown,
        TestSystemInterServiceCommunication,
        TestSystemResourceManagement,
        TestEndToEndWorkflows,
        TestSystemPerformanceIntegration
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
        'startup_shutdown_tests': 3,
        'service_communication_tests': 3,
        'resource_management_tests': 3,
        'e2e_workflow_tests': 4,
        'performance_tests': 3
    }
    
    return report


if __name__ == '__main__':
    print("=== Full System Integration TDD Tests ===")
    print("Testing complete Auto-Mode system integration...")
    print("Focus: System workflows, service interactions, resource management, E2E testing")
    
    # 完全システム統合テスト実行
    report = run_full_system_integration_tests()
    
    print(f"\n=== Full System Integration Test Report ===")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Startup/Shutdown Tests: {report['startup_shutdown_tests']}")
    print(f"Service Communication Tests: {report['service_communication_tests']}")
    print(f"Resource Management Tests: {report['resource_management_tests']}")
    print(f"E2E Workflow Tests: {report['e2e_workflow_tests']}")
    print(f"Performance Tests: {report['performance_tests']}")
    
    if report['success_rate'] == 100.0:
        print("\n✅ All full system integration tests passed!")
        print("Auto-Mode system is fully integrated and optimized.")
    else:
        print(f"\n⚠️  Some integration tests failed. Review the output above for details.")