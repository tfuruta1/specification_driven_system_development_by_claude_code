#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Structure Optimizer
インポート構造の最適化と循環依存の検出・修正
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque


class ImportAnalyzer:
    """インポート構造分析クラス"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.modules = {}
        self.dependencies = defaultdict(set)
        
    def analyze_file(self, file_path: Path) -> Dict[str, Set[str]]:
        """ファイルのインポート分析"""
        if not file_path.exists() or file_path.suffix != '.py':
            return {}
            
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return {}
        
        imports = {
            'absolute': set(),
            'relative': set(),
            'standard': set()
        }
        
        # インポートパターンの正規表現
        patterns = {
            'from_relative': r'^from\s+\.([\w\.]+)\s+import',
            'from_absolute': r'^from\s+([\w\.]+)\s+import',
            'import_absolute': r'^import\s+([\w\.]+)',
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 相対インポート
            match = re.match(patterns['from_relative'], line)
            if match:
                imports['relative'].add(match.group(1))
                continue
                
            # 絶対インポート (from)
            match = re.match(patterns['from_absolute'], line)
            if match:
                module = match.group(1)
                if module.startswith('.'):
                    imports['relative'].add(module[1:])
                elif '.' not in module or module in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'collections', 'tempfile', 'shutil', 'unittest', 'uuid', 're']:
                    imports['standard'].add(module)
                else:
                    imports['absolute'].add(module)
                continue
                
            # 絶対インポート (import)
            match = re.match(patterns['import_absolute'], line)
            if match:
                module = match.group(1)
                if '.' not in module or module in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'collections', 'tempfile', 'shutil', 'unittest', 'uuid', 're']:
                    imports['standard'].add(module)
                else:
                    imports['absolute'].add(module)
        
        return imports
    
    def analyze_directory(self) -> None:
        """ディレクトリ全体のインポート分析"""
        for py_file in self.base_path.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
                
            module_name = py_file.stem
            imports = self.analyze_file(py_file)
            self.modules[module_name] = imports
            
            # 依存関係グラフの構築
            for relative_import in imports['relative']:
                self.dependencies[module_name].add(relative_import)
    
    def detect_circular_imports(self) -> List[List[str]]:
        """循環インポートの検出"""
        def dfs(node: str, path: List[str], visited: Set[str]) -> List[List[str]]:
            if node in path:
                # 循環を発見
                cycle_start = path.index(node)
                return [path[cycle_start:] + [node]]
            
            if node in visited:
                return []
            
            visited.add(node)
            cycles = []
            
            for dependency in self.dependencies.get(node, []):
                cycles.extend(dfs(dependency, path + [node], visited))
            
            return cycles
        
        all_cycles = []
        visited = set()
        
        for module in self.modules.keys():
            if module not in visited:
                cycles = dfs(module, [], set())
                all_cycles.extend(cycles)
                visited.add(module)
        
        return all_cycles
    
    def get_dependency_layers(self) -> Dict[int, List[str]]:
        """依存関係の階層分析"""
        # トポロジカルソートによる階層化
        in_degree = defaultdict(int)
        
        for module in self.modules.keys():
            for dependency in self.dependencies.get(module, []):
                in_degree[dependency] += 1
        
        # 依存関係のないモジュールを第0層とする
        layers = defaultdict(list)
        queue = deque()
        
        for module in self.modules.keys():
            if in_degree[module] == 0:
                layers[0].append(module)
                queue.append((module, 0))
        
        while queue:
            current_module, layer = queue.popleft()
            
            for dependency in self.dependencies.get(current_module, []):
                in_degree[dependency] -= 1
                if in_degree[dependency] == 0:
                    layers[layer + 1].append(dependency)
                    queue.append((dependency, layer + 1))
        
        return dict(layers)
    
    def generate_report(self) -> str:
        """分析レポートの生成"""
        report_lines = [
            "=== Import Structure Analysis Report ===",
            f"分析対象: {self.base_path}",
            f"モジュール数: {len(self.modules)}",
            ""
        ]
        
        # 循環インポートの検出
        circular_imports = self.detect_circular_imports()
        if circular_imports:
            report_lines.extend([
                "⚠ 循環インポートが検出されました:",
                ""
            ])
            for i, cycle in enumerate(circular_imports, 1):
                report_lines.append(f"循環 {i}: {' -> '.join(cycle)}")
            report_lines.append("")
        else:
            report_lines.extend([
                "✓ 循環インポートは検出されませんでした",
                ""
            ])
        
        # 依存関係階層
        layers = self.get_dependency_layers()
        report_lines.extend([
            "依存関係階層:",
            ""
        ])
        
        for layer_num in sorted(layers.keys()):
            modules = layers[layer_num]
            report_lines.append(f"Layer {layer_num}: {', '.join(modules)}")
        
        report_lines.append("")
        
        # モジュール別詳細
        report_lines.extend([
            "モジュール別インポート詳細:",
            ""
        ])
        
        for module_name, imports in self.modules.items():
            report_lines.append(f"{module_name}:")
            if imports['standard']:
                report_lines.append(f"  標準ライブラリ: {', '.join(sorted(imports['standard']))}")
            if imports['relative']:
                report_lines.append(f"  相対インポート: {', '.join(sorted(imports['relative']))}")
            if imports['absolute']:
                report_lines.append(f"  絶対インポート: {', '.join(sorted(imports['absolute']))}")
            report_lines.append("")
        
        return '\n'.join(report_lines)


def main():
    """メイン実行関数"""
    base_path = Path('.claude/core')
    
    if not base_path.exists():
        print(f"エラー: {base_path} が見つかりません")
        return
    
    print("=== Import Structure Optimization ===")
    print(f"分析対象: {base_path.absolute()}")
    print("")
    
    # 分析実行
    analyzer = ImportAnalyzer(base_path)
    analyzer.analyze_directory()
    
    # レポート生成・表示
    report = analyzer.generate_report()
    print(report)
    
    # レポートファイルに保存
    report_file = base_path / 'import_analysis_report.txt'
    try:
        report_file.write_text(report, encoding='utf-8')
        print(f"レポートを保存しました: {report_file}")
    except Exception as e:
        print(f"レポート保存エラー: {e}")
    
    # 循環インポートがある場合は警告
    circular_imports = analyzer.detect_circular_imports()
    if circular_imports:
        print("\n⚠ 注意: 循環インポートが検出されました。修正が必要です。")
        return False
    else:
        print("\n✓ インポート構造は最適化されています。")
        return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)