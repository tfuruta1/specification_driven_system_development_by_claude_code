#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Analysis Tool
依存関係分析ツール
"""

import ast
import os
from pathlib import Path
from typing import Dict, Set, List, Tuple
import re


class DependencyAnalyzer:
    """依存関係分析クラス"""
    
    def __init__(self, core_path: Path):
        self.core_path = core_path
        self.dependencies: Dict[str, Set[str]] = {}
        self.file_info: Dict[str, Dict] = {}
        
    def analyze_file(self, file_path: Path) -> Dict:
        """ファイル分析"""
        info = {
            'imports': set(),
            'functions': [],
            'classes': [],
            'lines': 0,
            'complexity': 0
        }
        
        if not file_path.exists():
            return info
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            info['lines'] = len(content.splitlines())
            
            # AST分析
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            if node.module.startswith('.'):
                                # 相対インポート
                                module_name = node.module[1:] if node.module.startswith('.') else node.module
                                info['imports'].add(module_name)
                            elif 'auto_mode' in node.module:
                                info['imports'].add(node.module)
                                
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if 'auto_mode' in alias.name:
                                info['imports'].add(alias.name)
                                
                    elif isinstance(node, ast.FunctionDef):
                        info['functions'].append(node.name)
                        
                    elif isinstance(node, ast.ClassDef):
                        info['classes'].append(node.name)
                        
                    # 複雑度計算（簡易版）
                    elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                        info['complexity'] += 1
                        
            except SyntaxError:
                pass  # 構文エラーは無視
                
            # 遅延インポート検出
            lazy_imports = re.findall(r'from\s+\.(\w+)\s+import', content)
            info['lazy_imports'] = lazy_imports
            
            # シングルトンパターン検出
            singleton_pattern = 'auto_config' in content or 'auto_state' in content
            info['uses_singleton'] = singleton_pattern
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return info
    
    def build_dependency_graph(self) -> Dict[str, Dict]:
        """依存関係グラフ構築"""
        python_files = list(self.core_path.glob('*.py'))
        
        for file_path in python_files:
            if file_path.name.startswith('test_'):
                continue
                
            module_name = file_path.stem
            info = self.analyze_file(file_path)
            
            self.file_info[module_name] = info
            self.dependencies[module_name] = info['imports']
            
        return self.file_info
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """循環依存検出"""
        cycles = []
        visited = set()
        
        def dfs(node: str, path: List[str], recursion_stack: Set[str]) -> bool:
            if node in recursion_stack:
                # 循環検出
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
                
            if node in visited:
                return False
                
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor in self.dependencies:  # 分析済みモジュールのみ
                    dfs(neighbor, path + [neighbor], recursion_stack.copy())
                    
            recursion_stack.remove(node)
            return False
            
        for module in self.dependencies:
            if module not in visited:
                dfs(module, [module], set())
                
        return cycles
    
    def calculate_metrics(self) -> Dict:
        """品質メトリクス計算"""
        metrics = {
            'total_files': len(self.file_info),
            'total_lines': sum(info['lines'] for info in self.file_info.values()),
            'average_complexity': 0,
            'max_complexity': 0,
            'files_with_lazy_imports': 0,
            'files_with_singletons': 0,
            'dependency_count': sum(len(deps) for deps in self.dependencies.values()),
            'modules_with_most_dependencies': []
        }
        
        complexities = [info['complexity'] for info in self.file_info.values()]
        if complexities:
            metrics['average_complexity'] = sum(complexities) / len(complexities)
            metrics['max_complexity'] = max(complexities)
            
        for module, info in self.file_info.items():
            if info.get('lazy_imports'):
                metrics['files_with_lazy_imports'] += 1
                
            if info.get('uses_singleton'):
                metrics['files_with_singletons'] += 1
                
        # 最も依存関係の多いモジュール
        dep_counts = [(module, len(deps)) for module, deps in self.dependencies.items()]
        dep_counts.sort(key=lambda x: x[1], reverse=True)
        metrics['modules_with_most_dependencies'] = dep_counts[:5]
        
        return metrics
    
    def generate_report(self) -> str:
        """レポート生成"""
        cycles = self.find_circular_dependencies()
        metrics = self.calculate_metrics()
        
        report = []
        report.append("=" * 80)
        report.append("DEPENDENCY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # 基本統計
        report.append("BASIC STATISTICS:")
        report.append(f"  Total Files: {metrics['total_files']}")
        report.append(f"  Total Lines: {metrics['total_lines']}")
        report.append(f"  Average Complexity: {metrics['average_complexity']:.2f}")
        report.append(f"  Max Complexity: {metrics['max_complexity']}")
        report.append(f"  Total Dependencies: {metrics['dependency_count']}")
        report.append("")
        
        # 循環依存チェック
        report.append("CIRCULAR DEPENDENCY CHECK:")
        if cycles:
            report.append(f"  FOUND {len(cycles)} CIRCULAR DEPENDENCIES:")
            for i, cycle in enumerate(cycles, 1):
                report.append(f"    Cycle {i}: {' -> '.join(cycle)}")
        else:
            report.append("  No circular dependencies detected")
        report.append("")
        
        # 遅延インポート状況
        report.append("LAZY IMPORT STATUS:")
        report.append(f"  Files with lazy imports: {metrics['files_with_lazy_imports']}")
        for module, info in self.file_info.items():
            if info.get('lazy_imports'):
                report.append(f"    {module}: {info['lazy_imports']}")
        report.append("")
        
        # 依存関係の多いモジュール
        report.append("MODULES WITH MOST DEPENDENCIES:")
        for module, count in metrics['modules_with_most_dependencies']:
            report.append(f"  {module}: {count} dependencies")
            deps = list(self.dependencies.get(module, []))[:5]  # 最初の5つ
            if deps:
                report.append(f"    -> {', '.join(deps)}")
        report.append("")
        
        # 詳細依存関係マップ
        report.append("DEPENDENCY MAP:")
        for module in sorted(self.dependencies.keys()):
            deps = self.dependencies[module]
            if deps:
                report.append(f"  {module} -> {', '.join(sorted(deps))}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """メイン実行関数"""
    core_path = Path(__file__).parent
    analyzer = DependencyAnalyzer(core_path)
    
    print("Building dependency graph...")
    analyzer.build_dependency_graph()
    
    print("Generating report...")
    report = analyzer.generate_report()
    
    print(report)
    
    # レポートファイル出力
    report_file = core_path / "dependency_analysis_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_file}")


if __name__ == '__main__':
    main()