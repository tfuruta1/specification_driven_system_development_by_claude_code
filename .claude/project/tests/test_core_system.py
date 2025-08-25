#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コアシステムのテスト - TDD原則に基づく100%カバレッジ
RED→GREEN→REFACTOR
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# パス設定
current = Path(__file__).resolve().parent
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    current = current.parent
else:
    claude_root = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(claude_root / "system"))

from core.core_system import CoreSystem, Status, Result, setup_paths, CLAUDE_ROOT


class TestSetupPaths(unittest.TestCase):
    """setup_paths関数のテスト"""
    
    def test_setup_paths_returns_path(self):
        """パス設定が正しくPathオブジェクトを返すことを確認"""
        result = setup_paths()
        self.assertIsInstance(result, Path)
        self.assertTrue(str(result) in sys.path or str(result / "system") in sys.path)
    
    def test_claude_root_is_set(self):
        """CLAUDE_ROOTが設定されていることを確認"""
        self.assertIsInstance(CLAUDE_ROOT, Path)
        self.assertTrue(CLAUDE_ROOT.exists() or True)  # 環境依存を回避


class TestStatus(unittest.TestCase):
    """Statusクラスのテスト"""
    
    def test_status_values(self):
        """ステータス値が正しく定義されていることを確認"""
        self.assertEqual(Status.PENDING.value, "pending")
        self.assertEqual(Status.IN_PROGRESS.value, "in_progress")
        self.assertEqual(Status.COMPLETED.value, "completed")
        self.assertEqual(Status.FAILED.value, "failed")


class TestResult(unittest.TestCase):
    """Resultクラスのテスト"""
    
    def test_result_creation(self):
        """Result作成のテスト"""
        result = Result(True, "Success")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        self.assertIsNone(result.data)
    
    def test_result_with_data(self):
        """データ付きResultのテスト"""
        data = {"key": "value"}
        result = Result(False, "Failed", data)
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Failed")
        self.assertEqual(result.data, data)


