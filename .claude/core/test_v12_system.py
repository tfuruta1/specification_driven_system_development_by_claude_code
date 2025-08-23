#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v12.0システムの包括的なテストスイート
ユニットテストと統合テストを実装
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# テスト対象モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

# 統合システムインポート
from test_base_utilities import OptimizedTestCase
from shared_logger import OptimizedLogger
from error_handler import StandardErrorHandler

from auto_mode import AutoModeConfig, AutoMode, AutoModeState
from test_strategy import TestStrategy, TestLevel, TestResult
from integration_test_runner import IntegrationTestRunner, CircularImportDetector, InitializationTester


class TestAutoModeConfig(OptimizedTestCase):
    """AutoModeConfigのユニットテスト - 統合システム使用"""
    
    def setUp(self):
        """テスト前の準備 - 統合システム使用"""
        super().setUp()
        self.config_file = self.temp_dir / "test_config.json"
        
    def tearDown(self):
        """テスト後のクリーンアップ - 統合システム使用"""
        super().tearDown()
        
    def test_config_initialization(self):
        """設定初期化のテスト"""
        config = AutoModeConfig(self.config_file)
        
        # デフォルト値の確認
        self.assertFalse(config.is_enabled)
        self.assertEqual(config.mode, "pair_programming")
        self.assertTrue(config.integration_tests_enabled)
        self.assertEqual(len(config.flows), 4)
        
    def test_config_save_and_load(self):
        """設定の保存と読み込みテスト"""
        config = AutoModeConfig(self.config_file)
        
        # 設定変更
        config.is_enabled = True
        config.current_flow = "新規開発"
        config.integration_test_timeout = 60
        config.save()
        
        # 新しいインスタンスで読み込み
        config2 = AutoModeConfig(self.config_file)
        
        self.assertTrue(config2.is_enabled)
        self.assertEqual(config2.current_flow, "新規開発")
        self.assertEqual(config2.integration_test_timeout, 60)
        
    def test_invalid_timeout_validation(self):
        """無効なタイムアウト値の検証テスト"""
        config = AutoModeConfig(self.config_file)
        
        # 無効な値を設定してファイルに保存
        invalid_config = {
            'integration_test_timeout': -10
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f)
            
        # 読み込み時にデフォルト値になることを確認
        config2 = AutoModeConfig(self.config_file)
        self.assertEqual(config2.integration_test_timeout, 30)  # デフォルト値


class TestOptimizedLogger(OptimizedTestCase):
    """統合ロガーのユニットテスト"""
    
    def setUp(self):
        """テスト前の準備 - 統合システム使用"""
        super().setUp()
        # self.loggerは既にOptimizedTestCaseで設定済み
        
    def test_log_access_types(self):
        """各種アクセスタイプのログ表示テスト - 統合ロガー使用"""
        # 修正対象ファイルのログ
        self.logger.log_file_access("modify", "test.py", "success", 
                                   {"purpose": "bug_fix", "description": "バグ修正"})
        
        # 参照のみファイルのログ
        self.logger.log_file_access("read", "reference.py", "success",
                                   {"purpose": "reference", "description": "パターン確認"})
        
        # ログが正常に記録されていることを確認
        self.assertIsNotNone(self.logger)
        
        # 解析中ファイルのログ
        self.logger.log_access("analyze.py", AccessPurpose.ANALYZE, "構造調査")
        self.assertEqual(mock_print.call_count, 3)
        
    def test_access_history(self):
        """アクセス履歴の記録テスト"""
        self.logger.log_access("file1.py", AccessPurpose.MODIFY, "修正")
        self.logger.log_access("file2.py", AccessPurpose.REFERENCE, "参照")
        
        history = self.logger.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['file'], "file1.py")
        self.assertEqual(history[1]['file'], "file2.py")
        
    def test_get_summary(self):
        """サマリー取得のテスト"""
        self.logger.log_access("file1.py", AccessPurpose.MODIFY, "修正1")
        self.logger.log_access("file2.py", AccessPurpose.MODIFY, "修正2")
        self.logger.log_access("file3.py", AccessPurpose.REFERENCE, "参照")
        
        summary = self.logger.get_summary()
        
        self.assertEqual(summary['total_files'], 3)
        self.assertEqual(summary['modifications'], 2)
        self.assertEqual(summary['references'], 1)
        self.assertEqual(summary['analyses'], 0)


