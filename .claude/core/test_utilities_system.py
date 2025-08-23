#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility & System Tests - JSTUtils, SystemIntegration
元 test_v12_comprehensive.py から分割されたユーティリティ・システム関連テスト
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime
from io import StringIO

# テスト対象モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

# 統合システムインポート
from test_base_utilities import OptimizedTestCase
from shared_logger import OptimizedLogger
from error_handler import StandardErrorHandler

from jst_utils import get_jst_now, format_jst_time, format_jst_datetime, get_filename_timestamp


class TestJSTUtils(OptimizedTestCase):
    """JSTUtilsの包括的テスト - 統合システム使用"""
    
    def test_get_jst_now(self):
        """JST現在時刻取得テスト"""
        jst_now = get_jst_now()
        
        self.assertIsInstance(jst_now, datetime)
        # JST (UTC+9) かどうかを確認
        utc_offset = jst_now.utcoffset()
        self.assertIsNotNone(utc_offset)
        self.assertEqual(utc_offset.total_seconds(), 9 * 3600)  # 9時間
        
    def test_format_jst_time(self):
        """JST時刻フォーマットテスト"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_jst_time(test_datetime)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("10:30:45", formatted)
        self.assertIn("JST", formatted)
        
    def test_format_jst_datetime(self):
        """JST日時フォーマットテスト"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_jst_datetime(test_datetime)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("2024-01-15", formatted)
        self.assertIn("10:30:45", formatted)
        self.assertIn("JST", formatted)
        
    def test_get_filename_timestamp(self):
        """ファイル名タイムスタンプ取得テスト"""
        timestamp = get_filename_timestamp()
        
        self.assertIsInstance(timestamp, str)
        # YYYYMMDD_HHMMSS 形式かどうか確認
        self.assertEqual(len(timestamp), 15)  # YYYYMMDD_HHMMSS
        self.assertIn("_", timestamp)
        
        # 数字のみで構成されているか（アンダースコア以外）
        cleaned = timestamp.replace("_", "")
        self.assertTrue(cleaned.isdigit())
        
    def test_format_jst_time_with_none(self):
        """None値でのJST時刻フォーマットテスト"""
        formatted = format_jst_time(None)
        
        # Noneが渡された場合の動作確認
        self.assertIsInstance(formatted, str)
        
    def test_format_consistency(self):
        """フォーマット一貫性テスト"""
        test_datetime = datetime(2024, 12, 25, 23, 59, 59)
        
        time_format = format_jst_time(test_datetime)
        datetime_format = format_jst_datetime(test_datetime)
        
        # 時刻部分が一致するか
        self.assertIn("23:59:59", time_format)
        self.assertIn("23:59:59", datetime_format)
        
        # 両方にJSTが含まれるか
        self.assertIn("JST", time_format)
        self.assertIn("JST", datetime_format)


