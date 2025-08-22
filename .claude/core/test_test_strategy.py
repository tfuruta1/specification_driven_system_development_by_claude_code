"""
テスト戦略管理モジュールのテスト

テスト戦略の階層化（ユニット → 統合 → E2E）とテスト実行フロー管理をテスト
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# テスト対象モジュールのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# テスト対象をインポート（まだ存在しないが、TDDなので先にテストを定義）
try:
    from test_strategy import TestStrategy, TestLevel, TestResult, TestExecutionError
except ImportError:
    # TDDのRed phase - モジュールがまだ存在しない
    pass


class TestTestStrategy(unittest.TestCase):
    """テスト戦略管理のテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.strategy = TestStrategy()
    
    def test_test_levels_defined(self):
        """テストレベルが正しく定義されていること"""
        # TestLevelは階層順序を持つ
        self.assertEqual(TestLevel.UNIT.value, 1)
        self.assertEqual(TestLevel.INTEGRATION.value, 2)
        self.assertEqual(TestLevel.E2E.value, 3)
        
        # 階層順序でソート可能
        levels = [TestLevel.E2E, TestLevel.UNIT, TestLevel.INTEGRATION]
        sorted_levels = sorted(levels, key=lambda x: x.value)
        expected = [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]
        self.assertEqual(sorted_levels, expected)
    
    def test_test_strategy_initialization(self):
        """テスト戦略が正しく初期化されること"""
        strategy = TestStrategy()
        
        # デフォルトで全レベルが有効
        self.assertTrue(strategy.is_level_enabled(TestLevel.UNIT))
        self.assertTrue(strategy.is_level_enabled(TestLevel.INTEGRATION))
        self.assertTrue(strategy.is_level_enabled(TestLevel.E2E))
        
        # 実行順序が正しく設定されている
        execution_order = strategy.get_execution_order()
        expected_order = [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]
        self.assertEqual(execution_order, expected_order)
    
    def test_test_strategy_configuration(self):
        """テスト戦略の設定変更ができること"""
        strategy = TestStrategy()
        
        # 特定レベルを無効化
        strategy.disable_level(TestLevel.E2E)
        self.assertFalse(strategy.is_level_enabled(TestLevel.E2E))
        self.assertTrue(strategy.is_level_enabled(TestLevel.UNIT))
        
        # 実行順序が更新される
        execution_order = strategy.get_execution_order()
        self.assertNotIn(TestLevel.E2E, execution_order)
        
        # 再有効化
        strategy.enable_level(TestLevel.E2E)
        self.assertTrue(strategy.is_level_enabled(TestLevel.E2E))
    
    def test_test_result_tracking(self):
        """テスト結果の追跡ができること"""
        strategy = TestStrategy()
        
        # テスト結果を記録
        unit_result = TestResult(
            level=TestLevel.UNIT,
            passed=True,
            failed=0,
            total=10,
            duration=1.5,
            details="All unit tests passed"
        )
        strategy.record_result(unit_result)
        
        # 結果を取得できる
        results = strategy.get_results()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].level, TestLevel.UNIT)
        self.assertTrue(results[0].passed)
        
        # レベル別結果取得
        unit_results = strategy.get_results_for_level(TestLevel.UNIT)
        self.assertEqual(len(unit_results), 1)
        
        integration_results = strategy.get_results_for_level(TestLevel.INTEGRATION)
        self.assertEqual(len(integration_results), 0)
    
    def test_test_execution_flow(self):
        """テスト実行フローが正しく動作すること"""
        strategy = TestStrategy()
        
        # モックランナーを設定
        mock_unit_runner = Mock(return_value=TestResult(TestLevel.UNIT, True, 0, 5, 1.0))
        mock_integration_runner = Mock(return_value=TestResult(TestLevel.INTEGRATION, True, 0, 3, 2.0))
        
        strategy.set_runner(TestLevel.UNIT, mock_unit_runner)
        strategy.set_runner(TestLevel.INTEGRATION, mock_integration_runner)
        
        # フロー実行
        results = strategy.execute_flow()
        
        # 両方のテストが実行された
        mock_unit_runner.assert_called_once()
        mock_integration_runner.assert_called_once()
        
        # 結果が正しく記録された
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.passed for r in results))
    
    def test_test_execution_failure_handling(self):
        """テスト失敗時の処理が正しいこと"""
        strategy = TestStrategy()
        
        # ユニットテストが失敗
        failed_unit_result = TestResult(TestLevel.UNIT, False, 2, 5, 1.0, "2 tests failed")
        mock_unit_runner = Mock(return_value=failed_unit_result)
        mock_integration_runner = Mock()
        
        strategy.set_runner(TestLevel.UNIT, mock_unit_runner)
        strategy.set_runner(TestLevel.INTEGRATION, mock_integration_runner)
        
        # フロー実行（失敗時は後続テストをスキップ）
        results = strategy.execute_flow(stop_on_failure=True)
        
        # ユニットテストのみ実行された
        mock_unit_runner.assert_called_once()
        mock_integration_runner.assert_not_called()
        
        # 失敗結果が記録された
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].passed)
    
    def test_test_execution_error_handling(self):
        """テスト実行エラーの処理が正しいこと"""
        strategy = TestStrategy()
        
        # テスト実行中にエラーが発生
        mock_unit_runner = Mock(side_effect=TestExecutionError("Circular import detected"))
        strategy.set_runner(TestLevel.UNIT, mock_unit_runner)
        
        # エラーが適切にキャッチされる
        with self.assertRaises(TestExecutionError) as context:
            strategy.execute_flow()
        
        self.assertIn("Circular import detected", str(context.exception))
    
    def test_test_strategy_reporting(self):
        """テスト戦略のレポート生成ができること"""
        strategy = TestStrategy()
        
        # テスト結果を複数記録
        results = [
            TestResult(TestLevel.UNIT, True, 0, 10, 1.5),
            TestResult(TestLevel.INTEGRATION, False, 1, 5, 2.0),
            TestResult(TestLevel.E2E, True, 0, 3, 5.0)
        ]
        
        for result in results:
            strategy.record_result(result)
        
        # サマリーレポート生成
        summary = strategy.generate_summary()
        
        self.assertIn("total_tests", summary)
        self.assertIn("passed_tests", summary)
        self.assertIn("failed_tests", summary)
        self.assertIn("total_duration", summary)
        self.assertIn("success_rate", summary)
        
        # 期待値確認
        self.assertEqual(summary["total_tests"], 18)  # 10 + 5 + 3
        self.assertEqual(summary["failed_tests"], 1)
        self.assertEqual(summary["total_duration"], 8.5)  # 1.5 + 2.0 + 5.0
    
    def test_circular_import_detection(self):
        """循環参照検出機能のテスト"""
        strategy = TestStrategy()
        
        # 循環参照を模擬するモック
        mock_runner = Mock()
        mock_runner.side_effect = TestExecutionError("Circular import: moduleA -> moduleB -> moduleA")
        
        strategy.set_runner(TestLevel.INTEGRATION, mock_runner)
        
        # 循環参照エラーが検出される
        with self.assertRaises(TestExecutionError) as context:
            strategy.execute_single_level(TestLevel.INTEGRATION)
        
        error_message = str(context.exception)
        self.assertIn("Circular import", error_message)
        self.assertIn("moduleA -> moduleB -> moduleA", error_message)


if __name__ == "__main__":
    unittest.main()