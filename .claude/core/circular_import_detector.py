"""
循環インポート検出モジュール - Claude Code Core
IntegrationTestRunnerから分離された循環参照検出機能
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Set, Optional


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
        
    def get_analysis_summary(self) -> str:
        """解析結果サマリー"""
        summary = f"循環参照検出結果:\n"
        summary += f"検査したモジュール数: {len(self.visited_modules)}\n"
        summary += f"検出された循環参照数: {len(self.circular_imports)}\n"
        
        if self.circular_imports:
            summary += "\n循環参照詳細:\n"
            for i, circular in enumerate(self.circular_imports, 1):
                summary += f"  {i}. {circular}\n"
        else:
            summary += "\n循環参照は検出されませんでした。\n"
            
        return summary