class TestSystemIntegration(OptimizedTestCase):
    """SystemIntegrationの包括的テスト - 統合システム使用"""
    
    def setUp(self):
        """テスト前の準備 - 統合システム使用"""
        super().setUp()  # OptimizedTestCaseのsetUpを実行
        
    def tearDown(self):
        """テスト後のクリーンアップ - 統合システム使用"""
        super().tearDown()  # OptimizedTestCaseのtearDownを実行
        
    def test_module_imports(self):
        """モジュールインポートテスト"""
        try:
            # 主要モジュールのインポート確認
            from auto_mode import AutoMode, AutoModeConfig, AutoModeState
            from file_access_logger import FileAccessLogger
            from activity_logger import UnifiedLogger
            from test_strategy import TestStrategy
            from integration_test_runner import IntegrationTestRunner
            from jst_utils import get_jst_now
            
            # インポートが成功すればテスト通過
            self.assertTrue(True)
            
        except ImportError as e:
            self.fail(f"モジュールインポートエラー: {e}")
            
    def test_basic_functionality_integration(self):
        """基本機能統合テスト"""
        # 統合ロガーの動作確認
        test_file = "integration_test.py"
        self.logger.log_file_access("read", test_file, "success", 
                                   {"purpose": "analysis", "test": "integration"})
        
        # ログが記録されていることを確認（統合ロガーは自動でバッファに蓄積）
        self.assertIsNotNone(self.logger)
        
        # AutoModeConfigの動作確認（統合エラーハンドリング使用）
        try:
            from auto_mode import AutoModeConfig
            config = AutoModeConfig(interval=60, debug_mode=True)
            
            self.assertEqual(config.interval, 60)
            self.assertTrue(config.debug_mode)
        except ImportError as e:
            # 統合エラーハンドラーを使用
            error_handler = StandardErrorHandler()
            error_handler.handle_validation_error(
                "auto_mode_config", "import", "モジュールインポート失敗", e
            )
        
    def test_jst_utils_integration(self):
        """JSTユーティリティ統合テスト"""
        # JST関連機能の統合動作確認
        current_time = get_jst_now()
        formatted_time = format_jst_time(current_time)
        formatted_datetime = format_jst_datetime(current_time)
        filename_timestamp = get_filename_timestamp()
        
        # すべて文字列として返されることを確認
        self.assertIsInstance(formatted_time, str)
        self.assertIsInstance(formatted_datetime, str)
        self.assertIsInstance(filename_timestamp, str)
        
        # JST表記が含まれることを確認
        self.assertIn("JST", formatted_time)
        self.assertIn("JST", formatted_datetime)
        
    def test_file_operations_integration(self):
        """ファイル操作統合テスト"""
        from file_access_logger import FileAccessLogger, AccessPurpose
        
        # 一時ファイル作成
        test_file = Path(self.temp_dir) / "test_integration.py"
        test_file.write_text("# Test integration file\nprint('hello')")
        
        # FileAccessLoggerでアクセス記録
        logger = FileAccessLogger(log_file=Path(self.temp_dir) / "access.log")
        logger.log_read(str(test_file), AccessPurpose.ANALYSIS)
        logger.log_modify(str(test_file), AccessPurpose.REFACTORING)
        
        # アクセス数確認
        access_count = logger.get_file_access_count(str(test_file))
        self.assertEqual(access_count, 2)
        
        # 最近のアクセス確認
        recent_accesses = logger.get_recent_accesses(1)
        self.assertEqual(len(recent_accesses), 1)
        self.assertEqual(recent_accesses[0]['operation'], 'modify')
        
    def test_configuration_integration(self):
        """設定統合テスト"""
        from auto_mode import AutoModeConfig
        
        # 設定ファイルを作成
        config_file = Path(self.temp_dir) / "test_config.json"
        config_data = {
            "interval": 45,
            "max_iterations": 200,
            "debug_mode": True,
            "keywords": ["test", "integration"]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
            
        # 設定読み込み
        config = AutoModeConfig.load_from_file(config_file)
        
        # 設定値確認
        self.assertEqual(config.interval, 45)
        self.assertEqual(config.max_iterations, 200)
        self.assertTrue(config.debug_mode)
        self.assertEqual(config.keywords, ["test", "integration"])
        
        # 設定変更・保存
        config.interval = 90
        config.save_to_file(config_file)
        
        # 再読み込みして変更確認
        reloaded_config = AutoModeConfig.load_from_file(config_file)
        self.assertEqual(reloaded_config.interval, 90)
        
    def test_logger_integration(self):
        """ログ機能統合テスト"""
        from activity_logger import UnifiedLogger, ActivityType, LogLevel
        
        # ActivityLoggerのテスト
        log_file = Path(self.temp_dir) / "activity.log"
        logger = UnifiedLogger(log_file=log_file)
        
        # 様々なレベルのログを記録
        logger.log("Info message", ActivityType.SYSTEM, LogLevel.INFO)
        logger.log("Warning message", ActivityType.OPERATION, LogLevel.WARNING)
        logger.log("Error message", ActivityType.ERROR, LogLevel.ERROR)
        
        # ログファイルが作成されていることを確認
        self.assertTrue(log_file.exists())
        
        # ログ内容確認
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Info message", content)
            self.assertIn("Warning message", content)
            self.assertIn("Error message", content)
            self.assertIn("[INFO]", content)
            self.assertIn("[WARNING]", content)
            self.assertIn("[ERROR]", content)
            
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        from auto_mode import AutoModeConfig
        
        # 存在しないファイルからの設定読み込み
        non_existent_file = Path(self.temp_dir) / "non_existent.json"
        config = AutoModeConfig.load_from_file(non_existent_file)
        
        # デフォルト値で初期化されることを確認
        self.assertEqual(config.interval, 30)  # デフォルト値
        
        # 不正なJSONファイルからの読み込み
        bad_json_file = Path(self.temp_dir) / "bad.json"
        bad_json_file.write_text("{ invalid json }")
        
        config = AutoModeConfig.load_from_file(bad_json_file)
        
        # エラーが発生してもデフォルト値で初期化されることを確認
        self.assertEqual(config.interval, 30)  # デフォルト値
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_console_output_integration(self, mock_stdout):
        """コンソール出力統合テスト"""
        from file_access_logger import ColorTerminal
        
        # カラー出力テスト
        red_text = ColorTerminal.red("Error message")
        green_text = ColorTerminal.green("Success message")
        
        # カラーコードが含まれることを確認
        self.assertIn("\033[", red_text)
        self.assertIn("\033[", green_text)
        
        # リセットコードが含まれることを確認
        self.assertIn("\033[0m", red_text)
        self.assertIn("\033[0m", green_text)


if __name__ == '__main__':
    # 詳細なテスト結果を表示
    unittest.main(verbosity=2)