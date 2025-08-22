"""
統合テスト実行モジュールのテスト

循環参照検出、コンポーネント連携テスト、初期化エラー検出などの統合テスト機能をテスト
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import json

# テスト対象モジュールのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# テスト対象をインポート（まだ存在しないが、TDDなので先にテストを定義）
try:
    from integration_test_runner import (
        IntegrationTestRunner, 
        CircularImportDetector, 
        ComponentConnectivityTester,
        InitializationTester,
        IntegrationTestResult,
        IntegrationTestError
    )
    from test_strategy import TestLevel, TestResult
except ImportError:
    # TDDのRed phase - モジュールがまだ存在しない
    pass


class TestIntegrationTestRunner(unittest.TestCase):
    """統合テスト実行機能のテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.runner = IntegrationTestRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_integration_test_runner_initialization(self):
        """統合テスト実行器が正しく初期化されること"""
        runner = IntegrationTestRunner()
        
        # デフォルト設定確認
        self.assertTrue(runner.circular_import_detection_enabled)
        self.assertTrue(runner.component_connectivity_test_enabled)
        self.assertTrue(runner.initialization_test_enabled)
        
        # 検出器が正しく初期化される
        self.assertIsInstance(runner.circular_detector, CircularImportDetector)
        self.assertIsInstance(runner.connectivity_tester, ComponentConnectivityTester)
        self.assertIsInstance(runner.initialization_tester, InitializationTester)
    
    def test_run_integration_tests(self):
        """統合テストが正しく実行されること"""
        runner = IntegrationTestRunner()
        
        # モック設定
        with patch.object(runner.circular_detector, 'detect') as mock_circular:
            with patch.object(runner.connectivity_tester, 'test_connectivity') as mock_connectivity:
                with patch.object(runner.initialization_tester, 'test_initialization') as mock_init:
                    
                    # 成功ケース
                    mock_circular.return_value = []
                    mock_connectivity.return_value = True
                    mock_init.return_value = True
                    
                    result = runner.run()
                    
                    # 全てのテストが実行される
                    mock_circular.assert_called_once()
                    mock_connectivity.assert_called_once()
                    mock_init.assert_called_once()
                    
                    # 結果が正しい
                    self.assertIsInstance(result, IntegrationTestResult)
                    self.assertTrue(result.passed)
                    self.assertEqual(result.level, TestLevel.INTEGRATION)
    
    def test_integration_test_with_failures(self):
        """統合テスト失敗時の処理が正しいこと"""
        runner = IntegrationTestRunner()
        
        with patch.object(runner.circular_detector, 'detect') as mock_circular:
            with patch.object(runner.connectivity_tester, 'test_connectivity') as mock_connectivity:
                with patch.object(runner.initialization_tester, 'test_initialization') as mock_init:
                    
                    # 循環参照検出
                    mock_circular.return_value = ["moduleA -> moduleB -> moduleA"]
                    mock_connectivity.return_value = True
                    mock_init.return_value = True
                    
                    result = runner.run()
                    
                    # テスト失敗
                    self.assertFalse(result.passed)
                    self.assertIn("Circular import detected", result.details)
                    self.assertEqual(result.failed, 1)


