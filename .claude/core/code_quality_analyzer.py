#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Quality Analyzer
コード品質分析ツール
"""

import ast
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class CodeQualityAnalyzer:
    """コード品質分析クラス"""
    
    def __init__(self, core_path: Path):
        self.core_path = core_path
        self.quality_metrics: Dict[str, Dict] = {}
        
    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """循環複雑度計算"""
        complexity = 1  # 基本経路
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                
        return complexity
    
    def analyze_code_smells(self, content: str, file_path: Path) -> Dict[str, int]:
        """コードスメル検出"""
        smells = {
            'long_lines': 0,
            'long_functions': 0,
            'deep_nesting': 0,
            'duplicate_code_blocks': 0,
            'magic_numbers': 0,
            'god_class_methods': 0,
            'unused_imports': 0,
            'todo_comments': 0
        }
        
        lines = content.splitlines()
        
        # 長い行
        smells['long_lines'] = sum(1 for line in lines if len(line) > 120)
        
        # TODOコメント
        smells['todo_comments'] = sum(1 for line in lines if 'TODO' in line.upper() or 'FIXME' in line.upper())
        
        # マジックナンバー（簡易検出）
        magic_pattern = r'\b\d{2,}\b'
        smells['magic_numbers'] = len(re.findall(magic_pattern, content))
        
        try:
            tree = ast.parse(content)
            
            # 関数分析
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 長い関数（50行以上）
                    func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                    if func_lines > 50:
                        smells['long_functions'] += 1
                        
                elif isinstance(node, ast.ClassDef):
                    # God Class検出（メソッド数が多い）
                    method_count = sum(1 for child in node.body if isinstance(child, ast.FunctionDef))
                    if method_count > 20:
                        smells['god_class_methods'] += 1
                        
        except SyntaxError:
            pass
            
        return smells
    
    def calculate_maintainability_index(self, complexity: int, lines: int, vocabulary: int) -> float:
        """保守性指標計算（簡易版）"""
        if lines == 0 or vocabulary == 0:
            return 0.0
            
        # 簡略化された保守性指標計算
        mi = max(0, (171 - 5.2 * (complexity ** 0.23) - 0.23 * complexity - 16.2 * (lines ** 0.5)) * 100 / 171)
        return round(mi, 2)
    
    def analyze_file_quality(self, file_path: Path) -> Dict:
        """ファイル品質分析"""
        quality_data = {
            'file_size': 0,
            'lines_of_code': 0,
            'blank_lines': 0,
            'comment_lines': 0,
            'complexity': 0,
            'functions': [],
            'classes': [],
            'imports': [],
            'code_smells': {},
            'maintainability_index': 0.0,
            'technical_debt_ratio': 0.0
        }
        
        if not file_path.exists():
            return quality_data
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.splitlines()
            quality_data['file_size'] = len(content)
            quality_data['lines_of_code'] = len(lines)
            
            # 空行とコメント行計算
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    quality_data['blank_lines'] += 1
                elif stripped.startswith('#'):
                    quality_data['comment_lines'] += 1
                    
            # AST分析
            try:
                tree = ast.parse(content)
                
                # 全体の複雑度
                quality_data['complexity'] = self.calculate_cyclomatic_complexity(tree)
                
                # 関数とクラス情報
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_complexity = self.calculate_cyclomatic_complexity(node)
                        quality_data['functions'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'complexity': func_complexity
                        })
                        
                    elif isinstance(node, ast.ClassDef):
                        class_methods = sum(1 for child in node.body if isinstance(child, ast.FunctionDef))
                        quality_data['classes'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'methods': class_methods
                        })
                        
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            quality_data['imports'].append(node.module)
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                quality_data['imports'].append(alias.name)
                                
            except SyntaxError:
                pass
                
            # コードスメル分析
            quality_data['code_smells'] = self.analyze_code_smells(content, file_path)
            
            # 保守性指標計算
            vocabulary = len(set(quality_data['imports'] + [f['name'] for f in quality_data['functions']] + [c['name'] for c in quality_data['classes']]))
            quality_data['maintainability_index'] = self.calculate_maintainability_index(
                quality_data['complexity'], 
                quality_data['lines_of_code'], 
                max(vocabulary, 1)
            )
            
            # 技術的負債比率（簡易計算）
            total_smells = sum(quality_data['code_smells'].values())
            quality_data['technical_debt_ratio'] = min(100.0, (total_smells / max(quality_data['lines_of_code'], 1)) * 1000)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return quality_data
    
    def analyze_all_files(self) -> Dict[str, Dict]:
        """全ファイル品質分析"""
        python_files = list(self.core_path.glob('*.py'))
        
        for file_path in python_files:
            module_name = file_path.stem
            self.quality_metrics[module_name] = self.analyze_file_quality(file_path)
            
        return self.quality_metrics
    
    def calculate_system_metrics(self) -> Dict:
        """システム全体メトリクス計算"""
        if not self.quality_metrics:
            return {}
            
        metrics = {
            'total_files': len(self.quality_metrics),
            'total_lines': sum(m['lines_of_code'] for m in self.quality_metrics.values()),
            'total_size': sum(m['file_size'] for m in self.quality_metrics.values()),
            'average_complexity': 0,
            'max_complexity': 0,
            'total_functions': sum(len(m['functions']) for m in self.quality_metrics.values()),
            'total_classes': sum(len(m['classes']) for m in self.quality_metrics.values()),
            'average_maintainability': 0,
            'high_complexity_files': [],
            'low_maintainability_files': [],
            'total_technical_debt': 0,
            'code_smells_summary': defaultdict(int)
        }
        
        complexities = [m['complexity'] for m in self.quality_metrics.values() if m['complexity'] > 0]
        maintainabilities = [m['maintainability_index'] for m in self.quality_metrics.values() if m['maintainability_index'] > 0]
        
        if complexities:
            metrics['average_complexity'] = sum(complexities) / len(complexities)
            metrics['max_complexity'] = max(complexities)
            
        if maintainabilities:
            metrics['average_maintainability'] = sum(maintainabilities) / len(maintainabilities)
            
        # 高複雑度ファイル
        for module_name, data in self.quality_metrics.items():
            if data['complexity'] > 15:  # 閾値
                metrics['high_complexity_files'].append((module_name, data['complexity']))
                
            if data['maintainability_index'] < 20:  # 閾値
                metrics['low_maintainability_files'].append((module_name, data['maintainability_index']))
                
        # 技術的負債総計
        metrics['total_technical_debt'] = sum(m['technical_debt_ratio'] for m in self.quality_metrics.values())
        
        # コードスメル集計
        for module_data in self.quality_metrics.values():
            for smell_type, count in module_data['code_smells'].items():
                metrics['code_smells_summary'][smell_type] += count
                
        return metrics
    
    def generate_quality_report(self) -> str:
        """品質レポート生成"""
        system_metrics = self.calculate_system_metrics()
        
        report = []
        report.append("=" * 80)
        report.append("CODE QUALITY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        if not system_metrics:
            report.append("No quality data available")
            return "\n".join(report)
        
        # システム全体統計
        report.append("SYSTEM QUALITY METRICS:")
        report.append(f"  Total Files: {system_metrics['total_files']}")
        report.append(f"  Total Lines of Code: {system_metrics['total_lines']:,}")
        report.append(f"  Total File Size: {system_metrics['total_size']:,} bytes ({system_metrics['total_size']/1024:.1f} KB)")
        report.append(f"  Total Functions: {system_metrics['total_functions']}")
        report.append(f"  Total Classes: {system_metrics['total_classes']}")
        report.append("")
        
        # 複雑度統計
        report.append("COMPLEXITY METRICS:")
        report.append(f"  Average Complexity: {system_metrics['average_complexity']:.2f}")
        report.append(f"  Maximum Complexity: {system_metrics['max_complexity']}")
        report.append(f"  Average Maintainability Index: {system_metrics['average_maintainability']:.2f}")
        report.append("")
        
        # 高複雑度ファイル
        if system_metrics['high_complexity_files']:
            report.append("HIGH COMPLEXITY FILES (>15):")
            for module_name, complexity in sorted(system_metrics['high_complexity_files'], key=lambda x: x[1], reverse=True):
                report.append(f"  {module_name}: {complexity}")
            report.append("")
        
        # 低保守性ファイル
        if system_metrics['low_maintainability_files']:
            report.append("LOW MAINTAINABILITY FILES (<20):")
            for module_name, maintainability in sorted(system_metrics['low_maintainability_files'], key=lambda x: x[1]):
                report.append(f"  {module_name}: {maintainability:.2f}")
            report.append("")
        
        # コードスメル統計
        report.append("CODE SMELLS SUMMARY:")
        for smell_type, count in sorted(system_metrics['code_smells_summary'].items()):
            if count > 0:
                report.append(f"  {smell_type.replace('_', ' ').title()}: {count}")
        report.append("")
        
        # 技術的負債
        report.append("TECHNICAL DEBT:")
        report.append(f"  Total Technical Debt Ratio: {system_metrics['total_technical_debt']:.2f}")
        avg_debt = system_metrics['total_technical_debt'] / system_metrics['total_files']
        report.append(f"  Average Debt per File: {avg_debt:.2f}")
        report.append("")
        
        # 詳細ファイル分析
        report.append("DETAILED FILE ANALYSIS:")
        report.append(f"{'Module':<25} {'Lines':<8} {'Complex':<8} {'Maintain':<9} {'Debt':<8} {'Functions':<10}")
        report.append("-" * 75)
        
        for module_name in sorted(self.quality_metrics.keys()):
            data = self.quality_metrics[module_name]
            report.append(f"{module_name:<25} {data['lines_of_code']:<8} {data['complexity']:<8} {data['maintainability_index']:<9.1f} {data['technical_debt_ratio']:<8.1f} {len(data['functions']):<10}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """メイン実行関数"""
    core_path = Path(__file__).parent
    analyzer = CodeQualityAnalyzer(core_path)
    
    print("Analyzing code quality...")
    analyzer.analyze_all_files()
    
    print("Generating quality report...")
    report = analyzer.generate_quality_report()
    
    print(report)
    
    # レポートファイル出力
    report_file = core_path / "code_quality_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_file}")


if __name__ == '__main__':
    main()