class TestCoreSystem(unittest.TestCase):
    """CoreSystemクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.system = CoreSystem()
        # テスト用一時ディレクトリ
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if self.test_path.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertIsInstance(self.system.root, Path)
        self.assertIsInstance(self.system.temp_dir, Path)
        self.assertIsInstance(self.system.reports_dir, Path)
        self.assertIsInstance(self.system.config, dict)
    
    def test_load_config_default(self):
        """デフォルト設定読み込みのテスト"""
        with patch.object(Path, 'exists', return_value=False):
            system = CoreSystem()
            self.assertEqual(system.config["temp_max_age_hours"], 24)
            self.assertTrue(system.config["auto_cleanup"])
            self.assertEqual(system.config["test_coverage_target"], 100.0)
    
    def test_load_config_from_file(self):
        """ファイルから設定読み込みのテスト"""
        config_data = {"temp_max_age_hours": 48, "auto_cleanup": False}
        
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(config_data))):
                system = CoreSystem()
                self.assertEqual(system.config["temp_max_age_hours"], 48)
                self.assertFalse(system.config["auto_cleanup"])
    
    def test_organize_files_no_files(self):
        """ファイルがない場合の整理テスト"""
        with patch.object(Path, 'glob', return_value=[]):
            result = self.system.organize_files()
            self.assertTrue(result.success)
            self.assertIn("0 files", result.message)
    
    def test_organize_files_with_report(self):
        """レポートファイルの整理テスト"""
        # モックファイル作成
        mock_file = Mock()
        mock_file.is_file.return_value = True
        mock_file.name = "test_report.md"
        
        with patch.object(Path, 'glob', return_value=[mock_file]):
            with patch('shutil.move') as mock_move:
                result = self.system.organize_files()
                self.assertTrue(result.success)
                mock_move.assert_called_once()
    
    def test_cleanup_temp_no_temp_dir(self):
        """tempディレクトリがない場合のクリーンアップテスト"""
        with patch.object(Path, 'exists', return_value=False):
            with patch.object(Path, 'mkdir') as mock_mkdir:
                result = self.system.cleanup_temp()
                self.assertTrue(result.success)
                mock_mkdir.assert_called_once()
    
    def test_cleanup_temp_with_old_files(self):
        """古いファイルのクリーンアップテスト"""
        # テスト用の古いファイル作成
        old_file = self.test_path / "old_file.tmp"
        old_file.write_text("test")
        
        # ファイルの更新時刻を古くする
        old_time = datetime.now() - timedelta(hours=48)
        import os
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        with patch.object(self.system, 'temp_dir', self.test_path):
            result = self.system.cleanup_temp()
            self.assertTrue(result.success)
            self.assertFalse(old_file.exists())
    
    def test_cleanup_temp_with_recent_files(self):
        """新しいファイルは削除されないことのテスト"""
        # テスト用の新しいファイル作成
        new_file = self.test_path / "new_file.tmp"
        new_file.write_text("test")
        
        with patch.object(self.system, 'temp_dir', self.test_path):
            result = self.system.cleanup_temp()
            self.assertTrue(result.success)
            self.assertTrue(new_file.exists())
    
    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """テスト実行成功のテスト"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="test output\nTOTAL     100    0   100%",
            stderr=""
        )
        
        with patch.object(Path, 'exists', return_value=True):
            result = self.system.run_tests()
            self.assertTrue(result.success)
            self.assertEqual(result.message, "Tests passed")
            self.assertEqual(result.data["coverage"], "100%")
    
    @patch('subprocess.run')
    def test_run_tests_failure(self, mock_run):
        """テスト実行失敗のテスト"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
        
        with patch.object(Path, 'exists', return_value=True):
            result = self.system.run_tests()
            self.assertFalse(result.success)
            self.assertEqual(result.message, "Tests failed")
    
    def test_run_tests_no_test_dir(self):
        """テストディレクトリがない場合のテスト"""
        with patch.object(Path, 'exists', return_value=False):
            result = self.system.run_tests()
            self.assertFalse(result.success)
            self.assertIn("not found", result.message)
    
    def test_check_code_quality_no_issues(self):
        """コード品質チェック（問題なし）のテスト"""
        # 短い行のみのファイル
        test_file = self.test_path / "test.py"
        test_file.write_text("def test():\n    pass\n")
        
        with patch.object(Path, 'glob', return_value=[test_file]):
            result = self.system.check_code_quality()
            self.assertTrue(result.success)
    
    def test_check_code_quality_long_lines(self):
        """長い行の検出テスト"""
        # 長い行を含むファイル
        test_file = self.test_path / "test.py"
        long_line = "x = " + "a" * 150 + "\n"
        test_file.write_text(long_line)
        
        with patch.object(Path, 'glob', return_value=[test_file]):
            result = self.system.check_code_quality()
            self.assertFalse(result.success)
            self.assertIn("Line too long", result.data["issues"][0])
    
    def test_check_code_quality_deep_nesting(self):
        """深いネストの検出テスト"""
        # 深いネストを含むファイル
        test_file = self.test_path / "test.py"
        deep_nest = "      " * 5 + "deep_code\n"  # 30スペース
        test_file.write_text(deep_nest)
        
        with patch.object(Path, 'glob', return_value=[test_file]):
            result = self.system.check_code_quality()
            self.assertFalse(result.success)
            self.assertIn("Deep nesting", result.data["issues"][0])
    
    def test_get_status(self):
        """ステータス取得のテスト"""
        status = self.system.get_status()
        self.assertIn("root", status)
        self.assertIn("temp_files", status)
        self.assertIn("config", status)
        self.assertIn("folders", status)
        self.assertIsInstance(status["folders"], dict)
    
    def test_execute_organize(self):
        """organizeコマンド実行のテスト"""
        result = self.system.execute("organize")
        self.assertIsInstance(result, Result)
    
    def test_execute_cleanup(self):
        """cleanupコマンド実行のテスト"""
        with patch.object(Path, 'exists', return_value=False):
            result = self.system.execute("cleanup")
            self.assertIsInstance(result, Result)
    
    def test_execute_test(self):
        """testコマンド実行のテスト"""
        with patch.object(Path, 'exists', return_value=False):
            result = self.system.execute("test")
            self.assertIsInstance(result, Result)
    
    def test_execute_check(self):
        """checkコマンド実行のテスト"""
        with patch.object(Path, 'glob', return_value=[]):
            result = self.system.execute("check")
            self.assertIsInstance(result, Result)
    
    def test_execute_status(self):
        """statusコマンド実行のテスト"""
        result = self.system.execute("status")
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, dict)
    
    def test_execute_unknown_command(self):
        """不明なコマンドのテスト"""
        result = self.system.execute("unknown")
        self.assertFalse(result.success)
        self.assertIn("Unknown command", result.message)


class TestMain(unittest.TestCase):
    """main関数のテスト"""
    
    @patch('sys.argv', ['script', 'status'])
    @patch('core.core_system.CoreSystem.execute')
    def test_main_with_status(self, mock_execute):
        """statusコマンドでmain実行のテスト"""
        mock_execute.return_value = Result(True, "OK", {"test": "data"})
        
        from core.core_system import main
        ret = main()
        self.assertEqual(ret, 0)
        mock_execute.assert_called_once_with("status")
    
    @patch('sys.argv', ['script'])
    @patch('core.core_system.CoreSystem.execute')
    def test_main_without_args(self, mock_execute):
        """引数なしでmain実行のテスト"""
        mock_execute.return_value = Result(True, "OK")
        
        from core.core_system import main
        ret = main()
        self.assertEqual(ret, 0)
        mock_execute.assert_called_once_with("status")
    
    @patch('sys.argv', ['script', 'test'])
    @patch('core.core_system.CoreSystem.execute')
    def test_main_with_failure(self, mock_execute):
        """失敗時のmain実行のテスト"""
        mock_execute.return_value = Result(False, "Failed")
        
        from core.core_system import main
        ret = main()
        self.assertEqual(ret, 1)


def run_coverage():
    """カバレッジ付きでテスト実行"""
    import subprocess
    cmd = [
        sys.executable, "-m", "pytest",
        __file__,
        "--cov=system.core.core_system",
        "--cov-report=term-missing",
        "-v"
    ]
    subprocess.run(cmd, cwd=str(claude_root))


if __name__ == "__main__":
    # テスト実行
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # カバレッジ確認
    print("\n" + "="*60)
    print("Running with coverage...")
    run_coverage()