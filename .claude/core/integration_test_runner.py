"""
統合テスト実行モジュール

循環参照検出、コンポーネント連携テスト、初期化エラー検出などの統合テスト機能を提供
"""

import sys
import os
import importlib
import ast
import re
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from test_strategy import TestLevel, TestResult


@dataclass
class IntegrationTestResult(TestResult):
    """統合テスト結果データクラス"""
    circular_imports: List[str] = field(default_factory=list)
    connectivity_issues: List[str] = field(default_factory=list)
    initialization_errors: List[str] = field(default_factory=list)
    
    def get_summary(self) -> str:
        """サマリー文字列生成"""
        status = "PASSED" if self.passed else "FAILED"
        summary = f"Integration Tests - {status}\n"
        summary += f"Total: {self.total}, Passed: {self.total - self.failed}, Failed: {self.failed}\n"
        summary += f"Duration: {self.duration:.2f}s, Success Rate: {self.success_rate:.1f}%\n"
        
        if self.circular_imports:
            summary += f"\nCircular imports found:\n"
            for ci in self.circular_imports:
                summary += f"  - {ci}\n"
                
        if self.connectivity_issues:
            summary += f"\nConnectivity issues:\n"
            for issue in self.connectivity_issues:
                summary += f"  - {issue}\n"
                
        if self.initialization_errors:
            summary += f"\nInitialization errors:\n"
            for error in self.initialization_errors:
                summary += f"  - {error}\n"
                
        return summary


class IntegrationTestError(Exception):
    """統合テストエラー"""
    pass


