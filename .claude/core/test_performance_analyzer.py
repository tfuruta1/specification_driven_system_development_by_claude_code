#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Performance Analyzer
テストパフォーマンス分析ツール
"""

import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import importlib


class TestPerformanceAnalyzer:
    """テストパフォーマンス分析クラス"""
    
    def __init__(self, core_path: Path):
        self.core_path = core_path
        self.results: Dict[str, Dict] = {}
        
    def measure_import_time(self, module_name: str) -> Tuple[bool, float, str]:
        """モジュールインポート時間測定"""
        start_time = time.perf_counter()
        error_msg = ""
        success = False
        
        try:
            # パス設定
            sys.path.insert(0, str(self.core_path))
            
            # インポート実行
            module = importlib.import_module(module_name)
            success = True
            
        except Exception as e:
            error_msg = str(e)
            
        end_time = time.perf_counter()
        import_time = end_time - start_time
        
        return success, import_time, error_msg
    
    def analyze_test_files(self) -> Dict[str, Dict]:
        """テストファイル分析"""
        test_files = list(self.core_path.glob('test_*.py'))
        
        for test_file in test_files:
            module_name = test_file.stem
            
            # ファイルサイズ
            file_size = test_file.stat().st_size
            
            # 行数カウント
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
            except:
                lines = 0
            
            # インポート時間測定
            success, import_time, error = self.measure_import_time(module_name)
            
            self.results[module_name] = {
                'file_size': file_size,
                'lines': lines,
                'import_time': import_time,
                'import_success': success,
                'import_error': error
            }
            
        return self.results
    
    def analyze_core_modules(self) -> Dict[str, Dict]:
        """コアモジュール分析"""
        core_modules = [
            'auto_mode_core',
            'auto_mode_config', 
            'auto_mode_state',
            'auto_mode_interfaces'
        ]
        
        for module_name in core_modules:
            module_file = self.core_path / f"{module_name}.py"
            
            if module_file.exists():
                # ファイルサイズ
                file_size = module_file.stat().st_size
                
                # 行数カウント
                try:
                    with open(module_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                except:
                    lines = 0
                
                # インポート時間測定
                success, import_time, error = self.measure_import_time(module_name)
                
                self.results[f"core_{module_name}"] = {
                    'file_size': file_size,
                    'lines': lines,
                    'import_time': import_time,
                    'import_success': success,
                    'import_error': error
                }
        
        return self.results
    
    def calculate_performance_metrics(self) -> Dict:
        """パフォーマンスメトリクス計算"""
        if not self.results:
            return {}
            
        successful_imports = [r for r in self.results.values() if r['import_success']]
        failed_imports = [r for r in self.results.values() if not r['import_success']]
        
        metrics = {
            'total_files': len(self.results),
            'successful_imports': len(successful_imports),
            'failed_imports': len(failed_imports),
            'success_rate': len(successful_imports) / len(self.results) * 100 if self.results else 0,
            'average_import_time': sum(r['import_time'] for r in successful_imports) / len(successful_imports) if successful_imports else 0,
            'total_file_size': sum(r['file_size'] for r in self.results.values()),
            'total_lines': sum(r['lines'] for r in self.results.values()),
            'fastest_import': min(r['import_time'] for r in successful_imports) if successful_imports else 0,
            'slowest_import': max(r['import_time'] for r in successful_imports) if successful_imports else 0
        }
        
        return metrics
    
    def generate_performance_report(self) -> str:
        """パフォーマンスレポート生成"""
        metrics = self.calculate_performance_metrics()
        
        report = []
        report.append("=" * 80)
        report.append("TEST PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        if not metrics:
            report.append("No performance data available")
            return "\n".join(report)
        
        # 基本統計
        report.append("BASIC PERFORMANCE METRICS:")
        report.append(f"  Total Files Analyzed: {metrics['total_files']}")
        report.append(f"  Successful Imports: {metrics['successful_imports']}")
        report.append(f"  Failed Imports: {metrics['failed_imports']}")
        report.append(f"  Success Rate: {metrics['success_rate']:.1f}%")
        report.append("")
        
        # インポート時間
        report.append("IMPORT PERFORMANCE:")
        report.append(f"  Average Import Time: {metrics['average_import_time']:.4f}s")
        report.append(f"  Fastest Import: {metrics['fastest_import']:.4f}s")
        report.append(f"  Slowest Import: {metrics['slowest_import']:.4f}s")
        report.append("")
        
        # ファイルサイズ統計
        report.append("FILE SIZE STATISTICS:")
        report.append(f"  Total File Size: {metrics['total_file_size']:,} bytes ({metrics['total_file_size']/1024:.1f} KB)")
        report.append(f"  Total Lines of Code: {metrics['total_lines']:,}")
        report.append(f"  Average File Size: {metrics['total_file_size']/metrics['total_files']:.0f} bytes")
        report.append("")
        
        # 詳細結果
        report.append("DETAILED RESULTS:")
        report.append(f"{'Module':<30} {'Size(KB)':<10} {'Lines':<8} {'Import(ms)':<12} {'Status':<10}")
        report.append("-" * 70)
        
        for module_name, data in sorted(self.results.items()):
            size_kb = data['file_size'] / 1024
            import_ms = data['import_time'] * 1000
            status = "SUCCESS" if data['import_success'] else "FAILED"
            
            report.append(f"{module_name:<30} {size_kb:<10.1f} {data['lines']:<8} {import_ms:<12.2f} {status:<10}")
        
        # 失敗した インポート
        failed_modules = [(name, data) for name, data in self.results.items() if not data['import_success']]
        if failed_modules:
            report.append("")
            report.append("IMPORT FAILURES:")
            for module_name, data in failed_modules:
                report.append(f"  {module_name}: {data['import_error']}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """メイン実行関数"""
    core_path = Path(__file__).parent
    analyzer = TestPerformanceAnalyzer(core_path)
    
    print("Analyzing test file performance...")
    analyzer.analyze_test_files()
    
    print("Analyzing core module performance...")
    analyzer.analyze_core_modules()
    
    print("Generating performance report...")
    report = analyzer.generate_performance_report()
    
    print(report)
    
    # レポートファイル出力
    report_file = core_path / "test_performance_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_file}")


if __name__ == '__main__':
    main()