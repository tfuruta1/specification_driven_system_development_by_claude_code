#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File & Logging Tests - FileAccessLogger, ColorTerminal, ActivityLogger
元 test_v12_comprehensive.py から分割されたファイル・ログ関連テスト
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime
from io import StringIO

# テスト対象モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

from file_access_logger import FileAccessLogger, AccessPurpose, ColorTerminal
from activity_logger import UnifiedLogger as ActivityLogger, ActivityType, LogLevel


class TestFileAccessLogger(unittest.TestCase):
    """FileAccessLoggerの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "access_log.json"
        self.logger = FileAccessLogger(log_file=self.log_file)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.logger.log_file, self.log_file)
        self.assertEqual(len(self.logger.access_history), 0)
        
    def test_log_read_access(self):
        """読み取りアクセスログテスト"""
        test_file = "test.py"
        
        with patch('pathlib.Path.exists', return_value=True):
            self.logger.log_read(test_file, AccessPurpose.ANALYSIS)
            
        self.assertEqual(len(self.logger.access_history), 1)
        
        log_entry = self.logger.access_history[0]
        self.assertEqual(log_entry['file_path'], test_file)
        self.assertEqual(log_entry['operation'], 'read')
        self.assertEqual(log_entry['purpose'], AccessPurpose.ANALYSIS.value)
        
    def test_log_write_access(self):
        """書き込みアクセスログテスト"""
        test_file = "test.py"
        
        self.logger.log_write(test_file, AccessPurpose.CODE_GENERATION)
        
        self.assertEqual(len(self.logger.access_history), 1)
        
        log_entry = self.logger.access_history[0]
        self.assertEqual(log_entry['file_path'], test_file)
        self.assertEqual(log_entry['operation'], 'write')
        self.assertEqual(log_entry['purpose'], AccessPurpose.CODE_GENERATION.value)
        
    def test_log_modify_access(self):
        """変更アクセスログテスト"""
        test_file = "test.py"
        
        self.logger.log_modify(test_file, AccessPurpose.REFACTORING)
        
        self.assertEqual(len(self.logger.access_history), 1)
        
        log_entry = self.logger.access_history[0]
        self.assertEqual(log_entry['file_path'], test_file)
        self.assertEqual(log_entry['operation'], 'modify')
        self.assertEqual(log_entry['purpose'], AccessPurpose.REFACTORING.value)
        
    def test_get_file_access_count(self):
        """ファイルアクセス数取得テスト"""
        test_file = "test.py"
        
        # 初期状態
        count = self.logger.get_file_access_count(test_file)
        self.assertEqual(count, 0)
        
        # アクセス後
        self.logger.log_read(test_file, AccessPurpose.ANALYSIS)
        self.logger.log_write(test_file, AccessPurpose.CODE_GENERATION)
        
        count = self.logger.get_file_access_count(test_file)
        self.assertEqual(count, 2)
        
    def test_get_recent_accesses(self):
        """最近のアクセス取得テスト"""
        # 複数ファイルにアクセス
        for i in range(5):
            self.logger.log_read(f"test{i}.py", AccessPurpose.ANALYSIS)
            
        # 最新3件を取得
        recent = self.logger.get_recent_accesses(3)
        self.assertEqual(len(recent), 3)
        
        # 最新のものが最初に来る
        self.assertEqual(recent[0]['file_path'], "test4.py")
        self.assertEqual(recent[1]['file_path'], "test3.py")
        self.assertEqual(recent[2]['file_path'], "test2.py")
        
    def test_save_and_load_log(self):
        """ログ保存・読み込みテスト"""
        # ログエントリを作成
        self.logger.log_read("test.py", AccessPurpose.ANALYSIS)
        self.logger.log_write("test.py", AccessPurpose.CODE_GENERATION)
        
        # 保存
        self.logger.save_log()
        self.assertTrue(self.log_file.exists())
        
        # 新しいインスタンスで読み込み
        new_logger = FileAccessLogger(log_file=self.log_file)
        new_logger.load_log()
        
        self.assertEqual(len(new_logger.access_history), 2)
        self.assertEqual(new_logger.access_history[0]['file_path'], "test.py")
        
    def test_clear_log(self):
        """ログクリアテスト"""
        self.logger.log_read("test.py", AccessPurpose.ANALYSIS)
        self.assertEqual(len(self.logger.access_history), 1)
        
        self.logger.clear_log()
        self.assertEqual(len(self.logger.access_history), 0)
        
    def test_get_access_summary(self):
        """アクセス要約取得テスト"""
        # 様々なアクセスを記録
        self.logger.log_read("test1.py", AccessPurpose.ANALYSIS)
        self.logger.log_read("test2.py", AccessPurpose.ANALYSIS)
        self.logger.log_write("test1.py", AccessPurpose.CODE_GENERATION)
        self.logger.log_modify("test3.py", AccessPurpose.REFACTORING)
        
        summary = self.logger.get_access_summary()
        
        self.assertEqual(summary['total_accesses'], 4)
        self.assertEqual(summary['unique_files'], 3)
        self.assertEqual(summary['operations']['read'], 2)
        self.assertEqual(summary['operations']['write'], 1)
        self.assertEqual(summary['operations']['modify'], 1)


class TestColorTerminal(unittest.TestCase):
    """ColorTerminalの包括的テスト"""
    
    def test_color_output(self):
        """カラー出力テスト"""
        # 各色のテスト
        red_text = ColorTerminal.red("error")
        self.assertIn("\033[91m", red_text)
        self.assertIn("error", red_text)
        self.assertIn("\033[0m", red_text)
        
        green_text = ColorTerminal.green("success")
        self.assertIn("\033[92m", green_text)
        
        yellow_text = ColorTerminal.yellow("warning")
        self.assertIn("\033[93m", yellow_text)
        
        blue_text = ColorTerminal.blue("info")
        self.assertIn("\033[94m", blue_text)
        
    def test_reset_code(self):
        """リセットコードテスト"""
        colored_text = ColorTerminal.red("test")
        self.assertTrue(colored_text.endswith("\033[0m"))
        
    def test_empty_string(self):
        """空文字列テスト"""
        empty_colored = ColorTerminal.red("")
        self.assertEqual(empty_colored, "\033[91m\033[0m")


class TestActivityLogger(unittest.TestCase):
    """ActivityLoggerの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "activity.log"
        self.logger = ActivityLogger(log_file=self.log_file)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.logger.log_file, self.log_file)
        
    def test_log_info(self):
        """情報ログテスト"""
        with patch('builtins.print') as mock_print:
            self.logger.log(
                message="Test info message",
                activity_type=ActivityType.SYSTEM,
                level=LogLevel.INFO
            )
            
        # ログファイルに書き込まれることを確認
        self.assertTrue(self.log_file.exists())
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test info message", content)
            self.assertIn("[INFO]", content)
            
    def test_log_error(self):
        """エラーログテスト"""
        with patch('builtins.print') as mock_print:
            self.logger.log(
                message="Test error message",
                activity_type=ActivityType.ERROR,
                level=LogLevel.ERROR
            )
            
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test error message", content)
            self.assertIn("[ERROR]", content)
            
    def test_log_warning(self):
        """警告ログテスト"""
        with patch('builtins.print') as mock_print:
            self.logger.log(
                message="Test warning message",
                activity_type=ActivityType.SYSTEM,
                level=LogLevel.WARNING
            )
            
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test warning message", content)
            self.assertIn("[WARNING]", content)
            
    def test_log_debug(self):
        """デバッグログテスト"""
        with patch('builtins.print') as mock_print:
            self.logger.log(
                message="Test debug message",
                activity_type=ActivityType.SYSTEM,
                level=LogLevel.DEBUG
            )
            
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test debug message", content)
            self.assertIn("[DEBUG]", content)
            
    def test_context_manager(self):
        """コンテキストマネージャテスト"""
        with self.logger.log_activity("Test operation", ActivityType.OPERATION):
            pass
            
        # ログファイルに開始と終了が記録される
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("開始: Test operation", content)
            self.assertIn("完了: Test operation", content)
            
    def test_multiple_logs(self):
        """複数ログテスト"""
        messages = ["Message 1", "Message 2", "Message 3"]
        
        for msg in messages:
            self.logger.log(msg, ActivityType.SYSTEM, LogLevel.INFO)
            
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for msg in messages:
                self.assertIn(msg, content)
                
    def test_timestamp_format(self):
        """タイムスタンプ形式テスト"""
        self.logger.log("Test message", ActivityType.SYSTEM, LogLevel.INFO)
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # JST形式のタイムスタンプが含まれているか確認
            self.assertIn("JST", content)


if __name__ == '__main__':
    unittest.main()