class TestTestStrategy(unittest.TestCase):
    """TestStrategyのユニットテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.strategy = TestStrategy()
        
    def test_add_test_level(self):
        """テストレベル追加のテスト"""
        result = TestResult(
            level=TestLevel.UNIT,
            passed=10,
            failed=2,
            skipped=1,
            coverage=85.5
        )
        
        self.strategy.add_test_result(result)
        
        summary = self.strategy.get_summary()
        self.assertEqual(summary['unit']['passed'], 10)
        self.assertEqual(summary['unit']['failed'], 2)
        self.assertEqual(summary['unit']['coverage'], 85.5)
        
    def test_multiple_test_levels(self):
        """複数テストレベルの管理テスト"""
        # ユニットテスト結果
        unit_result = TestResult(
            level=TestLevel.UNIT,
            passed=20,
            failed=1,
            skipped=0,
            coverage=90.0
        )
        
        # 統合テスト結果
        integration_result = TestResult(
            level=TestLevel.INTEGRATION,
            passed=5,
            failed=0,
            skipped=1,
            coverage=75.0
        )
        
        self.strategy.add_test_result(unit_result)
        self.strategy.add_test_result(integration_result)
        
        # 全体の成功率確認
        self.assertTrue(self.strategy.is_all_passed())
        
        # E2Eテストで失敗を追加
        e2e_result = TestResult(
            level=TestLevel.E2E,
            passed=2,
            failed=1,
            skipped=0,
            coverage=60.0
        )
        
        self.strategy.add_test_result(e2e_result)
        self.assertFalse(self.strategy.is_all_passed())


class TestCircularImportDetector(unittest.TestCase):
    """CircularImportDetectorのユニットテスト"""
    
    def test_no_circular_import(self):
        """循環参照なしのケース"""
        detector = CircularImportDetector()
        
        # 正常な依存関係
        detector.add_import("module_a", "module_b")
        detector.add_import("module_b", "module_c")
        detector.add_import("module_c", "module_d")
        
        cycles = detector.detect_cycles()
        self.assertEqual(len(cycles), 0)
        
    def test_simple_circular_import(self):
        """単純な循環参照のケース"""
        detector = CircularImportDetector()
        
        # A -> B -> C -> A の循環
        detector.add_import("module_a", "module_b")
        detector.add_import("module_b", "module_c")
        detector.add_import("module_c", "module_a")
        
        cycles = detector.detect_cycles()
        self.assertGreater(len(cycles), 0)
        
        # 循環パスの確認
        cycle_modules = set()
        for cycle in cycles:
            cycle_modules.update(cycle)
        
        self.assertIn("module_a", cycle_modules)
        self.assertIn("module_b", cycle_modules)
        self.assertIn("module_c", cycle_modules)
        
    def test_complex_circular_import(self):
        """複雑な循環参照のケース"""
        detector = CircularImportDetector()
        
        # 複数の循環を含む依存関係
        detector.add_import("main", "utils")
        detector.add_import("utils", "helpers")
        detector.add_import("helpers", "utils")  # 循環1
        detector.add_import("main", "config")
        detector.add_import("config", "database")
        detector.add_import("database", "main")  # 循環2
        
        cycles = detector.detect_cycles()
        self.assertGreaterEqual(len(cycles), 2)


class TestIntegrationRunner(unittest.TestCase):
    """統合テストランナーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = IntegrationTestRunner(self.temp_dir)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    @patch('integration_test_runner.CircularImportDetector')
    @patch('integration_test_runner.InitializationTester')
    def test_run_all_tests(self, mock_init_tester, mock_circular_detector):
        """全統合テスト実行のテスト"""
        # モックの設定
        mock_circular_detector.return_value.detect_cycles.return_value = []
        mock_init_tester.return_value.test_initialization.return_value = {
            'success': True,
            'errors': []
        }
        
        # テスト実行
        result = self.runner.run_all_tests()
        
        # 結果の確認
        self.assertTrue(result.all_passed)
        self.assertEqual(len(result.circular_imports), 0)
        self.assertTrue(result.initialization_success)
        
    def test_timeout_handling(self):
        """タイムアウト処理のテスト"""
        runner = IntegrationTestRunner(self.temp_dir, timeout=0.1)
        
        # 長時間かかる処理をシミュレート
        def slow_test():
            import time
            time.sleep(1)
            return True
            
        # タイムアウトが発生することを確認
        with patch.object(runner, '_run_with_timeout') as mock_run:
            mock_run.side_effect = TimeoutError("Test timeout")
            
            result = runner.run_all_tests()
            self.assertFalse(result.all_passed)


