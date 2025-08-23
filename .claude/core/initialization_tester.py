"""
初期化テストモジュール - Claude Code Core
IntegrationTestRunnerから分離されたモジュール・クラス初期化テスト機能
"""

import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple


class InitializationTester:
    """初期化テスター"""
    
    def __init__(self):
        """初期化"""
        self.modules_to_test = []
        self.classes_to_test = []
        self.initialization_errors = []
        self.strict_mode = False
        
    def add_module(self, module_path: str):
        """テスト対象モジュール追加"""
        if module_path not in self.modules_to_test:
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
            module = importlib.import_module(module_path)
            
            # モジュールレベルでの初期化エラーがないかチェック
            if hasattr(module, '__init__') and callable(getattr(module, '__init__')):
                # モジュールに初期化関数がある場合は呼び出してテスト
                try:
                    module.__init__()
                except Exception as e:
                    error_msg = f"Module initialization function failed: {module_path} - {str(e)}"
                    self.initialization_errors.append(error_msg)
                    return False
                    
            return True
            
        except ImportError as e:
            error_msg = f"Module import failed: {module_path} - Import Error: {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
        except SyntaxError as e:
            error_msg = f"Module syntax error: {module_path} - Syntax Error: {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Module initialization failed: {module_path} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
            
    def _test_class_instantiation(self, class_config: Dict[str, Any]) -> bool:
        """クラス instantiation テスト"""
        try:
            module = importlib.import_module(class_config['module'])
            
            if not hasattr(module, class_config['class_name']):
                error_msg = f"Class not found: {class_config['class_name']} in {class_config['module']}"
                self.initialization_errors.append(error_msg)
                return False
                
            cls = getattr(module, class_config['class_name'])
            
            # クラスかどうかの検証
            if not inspect.isclass(cls):
                error_msg = f"Not a class: {class_config['class_name']} in {class_config['module']}"
                self.initialization_errors.append(error_msg)
                return False
            
            # __init__メソッドの存在確認と引数検証
            if hasattr(cls, '__init__'):
                init_signature = inspect.signature(cls.__init__)
                try:
                    # 引数の妥当性チェック（バインド試行）
                    init_signature.bind(None, *class_config['init_args'], **class_config['init_kwargs'])
                except TypeError as e:
                    error_msg = f"Invalid arguments for {class_config['class_name']}: {str(e)}"
                    self.initialization_errors.append(error_msg)
                    return False
            
            # インスタンス作成テスト
            instance = cls(*class_config['init_args'], **class_config['init_kwargs'])
            
            # インスタンス作成後の基本検証
            if instance is None:
                error_msg = f"Class instantiation returned None: {class_config['class_name']}"
                self.initialization_errors.append(error_msg)
                return False
                
            return True
            
        except ImportError as e:
            error_msg = f"Module import failed for class test: {class_config['module']} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
        except AttributeError as e:
            error_msg = f"Attribute error during instantiation: {class_config['class_name']} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
        except TypeError as e:
            error_msg = f"Type error during instantiation: {class_config['class_name']} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Class instantiation failed: {class_config['class_name']} - {str(e)}"
            self.initialization_errors.append(error_msg)
            return False
            
    def test_all_classes_in_module(self, module_path: str, skip_abstract: bool = True):
        """モジュール内の全クラスを自動テスト対象に追加"""
        try:
            module = importlib.import_module(module_path)
            
            for name in dir(module):
                obj = getattr(module, name)
                
                # クラスかどうかチェック
                if inspect.isclass(obj) and obj.__module__ == module_path:
                    # 抽象クラスのスキップ
                    if skip_abstract and inspect.isabstract(obj):
                        continue
                        
                    # __init__メソッドの引数をチェック
                    if hasattr(obj, '__init__'):
                        signature = inspect.signature(obj.__init__)
                        params = list(signature.parameters.values())[1:]  # selfを除く
                        
                        # デフォルト値がない必須パラメータがある場合はスキップ
                        required_params = [p for p in params if p.default == inspect.Parameter.empty]
                        if required_params:
                            continue
                    
                    # テスト対象に追加
                    self.add_class(module_path, name)
                    
        except Exception as e:
            error_msg = f"Failed to analyze module for auto-testing: {module_path} - {str(e)}"
            self.initialization_errors.append(error_msg)
            
    def get_initialization_report(self) -> str:
        """初期化テストレポート生成"""
        report = f"初期化テスト結果:\n"
        report += f"テストしたモジュール数: {len(self.modules_to_test)}\n"
        report += f"テストしたクラス数: {len(self.classes_to_test)}\n"
        report += f"検出されたエラー数: {len(self.initialization_errors)}\n"
        
        if self.modules_to_test:
            report += "\nテストしたモジュール:\n"
            for module in self.modules_to_test:
                report += f"  - {module}\n"
                
        if self.classes_to_test:
            report += "\nテストしたクラス:\n"
            for class_config in self.classes_to_test:
                report += f"  - {class_config['class_name']} ({class_config['module']})\n"
                
        if self.initialization_errors:
            report += "\n初期化エラー:\n"
            for error in self.initialization_errors:
                report += f"  - {error}\n"
        else:
            report += "\n全ての初期化テストが成功しました。\n"
            
        return report
        
    def set_strict_mode(self, enabled: bool):
        """厳密モード設定"""
        self.strict_mode = enabled
        
    def clear_modules(self):
        """モジュールリストクリア"""
        self.modules_to_test.clear()
        
    def clear_classes(self):
        """クラスリストクリア"""
        self.classes_to_test.clear()
        
    def clear_errors(self):
        """エラーリストクリア"""
        self.initialization_errors.clear()
        
    def get_error_count(self) -> int:
        """エラー数を取得"""
        return len(self.initialization_errors)
        
    def has_errors(self) -> bool:
        """エラーがあるかどうか"""
        return len(self.initialization_errors) > 0