class TestCircularImportDetector(unittest.TestCase):
    """循環参照検出機能のテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.detector = CircularImportDetector()
    
    def test_circular_import_detector_initialization(self):
        """循環参照検出器が正しく初期化されること"""
        detector = CircularImportDetector()
        
        self.assertEqual(detector.visited_modules, set())
        self.assertEqual(detector.current_path, [])
        self.assertEqual(detector.circular_imports, [])
    
    @patch('sys.modules')
    def test_detect_no_circular_imports(self, mock_modules):
        """循環参照がない場合の検出テスト"""
        # 正常なモジュール構造をモック
        mock_modules.keys.return_value = ['moduleA', 'moduleB']
        
        detector = CircularImportDetector()
        
        with patch.object(detector, '_analyze_module') as mock_analyze:
            mock_analyze.return_value = []
            
            circular_imports = detector.detect()
            
            self.assertEqual(circular_imports, [])
            self.assertEqual(len(detector.circular_imports), 0)
    
    @patch('sys.modules')
    def test_detect_circular_imports(self, mock_modules):
        """循環参照がある場合の検出テスト"""
        mock_modules.keys.return_value = ['moduleA', 'moduleB']
        
        detector = CircularImportDetector()
        
        # 循環参照を模擬
        with patch.object(detector, '_analyze_module') as mock_analyze:
            def side_effect(file_path, module_name):
                # 循環参照を検出
                if module_name == 'moduleA':
                    detector.circular_imports.append("moduleA -> moduleB -> moduleA")
                return []
            
            mock_analyze.side_effect = side_effect
            
            circular_imports = detector.detect()
            
            self.assertEqual(len(circular_imports), 1)
            self.assertIn("moduleA -> moduleB -> moduleA", circular_imports[0])
    
    def test_analyze_module_dependencies(self):
        """モジュール依存関係の分析テスト"""
        detector = CircularImportDetector()
        
        # テスト用の一時ファイル作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
from collections import defaultdict
import sys
""")
            temp_file = f.name
        
        try:
            # ファイルの依存関係を分析
            dependencies = detector._get_module_imports(temp_file)
            
            expected = ['os', 'collections', 'sys']
            for dep in expected:
                self.assertIn(dep, dependencies)
        
        finally:
            os.unlink(temp_file)
    
    def test_circular_import_path_tracking(self):
        """循環参照パスの追跡テスト"""
        detector = CircularImportDetector()
        
        # パス追跡のシミュレーション
        detector._enter_module('moduleA')
        self.assertIn('moduleA', detector.visited_modules)
        self.assertEqual(detector.current_path, ['moduleA'])
        
        detector._enter_module('moduleB')
        self.assertEqual(detector.current_path, ['moduleA', 'moduleB'])
        
        # 循環検出（moduleAに戻る）
        is_circular = detector._is_circular('moduleA')
        self.assertTrue(is_circular)
        
        circular_path = detector._get_circular_path('moduleA')
        expected_path = "moduleA -> moduleB -> moduleA"
        self.assertEqual(circular_path, expected_path)