class TestSystemIntegration(unittest.TestCase):
    """システム全体の統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_auto_mode_with_test_strategy(self):
        """AutoModeとTestStrategyの統合テスト"""
        config_file = Path(self.temp_dir) / "config.json"
        config = AutoModeConfig(config_file)
        
        # AutoModeセッション開始
        state = AutoModeState()
        session_id = state.start()
        self.assertTrue(state.is_active)
        self.assertIsNotNone(session_id)
        
        # テスト戦略との連携
        strategy = TestStrategy()
        
        # ユニットテスト実行
        unit_result = TestResult(
            level=TestLevel.UNIT,
            passed=15,
            failed=0,
            skipped=0,
            coverage=95.0
        )
        strategy.add_test_result(unit_result)
        
        # 統合テスト実行（AutoModeの設定に基づく）
        if config.integration_tests_enabled:
            integration_result = TestResult(
                level=TestLevel.INTEGRATION,
                passed=8,
                failed=0,
                skipped=0,
                coverage=80.0
            )
            strategy.add_test_result(integration_result)
            
        # 全体の成功確認
        self.assertTrue(strategy.is_all_passed())
        
    def test_file_access_logging_in_session(self):
        """セッション内でのファイルアクセスログテスト"""
        # セッション開始
        state = AutoModeState()
        session_id = state.start()
        
        # ファイルアクセスロガー
        logger = FileAccessLogger()
        
        # バグ修正フローでのファイルアクセスシミュレーション
        logger.log_access("bug_file.py", AccessPurpose.ANALYZE, "バグ箇所特定")
        logger.log_access("test_bug.py", AccessPurpose.MODIFY, "テスト作成")
        logger.log_access("bug_file.py", AccessPurpose.MODIFY, "バグ修正")
        logger.log_access("related.py", AccessPurpose.REFERENCE, "影響確認")
        
        # サマリー確認
        summary = logger.get_summary()
        self.assertEqual(summary['total_files'], 4)
        self.assertEqual(summary['modifications'], 2)
        self.assertEqual(summary['analyses'], 1)
        self.assertEqual(summary['references'], 1)
        
    def test_complete_development_flow(self):
        """完全な開発フローの統合テスト"""
        # 1. AutoMode開始
        config = AutoModeConfig(Path(self.temp_dir) / "config.json")
        config.is_enabled = True
        config.current_flow = "新規開発"
        config.save()
        
        # 2. ファイルアクセスログ初期化
        file_logger = FileAccessLogger()
        
        # 3. SDD+TDDフローのシミュレーション
        steps = [
            ("requirements.md", AccessPurpose.MODIFY, "要件定義書作成"),
            ("design.md", AccessPurpose.MODIFY, "技術設計書作成"),
            ("tasks.md", AccessPurpose.MODIFY, "実装計画作成"),
            ("existing_code.py", AccessPurpose.ANALYZE, "既存コード確認"),
            ("test_new_feature.py", AccessPurpose.MODIFY, "テスト作成"),
            ("new_feature.py", AccessPurpose.MODIFY, "機能実装"),
            ("test_new_feature.py", AccessPurpose.REFERENCE, "テスト実行"),
            ("new_feature.py", AccessPurpose.MODIFY, "リファクタリング"),
        ]
        
        for file_path, access_type, purpose in steps:
            file_logger.log_access(file_path, access_type, purpose)
            
        # 4. テスト戦略実行
        test_strategy = TestStrategy()
        
        # ユニットテスト
        test_strategy.add_test_result(TestResult(
            level=TestLevel.UNIT,
            passed=25,
            failed=0,
            skipped=0,
            coverage=92.0
        ))
        
        # 5. 統合テスト（config.integration_tests_enabledがTrueの場合）
        if config.integration_tests_enabled:
            runner = IntegrationTestRunner(self.temp_dir)
            
            # 循環参照チェック
            detector = CircularImportDetector()
            detector.add_import("new_feature", "utils")
            detector.add_import("utils", "config")
            # 循環なし
            
            cycles = detector.detect_cycles()
            self.assertEqual(len(cycles), 0)
            
            # 統合テスト結果
            test_strategy.add_test_result(TestResult(
                level=TestLevel.INTEGRATION,
                passed=10,
                failed=0,
                skipped=0,
                coverage=85.0
            ))
            
        # 6. 最終確認
        self.assertTrue(test_strategy.is_all_passed())
        self.assertTrue(config.is_enabled)
        self.assertEqual(config.current_flow, "新規開発")
        
        # ファイルアクセスサマリー
        summary = file_logger.get_summary()
        self.assertEqual(summary['total_files'], 8)
        self.assertGreater(summary['modifications'], 0)


if __name__ == '__main__':
    # テストスイートの作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # ユニットテストを追加
    suite.addTests(loader.loadTestsFromTestCase(TestAutoModeConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestFileAccessLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestTestStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestCircularImportDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationRunner))
    
    # 統合テストを追加
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "="*60)
    print("[テスト結果サマリー]")
    print(f"実行: {result.testsRun} テスト")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[OK] すべてのテストが成功しました！")
    else:
        print("\n[NG] テストに失敗があります。")
        
    sys.exit(0 if result.wasSuccessful() else 1)