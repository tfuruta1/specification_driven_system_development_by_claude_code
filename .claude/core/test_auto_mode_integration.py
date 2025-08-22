"""
auto_mode.pyの統合テスト対応テスト

TDDフローに統合テスト機能を追加するためのテスト
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import json
from pathlib import Path

# テスト対象モジュールのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 既存のauto_mode.pyをインポート
from auto_mode import AutoMode, AutoModeConfig, AutoModeState

# 統合テスト機能をインポート（まだ存在しないが、TDDなので先にテストを定義）
try:
    from test_strategy import TestStrategy, TestLevel, TestResult
    from integration_test_runner import IntegrationTestRunner, IntegrationTestResult
except ImportError:
    # TDDのRed phase - モジュールがまだ存在しない
    pass


class TestAutoModeIntegrationSupport(unittest.TestCase):
    """AutoModeの統合テスト対応機能のテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.temp_dir = tempfile.mkdtemp()
        self.auto_mode = AutoMode(base_dir=self.temp_dir)
    
    def test_auto_mode_has_test_strategy(self):
        """AutoModeがテスト戦略を持つこと"""
        # テスト戦略が初期化される
        self.assertTrue(hasattr(self.auto_mode, 'test_strategy'))
        self.assertIsInstance(self.auto_mode.test_strategy, TestStrategy)
        
        # デフォルトで全レベルが有効
        self.assertTrue(self.auto_mode.test_strategy.is_level_enabled(TestLevel.UNIT))
        self.assertTrue(self.auto_mode.test_strategy.is_level_enabled(TestLevel.INTEGRATION))
        self.assertTrue(self.auto_mode.test_strategy.is_level_enabled(TestLevel.E2E))
    
    def test_auto_mode_has_integration_test_runner(self):
        """AutoModeが統合テスト実行機能を持つこと"""
        # 統合テスト実行器が初期化される
        self.assertTrue(hasattr(self.auto_mode, 'integration_runner'))
        self.assertIsInstance(self.auto_mode.integration_runner, IntegrationTestRunner)
        
        # 検出機能が有効
        self.assertTrue(self.auto_mode.integration_runner.circular_import_detection_enabled)
        self.assertTrue(self.auto_mode.integration_runner.component_connectivity_test_enabled)
        self.assertTrue(self.auto_mode.integration_runner.initialization_test_enabled)
    
    def test_tdd_workflow_includes_integration_tests(self):
        """TDDワークフローに統合テストが含まれること"""
        # ワークフロー実行メソッドが存在
        self.assertTrue(hasattr(self.auto_mode, 'execute_tdd_workflow'))
        
        # ワークフロー段階定義
        workflow_phases = self.auto_mode.get_tdd_workflow_phases()
        expected_phases = [
            'requirements_analysis',
            'unit_test_creation',
            'unit_test_execution',
            'integration_test_execution',  # 新規追加
            'implementation',
            'refactoring',
            'documentation'
        ]
        
        self.assertEqual(workflow_phases, expected_phases)
    
    def test_execute_tdd_workflow_with_integration_tests(self):
        """統合テスト付きTDDワークフロー実行テスト"""
        # モックテスト結果を設定
        mock_unit_result = TestResult(TestLevel.UNIT, True, 0, 5, 1.0)
        mock_integration_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=3,
            duration=2.0,
            details="All integration tests passed",
            circular_imports=[],
            connectivity_issues=[],
            initialization_errors=[]
        )
        
        with patch.object(self.auto_mode.test_strategy, 'execute_single_level') as mock_unit:
            with patch.object(self.auto_mode.integration_runner, 'run') as mock_integration:
                mock_unit.return_value = mock_unit_result
                mock_integration.return_value = mock_integration_result
                
                # TDDワークフロー実行
                result = self.auto_mode.execute_tdd_workflow()
                
                # 全段階が実行される
                self.assertTrue(result['success'])
                
                # ユニットテストと統合テストが両方実行される
                mock_unit.assert_called_with(TestLevel.UNIT)
                mock_integration.assert_called_once()
                
                # 結果が記録される
                self.assertIn('unit_test_result', result)
                self.assertIn('integration_test_result', result)
    
    def test_integration_test_failure_handling(self):
        """統合テスト失敗時の処理テスト"""
        # 統合テストが失敗した場合
        failed_integration_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=False,
            failed=1,
            total=3,
            duration=1.5,
            details="Circular import detected",
            circular_imports=["moduleA -> moduleB -> moduleA"],
            connectivity_issues=[],
            initialization_errors=[]
        )
        
        with patch.object(self.auto_mode.test_strategy, 'execute_single_level') as mock_unit:
            with patch.object(self.auto_mode.integration_runner, 'run') as mock_integration:
                mock_unit.return_value = TestResult(TestLevel.UNIT, True, 0, 5, 1.0)
                mock_integration.return_value = failed_integration_result
                
                # TDDワークフロー実行
                result = self.auto_mode.execute_tdd_workflow()
                
                # ワークフローは失敗で停止
                self.assertFalse(result['success'])
                self.assertIn('integration_test_failed', result['error'])
                
                # 循環参照情報が含まれる
                self.assertIn('circular_imports', result)
                self.assertEqual(len(result['circular_imports']), 1)
    
    def test_integration_test_configuration(self):
        """統合テスト設定機能のテスト"""
        # 統合テスト設定変更
        self.auto_mode.configure_integration_tests(
            circular_import_detection=True,
            component_connectivity_test=False,
            initialization_test=True
        )
        
        # 設定が反映される
        self.assertTrue(self.auto_mode.integration_runner.circular_import_detection_enabled)
        self.assertFalse(self.auto_mode.integration_runner.component_connectivity_test_enabled)
        self.assertTrue(self.auto_mode.integration_runner.initialization_test_enabled)
    
    def test_integration_test_reporting(self):
        """統合テストレポート機能のテスト"""
        # テスト結果を設定
        integration_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=False,
            failed=1,
            total=3,
            duration=2.5,
            details="Component connectivity issues found",
            circular_imports=[],
            connectivity_issues=["ServiceA cannot connect to ServiceB"],
            initialization_errors=[]
        )
        
        # レポート生成
        report = self.auto_mode.generate_integration_test_report(integration_result)
        
        # レポート内容確認
        self.assertIn("Integration Test Report", report)
        self.assertIn("Failed: 1", report)
        self.assertIn("Duration: 2.5s", report)
        self.assertIn("Component connectivity issues found", report)
        self.assertIn("ServiceA cannot connect to ServiceB", report)
    
    def test_auto_mode_workflow_phases_validation(self):
        """ワークフロー段階の検証テスト"""
        # 各段階のメソッドが存在することを確認
        phases = self.auto_mode.get_tdd_workflow_phases()
        
        for phase in phases:
            method_name = f"execute_{phase}"
            self.assertTrue(
                hasattr(self.auto_mode, method_name),
                f"Method {method_name} should exist for phase {phase}"
            )
    
    def test_session_integration_test_tracking(self):
        """セッション中の統合テスト追跡テスト"""
        # セッション開始
        session_id = self.auto_mode.state.start()
        
        # 統合テスト実行
        integration_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=2,
            duration=1.8,
            details="Integration tests passed",
            circular_imports=[],
            connectivity_issues=[],
            initialization_errors=[]
        )
        
        # セッションに統合テスト結果を記録
        self.auto_mode.track_integration_test_in_session(session_id, integration_result)
        
        # セッション情報に統合テスト結果が含まれる
        session_info = self.auto_mode.get_session_info(session_id)
        self.assertIn('integration_test_results', session_info)
        self.assertEqual(len(session_info['integration_test_results']), 1)
        
        # 統合テスト結果の詳細が保存される
        saved_result = session_info['integration_test_results'][0]
        self.assertTrue(saved_result['passed'])
        self.assertEqual(saved_result['total'], 2)
        self.assertEqual(saved_result['duration'], 1.8)
    
    def test_auto_mode_start_with_integration_test_setup(self):
        """統合テスト設定付きAuto-Mode開始テスト"""
        # Auto-Mode開始時に統合テストが自動設定される
        with patch.object(self.auto_mode, '_setup_integration_tests') as mock_setup:
            success = self.auto_mode.execute_command("start")
            
            self.assertTrue(success)
            mock_setup.assert_called_once()
            
            # 統合テスト設定が有効になる
            self.assertTrue(self.auto_mode.is_integration_tests_enabled())
    
    def test_circular_import_detection_in_workflow(self):
        """ワークフロー中の循環参照検出テスト"""
        # 循環参照が検出された場合のワークフロー動作
        integration_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=False,
            failed=1,
            total=1,
            duration=0.5,
            details="Circular import detected in module chain",
            circular_imports=["moduleA -> moduleB -> moduleC -> moduleA"],
            connectivity_issues=[],
            initialization_errors=[]
        )
        
        with patch.object(self.auto_mode.integration_runner, 'run') as mock_integration:
            mock_integration.return_value = integration_result
            
            # ワークフロー実行
            result = self.auto_mode.execute_integration_test_phase()
            
            # 循環参照エラーが適切に処理される
            self.assertFalse(result['success'])
            self.assertIn('circular_import_detected', result['error_type'])
            self.assertEqual(len(result['circular_imports']), 1)
            self.assertIn("moduleA -> moduleB -> moduleC -> moduleA", result['circular_imports'])
    
    def test_integration_test_retry_mechanism(self):
        """統合テストリトライ機構のテスト"""
        # 初回は失敗、リトライで成功するシナリオ
        failed_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=False,
            failed=1,
            total=1,
            duration=0.3,
            details="Temporary initialization error",
            circular_imports=[],
            connectivity_issues=[],
            initialization_errors=["Service initialization failed"]
        )
        
        success_result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=1,
            duration=0.5,
            details="Integration tests passed on retry",
            circular_imports=[],
            connectivity_issues=[],
            initialization_errors=[]
        )
        
        with patch.object(self.auto_mode.integration_runner, 'run') as mock_integration:
            # 1回目は失敗、2回目は成功
            mock_integration.side_effect = [failed_result, success_result]
            
            # リトライ付きで実行
            result = self.auto_mode.execute_integration_test_with_retry(max_retries=1)
            
            # 最終的に成功
            self.assertTrue(result['success'])
            self.assertEqual(result['retry_count'], 1)
            
            # 2回実行された
            self.assertEqual(mock_integration.call_count, 2)