class CircularImportDetector:
    """循環参照検出器"""
    
    def __init__(self):
        """初期化"""
        self.visited_modules: Set[str] = set()
        self.current_path: List[str] = []
        self.circular_imports: List[str] = []
        
    def detect(self, root_path: str = None) -> List[str]:
        """
        循環参照検出実行
        
        Args:
            root_path: 検出対象のルートパス
            
        Returns:
            検出された循環参照のリスト
        """
        self._reset()
        
        if root_path is None:
            # 現在のプロジェクトディレクトリを使用
            root_path = os.getcwd()
            
        # Pythonモジュールを検索
        python_files = self._find_python_files(root_path)
        
        for python_file in python_files:
            module_name = self._get_module_name(python_file, root_path)
            if module_name not in self.visited_modules:
                self._analyze_module(python_file, module_name)
                
        return self.circular_imports
        
    def _reset(self):
        """状態リセット"""
        self.visited_modules.clear()
        self.current_path.clear()
        self.circular_imports.clear()
        
    def _find_python_files(self, root_path: str) -> List[str]:
        """Pythonファイル検索"""
        python_files = []
        root = Path(root_path)
        
        for file_path in root.rglob("*.py"):
            # __pycache__やテストファイルは除外
            if "__pycache__" not in str(file_path) and not str(file_path).endswith("_test.py"):
                python_files.append(str(file_path))
                
        return python_files
        
    def _get_module_name(self, file_path: str, root_path: str) -> str:
        """ファイルパスからモジュール名生成"""
        relative_path = Path(file_path).relative_to(Path(root_path))
        module_name = str(relative_path.with_suffix('')).replace(os.sep, '.')
        return module_name
        
    def _analyze_module(self, file_path: str, module_name: str) -> List[str]:
        """
        モジュール解析
        
        Args:
            file_path: ファイルパス
            module_name: モジュール名
            
        Returns:
            検出された循環参照
        """
        if self._is_circular(module_name):
            circular_path = self._get_circular_path(module_name)
            self.circular_imports.append(circular_path)
            return [circular_path]
            
        self._enter_module(module_name)
        
        try:
            imports = self._get_module_imports(file_path)
            
            for imported_module in imports:
                if imported_module not in self.visited_modules:
                    # 対応するファイルが存在する場合のみ再帰解析
                    imported_file = self._find_module_file(imported_module)
                    if imported_file:
                        self._analyze_module(imported_file, imported_module)
                        
        except Exception as e:
            # ファイル読み込みエラーは無視
            pass
        finally:
            self._exit_module()
            
        return []
        
    def _get_module_imports(self, file_path: str) -> List[str]:
        """モジュールのインポート文解析"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # ASTを使用してインポート文を解析
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
        except Exception:
            # パースエラーの場合は正規表現でフォールバック
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # import文を正規表現で抽出
                import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+([^#\n]+)'
                matches = re.findall(import_pattern, content, re.MULTILINE)
                
                for from_module, import_items in matches:
                    if from_module:
                        imports.append(from_module)
                        
            except Exception:
                pass
                
        return imports
        
    def _find_module_file(self, module_name: str) -> Optional[str]:
        """モジュール名に対応するファイルを検索"""
        # 簡略化: 実際の実装では sys.path を使用してより正確に検索
        current_dir = Path.cwd()
        module_path = current_dir / (module_name.replace('.', os.sep) + '.py')
        
        if module_path.exists():
            return str(module_path)
            
        return None
        
    def _enter_module(self, module_name: str):
        """モジュール進入"""
        self.visited_modules.add(module_name)
        self.current_path.append(module_name)
        
    def _exit_module(self):
        """モジュール退出"""
        if self.current_path:
            self.current_path.pop()
            
    def _is_circular(self, module_name: str) -> bool:
        """循環参照チェック"""
        return module_name in self.current_path
        
    def _get_circular_path(self, module_name: str) -> str:
        """循環参照パス生成"""
        if module_name not in self.current_path:
            return ""
            
        start_index = self.current_path.index(module_name)
        circular_path = self.current_path[start_index:] + [module_name]
        return " -> ".join(circular_path)


class ComponentConnectivityTester:
    """コンポーネント連携テスター"""
    
    def __init__(self):
        """初期化"""
        self.components = []
        self.connections = []
        self.strict_mode = False
        
    def register_component(self, name: str, module_path: str, class_name: str = None):
        """コンポーネント登録"""
        self.components.append({
            'name': name,
            'module_path': module_path,
            'class_name': class_name or name
        })
        
    def add_expected_connection(self, from_component: str, to_component: str, 
                              connection_type: str, **kwargs):
        """期待されるコネクション追加"""
        connection = {
            'from_component': from_component,
            'to_component': to_component,
            'connection_type': connection_type,
            **kwargs
        }
        self.connections.append(connection)
        
    def test_connectivity(self) -> bool:
        """コンポーネント連携テスト実行"""
        for connection in self.connections:
            if not self._verify_connection(connection):
                return False
        return True
        
    def _verify_connection(self, connection: Dict[str, Any]) -> bool:
        """コネクション検証"""
        connection_type = connection['connection_type']
        
        if connection_type == 'method_call':
            return self._verify_method_connection(connection)
        elif connection_type == 'import':
            return self._verify_import_connection(connection)
        elif connection_type == 'attribute_access':
            return self._verify_attribute_connection(connection)
        else:
            return True  # 未知のタイプはスキップ
            
    def _verify_method_connection(self, connection: Dict[str, Any]) -> bool:
        """メソッド呼び出しコネクション検証"""
        to_component = connection['to_component']
        method_name = connection.get('method_name')
        
        if not method_name:
            return True
            
        # コンポーネント検索
        component = self._find_component(to_component)
        if not component:
            return False
            
        try:
            # モジュールインポート
            module = importlib.import_module(component['module_path'])
            
            # クラス取得
            if hasattr(module, component['class_name']):
                cls = getattr(module, component['class_name'])
                
                # メソッド存在チェック
                return hasattr(cls, method_name)
            else:
                return False
                
        except Exception:
            return False
            
    def _verify_import_connection(self, connection: Dict[str, Any]) -> bool:
        """インポートコネクション検証"""
        to_component = connection['to_component']
        component = self._find_component(to_component)
        
        if not component:
            return False
            
        try:
            # インポート可能かテスト
            importlib.import_module(component['module_path'])
            return True
        except Exception:
            return False
            
    def _verify_attribute_connection(self, connection: Dict[str, Any]) -> bool:
        """属性アクセスコネクション検証"""
        to_component = connection['to_component']
        attribute_name = connection.get('attribute_name')
        
        if not attribute_name:
            return True
            
        component = self._find_component(to_component)
        if not component:
            return False
            
        try:
            module = importlib.import_module(component['module_path'])
            
            if hasattr(module, component['class_name']):
                cls = getattr(module, component['class_name'])
                return hasattr(cls, attribute_name)
            else:
                return hasattr(module, attribute_name)
                
        except Exception:
            return False
            
    def _find_component(self, name: str) -> Optional[Dict[str, Any]]:
        """コンポーネント検索"""
        for component in self.components:
            if component['name'] == name:
                return component
        return None


class InitializationTester:
    """初期化テスター"""
    
    def __init__(self):
        """初期化"""
        self.modules_to_test = []
        self.classes_to_test = []
        self.initialization_errors = []
        
    def add_module(self, module_path: str):
        """テスト対象モジュール追加"""
        self.modules_to_test.append(module_path)
        
    def add_class(self, module_path: str, class_name: str, init_args: tuple = (), 
                  init_kwargs: dict = None):
        """テスト対象クラス追加"""
        if init_kwargs is None:
            init_kwargs = {}
            
        self.classes_to_test.append({
            'module': module_path,
            'class_name': class_name,
            'init_args': init_args,
            'init_kwargs': init_kwargs
        })
        
    def test_initialization(self) -> bool:
        """初期化テスト実行"""
        self.initialization_errors.clear()
        success = True
        
        # モジュール初期化テスト
        for module_path in self.modules_to_test:
            if not self._test_module_import(module_path):
                success = False
                
        # クラス初期化テスト
        for class_config in self.classes_to_test:
            if not self._test_class_instantiation(class_config):
                success = False
                
        return success
        
    def _test_module_import(self, module_path: str) -> bool:
        """モジュールインポートテスト"""
        try:
            importlib.import_module(module_path)
            return True
        except Exception as e:
            error_msg = f"Module import failed: {module_path} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
            
    def _test_class_instantiation(self, class_config: Dict[str, Any]) -> bool:
        """クラス instantiation テスト"""
        try:
            module = importlib.import_module(class_config['module'])
            cls = getattr(module, class_config['class_name'])
            
            # インスタンス作成テスト
            instance = cls(*class_config['init_args'], **class_config['init_kwargs'])
            return True
            
        except Exception as e:
            error_msg = f"Class instantiation failed: {class_config['class_name']} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False


class IntegrationTestRunner:
    """統合テスト実行器"""
    
    def __init__(self):
        """初期化"""
        self.circular_import_detection_enabled = True
        self.component_connectivity_test_enabled = True
        self.initialization_test_enabled = True
        
        self.circular_detector = CircularImportDetector()
        self.connectivity_tester = ComponentConnectivityTester()
        self.initialization_tester = InitializationTester()
        
    def run(self, root_path: str = None) -> IntegrationTestResult:
        """
        統合テスト実行
        
        Args:
            root_path: テスト対象のルートパス
            
        Returns:
            統合テスト結果
        """
        start_time = time.time()
        total_tests = 0
        failed_tests = 0
        details = []
        
        # 検出結果格納
        circular_imports = []
        connectivity_issues = []
        initialization_errors = []
        
        # 循環参照検出
        if self.circular_import_detection_enabled:
            total_tests += 1
            circular_imports = self.circular_detector.detect(root_path)
            if circular_imports:
                failed_tests += 1
                details.append("Circular import detected")
                
        # コンポーネント連携テスト
        if self.component_connectivity_test_enabled:
            total_tests += 1
            if not self.connectivity_tester.test_connectivity():
                failed_tests += 1
                connectivity_issues = ["Component connectivity test failed"]
                details.append("Component connectivity issues found")
                
        # 初期化テスト
        if self.initialization_test_enabled:
            total_tests += 1
            if not self.initialization_tester.test_initialization():
                failed_tests += 1
                initialization_errors = self.initialization_tester.initialization_errors
                details.append("Initialization errors detected")
                
        # 結果作成
        duration = time.time() - start_time
        passed = failed_tests == 0
        
        result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=passed,
            failed=failed_tests,
            total=total_tests,
            duration=duration,
            details="; ".join(details) if details else "All integration tests passed",
            circular_imports=circular_imports,
            connectivity_issues=connectivity_issues,
            initialization_errors=initialization_errors
        )
        
        return result
        
    def configure(self, circular_import_detection: bool = None,
                 component_connectivity_test: bool = None,
                 initialization_test: bool = None):
        """統合テスト設定"""
        if circular_import_detection is not None:
            self.circular_import_detection_enabled = circular_import_detection
            
        if component_connectivity_test is not None:
            self.component_connectivity_test_enabled = component_connectivity_test
            
        if initialization_test is not None:
            self.initialization_test_enabled = initialization_test
            
    def get_circular_detector(self) -> CircularImportDetector:
        """循環参照検出器取得"""
        return self.circular_detector
        
    def get_connectivity_tester(self) -> ComponentConnectivityTester:
        """連携テスター取得"""
        return self.connectivity_tester
        
    def get_initialization_tester(self) -> InitializationTester:
        """初期化テスター取得"""
        return self.initialization_tester