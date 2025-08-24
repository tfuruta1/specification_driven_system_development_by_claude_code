#!/usr/bin/env python3
"""
Comprehensive Test Runner with 100% Coverage Reporting
TDD Test Engineer - Achieving 100% Test Coverage
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import pytest


class ComprehensiveTestRunner:
    """
    Comprehensive test runner that ensures 100% coverage
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize test runner with project root"""
        if project_root is None:
            # Auto-detect project root
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent.parent.parent  # Go up to project root
            
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / ".claude" / "project" / "tests"
        self.core_dir = self.project_root / ".claude" / "system" / "core"
        self.coverage_dir = self.tests_dir / "coverage_reports"
        
        # Ensure coverage reports directory exists
        self.coverage_dir.mkdir(parents=True, exist_ok=True)
        
    def identify_core_modules(self) -> List[Path]:
        """
        Identify all core modules that need testing
        """
        core_modules = []
        
        if not self.core_dir.exists():
            print(f"Warning: Core directory not found at {self.core_dir}")
            return core_modules
            
        for py_file in self.core_dir.glob("*.py"):
            # Skip test files and __pycache__
            if not py_file.name.startswith("test_") and py_file.name != "__pycache__":
                core_modules.append(py_file)
                
        return sorted(core_modules)
    
    def identify_missing_test_files(self) -> List[str]:
        """
        Identify modules that don't have corresponding test files
        """
        core_modules = self.identify_core_modules()
        missing_tests = []
        
        for module_path in core_modules:
            module_name = module_path.stem
            expected_test_file = self.tests_dir / "unit_tests" / "core" / f"test_{module_name}.py"
            
            if not expected_test_file.exists():
                missing_tests.append(module_name)
                
        return missing_tests
    
    def run_pytest_with_coverage(self) -> Dict[str, Any]:
        """
        Run pytest with coverage reporting
        """
        try:
            # Run pytest with coverage
            pytest_args = [
                str(self.tests_dir / "unit_tests"),
                "-v",
                "--tb=short",
                f"--cov={self.core_dir}",
                f"--cov-report=html:{self.coverage_dir}/html",
                f"--cov-report=json:{self.coverage_dir}/coverage.json",
                f"--cov-report=term-missing",
                "--cov-report=xml:" + str(self.coverage_dir / "coverage.xml")
            ]
            
            result = pytest.main(pytest_args)
            
        except Exception as e:
            print(f"Error running pytest: {e}")
            result = 1
            
        return {
            "pytest_exit_code": result,
            "success": result == 0
        }
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive coverage report
        """
        json_report_file = self.coverage_dir / "coverage.json"
        
        if not json_report_file.exists():
            return {
                "coverage_percentage": 0,
                "lines_covered": 0,
                "lines_missing": 0,
                "files_analyzed": 0,
                "html_report": "",
                "json_report": "",
                "text_report": ""
            }
        
        try:
            # Load coverage data
            with open(json_report_file, 'r') as f:
                coverage_data = json.load(f)
                
            return {
                "coverage_percentage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                "files_analyzed": len(coverage_data.get("files", {})),
                "html_report": str(self.coverage_dir / "html" / "index.html"),
                "json_report": str(json_report_file),
                "text_report": "Coverage displayed in terminal"
            }
        except Exception as e:
            print(f"Error reading coverage report: {e}")
            return {
                "coverage_percentage": 0,
                "lines_covered": 0,
                "lines_missing": 0,
                "files_analyzed": 0,
                "html_report": "",
                "json_report": "",
                "text_report": ""
            }
    
    def analyze_uncovered_lines(self) -> Dict[str, List[int]]:
        """
        Analyze which lines are not covered by tests
        """
        json_report_file = self.coverage_dir / "coverage.json"
        
        if not json_report_file.exists():
            return {}
            
        try:
            with open(json_report_file, 'r') as f:
                coverage_data = json.load(f)
            
            uncovered_by_file = {}
            
            for filename, file_data in coverage_data.get("files", {}).items():
                missing_lines = file_data.get("missing_lines", [])
                if missing_lines:
                    # Convert absolute path to relative for readability
                    try:
                        relative_path = os.path.relpath(filename, self.project_root)
                        uncovered_by_file[relative_path] = missing_lines
                    except ValueError:
                        uncovered_by_file[filename] = missing_lines
                    
            return uncovered_by_file
        except Exception as e:
            print(f"Error analyzing uncovered lines: {e}")
            return {}
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """
        Run comprehensive test suite with detailed reporting
        """
        print("="*80)
        print("COMPREHENSIVE TEST SUITE WITH 100% COVERAGE TARGET")
        print("TDD Test Engineer - Achieving Excellence")
        print("="*80)
        
        # 1. Identify core modules
        core_modules = self.identify_core_modules()
        print(f"\n[ANALYSIS] Found {len(core_modules)} core modules to test")
        for module in core_modules:
            print(f"  - {module.name}")
        
        # 2. Check for missing test files
        missing_tests = self.identify_missing_test_files()
        if missing_tests:
            print(f"\n[WARNING] {len(missing_tests)} modules lack test files:")
            for module in missing_tests:
                print(f"   - {module}")
        
        # 3. Run tests with coverage
        print(f"\n[RUNNING] Executing comprehensive test suite...")
        test_results = self.run_pytest_with_coverage()
        
        # 4. Generate coverage reports
        print(f"\n[COVERAGE] Generating detailed coverage reports...")
        coverage_results = self.generate_coverage_report()
        
        # 5. Analyze uncovered lines
        uncovered_lines = self.analyze_uncovered_lines()
        
        # 6. Generate summary report
        summary = {
            "core_modules_count": len(core_modules),
            "missing_test_files": missing_tests,
            "test_execution": test_results,
            "coverage": coverage_results,
            "uncovered_lines": uncovered_lines,
            "coverage_target_met": coverage_results["coverage_percentage"] >= 100.0
        }
        
        # 7. Print summary
        self.print_summary(summary)
        
        # 8. Save summary to file
        summary_file = self.coverage_dir / "test_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """
        Print formatted test summary
        """
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        
        # Test execution results
        if summary["test_execution"]["success"]:
            print("[SUCCESS] All tests passed successfully")
        else:
            print("[FAILED] Some tests failed")
            
        # Coverage results
        coverage_pct = summary["coverage"]["coverage_percentage"]
        print(f"[COVERAGE] {coverage_pct:.1f}% line coverage")
        
        if coverage_pct >= 100.0:
            print("[TARGET] 100% coverage achieved!")
        else:
            print(f"[TARGET] {100.0 - coverage_pct:.1f}% remaining to reach 100%")
        
        # Missing test files
        if summary["missing_test_files"]:
            print(f"\n[MISSING TESTS] {len(summary['missing_test_files'])} files need tests")
        
        # Uncovered lines
        if summary["uncovered_lines"]:
            print(f"\n[UNCOVERED LINES]:")
            for file_path, lines in summary["uncovered_lines"].items():
                print(f"   {file_path}: lines {lines}")
        
        print("\n" + "="*80)
        print(f"[REPORTS] Generated in {self.coverage_dir}")
        print("="*80)


def main():
    """
    Main entry point for comprehensive test runner
    """
    runner = ComprehensiveTestRunner()
    summary = runner.run_comprehensive_test_suite()
    
    # Exit with appropriate code
    if summary["test_execution"]["success"] and summary["coverage_target_met"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()