#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KISS原則チェッカー - Phase 3テスト戦略統一版
Keep It Simple, Stupid 原則の適用状況を監視・評価

KISS原則チェック項目:
1. テストメソッドの複雑度
2. ファイル行数の適切性  
3. メソッド数の適切性
4. 命名規則の明確性
5. アサーション数の適切性
"""

import ast
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class KISSViolationType(Enum):
    """KISS原則違反タイプ"""
    TOO_COMPLEX = "too_complex"              # 複雑すぎる
    TOO_LONG = "too_long"                    # 長すぎる
    TOO_MANY_METHODS = "too_many_methods"    # メソッド数過多
    UNCLEAR_NAMING = "unclear_naming"        # 不明確な命名
    TOO_MANY_ASSERTIONS = "too_many_assertions"  # アサーション過多


@dataclass
class KISSViolation:
    """KISS原則違反情報"""
    violation_type: KISSViolationType
    file_path: str
    line_number: int
    method_name: str
    description: str
    current_value: Any
    recommended_value: Any
    severity: str = "medium"  # low, medium, high


@dataclass 
class KISSMetrics:
    """KISS原則メトリクス"""
    file_path: str
    total_lines: int = 0
    method_count: int = 0
    max_method_lines: int = 0
    max_method_complexity: int = 0
    average_method_lines: float = 0.0
    violations: List[KISSViolation] = field(default_factory=list)
    
    @property
    def compliance_score(self) -> float:
        """KISS準拠スコア (0-100)"""
        if not self.violations:
            return 100.0
            
        # 違反の重みづけ
        severity_weights = {"low": 1, "medium": 3, "high": 5}
        total_penalty = sum(severity_weights[v.severity] for v in self.violations)
        
        # スコア計算 (100から違反ペナルティを引く)
        score = max(0, 100 - (total_penalty * 2))
        return score


class KISSPrincipleChecker:
    """
    KISS原則チェッカー
    
    シンプルで明確なテストコードを維持するための品質監視ツール
    """
    
    def __init__(self):
        """初期化"""
        # KISS原則の基準値
        self.standards = {
            "max_file_lines": 500,           # 1ファイル最大行数
            "max_method_lines": 30,          # 1メソッド最大行数  
            "max_methods_per_class": 20,     # 1クラス最大メソッド数
            "max_assertions_per_test": 5,    # 1テスト最大アサーション数
            "max_cyclomatic_complexity": 10  # 循環複雑度
        }
        
        # 明確な命名パターン
        self.clear_naming_patterns = {
            "test_methods": r"^test_[a-z_]+_(red|green|refactor|[a-z_]+)$",
            "helper_methods": r"^_[a-z_]+$",
            "setup_teardown": r"^(setUp|tearDown|setUpClass|tearDownClass)$"
        }
        
    def check_directory(self, directory_path: str) -> Dict[str, KISSMetrics]:
        """ディレクトリ内のテストファイルをKISS原則でチェック"""
        results = {}
        
        test_files = self._find_test_files(directory_path)
        
        for test_file in test_files:
            metrics = self._check_file(test_file)
            results[str(test_file)] = metrics
            
        return results
        
    def _find_test_files(self, directory_path: str) -> List[Path]:
        """テストファイルを検索"""
        directory = Path(directory_path)
        
        if not directory.exists():
            return []
            
        # test_*.py パターンのファイルを検索
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(directory.rglob(pattern))
            
        return test_files
        
    def _check_file(self, file_path: Path) -> KISSMetrics:
        """単一ファイルのKISS原則チェック"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
        except Exception as e:
            # ファイル読み込みエラー
            return KISSMetrics(
                file_path=str(file_path),
                violations=[KISSViolation(
                    violation_type=KISSViolationType.TOO_COMPLEX,
                    file_path=str(file_path),
                    line_number=0,
                    method_name="<file>",
                    description=f"File read error: {e}",
                    current_value=str(e),
                    recommended_value="Fix file encoding or permissions",
                    severity="high"
                )]
            )
            
        metrics = KISSMetrics(
            file_path=str(file_path),
            total_lines=len(lines)
        )
        
        # ASTを使用したコード解析
        try:
            tree = ast.parse(content)
            self._analyze_ast(tree, metrics, lines)
            
        except SyntaxError as e:
            metrics.violations.append(KISSViolation(
                violation_type=KISSViolationType.TOO_COMPLEX,
                file_path=str(file_path),
                line_number=e.lineno or 0,
                method_name="<syntax>",
                description=f"Syntax error: {e.msg}",
                current_value="Syntax error",
                recommended_value="Fix syntax errors",
                severity="high"
            ))
            
        # ファイルレベルのチェック
        self._check_file_complexity(metrics)
        
        return metrics
        
    def _analyze_ast(self, tree: ast.AST, metrics: KISSMetrics, lines: List[str]):
        """AST解析によるKISS原則チェック"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node, metrics, lines)
            elif isinstance(node, ast.FunctionDef):
                self._analyze_function(node, metrics, lines)
                
    def _analyze_class(self, class_node: ast.ClassDef, metrics: KISSMetrics, lines: List[str]):
        """クラス解析"""
        # メソッド数カウント
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        method_count = len(methods)
        metrics.method_count = method_count
        
        # メソッド数チェック
        if method_count > self.standards["max_methods_per_class"]:
            metrics.violations.append(KISSViolation(
                violation_type=KISSViolationType.TOO_MANY_METHODS,
                file_path=metrics.file_path,
                line_number=class_node.lineno,
                method_name=class_node.name,
                description=f"Class has too many methods ({method_count})",
                current_value=method_count,
                recommended_value=self.standards["max_methods_per_class"],
                severity="medium"
            ))
            
        # 各メソッドの解析
        method_lines = []
        for method in methods:
            method_line_count = self._count_method_lines(method, lines)
            method_lines.append(method_line_count)
            
            # メソッド行数チェック
            if method_line_count > self.standards["max_method_lines"]:
                metrics.violations.append(KISSViolation(
                    violation_type=KISSViolationType.TOO_LONG,
                    file_path=metrics.file_path,
                    line_number=method.lineno,
                    method_name=method.name,
                    description=f"Method too long ({method_line_count} lines)",
                    current_value=method_line_count,
                    recommended_value=self.standards["max_method_lines"],
                    severity="medium"
                ))
                
            # 命名規則チェック
            self._check_method_naming(method, metrics)
            
            # テストメソッドの場合はアサーション数チェック
            if method.name.startswith('test_'):
                self._check_test_method_assertions(method, metrics)
                
        # メトリクス更新
        if method_lines:
            metrics.max_method_lines = max(method_lines)
            metrics.average_method_lines = sum(method_lines) / len(method_lines)
            
    def _analyze_function(self, func_node: ast.FunctionDef, metrics: KISSMetrics, lines: List[str]):
        """関数解析（クラス外の関数）"""
        method_line_count = self._count_method_lines(func_node, lines)
        
        if method_line_count > self.standards["max_method_lines"]:
            metrics.violations.append(KISSViolation(
                violation_type=KISSViolationType.TOO_LONG,
                file_path=metrics.file_path,
                line_number=func_node.lineno,
                method_name=func_node.name,
                description=f"Function too long ({method_line_count} lines)",
                current_value=method_line_count,
                recommended_value=self.standards["max_method_lines"],
                severity="medium"
            ))
            
    def _count_method_lines(self, method_node: ast.FunctionDef, lines: List[str]) -> int:
        """メソッドの実際の行数を計算（空行・コメント除く）"""
        start_line = method_node.lineno - 1  # 0-based index
        
        # メソッドの終了行を見つける
        end_line = start_line
        for i, line in enumerate(lines[start_line:], start_line):
            if line.strip() and not line.startswith(' ') and not line.startswith('\t') and i > start_line:
                break
            end_line = i
            
        # 実際のコード行数（空行とコメント行を除く）
        code_lines = 0
        for i in range(start_line, min(end_line + 1, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                code_lines += 1
                
        return code_lines
        
    def _check_file_complexity(self, metrics: KISSMetrics):
        """ファイルレベルの複雑度チェック"""
        if metrics.total_lines > self.standards["max_file_lines"]:
            metrics.violations.append(KISSViolation(
                violation_type=KISSViolationType.TOO_LONG,
                file_path=metrics.file_path,
                line_number=0,
                method_name="<file>",
                description=f"File too long ({metrics.total_lines} lines)",
                current_value=metrics.total_lines,
                recommended_value=self.standards["max_file_lines"],
                severity="high"
            ))
            
    def _check_method_naming(self, method_node: ast.FunctionDef, metrics: KISSMetrics):
        """メソッド命名規則チェック"""
        method_name = method_node.name
        
        # テストメソッドの命名チェック
        if method_name.startswith('test_'):
            pattern = self.clear_naming_patterns["test_methods"]
            if not re.match(pattern, method_name):
                metrics.violations.append(KISSViolation(
                    violation_type=KISSViolationType.UNCLEAR_NAMING,
                    file_path=metrics.file_path,
                    line_number=method_node.lineno,
                    method_name=method_name,
                    description="Test method naming not clear (should include red/green/refactor or be descriptive)",
                    current_value=method_name,
                    recommended_value="test_feature_description_[red|green|refactor]",
                    severity="low"
                ))
                
    def _check_test_method_assertions(self, method_node: ast.FunctionDef, metrics: KISSMetrics):
        """テストメソッドのアサーション数チェック"""
        assertion_count = 0
        
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr') and node.func.attr.startswith('assert'):
                    assertion_count += 1
                elif hasattr(node.func, 'id') and node.func.id.startswith('assert'):
                    assertion_count += 1
                    
        if assertion_count > self.standards["max_assertions_per_test"]:
            metrics.violations.append(KISSViolation(
                violation_type=KISSViolationType.TOO_MANY_ASSERTIONS,
                file_path=metrics.file_path,
                line_number=method_node.lineno,
                method_name=method_node.name,
                description=f"Too many assertions in test method ({assertion_count})",
                current_value=assertion_count,
                recommended_value=self.standards["max_assertions_per_test"],
                severity="medium"
            ))
            
    def generate_report(self, results: Dict[str, KISSMetrics]) -> Dict[str, Any]:
        """KISS原則チェック結果のレポート生成"""
        if not results:
            return {
                "status": "No test files found",
                "overall_compliance": 100.0,
                "files_checked": 0,
                "total_violations": 0
            }
            
        # 全体統計
        total_files = len(results)
        total_violations = sum(len(metrics.violations) for metrics in results.values())
        compliance_scores = [metrics.compliance_score for metrics in results.values()]
        overall_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        
        # 違反タイプ別集計
        violation_types = {}
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        
        for metrics in results.values():
            for violation in metrics.violations:
                violation_type = violation.violation_type.value
                violation_types[violation_type] = violation_types.get(violation_type, 0) + 1
                severity_counts[violation.severity] += 1
                
        # 推奨事項
        recommendations = self._generate_recommendations(violation_types, severity_counts)
        
        return {
            "overall_compliance": round(overall_compliance, 1),
            "status": "🟢 EXCELLENT" if overall_compliance >= 90 else 
                     "🟡 GOOD" if overall_compliance >= 70 else 
                     "🔴 NEEDS IMPROVEMENT",
            "files_checked": total_files,
            "total_violations": total_violations,
            "violation_breakdown": violation_types,
            "severity_breakdown": severity_counts,
            "recommendations": recommendations,
            "file_details": {
                file_path: {
                    "compliance_score": metrics.compliance_score,
                    "violations": len(metrics.violations),
                    "total_lines": metrics.total_lines,
                    "method_count": metrics.method_count,
                    "max_method_lines": metrics.max_method_lines
                }
                for file_path, metrics in results.items()
            }
        }
        
    def _generate_recommendations(self, violation_types: Dict[str, int], 
                                severity_counts: Dict[str, int]) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []
        
        if violation_types.get("too_long", 0) > 0:
            recommendations.append("📏 Split long methods and files into smaller, focused units")
            
        if violation_types.get("too_many_methods", 0) > 0:
            recommendations.append("🔄 Consider splitting large test classes by functionality")
            
        if violation_types.get("unclear_naming", 0) > 0:
            recommendations.append("📝 Use clear, descriptive naming with red/green/refactor indicators")
            
        if violation_types.get("too_many_assertions", 0) > 0:
            recommendations.append("🎯 Focus each test method on a single behavior (one concept per test)")
            
        if severity_counts["high"] > 0:
            recommendations.append("🚨 Address high-severity violations first for maximum impact")
            
        if not recommendations:
            recommendations.append("✅ Excellent KISS principle compliance! Keep up the simple, clear code.")
            
        return recommendations


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KISS Principle Checker for Tests')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to check (default: current directory)')
    parser.add_argument('--output', '-o', choices=['console', 'json'], default='console',
                       help='Output format')
    parser.add_argument('--strict', action='store_true', 
                       help='Use stricter standards')
    
    args = parser.parse_args()
    
    # Strictモードの場合は基準を厳しく
    checker = KISSPrincipleChecker()
    if args.strict:
        checker.standards.update({
            "max_file_lines": 300,
            "max_method_lines": 20,
            "max_methods_per_class": 15,
            "max_assertions_per_test": 3
        })
        
    # チェック実行
    results = checker.check_directory(args.directory)
    report = checker.generate_report(results)
    
    # 結果出力
    if args.output == 'json':
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        # コンソール出力
        print("=" * 80)
        print("KISS原則チェック結果")  
        print("=" * 80)
        print(f"総合準拠率: {report['overall_compliance']}% {report['status']}")
        print(f"チェックファイル数: {report['files_checked']}")
        print(f"違反総数: {report['total_violations']}")
        
        if report['violation_breakdown']:
            print("\n違反タイプ別:")
            for vtype, count in report['violation_breakdown'].items():
                print(f"  {vtype}: {count}件")
                
        if report['recommendations']:
            print("\n推奨事項:")
            for rec in report['recommendations']:
                print(f"  {rec}")
                
        print("=" * 80)


if __name__ == "__main__":
    main()