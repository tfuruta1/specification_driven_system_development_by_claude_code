#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Strategy & Integration Tests
元 test_v12_comprehensive.py から分割されたテスト戦略・統合テスト関連
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

from test_strategy import TestStrategy, TestLevel, TestResult, TestExecutionError
from integration_test_runner import (
    IntegrationTestRunner, 
    CircularImportDetector, 
    InitializationTester,
    ComponentConnectivityTester,
    IntegrationTestResult
)


class TestTestStrategy(unittest.TestCase):
    """TestStrategyの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.strategy = TestStrategy(base_path=Path(self.temp_dir))
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.strategy.base_path, Path(self.temp_dir))
        self.assertIsInstance(self.strategy.test_results, list)
        
    def test_execute_unit_tests(self):
        """ユニットテスト実行テスト"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="test output",
                stderr=""
            )
            
            result = self.strategy.execute_tests(TestLevel.UNIT)
            
            self.assertIsInstance(result, TestResult)
            self.assertEqual(result.level, TestLevel.UNIT)
            self.assertTrue(result.passed)
            mock_run.assert_called()
            
    def test_execute_integration_tests(self):
        """統合テスト実行テスト"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="integration test output",
                stderr=""
            )
            
            result = self.strategy.execute_tests(TestLevel.INTEGRATION)
            
            self.assertIsInstance(result, TestResult)
            self.assertEqual(result.level, TestLevel.INTEGRATION)
            self.assertTrue(result.passed)
            
    def test_execute_system_tests(self):
        """システムテスト実行テスト"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="system test output",
                stderr=""
            )
            
            result = self.strategy.execute_tests(TestLevel.SYSTEM)
            
            self.assertIsInstance(result, TestResult)
            self.assertEqual(result.level, TestLevel.SYSTEM)
            self.assertTrue(result.passed)
            
    def test_failed_test_execution(self):
        """テスト失敗の場合のテスト"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="test failed"
            )
            
            result = self.strategy.execute_tests(TestLevel.UNIT)
            
            self.assertFalse(result.passed)
            self.assertIn("test failed", result.error_message)
            
    def test_test_execution_exception(self):
        """テスト実行例外のテスト"""
        with patch('subprocess.run', side_effect=Exception("execution error")):
            
            with self.assertRaises(TestExecutionError):
                self.strategy.execute_tests(TestLevel.UNIT)
                
    def test_get_test_results(self):
        """テスト結果取得テスト"""
        # 複数のテストを実行
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            self.strategy.execute_tests(TestLevel.UNIT)
            self.strategy.execute_tests(TestLevel.INTEGRATION)
            
        results = self.strategy.get_test_results()
        self.assertEqual(len(results), 2)
        
    def test_clear_results(self):
        """結果クリアテスト"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            self.strategy.execute_tests(TestLevel.UNIT)
            
        self.assertEqual(len(self.strategy.test_results), 1)
        
        self.strategy.clear_results()
        self.assertEqual(len(self.strategy.test_results), 0)
        
    def test_generate_report(self):
        """レポート生成テスト"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            self.strategy.execute_tests(TestLevel.UNIT)
            
        report = self.strategy.generate_report()
        
        self.assertIn("テスト実行レポート", report)
        self.assertIn("UNIT", report)
        
    def test_validate_test_environment(self):
        """テスト環境検証テスト"""
        # 正常なケース
        with patch('pathlib.Path.exists', return_value=True):
            is_valid = self.strategy.validate_test_environment()
            self.assertTrue(is_valid)
            
        # 異常なケース
        with patch('pathlib.Path.exists', return_value=False):
            is_valid = self.strategy.validate_test_environment()
            self.assertFalse(is_valid)


class TestCircularImportDetector(unittest.TestCase):
    """CircularImportDetectorの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = CircularImportDetector(Path(self.temp_dir))
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.detector.base_path, Path(self.temp_dir))
        
    def test_no_circular_imports(self):
        """循環インポートなしのテスト"""
        # 正常なファイルを作成
        file1 = Path(self.temp_dir) / "module1.py"
        file2 = Path(self.temp_dir) / "module2.py"
        
        file1.write_text("import json\n")
        file2.write_text("from module1 import something\n")
        
        result = self.detector.detect_circular_imports()
        
        self.assertFalse(result.has_circular_imports)
        self.assertEqual(len(result.circular_chains), 0)
        
    def test_detect_circular_imports(self):
        """循環インポート検出テスト"""
        # 循環インポートを持つファイルを作成
        file1 = Path(self.temp_dir) / "module1.py"
        file2 = Path(self.temp_dir) / "module2.py"
        
        file1.write_text("from module2 import func2\n")
        file2.write_text("from module1 import func1\n")
        
        result = self.detector.detect_circular_imports()
        
        self.assertTrue(result.has_circular_imports)
        self.assertGreater(len(result.circular_chains), 0)
        
    def test_self_import(self):
        """自己インポート検出テスト"""
        file1 = Path(self.temp_dir) / "module1.py"
        file1.write_text("from module1 import func1\n")
        
        result = self.detector.detect_circular_imports()
        
        self.assertTrue(result.has_circular_imports)


