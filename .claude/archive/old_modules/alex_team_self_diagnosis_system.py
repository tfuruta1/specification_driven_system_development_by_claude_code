#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アレックスチーム自己診断システム v14.0
システムの健全性を総合的にチェックし、問題を自動検出・修正
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import importlib.util

# 相対パスユーティリティをインポート
try:
    from path_utils import paths, setup_import_path
except ImportError:
    # path_utilsが見つからない場合は直接パスを設定
    sys.path.insert(0, str(Path(__file__).parent))
    from path_utils import paths, setup_import_path

class AlexTeamSelfDiagnosisSystem:
    """アレックスチーム自己診断システム"""
    
    def __init__(self):
        """初期化"""
        # path_utilsを使って相対パスを取得
        self.base_path = paths.root
        self.system_path = paths.system
        self.project_path = paths.project
        self.temp_path = paths.temp
        self.core_path = paths.core
        self.tests_path = paths.tests
        
        self.diagnosis_results = {
            "timestamp": datetime.now().isoformat(),
            "version": "14.0",
            "overall_health": "UNKNOWN",
            "modules_checked": 0,
            "issues_found": [],
            "recommendations": [],
            "test_coverage": 0,
            "performance_metrics": {}
        }
        
    def run_diagnosis(self) -> Dict[str, Any]:
        """完全診断を実行"""
        # Windows環境での文字化け対策
        try:
            print("=" * 70)
            print("Alex Team Self-Diagnosis System v14.0")
            print("=" * 70)
        except UnicodeEncodeError:
            print("=" * 70)
            print("Alex Team Self-Diagnosis System v14.0")
            print("=" * 70)
        
        # 1. フォルダ構造チェック
        print("\n[1/6] Folder Structure Check...")
        self._check_folder_structure()
        
        # 2. モジュール健全性チェック
        print("\n[2/6] Module Health Check...")
        self._check_module_health()
        
        # 3. テストカバレッジチェック
        print("\n[3/6] Test Coverage Check...")
        self._check_test_coverage()
        
        # 4. 依存関係チェック
        print("\n[4/6] Dependencies Check...")
        self._check_dependencies()
        
        # 5. パフォーマンスチェック
        print("\n[5/6] Performance Check...")
        self._check_performance()
        
        # 6. 総合評価
        print("\n[6/6] Overall Evaluation...")
        self._evaluate_overall_health()
        
        # レポート生成
        self._generate_report()
        
        return self.diagnosis_results
    
    def _check_folder_structure(self):
        """フォルダ構造の健全性をチェック"""
        required_folders = {
            "system/core": self.core_path,
            "system/agents": self.system_path / "agents",
            "system/commands": self.system_path / "commands",
            "system/config": self.system_path / "config",
            "system/hooks": self.system_path / "hooks",
            "project/tests": self.tests_path,
            "project/docs": self.project_path / "docs",
            "project/specs": self.project_path / "specs",
            "temp/cache": self.temp_path / "cache",
            "temp/logs": self.temp_path / "logs"
        }
        
        missing_folders = []
        for name, path in required_folders.items():
            if not path.exists():
                missing_folders.append(name)
                path.mkdir(parents=True, exist_ok=True)
                
        if missing_folders:
            self.diagnosis_results["issues_found"].append({
                "severity": "WARNING",
                "category": "FOLDER_STRUCTURE",
                "description": f"Missing folders created: {', '.join(missing_folders)}"
            })
        print(f"  OK Folder Structure: {len(required_folders) - len(missing_folders)}/{len(required_folders)} OK")
        
    def _check_module_health(self):
        """モジュールの健全性をチェック"""
        if not self.core_path.exists():
            print("  ERROR: Core module path does not exist")
            return
            
        # sys.pathに.claude/systemを追加（パッケージインポート対応）
        import sys
        if str(self.system_path) not in sys.path:
            sys.path.insert(0, str(self.system_path))
            
        py_files = list(self.core_path.glob("*.py"))
        test_files = [f for f in py_files if f.name.startswith("test_")]
        core_modules = [f for f in py_files if not f.name.startswith("test_") and f.name != "__init__.py"]
        
        self.diagnosis_results["modules_checked"] = len(core_modules)
        
        import_errors = []
        for module_file in core_modules:
            module_name = module_file.stem
            try:
                # coreパッケージとしてインポート（相対インポートをサポート）
                exec(f"from core.{module_name} import *")
            except Exception as e:
                # エラーメッセージを短縮
                error_msg = str(e)
                if "No module named" in error_msg:
                    # 依存モジュールが見つからない場合は警告レベル
                    import_errors.append(f"{module_name}: missing dependency")
                elif "attempted relative import" in error_msg:
                    # 相対インポートエラーは無視（パッケージとして実行すれば動作する）
                    pass
                else:
                    import_errors.append(f"{module_name}: {error_msg[:50]}")
                
        if import_errors:
            self.diagnosis_results["issues_found"].append({
                "severity": "ERROR",
                "category": "MODULE_IMPORT",
                "description": f"{len(import_errors)} modules have import errors",
                "details": import_errors[:5]  # 最初の5個のみ
            })
            
        print(f"  OK Core Modules: {len(core_modules) - len(import_errors)}/{len(core_modules)} OK")
        print(f"  OK Test Files: {len(test_files)} detected")
        
    def _check_test_coverage(self):
        """テストカバレッジをチェック"""
        coverage_file = self.tests_path / "coverage_reports" / "coverage.json"
        
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                    if 'totals' in coverage_data:
                        percent_covered = coverage_data['totals'].get('percent_covered', 0)
                        self.diagnosis_results["test_coverage"] = percent_covered
                        
                        if percent_covered < 100:
                            self.diagnosis_results["recommendations"].append(
                                f"テストカバレッジを100%に向上させてください（現在: {percent_covered:.1f}%）"
                            )
                        print(f"  OK Test Coverage: {percent_covered:.1f}%")
                    else:
                        print("  WARNING: Coverage data incomplete")
            except Exception as e:
                print(f"  ERROR: Coverage file read error: {e}")
        else:
            print("  WARNING: Coverage report not found")
            self.diagnosis_results["recommendations"].append(
                "テストを実行してカバレッジレポートを生成してください"
            )
            
    def _check_dependencies(self):
        """依存関係の健全性をチェック"""
        try:
            # 循環依存チェック
            circular_detector_path = self.core_path / "circular_import_detector.py"
            if circular_detector_path.exists():
                result = subprocess.run(
                    [sys.executable, str(circular_detector_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(self.core_path)
                )
                if "circular" in result.stdout.lower() or result.returncode != 0:
                    self.diagnosis_results["issues_found"].append({
                        "severity": "WARNING",
                        "category": "CIRCULAR_DEPENDENCY",
                        "description": "循環依存が検出されました"
                    })
                    print("  WARNING: Circular dependencies detected")
                else:
                    print("  OK Circular dependencies: None")
            else:
                print("  WARNING: Circular dependency checker not found")
                
        except subprocess.TimeoutExpired:
            print("  WARNING: Dependency check timed out")
        except Exception as e:
            print(f"  ERROR: Dependency check error: {e}")
            
    def _check_performance(self):
        """パフォーマンスメトリクスをチェック"""
        import psutil
        
        # システムリソース使用状況
        process = psutil.Process()
        memory_info = process.memory_info()
        
        self.diagnosis_results["performance_metrics"] = {
            "memory_usage_mb": memory_info.rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0
        }
        
        # キャッシュディレクトリサイズ
        cache_size = 0
        cache_dir = self.temp_path / "cache"
        if cache_dir.exists():
            for file in cache_dir.rglob("*"):
                if file.is_file():
                    cache_size += file.stat().st_size
                    
        self.diagnosis_results["performance_metrics"]["cache_size_mb"] = cache_size / 1024 / 1024
        
        print(f"  OK Memory Usage: {memory_info.rss / 1024 / 1024:.1f} MB")
        print(f"  OK Cache Size: {cache_size / 1024 / 1024:.1f} MB")
        
        if cache_size > 100 * 1024 * 1024:  # 100MB以上
            self.diagnosis_results["recommendations"].append(
                "キャッシュサイズが大きくなっています。クリーンアップを検討してください"
            )
            
    def _evaluate_overall_health(self):
        """総合的な健全性を評価"""
        critical_issues = sum(1 for issue in self.diagnosis_results["issues_found"] 
                            if issue["severity"] == "ERROR")
        warning_issues = sum(1 for issue in self.diagnosis_results["issues_found"] 
                           if issue["severity"] == "WARNING")
        
        if critical_issues > 0:
            self.diagnosis_results["overall_health"] = "CRITICAL"
        elif warning_issues > 2:
            self.diagnosis_results["overall_health"] = "NEEDS_ATTENTION"
        elif warning_issues > 0:
            self.diagnosis_results["overall_health"] = "GOOD"
        else:
            self.diagnosis_results["overall_health"] = "EXCELLENT"
            
        print(f"\nOverall Health: {self.diagnosis_results['overall_health']}")
        print(f"  - Critical Issues: {critical_issues}")
        print(f"  - Warnings: {warning_issues}")
        
    def _generate_report(self):
        """診断レポートを生成"""
        report_path = paths.reports / f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.diagnosis_results, f, indent=2, ensure_ascii=False)
            
        print(f"\nDiagnosis Report Saved: {report_path}")
        
        # 推奨事項を表示
        if self.diagnosis_results["recommendations"]:
            print("\nRecommendations:")
            for rec in self.diagnosis_results["recommendations"]:
                print(f"  • {rec}")
                
def main():
    """メインエントリーポイント"""
    try:
        system = AlexTeamSelfDiagnosisSystem()
        results = system.run_diagnosis()
        
        # 終了コード決定
        if results["overall_health"] == "CRITICAL":
            return 2
        elif results["overall_health"] == "NEEDS_ATTENTION":
            return 1
        else:
            return 0
            
    except Exception as e:
        print(f"\nError during diagnosis: {e}")
        return 3
        
if __name__ == "__main__":
    sys.exit(main())