class TestComponentConnectivityTester(unittest.TestCase):
    """コンポーネント連携テストのテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.tester = ComponentConnectivityTester()
    
    def test_component_connectivity_tester_initialization(self):
        """コンポーネント連携テスターが正しく初期化されること"""
        tester = ComponentConnectivityTester()
        
        self.assertEqual(tester.components, [])
        self.assertEqual(tester.connections, [])
        self.assertFalse(tester.strict_mode)
    
    def test_register_components(self):
        """コンポーネント登録機能のテスト"""
        tester = ComponentConnectivityTester()
        
        # コンポーネント登録
        tester.register_component('ComponentA', 'src.components.ComponentA')
        tester.register_component('ComponentB', 'src.components.ComponentB')
        
        self.assertEqual(len(tester.components), 2)
        self.assertIn('ComponentA', [c['name'] for c in tester.components])
        self.assertIn('ComponentB', [c['name'] for c in tester.components])
    
    def test_test_component_connectivity(self):
        """コンポーネント間の連携テスト"""
        tester = ComponentConnectivityTester()
        
        # コンポーネントとコネクションの設定
        tester.register_component('ServiceA', 'src.services.ServiceA')
        tester.register_component('ServiceB', 'src.services.ServiceB')
        tester.add_expected_connection('ServiceA', 'ServiceB', 'method_call')
        
        # モックを使用した連携テスト
        with patch.object(tester, '_verify_connection') as mock_verify:
            mock_verify.return_value = True
            
            result = tester.test_connectivity()
            
            self.assertTrue(result)
            mock_verify.assert_called()
    
    def test_failed_connectivity_detection(self):
        """連携失敗の検出テスト"""
        tester = ComponentConnectivityTester()
        
        tester.register_component('ServiceA', 'src.services.ServiceA')
        tester.register_component('ServiceB', 'src.services.ServiceB')
        tester.add_expected_connection('ServiceA', 'ServiceB', 'missing_method')
        
        with patch.object(tester, '_verify_connection') as mock_verify:
            mock_verify.return_value = False
            
            result = tester.test_connectivity()
            
            self.assertFalse(result)
    
    def test_connection_verification(self):
        """コネクション検証機能のテスト"""
        tester = ComponentConnectivityTester()
        
        # 有効なコネクションの検証
        connection = {
            'from_component': 'ServiceA',
            'to_component': 'ServiceB',
            'connection_type': 'method_call',
            'method_name': 'process_data'
        }
        
        # モックオブジェクトでメソッド存在確認
        mock_service_b_class = Mock()
        mock_service_b_class.process_data = Mock()
        
        mock_module = Mock()
        mock_module.ServiceB = mock_service_b_class
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = mock_module
            
            result = tester._verify_method_connection(connection)
            
            self.assertTrue(result)


class TestInitializationTester(unittest.TestCase):
    """初期化テストのテストクラス"""
    
    def setUp(self):
        """各テストの前処理"""
        self.tester = InitializationTester()
    
    def test_initialization_tester_setup(self):
        """初期化テスターの設定テスト"""
        tester = InitializationTester()
        
        self.assertEqual(tester.modules_to_test, [])
        self.assertEqual(tester.initialization_errors, [])
    
    def test_module_initialization_success(self):
        """モジュール初期化成功のテスト"""
        tester = InitializationTester()
        
        # 初期化テスト対象を設定
        tester.add_module('src.services.DataAccessService')
        
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_import.return_value = mock_module
            
            result = tester.test_initialization()
            
            self.assertTrue(result)
            self.assertEqual(len(tester.initialization_errors), 0)
    
    def test_module_initialization_failure(self):
        """モジュール初期化失敗のテスト"""
        tester = InitializationTester()
        
        tester.add_module('src.services.ProblematicService')
        
        # ImportErrorを発生させる
        with patch('importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("Circular import detected")
            
            result = tester.test_initialization()
            
            self.assertFalse(result)
            self.assertEqual(len(tester.initialization_errors), 1)
            self.assertIn("Circular import", tester.initialization_errors[0])
    
    def test_class_instantiation_test(self):
        """クラス instantiation テスト"""
        tester = InitializationTester()
        
        # テスト対象クラスの設定
        tester.add_class('src.services.DataAccessService', 'DataAccessService')
        
        mock_class = Mock()
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.DataAccessService = mock_class
            mock_import.return_value = mock_module
            
            # 正しい辞書形式を渡す
            class_config = {
                'module': 'src.services.DataAccessService',
                'class_name': 'DataAccessService',
                'init_args': (),
                'init_kwargs': {}
            }
            
            result = tester._test_class_instantiation(class_config)
            
            self.assertTrue(result)
            mock_class.assert_called_once()


class TestIntegrationTestResult(unittest.TestCase):
    """統合テスト結果のテストクラス"""
    
    def test_integration_test_result_creation(self):
        """統合テスト結果の作成テスト"""
        result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=True,
            failed=0,
            total=5,
            duration=3.2,
            details="All integration tests passed",
            circular_imports=[],
            connectivity_issues=[],
            initialization_errors=[]
        )
        
        self.assertEqual(result.level, TestLevel.INTEGRATION)
        self.assertTrue(result.passed)
        self.assertEqual(result.total, 5)
        self.assertEqual(result.duration, 3.2)
        self.assertEqual(len(result.circular_imports), 0)
    
    def test_integration_test_result_with_failures(self):
        """失敗を含む統合テスト結果のテスト"""
        circular_imports = ["moduleA -> moduleB -> moduleA"]
        connectivity_issues = ["ServiceA cannot connect to ServiceB"]
        
        result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=False,
            failed=2,
            total=5,
            duration=2.8,
            details="Integration tests failed",
            circular_imports=circular_imports,
            connectivity_issues=connectivity_issues,
            initialization_errors=[]
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.failed, 2)
        self.assertEqual(len(result.circular_imports), 1)
        self.assertEqual(len(result.connectivity_issues), 1)
    
    def test_integration_test_result_summary(self):
        """統合テスト結果のサマリー生成テスト"""
        result = IntegrationTestResult(
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
        
        summary = result.get_summary()
        
        self.assertIn("Integration Tests", summary)
        self.assertIn("Failed: 1", summary)
        self.assertIn("Circular imports found", summary)
        self.assertIn("moduleA -> moduleB -> moduleA", summary)


if __name__ == "__main__":
    unittest.main()