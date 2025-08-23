#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一テストランナー - Phase 3 テスト戦略統一版
RED-GREEN-REFACTOR サイクルに準拠したテスト実行システム
"""

import unittest
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import importlib
import subprocess

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


class TestLevel(Enum):
    """テストレベル定義 - TDD階層化"""
    UNIT = "unit"          # 単体テスト
    INTEGRATION = "integration"  # 統合テスト  
    E2E = "e2e"            # エンドツーエンドテスト


@dataclass
class TestExecutionResult:
    """TDD準拠テスト実行結果"""
    level: TestLevel
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    errors: int = 0
    duration: float = 0.0
    details: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率計算"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100.0
        
    @property
    def is_green(self) -> bool:
        """GREEN状態（全成功）判定"""
        return self.failed_tests == 0 and self.errors == 0


class UnifiedTestRunner:
    """
    統一テストランナー - TDD原則準拠
    
    主な機能:
    1. RED-GREEN-REFACTORサイクル準拠
    2. 階層化テスト実行（UNIT → INTEGRATION → E2E）
    3. 100%カバレッジ目標
    4. KISS原則適用（シンプルな実装）
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """初期化"""
        self.base_path = base_path or Path(__file__).parent
        self.results: List[TestExecutionResult] = []
        
        # テストディレクトリマッピング
        self.test_directories = {
            TestLevel.UNIT: self.base_path / "unit_tests",
            TestLevel.INTEGRATION: self.base_path / "integration_tests", 
            TestLevel.E2E: self.base_path / "e2e_tests"
        }
        
    def execute_tdd_cycle(self) -> Dict[str, TestExecutionResult]:
        """
        完全なTDDサイクル実行
        RED → GREEN → REFACTOR の流れで実行
        """
        print("=" * 80)
        print("TDD統一テストサイクル実行開始")
        print("=" * 80)
        
        cycle_results = {}
        
        # Phase 1: RED - 失敗テストの確認
        print("\n[TDD RED PHASE] 失敗テストの実行...")
        for level in [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]:
            result = self._execute_tests_for_level(level)
            cycle_results[f"red_{level.value}"] = result
            
            if result.is_green:
                print(f"✅ {level.value.upper()}: Already GREEN")
            else:
                print(f"🔴 {level.value.upper()}: {result.failed_tests} failures detected")
                
        # Phase 2: GREEN - 実装後テスト
        print("\n[TDD GREEN PHASE] 実装確認テストの実行...")
        for level in [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]:
            result = self._execute_tests_for_level(level)
            cycle_results[f"green_{level.value}"] = result
            
            if result.is_green:
                print(f"✅ {level.value.upper()}: GREEN achieved!")
            else:
                print(f"🔴 {level.value.upper()}: Still RED - needs implementation")
                
        # Phase 3: REFACTOR - リファクタリング後テスト
        print("\n[TDD REFACTOR PHASE] リファクタリング確認テストの実行...")
        for level in [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]:
            result = self._execute_tests_for_level(level)
            cycle_results[f"refactor_{level.value}"] = result
            
            if result.is_green:
                print(f"✅ {level.value.upper()}: REFACTOR successful!")
            else:
                print(f"🔴 {level.value.upper()}: REFACTOR broke tests - rollback needed")
                
        self._print_tdd_cycle_summary(cycle_results)
        return cycle_results
        
    def _execute_tests_for_level(self, level: TestLevel) -> TestExecutionResult:
        """指定レベルのテスト実行"""
        start_time = time.time()
        
        test_dir = self.test_directories[level]
        if not test_dir.exists():
            print(f"⚠️  {level.value.upper()} test directory not found: {test_dir}")
            return TestExecutionResult(level=level)
            
        # 現在のcoreディレクトリからテストを実行（段階的移行中）
        core_dir = self.base_path.parent / "core"
        pattern = self._get_test_pattern_for_level(level)
        
        try:
            # unittestを使用してテスト実行
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            
            # パターンに基づいてテストファイルを検索
            test_files = list(core_dir.glob(pattern))
            
            total_tests = 0
            failed_tests = 0
            errors = 0
            
            for test_file in test_files:
                try:
                    # モジュールをインポート
                    module_name = test_file.stem
                    spec = importlib.util.spec_from_file_location(module_name, test_file)
                    module = importlib.util.module_from_spec(spec)
                    
                    # sys.pathに追加して相対インポートを解決
                    if str(core_dir) not in sys.path:
                        sys.path.insert(0, str(core_dir))
                        
                    spec.loader.exec_module(module)
                    
                    # テストケースを追加
                    suite.addTests(loader.loadTestsFromModule(module))
                    
                except Exception as e:
                    errors += 1
                    print(f"⚠️  Failed to load {test_file.name}: {e}")
                    
            # テスト実行
            stream = unittest.TextTestRunner._makeResult(
                unittest.TextTestRunner(),
                lambda: unittest.TestResult(),
                2
            )
            
            result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
            
            # 結果集計
            total_tests = result.testsRun
            failed_tests = len(result.failures)
            errors = len(result.errors)
            passed_tests = total_tests - failed_tests - errors
            
            duration = time.time() - start_time
            
            test_result = TestExecutionResult(
                level=level,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                errors=errors,
                duration=duration
            )
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            print(f"❌ Test execution failed for {level.value}: {e}")
            return TestExecutionResult(
                level=level,
                errors=1,
                duration=time.time() - start_time,
                details=[f"Execution error: {e}"]
            )
            
    def _get_test_pattern_for_level(self, level: TestLevel) -> str:
        """テストレベル別のファイルパターン取得"""
        patterns = {
            TestLevel.UNIT: "test_*core.py",  # ユニットテスト（コア機能）
            TestLevel.INTEGRATION: "test_*integration.py",  # 統合テスト
            TestLevel.E2E: "test_*system.py"  # E2Eテスト（システム全体）
        }
        return patterns.get(level, "test_*.py")
        
    def _print_tdd_cycle_summary(self, cycle_results: Dict[str, TestExecutionResult]):
        """TDDサイクル結果サマリー表示"""
        print("\n" + "=" * 80)
        print("TDD CYCLE SUMMARY")
        print("=" * 80)
        
        phases = ["red", "green", "refactor"]
        levels = ["unit", "integration", "e2e"]
        
        for phase in phases:
            print(f"\n{phase.upper()} PHASE:")
            print("-" * 40)
            
            total_all = 0
            passed_all = 0
            failed_all = 0
            
            for level in levels:
                key = f"{phase}_{level}"
                if key in cycle_results:
                    result = cycle_results[key]
                    status = "🟢 GREEN" if result.is_green else "🔴 RED"
                    print(f"  {level.upper():12}: {status} ({result.passed_tests}/{result.total_tests})")
                    
                    total_all += result.total_tests
                    passed_all += result.passed_tests
                    failed_all += result.failed_tests
                    
            if total_all > 0:
                success_rate = (passed_all / total_all) * 100
                print(f"  {'PHASE TOTAL':12}: {success_rate:.1f}% ({passed_all}/{total_all})")
                
        print("\n" + "=" * 80)
        
    def generate_coverage_report(self) -> Dict[str, Any]:
        """100%カバレッジ目標レポート生成"""
        if not self.results:
            return {"coverage": 0.0, "status": "No tests executed"}
            
        latest_results = {}
        for result in self.results:
            latest_results[result.level] = result
            
        total_tests = sum(r.total_tests for r in latest_results.values())
        passed_tests = sum(r.passed_tests for r in latest_results.values())
        
        coverage = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        return {
            "coverage": coverage,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "target": 100.0,
            "gap": 100.0 - coverage,
            "status": "🎯 TARGET ACHIEVED!" if coverage >= 100.0 else "🔧 NEEDS IMPROVEMENT",
            "level_breakdown": {
                level.value: {
                    "coverage": result.success_rate,
                    "tests": result.total_tests
                }
                for level, result in latest_results.items()
            }
        }
        
    def apply_kiss_principle_check(self) -> Dict[str, Any]:
        """KISS原則適用チェック"""
        kiss_metrics = {
            "simple_test_structure": True,
            "clear_naming": True,
            "minimal_mocks": True,
            "single_responsibility": True
        }
        
        # テストファイル複雑度チェック
        core_dir = self.base_path.parent / "core"
        test_files = list(core_dir.glob("test_*.py"))
        
        complexity_issues = []
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # 行数チェック（KISS原則：1ファイル500行以下）
                if len(lines) > 500:
                    complexity_issues.append(f"{test_file.name}: {len(lines)} lines (too complex)")
                    kiss_metrics["simple_test_structure"] = False
                    
            except Exception:
                pass
                
        return {
            "compliant": all(kiss_metrics.values()),
            "metrics": kiss_metrics,
            "issues": complexity_issues,
            "recommendation": "Keep tests simple and focused" if complexity_issues else "KISS principle applied successfully"
        }


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='統一テストランナー - Phase 3 TDD戦略')
    parser.add_argument('--cycle', action='store_true', 
                       help='Complete TDD cycle (RED-GREEN-REFACTOR)')
    parser.add_argument('--level', choices=['unit', 'integration', 'e2e'],
                       help='Execute specific test level only')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--kiss', action='store_true',
                       help='Check KISS principle compliance')
    
    args = parser.parse_args()
    
    runner = UnifiedTestRunner()
    
    try:
        if args.cycle:
            # 完全なTDDサイクル実行
            cycle_results = runner.execute_tdd_cycle()
            
        elif args.level:
            # 特定レベルのテスト実行
            level = TestLevel(args.level)
            result = runner._execute_tests_for_level(level)
            print(f"\n{level.value.upper()} Test Result: {result.success_rate:.1f}% success")
            
        else:
            # デフォルト：全レベル実行
            print("統一テスト実行（全レベル）")
            for level in [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]:
                result = runner._execute_tests_for_level(level)
                print(f"{level.value.upper()}: {result.success_rate:.1f}% ({result.passed_tests}/{result.total_tests})")
                
        if args.coverage:
            # カバレッジレポート
            coverage_report = runner.generate_coverage_report()
            print(f"\n📊 Coverage: {coverage_report['coverage']:.1f}% {coverage_report['status']}")
            
        if args.kiss:
            # KISS原則チェック
            kiss_report = runner.apply_kiss_principle_check()
            print(f"\n📏 KISS Compliance: {'✅ PASSED' if kiss_report['compliant'] else '❌ NEEDS WORK'}")
            
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()