class TestInitializationTester(unittest.TestCase):
    """InitializationTesterの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.tester = InitializationTester(Path(self.temp_dir))
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.tester.base_path, Path(self.temp_dir))
        
    def test_successful_module_loading(self):
        """モジュール読み込み成功テスト"""
        # 正常なモジュールを作成
        module_file = Path(self.temp_dir) / "test_module.py"
        module_file.write_text("""
def test_function():
    return "success"

class TestClass:
    def __init__(self):
        self.value = 42
""")
        
        result = self.tester.test_module_initialization("test_module")
        
        self.assertTrue(result.success)
        self.assertIsNone(result.error)
        
    def test_failed_module_loading(self):
        """モジュール読み込み失敗テスト"""
        # 存在しないモジュール
        result = self.tester.test_module_initialization("non_existent_module")
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        
    def test_syntax_error_module(self):
        """構文エラーモジュールテスト"""
        # 構文エラーのあるモジュールを作成
        module_file = Path(self.temp_dir) / "bad_module.py"
        module_file.write_text("def bad_function(\n")  # 構文エラー
        
        result = self.tester.test_module_initialization("bad_module")
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)


class TestComponentConnectivityTester(unittest.TestCase):
    """ComponentConnectivityTesterの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.tester = ComponentConnectivityTester(Path(self.temp_dir))
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.tester.base_path, Path(self.temp_dir))
        
    def test_component_connectivity(self):
        """コンポーネント接続性テスト"""
        # テスト用コンポーネントを作成
        comp1 = Path(self.temp_dir) / "component1.py"
        comp2 = Path(self.temp_dir) / "component2.py"
        
        comp1.write_text("""
def get_data():
    return {"key": "value"}
""")
        
        comp2.write_text("""
from component1 import get_data

def process_data():
    data = get_data()
    return data["key"]
""")
        
        result = self.tester.test_connectivity("component1", "component2")
        
        self.assertTrue(result.connected)
        self.assertIsNone(result.error)


class TestIntegrationTestRunner(unittest.TestCase):
    """IntegrationTestRunnerの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = IntegrationTestRunner(Path(self.temp_dir))
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.runner.base_path, Path(self.temp_dir))
        
    def test_run_all_tests(self):
        """全テスト実行テスト"""
        # テスト用ファイルを作成
        test_file = Path(self.temp_dir) / "test_module.py"
        test_file.write_text("# Test module")
        
        with patch.object(self.runner.circular_detector, 'detect_circular_imports') as mock_circular:
            with patch.object(self.runner.init_tester, 'test_module_initialization') as mock_init:
                with patch.object(self.runner.connectivity_tester, 'test_connectivity') as mock_conn:
                    
                    # モックの設定
                    mock_circular.return_value = MagicMock(has_circular_imports=False)
                    mock_init.return_value = MagicMock(success=True)
                    mock_conn.return_value = MagicMock(connected=True)
                    
                    result = self.runner.run_integration_tests()
                    
                    self.assertIsInstance(result, IntegrationTestResult)
                    self.assertTrue(result.overall_success)
                    
    def test_generate_report(self):
        """レポート生成テスト"""
        # テスト結果を設定
        self.runner.last_result = IntegrationTestResult(
            overall_success=True,
            circular_import_result=MagicMock(has_circular_imports=False),
            initialization_results=[],
            connectivity_results=[]
        )
        
        report = self.runner.generate_detailed_report()
        
        self.assertIn("統合テスト結果レポート", report)
        self.assertIn("全体結果", report)


if __name__ == '__main__':
    unittest.main()