#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合ロガーシステムのTDDテスト
RED Phase: 失敗するテストを先に書く
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# テスト対象のインポート
from logger import UnifiedLogger, IntegratedLogger, FileUtils, PathUtils


class TestUnifiedLogger(unittest.TestCase):
    """統合ロガーのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logger = UnifiedLogger()
        
    def tearDown(self):
        """テスト後の清掃"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """ロガー初期化テスト"""
        logger = UnifiedLogger()
        self.assertIsNotNone(logger)
        self.assertIsNotNone(logger.log_dir)
        self.assertIsNotNone(logger.log_file)
    
    def test_basic_logging(self):
        """基本ログ出力テスト"""
        with patch('builtins.print') as mock_print:
            self.logger.info("Test message")
            mock_print.assert_called()
    
    def test_component_logging(self):
        """コンポーネント指定ログテスト"""
        with patch('builtins.print') as mock_print:
            self.logger.info("Test message", component="TEST")
            args = mock_print.call_args[0][0]
            self.assertIn("[TEST]", args)
    
    def test_all_log_levels(self):
        """全ログレベルテスト"""
        with patch('builtins.print'):
            self.logger.info("Info test")
            self.logger.warning("Warning test")
            self.logger.error("Error test") 
            self.logger.debug("Debug test")
            self.logger.critical("Critical test")
    
    def test_file_output(self):
        """ファイル出力テスト"""
        # 一時ログファイルを使用
        temp_log = self.temp_dir / "test.log"
        self.logger.log_file = temp_log
        
        self.logger.info("Test file output")
        
        self.assertTrue(temp_log.exists())
        content = temp_log.read_text(encoding='utf-8')
        self.assertIn("Test file output", content)
        self.assertIn("[INFO]", content)


class TestIntegratedLogger(unittest.TestCase):
    """統合ロガー（エイリアス）のテストケース"""
    
    def test_integrated_logger_creation(self):
        """統合ロガー作成テスト"""
        logger = IntegratedLogger("TestLogger")
        self.assertEqual(logger.name, "TestLogger")
    
    def test_configure_method(self):
        """設定メソッドテスト"""
        logger = IntegratedLogger()
        # メソッドが存在し、エラーなく実行できることを確認
        logger.configure({"level": "INFO"})
    
    def test_file_output_setting(self):
        """ファイル出力設定テスト"""
        logger = IntegratedLogger()
        test_path = "/tmp/test.log"
        logger.set_file_output(test_path)
        self.assertEqual(str(logger.log_file), test_path)


class TestFileUtils(unittest.TestCase):
    """ファイルユーティリティのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file_utils = FileUtils()
    
    def tearDown(self):
        """テスト後の清掃"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_safe_read_existing_file(self):
        """既存ファイル読み込みテスト"""
        test_file = self.temp_dir / "test.txt"
        test_content = "Test content"
        test_file.write_text(test_content, encoding='utf-8')
        
        result = self.file_utils.safe_read(str(test_file))
        self.assertEqual(result, test_content)
    
    def test_safe_read_nonexistent_file(self):
        """存在しないファイル読み込みテスト"""
        result = self.file_utils.safe_read("/nonexistent/file.txt")
        self.assertIsNone(result)
    
    def test_safe_write(self):
        """安全書き込みテスト"""
        test_file = self.temp_dir / "write_test.txt"
        test_content = "Write test content"
        
        result = self.file_utils.safe_write(str(test_file), test_content)
        self.assertTrue(result)
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(encoding='utf-8'), test_content)


class TestPathUtils(unittest.TestCase):
    """パスユーティリティのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        self.path_utils = PathUtils()
    
    def test_find_project_root(self):
        """プロジェクトルート検索テスト"""
        root = self.path_utils.find_project_root()
        self.assertIsInstance(root, Path)
    
    def test_to_relative(self):
        """相対パス変換テスト"""
        abs_path = Path("/some/absolute/path")
        result = self.path_utils.to_relative(abs_path)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()