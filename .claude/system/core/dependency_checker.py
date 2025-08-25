#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依存関係チェッカー統合モジュール - DRY原則適用
circular_import_detector.py, verify_circular_dependency_resolution.py, 
verify_circular_resolution.py を統合

YAGNI: 現在使用されている機能のみを統合
DRY: 重複する循環依存チェック機能を統合
KISS: シンプルな依存関係検証インターフェース
TDD: テスト可能な最小限の実装
"""

import os
import ast
import sys
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    from .common_base import BaseResult, create_result
    from .logger import logger
except ImportError:
    from common_base import BaseResult, create_result
    from logger import logger


@dataclass
class DependencyCheckResult:
    """依存関係チェック結果"""
    has_circular_deps: bool = False
    circular_paths: List[List[str]] = None
    total_modules: int = 0
    checked_modules: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.circular_paths is None:
            self.circular_paths = []
        if self.errors is None:
            self.errors = []


class UnifiedDependencyChecker:
    """統合依存関係チェッカー - KISS原則に基づく最小実装"""
    
    def __init__(self, root_path: Optional[Path] = None):
        """初期化"""
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.visited: Set[str] = set()
        self.current_path: List[str] = []
        
    def check_all_dependencies(self) -> DependencyCheckResult:
        """全依存関係をチェック - メインエントリーポイント"""
        result = DependencyCheckResult()
        
        try:
            # Python ファイルを探索
            python_files = list(self.root_path.rglob("*.py"))
            result.total_modules = len(python_files)
            
            # 循環依存をチェック
            circular_paths = self._detect_circular_imports(python_files)
            result.circular_paths = circular_paths
            result.has_circular_deps = len(circular_paths) > 0
            result.checked_modules = len(self.visited)
            
            if result.has_circular_deps:
                logger.warning(f"Circular dependencies detected: {len(circular_paths)}")
            else:
                logger.info("No circular dependencies found")
                
        except Exception as e:
            result.errors.append(f"Dependency check failed: {e}")
            logger.error(f"Dependency check error: {e}")
            
        return result
    
    def _detect_circular_imports(self, python_files: List[Path]) -> List[List[str]]:
        """循環依存を検出 - 簡素化されたアルゴリズム"""
        circular_paths = []
        
        for py_file in python_files:
            if py_file.suffix != '.py':
                continue
                
            module_name = self._get_module_name(py_file)
            if module_name and module_name not in self.visited:
                path = self._check_module_circular(py_file, module_name, [])
                if path:
                    circular_paths.append(path)
                    
        return circular_paths
    
    def _check_module_circular(self, file_path: Path, module_name: str, 
                             path_stack: List[str]) -> Optional[List[str]]:
        """モジュールの循環依存をチェック"""
        if module_name in path_stack:
            # 循環依存発見
            cycle_start = path_stack.index(module_name)
            return path_stack[cycle_start:] + [module_name]
            
        if module_name in self.visited:
            return None
            
        self.visited.add(module_name)
        new_stack = path_stack + [module_name]
        
        try:
            # ファイルの import を解析
            imports = self._extract_imports(file_path)
            
            for imported_module in imports:
                imported_path = self._resolve_import_path(imported_module, file_path)
                if imported_path and imported_path.exists():
                    imported_name = self._get_module_name(imported_path)
                    if imported_name:
                        circular = self._check_module_circular(
                            imported_path, imported_name, new_stack
                        )
                        if circular:
                            return circular
                            
        except Exception as e:
            logger.debug(f"Error checking {module_name}: {e}")
            
        return None
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """ファイルから import 文を抽出 - 最小限の実装"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # AST を使用せず、正規表現で簡単に抽出
            import_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('from ') and 'import' in line:
                    import_lines.append(line)
                elif line.startswith('import '):
                    import_lines.append(line)
                    
            for line in import_lines:
                if line.startswith('from '):
                    # from module import something
                    parts = line.split()
                    if len(parts) >= 2:
                        module = parts[1]
                        if not module.startswith('.'):  # 相対importは除外
                            imports.append(module)
                elif line.startswith('import '):
                    # import module
                    parts = line.split()
                    for part in parts[1:]:
                        if ',' in part:
                            for sub in part.split(','):
                                imports.append(sub.strip())
                        else:
                            imports.append(part)
                            
        except Exception as e:
            logger.debug(f"Error extracting imports from {file_path}: {e}")
            
        return imports
    
    def _get_module_name(self, file_path: Path) -> Optional[str]:
        """ファイルパスからモジュール名を取得"""
        try:
            relative_path = file_path.relative_to(self.root_path)
            parts = relative_path.parts[:-1] + (relative_path.stem,)
            return '.'.join(parts)
        except ValueError:
            return file_path.stem
    
    def _resolve_import_path(self, module_name: str, current_file: Path) -> Optional[Path]:
        """モジュール名からファイルパスを解決 - 簡素化版"""
        # 同じディレクトリから検索
        current_dir = current_file.parent
        
        # モジュール名を相対パスに変換
        module_parts = module_name.split('.')
        potential_path = current_dir
        
        for part in module_parts:
            potential_path = potential_path / part
            
        # .py ファイルを探す
        py_file = potential_path.with_suffix('.py')
        if py_file.exists():
            return py_file
            
        # __init__.py があるディレクトリを探す
        init_file = potential_path / '__init__.py'
        if init_file.exists():
            return init_file
            
        return None


def check_dependencies(root_path: Optional[str] = None) -> DependencyCheckResult:
    """依存関係チェックのメインエントリーポイント"""
    checker = UnifiedDependencyChecker(root_path)
    return checker.check_all_dependencies()


def main():
    """コマンドライン実行用メイン関数"""
    print("Unified Dependency Checker")
    print("=" * 40)
    
    root = sys.argv[1] if len(sys.argv) > 1 else None
    result = check_dependencies(root)
    
    print(f"Total modules: {result.total_modules}")
    print(f"Checked modules: {result.checked_modules}")
    
    if result.has_circular_deps:
        print(f"\nCircular dependencies found: {len(result.circular_paths)}")
        for i, path in enumerate(result.circular_paths, 1):
            print(f"  {i}. {' -> '.join(path)}")
        return 1
    else:
        print("\nNo circular dependencies detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())