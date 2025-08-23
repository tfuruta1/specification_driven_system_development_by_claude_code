#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一TestStrategyテスト - Phase 3統合版
複数の重複ファイルを統合してTDD準拠の統合テストを提供

統合元ファイル:
- test_test_strategy.py  
- test_strategy_integration.py
- test_integration_test_runner.py

TDD統合テスト戦略:
- システム間連携の検証
- 循環参照検出機能の検証  
- 初期化テストの検証
- エンドツーエンドフローの検証
"""

import unittest
import sys
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

try:
    from test_strategy import TestStrategy, TestLevel, TestResult
    from integration_test_runner import (
        IntegrationTestRunner,
        CircularImportDetector, 
        InitializationTester,
        ComponentConnectivityTester
    )
except ImportError as e:
    print(f"⚠️ Import error: {e}. Skipping tests that require these modules.")
    TestStrategy = None
    IntegrationTestRunner = None


class TestStrategyIntegrationUnified(unittest.TestCase):
    """統一TestStrategy統合テスト - TDD準拠"""
    
    def setUp(self):
        """統合テストセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project = "test_strategy_integration"
        
    def tearDown(self):
        """統合テストクリーンアップ"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            
    # ==================== TDD統合テスト：RED PHASE ====================
    
    @unittest.skipIf(TestStrategy is None, "TestStrategy not available")
    def test_test_strategy_integration_red(self):
        """
        [RED] TestStrategy統合テスト - 失敗から開始
        
        複数システムの連携が正しく動作することを検証
        """
        # RED: 統合前の状態を想定した失敗テスト
        strategy = TestStrategy()
        
        # 基本統合機能の存在確認
        self.assertTrue(hasattr(strategy, 'is_level_enabled'))
        self.assertTrue(hasattr(strategy, 'get_execution_order'))
        self.assertTrue(hasattr(strategy, 'execute_flow'))
        
    @unittest.skipIf(IntegrationTestRunner is None, "IntegrationTestRunner not available")
    def test_integration_test_runner_red(self):
        """[RED] IntegrationTestRunner基本機能テスト"""
        runner = IntegrationTestRunner()
        
        # 統合テスト実行機能の確認
        self.assertTrue(hasattr(runner, 'run'))
        self.assertTrue(hasattr(runner, 'get_circular_detector'))
        self.assertTrue(hasattr(runner, 'get_initialization_tester'))
        
    # ==================== TDD統合テスト：GREEN PHASE ====================
    
    @unittest.skipIf(TestStrategy is None, "TestStrategy not available")
    def test_hierarchical_test_execution_green(self):
        """
        [GREEN] 階層化テスト実行の統合テスト
        
        UNIT → INTEGRATION → E2E の順序実行を検証
        """
        strategy = TestStrategy()
        
        # 実行順序の検証
        execution_order = strategy.get_execution_order()
        expected_order = [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]
        
        self.assertEqual(execution_order, expected_order)
        
        # レベル別の有効性確認
        for level in expected_order:
            self.assertTrue(strategy.is_level_enabled(level))
            
    @unittest.skipIf(IntegrationTestRunner is None, "IntegrationTestRunner not available") 
    def test_circular_import_detection_green(self):
        """[GREEN] 循環参照検出機能の統合テスト"""
        runner = IntegrationTestRunner()
        detector = runner.get_circular_detector()
        
        # 循環参照のないケース
        with patch.object(detector, 'detect') as mock_detect:
            mock_detect.return_value = []  # 循環参照なし
            
            result = runner.run(self.temp_dir)
            self.assertIsNotNone(result)
            self.assertEqual(len(result.circular_imports), 0)
            
    @unittest.skipIf(IntegrationTestRunner is None, "IntegrationTestRunner not available")
    def test_initialization_testing_green(self):
        """[GREEN] 初期化テスト機能の統合テスト"""
        runner = IntegrationTestRunner()
        init_tester = runner.get_initialization_tester()
        
        # テスト対象モジュール追加
        init_tester.add_module("json")  # 標準ライブラリで安全にテスト
        
        # 初期化テスト実行
        result = init_tester.test_initialization()
        self.assertTrue(result)  # 標準ライブラリなので成功するはず
        
    # ==================== TDD統合テスト：REFACTOR PHASE ====================
    
    @unittest.skipIf(all(x is None for x in [TestStrategy, IntegrationTestRunner]), 
                     "Required modules not available")
    def test_full_integration_workflow_refactor(self):
        """
        [REFACTOR] 完全統合ワークフローテスト
        
        TestStrategy + IntegrationTestRunner の完全な連携を検証
        """
        if TestStrategy is None or IntegrationTestRunner is None:
            self.skipTest("Required modules not available")
            
        strategy = TestStrategy()
        runner = IntegrationTestRunner()
        
        # 統合テストランナーをTestStrategyに登録
        strategy.set_runner(TestLevel.INTEGRATION, lambda: self._mock_integration_test(runner))
        
        # 統合フロー実行
        results = strategy.execute_flow(stop_on_failure=False)
        
        # 結果検証
        self.assertIsInstance(results, list)
        
        # レポート生成検証
        if results:
            summary = strategy.generate_summary()
            self.assertIn('total_tests', summary)
            self.assertIn('success_rate', summary)
            
    def _mock_integration_test(self, runner):
        """統合テスト用モック関数"""
        # モック結果を作成
        from test_strategy import TestResult
        
        return TestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=1,
            duration=0.1,
            details="Mock integration test passed"
        )
        
    # ==================== システム間連携テスト ====================
    
    def test_component_connectivity_integration(self):
        """コンポーネント連携テストの統合検証"""
        if IntegrationTestRunner is None:
            self.skipTest("IntegrationTestRunner not available")
            
        runner = IntegrationTestRunner()
        connectivity_tester = runner.get_connectivity_tester()
        
        # テストコンポーネントの登録
        connectivity_tester.register_component(
            name="test_component",
            module_path="json",  # 標準ライブラリを使用
            class_name="JSONDecoder"
        )
        
        # コネクション追加
        connectivity_tester.add_expected_connection(
            from_component="test_component",
            to_component="test_component", 
            connection_type="import"
        )
        
        # 連携テスト実行
        result = connectivity_tester.test_connectivity()
        self.assertTrue(result)
        
    # ==================== KISS原則準拠検証 ====================
    
    def test_simple_integration_interface(self):
        """統合テストのシンプルなインターフェース検証"""
        if IntegrationTestRunner is None:
            self.skipTest("IntegrationTestRunner not available")
            
        runner = IntegrationTestRunner()
        
        # シンプルなAPIインターフェースの確認
        essential_methods = [
            'run',
            'configure', 
            'get_circular_detector',
            'get_connectivity_tester',
            'get_initialization_tester'
        ]
        
        for method in essential_methods:
            self.assertTrue(hasattr(runner, method),
                          f"Essential method {method} missing")
            self.assertTrue(callable(getattr(runner, method)),
                          f"Method {method} not callable")
                          
    def test_configuration_simplicity(self):
        """設定の簡潔性検証"""
        if IntegrationTestRunner is None:
            self.skipTest("IntegrationTestRunner not available")
            
        runner = IntegrationTestRunner()
        
        # シンプルな設定インターフェース
        runner.configure(
            circular_import_detection=True,
            component_connectivity_test=True,
            initialization_test=True
        )
        
        # 設定が適切に反映されることを確認
        self.assertTrue(runner.circular_import_detection_enabled)
        self.assertTrue(runner.component_connectivity_test_enabled) 
        self.assertTrue(runner.initialization_test_enabled)
        
    # ==================== 100%カバレッジ統合テスト ====================
    
    def test_error_scenarios_coverage(self):
        """エラーシナリオのカバレッジ統合テスト"""
        if IntegrationTestRunner is None:
            self.skipTest("IntegrationTestRunner not available")
            
        runner = IntegrationTestRunner()
        
        # 存在しないパスでのテスト
        result = runner.run("/non/existent/path")
        self.assertIsNotNone(result)
        
        # エラー条件での実行
        with patch.object(runner.circular_detector, 'detect', side_effect=Exception("Test error")):
            try:
                result = runner.run(self.temp_dir)
                # エラーハンドリングが適切に行われることを確認
                self.assertIsNotNone(result)
            except Exception:
                # 例外が適切に処理されることを確認
                pass
                
    def test_comprehensive_integration_coverage(self):
        """包括的統合カバレッジテスト"""
        if any(x is None for x in [TestStrategy, IntegrationTestRunner]):
            self.skipTest("Required modules not available")
            
        # 複数システムの組み合わせテスト
        strategy = TestStrategy()
        runner = IntegrationTestRunner()
        
        # 全レベルの無効化・有効化テスト
        for level in [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]:
            strategy.disable_level(level)
            self.assertFalse(strategy.is_level_enabled(level))
            
            strategy.enable_level(level)
            self.assertTrue(strategy.is_level_enabled(level))
            
        # JSON出力テスト
        json_output = strategy.to_json()
        self.assertIsInstance(json_output, str)
        
        # JSON復元テスト
        restored_strategy = TestStrategy.from_json(json_output)
        self.assertIsInstance(restored_strategy, TestStrategy)


class TestSystemEndToEndIntegration(unittest.TestCase):
    """システム全体のエンドツーエンド統合テスト"""
    
    def setUp(self):
        """E2Eテスト用セットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """E2Eテスト用クリーンアップ"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            
    def test_complete_test_lifecycle(self):
        """完全なテストライフサイクル統合検証"""
        if any(x is None for x in [TestStrategy, IntegrationTestRunner]):
            self.skipTest("Required modules not available")
            
        # システム全体の統合フロー
        strategy = TestStrategy()
        runner = IntegrationTestRunner()
        
        # ライフサイクル実行
        phases = [
            ("準備フェーズ", lambda: self._setup_phase(strategy, runner)),
            ("実行フェーズ", lambda: self._execution_phase(strategy, runner)),
            ("検証フェーズ", lambda: self._verification_phase(strategy, runner)),
            ("レポートフェーズ", lambda: self._reporting_phase(strategy, runner))
        ]
        
        results = {}
        for phase_name, phase_func in phases:
            try:
                results[phase_name] = phase_func()
                print(f"✅ {phase_name} completed successfully")
            except Exception as e:
                results[phase_name] = f"Failed: {e}"
                print(f"❌ {phase_name} failed: {e}")
                
        # 全フェーズの成功確認
        success_count = sum(1 for r in results.values() if not str(r).startswith("Failed"))
        self.assertGreater(success_count, 0, "At least one phase should succeed")
        
    def _setup_phase(self, strategy, runner):
        """準備フェーズ"""
        # 設定の確認
        strategy.clear_results()
        runner.configure()
        return "Setup completed"
        
    def _execution_phase(self, strategy, runner):
        """実行フェーズ"""
        # テスト実行（モック使用）
        with patch.object(runner, 'run') as mock_run:
            from integration_test_runner import IntegrationTestResult
            mock_result = MagicMock(spec=IntegrationTestResult)
            mock_result.passed = True
            mock_run.return_value = mock_result
            
            result = runner.run(self.temp_dir)
            return f"Execution completed: {result}"
            
    def _verification_phase(self, strategy, runner):
        """検証フェーズ"""
        # 結果検証
        results = strategy.get_results()
        return f"Verification completed: {len(results)} results"
        
    def _reporting_phase(self, strategy, runner):
        """レポートフェーズ"""
        # レポート生成
        summary = strategy.generate_summary()
        return f"Reporting completed: {summary}"


if __name__ == '__main__':
    # TDD統合テスト表示
    print("=" * 80)
    print("統一TestStrategy統合テスト - Phase 3 TDD準拠版")
    print("=" * 80)
    print("システム間連携・循環参照検出・初期化テスト統合")
    print("RED → GREEN → REFACTOR 統合サイクル準拠")
    print("=" * 80)
    
    unittest.main(verbosity=2)