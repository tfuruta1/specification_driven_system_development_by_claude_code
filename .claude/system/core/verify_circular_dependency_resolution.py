#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circular Dependency Resolution Verification Script
循環依存解消検証スクリプト
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


class CircularImportAnalyzer:
    """循環インポート分析クラス"""
    
    def __init__(self, core_path: Path):
        self.core_path = core_path
        self.import_graph: Dict[str, Set[str]] = {}
        
    def analyze_file_imports(self, file_path: Path) -> Set[str]:
        """ファイルのインポート依存関係を分析"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('.'):
                        # 相対インポート
                        module_name = node.module[1:]  # Remove leading dot
                        imports.add(module_name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('.'):
                            module_name = alias.name[1:]
                            imports.add(module_name)
                            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return imports
    
    def build_import_graph(self):
        """インポートグラフ構築"""
        target_files = [
            'auto_mode_core.py',
            'auto_mode_config.py', 
            'auto_mode_state.py',
            'auto_mode_interfaces.py'
        ]
        
        for file_name in target_files:
            file_path = self.core_path / file_name
            if file_path.exists():
                module_name = file_name[:-3]  # Remove .py
                imports = self.analyze_file_imports(file_path)
                self.import_graph[module_name] = imports
                
    def find_circular_imports(self) -> List[List[str]]:
        """循環インポートの検出"""
        visited = set()
        recursion_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in recursion_stack:
                # 循環発見
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
                
            if node in visited:
                return False
                
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)
            
            for neighbor in self.import_graph.get(node, []):
                if neighbor in self.import_graph:  # Only consider analyzed modules
                    dfs(neighbor, path.copy())
                    
            recursion_stack.remove(node)
            return False
            
        for module in self.import_graph:
            if module not in visited:
                dfs(module, [])
                
        return cycles
    
    def check_lazy_import_elimination(self) -> Tuple[bool, List[str]]:
        """遅延インポートの除去確認"""
        core_file = self.core_path / 'auto_mode_core.py'
        
        if not core_file.exists():
            return False, ["auto_mode_core.py not found"]
            
        try:
            with open(core_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues = []
            
            # 遅延インポート関数の確認
            if '_get_auto_config' in content:
                issues.append("_get_auto_config lazy import function still exists")
                
            if '_get_auto_state' in content:
                issues.append("_get_auto_state lazy import function still exists")
                
            # 動的インポートの確認
            if 'from .auto_mode_config import auto_config' in content:
                issues.append("Direct singleton import from config module still exists")
                
            if 'from .auto_mode_state import auto_state' in content:
                issues.append("Direct singleton import from state module still exists")
                
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Error reading auto_mode_core.py: {e}"]
    
    def check_interface_usage(self) -> Tuple[bool, List[str]]:
        """インターフェース使用確認"""
        core_file = self.core_path / 'auto_mode_core.py'
        
        if not core_file.exists():
            return False, ["auto_mode_core.py not found"]
            
        try:
            with open(core_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues = []
            
            # インターフェースインポートの確認
            if 'from .auto_mode_interfaces import' not in content:
                issues.append("Interface imports not found in auto_mode_core.py")
                
            # サービスロケーター使用確認
            if 'get_config_service' not in content:
                issues.append("Service locator for config not used")
                
            if 'get_state_service' not in content:
                issues.append("Service locator for state not used")
                
            # 依存性注入パターン確認
            if '_config_service' not in content:
                issues.append("Dependency injection pattern not implemented for config")
                
            if '_state_service' not in content:
                issues.append("Dependency injection pattern not implemented for state")
                
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Error checking interface usage: {e}"]


def main():
    """メイン検証関数"""
    print("=== Circular Dependency Resolution Verification ===\n")
    
    core_path = Path(__file__).parent
    analyzer = CircularImportAnalyzer(core_path)
    
    # インポートグラフ構築
    print("1. Building import graph...")
    analyzer.build_import_graph()
    
    # インポートグラフ表示
    print("Import Graph:")
    for module, imports in analyzer.import_graph.items():
        print(f"  {module} -> {list(imports)}")
    print()
    
    # 循環インポート検出
    print("2. Checking for circular imports...")
    cycles = analyzer.find_circular_imports()
    
    if cycles:
        print(f"❌ Found {len(cycles)} circular import(s):")
        for i, cycle in enumerate(cycles, 1):
            print(f"  Cycle {i}: {' -> '.join(cycle)}")
    else:
        print("✅ No circular imports detected")
    print()
    
    # 遅延インポート除去確認
    print("3. Checking lazy import elimination...")
    lazy_removed, lazy_issues = analyzer.check_lazy_import_elimination()
    
    if lazy_removed:
        print("✅ All lazy imports successfully removed")
    else:
        print("❌ Lazy import issues found:")
        for issue in lazy_issues:
            print(f"  - {issue}")
    print()
    
    # インターフェース使用確認
    print("4. Checking interface implementation...")
    interface_ok, interface_issues = analyzer.check_interface_usage()
    
    if interface_ok:
        print("✅ Interface abstraction properly implemented")
    else:
        print("❌ Interface implementation issues found:")
        for issue in interface_issues:
            print(f"  - {issue}")
    print()
    
    # 総合結果
    print("=== SUMMARY ===")
    all_checks_passed = (
        len(cycles) == 0 and
        lazy_removed and
        interface_ok
    )
    
    if all_checks_passed:
        print("🎉 SUCCESS: Circular dependency resolution completed!")
        print("   - No circular imports detected")
        print("   - All lazy imports eliminated")
        print("   - Interface abstraction implemented")
    else:
        print("❌ ISSUES DETECTED: Please review the problems above")
        
    return all_checks_passed


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)