class TestAutoModeConfigIntegrationSettings(unittest.TestCase):
    """AutoModeConfig の統合テスト設定のテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "auto_config.json"
    
    def test_integration_test_settings_in_config(self):
        """設定に統合テスト設定が含まれること"""
        config = AutoModeConfig(self.config_file)
        
        # デフォルト統合テスト設定
        self.assertTrue(config.integration_tests_enabled)
        self.assertTrue(config.circular_import_detection)
        self.assertTrue(config.component_connectivity_test)
        self.assertTrue(config.initialization_test)
        self.assertEqual(config.integration_test_timeout, 30)
    
    def test_integration_test_config_save_load(self):
        """統合テスト設定の保存・読み込みテスト"""
        # 設定作成・変更
        config = AutoModeConfig(self.config_file)
        config.integration_tests_enabled = True
        config.circular_import_detection = False
        config.component_connectivity_test = True
        config.initialization_test = True
        config.integration_test_timeout = 45
        
        # 保存
        config.save()
        
        # 新しいインスタンスで読み込み
        config2 = AutoModeConfig(self.config_file)
        
        # 設定が正しく読み込まれる
        self.assertTrue(config2.integration_tests_enabled)
        self.assertFalse(config2.circular_import_detection)
        self.assertTrue(config2.component_connectivity_test)
        self.assertTrue(config2.initialization_test)
        self.assertEqual(config2.integration_test_timeout, 45)
    
    def test_config_validation(self):
        """設定値検証のテスト"""
        config = AutoModeConfig(self.config_file)
        
        # 無効な設定値の検証
        with self.assertRaises(ValueError):
            config.integration_test_timeout = -1
        
        with self.assertRaises(ValueError):
            config.integration_test_timeout = 0
        
        # 有効な設定値は受け入れられる
        config.integration_test_timeout = 60
        self.assertEqual(config.integration_test_timeout, 60)


if __name__ == "__main__":
    unittest.main()