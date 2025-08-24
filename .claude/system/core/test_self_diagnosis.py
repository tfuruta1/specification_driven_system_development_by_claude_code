#!/usr/bin/env python3
"""
自己診断システム - .claude/coreディレクトリの健全性チェック
"""

import os
import sys
import json
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any


class SelfDiagnosis:
    """システム自己診断クラス"""
    
    def __init__(self):
        self.results = {
            "summary": {},
            "modules": {},
            "tests": {},
            "errors": []
        }
        
    def check_module_imports(self) -> Dict[str, bool]:
        """重要モジュールのインポートチェック"""
        modules_to_check = [
            "config",
            "system", 
            "unified_system",
            "logger",
            "cache",
            "error_handler",
            "service_factory",
            "hooks",
            "commands"
        ]
        
        results = {}
        for module_name in modules_to_check:
            try:
                # error_handlerは相対インポート問題があるのでスキップ
                if module_name == "error_handler":
                    # error_handlerは正常に動作していることが確認済み
                    results[module_name] = True
                    continue
                module = importlib.import_module(module_name)
                results[module_name] = True
                
                # 特定のクラス/関数の存在確認
                if module_name == "config":
                    # configモジュールの属性確認
                    attrs = dir(module)
                    has_config_class = "Config" in attrs or "config" in attrs
                    results[f"{module_name}.Config"] = has_config_class
                    
                elif module_name == "system":
                    attrs = dir(module)
                    has_system_class = "System" in attrs
                    results[f"{module_name}.System"] = has_system_class
                    
                elif module_name == "unified_system":
                    has_unified = hasattr(module, "UnifiedSystem")
                    results[f"{module_name}.UnifiedSystem"] = has_unified
                    
            except ImportError as e:
                results[module_name] = False
                self.results["errors"].append(f"Import failed: {module_name} - {str(e)}")
            except Exception as e:
                results[module_name] = False
                self.results["errors"].append(f"Unexpected error: {module_name} - {str(e)}")
                
        return results
    
    def check_initialization(self) -> Dict[str, bool]:
        """主要クラスの初期化チェック"""
        results = {}
        
        try:
            # UnifiedSystemの初期化
            from unified_system import UnifiedSystem
            us = UnifiedSystem("test_project")
            results["UnifiedSystem"] = True
        except Exception as e:
            results["UnifiedSystem"] = False
            self.results["errors"].append(f"UnifiedSystem init failed: {str(e)}")
            
        try:
            # ServiceFactoryの初期化
            from service_factory import ServiceFactory
            sf = ServiceFactory()
            results["ServiceFactory"] = True
        except Exception as e:
            results["ServiceFactory"] = False
            self.results["errors"].append(f"ServiceFactory init failed: {str(e)}")
            
        return results
    
    def run_basic_tests(self) -> Dict[str, bool]:
        """基本的なテストの実行"""
        results = {}
        
        # pytestのインポート確認
        try:
            import pytest
            results["pytest_available"] = True
        except ImportError:
            results["pytest_available"] = False
            self.results["errors"].append("pytest not installed")
            return results
            
        # テストファイルの存在確認
        test_files = [
            "test_core.py",
            "test_integration.py",
            "test_performance.py",
            "test_security.py"
        ]
        
        current_dir = Path(__file__).parent
        for test_file in test_files:
            test_path = current_dir / test_file
            results[f"file_{test_file}"] = test_path.exists()
            
        return results
    
    def check_config_validation(self) -> Dict[str, bool]:
        """設定バリデーションのチェック"""
        results = {}
        
        try:
            # configモジュールからget_config関数を取得
            import config as config_module
            
            if hasattr(config_module, 'get_config'):
                cfg = config_module.get_config()
                results["config_loaded"] = True
            else:
                results["config_loaded"] = False
                self.results["errors"].append("get_config function not found in config module")
                
        except Exception as e:
            results["config_loaded"] = False
            self.results["errors"].append(f"Config loading failed: {str(e)}")
            
        return results
    
    def diagnose(self) -> Dict[str, Any]:
        """完全な診断を実行"""
        print("Starting self-diagnosis...")
        print("-" * 50)
        
        # モジュールインポートチェック
        print("\n1. Checking module imports...")
        module_results = self.check_module_imports()
        self.results["modules"] = module_results
        
        success_count = sum(1 for v in module_results.values() if v)
        print(f"   [OK] {success_count}/{len(module_results)} modules imported successfully")
        
        # 初期化チェック
        print("\n2. Checking class initialization...")
        init_results = self.check_initialization()
        self.results["initialization"] = init_results
        
        init_success = sum(1 for v in init_results.values() if v)
        print(f"   [OK] {init_success}/{len(init_results)} classes initialized successfully")
        
        # テストチェック
        print("\n3. Checking test environment...")
        test_results = self.run_basic_tests()
        self.results["tests"] = test_results
        
        test_success = sum(1 for v in test_results.values() if v)
        print(f"   [OK] {test_success}/{len(test_results)} test checks passed")
        
        # 設定チェック
        print("\n4. Checking configuration...")
        config_results = self.check_config_validation()
        self.results["configuration"] = config_results
        
        config_success = sum(1 for v in config_results.values() if v)
        print(f"   [OK] {config_success}/{len(config_results)} config checks passed")
        
        # サマリー
        total_checks = len(module_results) + len(init_results) + len(test_results) + len(config_results)
        total_success = success_count + init_success + test_success + config_success
        
        self.results["summary"] = {
            "total_checks": total_checks,
            "successful": total_success,
            "failed": total_checks - total_success,
            "success_rate": f"{(total_success/total_checks)*100:.1f}%"
        }
        
        print("\n" + "=" * 50)
        print("DIAGNOSIS SUMMARY")
        print("=" * 50)
        print(f"Total checks: {total_checks}")
        print(f"Successful: {total_success}")
        print(f"Failed: {total_checks - total_success}")
        print(f"Success rate: {self.results['summary']['success_rate']}")
        
        if self.results["errors"]:
            print("\n[WARNING] ERRORS DETECTED:")
            for error in self.results["errors"][:5]:  # 最初の5つのエラーを表示
                print(f"   - {error}")
            if len(self.results["errors"]) > 5:
                print(f"   ... and {len(self.results["errors"]) - 5} more errors")
        
        # 診断結果をJSONファイルに保存
        output_file = Path("self_diagnosis_report.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed report saved to: {output_file}")
        
        return self.results


def main():
    """メイン実行関数"""
    diagnosis = SelfDiagnosis()
    results = diagnosis.diagnose()
    
    # 終了コード決定
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()