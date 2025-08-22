#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v12.0システムの簡単な動作確認テスト
"""

import unittest
import json
import sys
import tempfile
import shutil
from pathlib import Path

# テスト対象モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))


class TestV12BasicFunctionality(unittest.TestCase):
    """v12.0基本機能の動作確認テスト"""
    
    def test_auto_mode_import(self):
        """auto_modeモジュールのインポートテスト"""
        try:
            from auto_mode import AutoModeConfig, AutoMode, AutoModeState
            self.assertTrue(True, "auto_modeモジュールのインポート成功")
        except ImportError as e:
            self.fail(f"auto_modeモジュールのインポート失敗: {e}")
            
    def test_file_access_logger_import(self):
        """file_access_loggerモジュールのインポートテスト"""
        try:
            from file_access_logger import FileAccessLogger, AccessPurpose
            self.assertTrue(True, "file_access_loggerモジュールのインポート成功")
        except ImportError as e:
            self.fail(f"file_access_loggerモジュールのインポート失敗: {e}")
            
    def test_test_strategy_import(self):
        """test_strategyモジュールのインポートテスト"""
        try:
            from test_strategy import TestStrategy, TestLevel, TestResult
            self.assertTrue(True, "test_strategyモジュールのインポート成功")
        except ImportError as e:
            self.fail(f"test_strategyモジュールのインポート失敗: {e}")
            
    def test_integration_test_runner_import(self):
        """integration_test_runnerモジュールのインポートテスト"""
        try:
            from integration_test_runner import IntegrationTestRunner, CircularImportDetector
            self.assertTrue(True, "integration_test_runnerモジュールのインポート成功")
        except ImportError as e:
            self.fail(f"integration_test_runnerモジュールのインポート失敗: {e}")
            
    def test_auto_mode_config_basic(self):
        """AutoModeConfigの基本動作テスト"""
        from auto_mode import AutoModeConfig
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            config = AutoModeConfig(config_file)
            
            # デフォルト値の確認
            self.assertFalse(config.is_enabled)
            self.assertEqual(config.mode, "pair_programming")
            self.assertTrue(config.integration_tests_enabled)
            
            # 値の変更と保存
            config.is_enabled = True
            config.current_flow = "新規開発"
            config.save()
            
            # ファイルが作成されたか確認
            self.assertTrue(config_file.exists())
            
            # 新しいインスタンスで読み込み
            config2 = AutoModeConfig(config_file)
            self.assertTrue(config2.is_enabled)
            self.assertEqual(config2.current_flow, "新規開発")
            
    def test_auto_mode_state_basic(self):
        """AutoModeStateの基本動作テスト"""
        from auto_mode import AutoModeState
        
        state = AutoModeState()
        
        # 初期状態の確認
        self.assertFalse(state.is_active)
        self.assertIsNone(state.current_session)
        
        # セッション開始
        session_id = state.start()
        self.assertTrue(state.is_active)
        self.assertIsNotNone(session_id)
        self.assertEqual(state.session_count, 1)
        
        # 状態取得
        status = state.get_status()
        self.assertTrue(status['active'])
        self.assertEqual(status['session_id'], session_id)
        
        # セッション停止
        state.stop()
        self.assertFalse(state.is_active)
        self.assertIsNone(state.current_session)
        
    def test_file_access_logger_basic(self):
        """FileAccessLoggerの基本動作テスト"""
        from file_access_logger import FileAccessLogger, AccessPurpose
        
        logger = FileAccessLogger()
        
        # ログ記録（メソッド名を確認）
        try:
            # log_file_accessメソッドを試す
            logger.log_file_access("test.py", AccessPurpose.MODIFY, "テスト修正")
            self.assertTrue(True, "log_file_accessメソッド呼び出し成功")
        except AttributeError:
            try:
                # logメソッドを試す
                logger.log("test.py", AccessPurpose.MODIFY, "テスト修正")
                self.assertTrue(True, "logメソッド呼び出し成功")
            except AttributeError as e:
                # 実際のメソッド名を調べる
                methods = [m for m in dir(logger) if not m.startswith('_')]
                self.fail(f"適切なログメソッドが見つかりません。利用可能なメソッド: {methods}")
                
    def test_test_strategy_basic(self):
        """TestStrategyの基本動作テスト"""
        from test_strategy import TestStrategy, TestLevel, TestResult
        
        strategy = TestStrategy()
        
        # TestResultの作成（正しいパラメータで）
        try:
            result = TestResult(
                level=TestLevel.UNIT,
                passed=True,
                failed=0,
                total=10,
                duration=1.5,
                details="ユニットテスト成功"
            )
            self.assertTrue(True, "TestResult作成成功")
            self.assertEqual(result.success_rate, 100.0)
        except TypeError as e:
            # パラメータが異なる場合
            self.fail(f"TestResultのパラメータエラー: {e}")
            
    def test_circular_import_detector_basic(self):
        """CircularImportDetectorの基本動作テスト"""
        from integration_test_runner import CircularImportDetector
        
        detector = CircularImportDetector()
        
        # メソッド名を確認
        methods = [m for m in dir(detector) if not m.startswith('_')]
        self.assertIn('detect', methods, "detectメソッドが存在")
        
        # 循環検出のテスト
        cycles = detector.detect()
        self.assertIsInstance(cycles, list, "detectはリストを返す")
        
    def test_integration_components(self):
        """v12.0コンポーネントの統合テスト"""
        from auto_mode import AutoModeConfig, AutoModeState
        from file_access_logger import FileAccessLogger, AccessPurpose
        
        # 1. AutoMode設定
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AutoModeConfig(Path(temp_dir) / "config.json")
            config.is_enabled = True
            config.current_flow = "新規開発"
            
            # 2. セッション開始
            state = AutoModeState()
            session_id = state.start()
            
            # 3. ファイルアクセスログ
            logger = FileAccessLogger()
            
            # 統合動作確認
            self.assertTrue(config.is_enabled)
            self.assertTrue(state.is_active)
            self.assertIsNotNone(session_id)
            
            print(f"\n[統合テスト成功]")
            print(f"- AutoMode設定: 有効")
            print(f"- 開発フロー: {config.current_flow}")
            print(f"- セッションID: {session_id}")
            print(f"- 統合テスト: {config.integration_tests_enabled}")


if __name__ == '__main__':
    # テスト実行
    unittest.main(verbosity=2)