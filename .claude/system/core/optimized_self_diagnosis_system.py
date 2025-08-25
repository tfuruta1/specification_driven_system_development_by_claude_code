#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI往復最適化統合自己診断システム v15.0
診断→問題特定→改善提案→実装指示まで一括処理

参考: https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e
目標: 診断後の改善実装で AI往復 20回→3-5回に削減
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from .common_base import BaseManager, BaseResult, TaskStatus, create_result
    from .ai_batch_optimizer import AIBatchOptimizer, BatchTask, BatchTaskType
    from .automated_test_generator import AutomatedTestGenerator
    from .dependency_checker import UnifiedDependencyChecker
    from .path_utils import paths
    from .logger import logger
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from common_base import BaseManager, BaseResult, TaskStatus, create_result
    from ai_batch_optimizer import AIBatchOptimizer, BatchTask, BatchTaskType
    from automated_test_generator import AutomatedTestGenerator
    from dependency_checker import UnifiedDependencyChecker
    from path_utils import paths
    from logger import logger


class DiagnosisSeverity(Enum):
    """診断問題の重要度"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ImprovementActionType(Enum):
    """改善アクション種別"""
    CODE_FIX = "code_fix"
    TEST_GENERATION = "test_generation"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


@dataclass
class DiagnosisIssue:
    """診断で発見された問題"""
    category: str
    severity: DiagnosisSeverity
    description: str
    affected_modules: List[str]
    recommended_actions: List[ImprovementActionType]
    ai_batch_specification: Optional[Dict[str, Any]] = None


@dataclass
class ImprovementBatchSpec:
    """改善バッチ処理仕様"""
    issue_id: str
    action_type: ImprovementActionType
    priority: int
    specification: Dict[str, Any]
    expected_outcomes: List[str]
    validation_commands: List[str]


class OptimizedSelfDiagnosisSystem(BaseManager):
    """AI往復最適化統合自己診断システム"""
    
    def __init__(self):
        """初期化"""
        super().__init__("OptimizedSelfDiagnosisSystem")
        
        # パスの設定
        self.base_path = paths.root
        self.system_path = paths.system
        self.core_path = paths.core
        self.tests_path = paths.tests
        
        # 診断結果
        self.diagnosis_results = {
            "timestamp": datetime.now().isoformat(),
            "version": "15.0",
            "overall_health": "UNKNOWN",
            "issues_found": [],
            "improvement_batches": [],
            "ai_optimization_metrics": {},
            "test_coverage": 0,
            "performance_metrics": {}
        }
        
        # AI最適化コンポーネント
        self.ai_optimizer = None
        self.test_generator = None
        self.dependency_checker = None
        
    def initialize(self) -> BaseResult:
        """システム初期化"""
        try:
            # AI最適化システム初期化
            self.ai_optimizer = AIBatchOptimizer()
            self.test_generator = AutomatedTestGenerator()
            self.dependency_checker = UnifiedDependencyChecker()
            
            # 各コンポーネント初期化
            components = [
                ("AI Optimizer", self.ai_optimizer),
                ("Test Generator", self.test_generator)
            ]
            
            for name, component in components:
                if hasattr(component, 'initialize'):
                    result = component.initialize()
                    if not result.success:
                        return create_result(False, f"{name} initialization failed: {result.message}")
            
            logger.info("Optimized Self-Diagnosis System v15.0 initialized")
            return create_result(True, "System initialized successfully")
            
        except Exception as e:
            return create_result(False, f"Initialization failed: {e}")
    
    def cleanup(self) -> BaseResult:
        """クリーンアップ"""
        try:
            components = [self.ai_optimizer, self.test_generator]
            for component in components:
                if component and hasattr(component, 'cleanup'):
                    component.cleanup()
            return create_result(True, "Cleanup completed")
        except Exception as e:
            return create_result(False, f"Cleanup failed: {e}")
    
    def run_optimized_diagnosis_cycle(self) -> BaseResult:
        """
        AI往復最適化診断サイクル - メインエントリーポイント
        診断→問題分析→改善仕様作成→AI一括実装指示
        """
        try:
            print("=" * 80)
            print("Alex Team Optimized Self-Diagnosis System v15.0")
            print("AI Roundtrip Optimization: 20 rounds -> 3-5 rounds")
            print("=" * 80)
            
            # Phase 1: 従来の診断実行
            print("\n[Phase 1] Comprehensive Diagnosis")
            diagnosis_result = self._run_comprehensive_diagnosis()
            
            if not diagnosis_result.success:
                return diagnosis_result
            
            # Phase 2: 問題分析とバッチ仕様作成
            print("\n[Phase 2] Issue Analysis & Batch Specification Creation")
            batch_specs = self._create_improvement_batch_specifications()
            
            # Phase 3: AI往復最適化改善提案生成
            print("\n[Phase 3] AI-Optimized Improvement Proposals")
            improvement_proposals = self._generate_ai_optimized_proposals(batch_specs)
            
            # Phase 4: 統合レポート生成
            print("\n[Phase 4] Integrated Report Generation")
            report_result = self._generate_optimized_report(improvement_proposals)
            
            self.diagnosis_results["ai_optimization_metrics"] = {
                "total_issues": len(batch_specs),
                "batch_specifications_created": len(batch_specs),
                "ai_proposals_generated": len(improvement_proposals),
                "estimated_roundtrip_reduction": "75-85%",
                "estimated_time_saving": "2-3 hours → 30-45 minutes"
            }
            
            return create_result(
                True, 
                "Optimized diagnosis cycle completed successfully",
                {
                    "diagnosis": self.diagnosis_results,
                    "improvement_proposals": improvement_proposals,
                    "batch_count": len(batch_specs)
                }
            )
            
        except Exception as e:
            logger.error(f"Optimized diagnosis cycle failed: {e}")
            return create_result(False, f"Diagnosis cycle failed: {e}")
    
    def _run_comprehensive_diagnosis(self) -> BaseResult:
        """包括的診断実行"""
        try:
            issues = []
            
            # 1. フォルダ構造チェック
            print("  [1/6] Folder Structure Analysis...")
            folder_issues = self._analyze_folder_structure()
            issues.extend(folder_issues)
            
            # 2. モジュール健全性チェック  
            print("  [2/6] Module Health Analysis...")
            module_issues = self._analyze_module_health()
            issues.extend(module_issues)
            
            # 3. テストカバレッジ分析
            print("  [3/6] Test Coverage Analysis...")
            coverage_issues = self._analyze_test_coverage()
            issues.extend(coverage_issues)
            
            # 4. 依存関係分析
            print("  [4/6] Dependencies Analysis...")
            dependency_issues = self._analyze_dependencies()
            issues.extend(dependency_issues)
            
            # 5. パフォーマンス分析
            print("  [5/6] Performance Analysis...")
            performance_issues = self._analyze_performance()
            issues.extend(performance_issues)
            
            # 6. 品質メトリクス分析
            print("  [6/6] Quality Metrics Analysis...")
            quality_issues = self._analyze_code_quality()
            issues.extend(quality_issues)
            
            self.diagnosis_results["issues_found"] = [asdict(issue) for issue in issues]
            self._evaluate_overall_health()
            
            print(f"\nDiagnosis completed: {len(issues)} issues identified")
            return create_result(True, f"Comprehensive diagnosis completed with {len(issues)} issues")
            
        except Exception as e:
            return create_result(False, f"Comprehensive diagnosis failed: {e}")
    
    def _analyze_folder_structure(self) -> List[DiagnosisIssue]:
        """フォルダ構造分析"""
        issues = []
        required_folders = {
            "system/core": self.core_path,
            "project/tests": self.tests_path,
            "system/templates": self.system_path / "templates",
        }
        
        missing_folders = []
        for name, path in required_folders.items():
            if not path.exists():
                missing_folders.append(name)
        
        if missing_folders:
            issues.append(DiagnosisIssue(
                category="FOLDER_STRUCTURE",
                severity=DiagnosisSeverity.MEDIUM,
                description=f"Missing folders: {', '.join(missing_folders)}",
                affected_modules=[],
                recommended_actions=[ImprovementActionType.CODE_FIX],
                ai_batch_specification={
                    "task_type": "folder_creation",
                    "folders_to_create": missing_folders,
                    "template_source": "system/templates"
                }
            ))
        
        return issues
    
    def _analyze_module_health(self) -> List[DiagnosisIssue]:
        """モジュール健全性分析"""
        issues = []
        
        if not self.core_path.exists():
            return [DiagnosisIssue(
                category="MODULE_HEALTH",
                severity=DiagnosisSeverity.CRITICAL,
                description="Core module path does not exist",
                affected_modules=[],
                recommended_actions=[ImprovementActionType.CODE_FIX]
            )]
        
        py_files = list(self.core_path.glob("*.py"))
        import_errors = []
        
        for py_file in py_files:
            module_name = py_file.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            except Exception as e:
                import_errors.append((module_name, str(e)))
        
        if import_errors:
            affected_modules = [name for name, _ in import_errors]
            issues.append(DiagnosisIssue(
                category="MODULE_IMPORT",
                severity=DiagnosisSeverity.HIGH,
                description=f"Import errors in {len(import_errors)} modules",
                affected_modules=affected_modules,
                recommended_actions=[ImprovementActionType.CODE_FIX, ImprovementActionType.REFACTORING],
                ai_batch_specification={
                    "task_type": "import_error_fix",
                    "modules_with_errors": import_errors,
                    "fix_patterns": ["missing_imports", "circular_imports", "path_issues"]
                }
            ))
        
        return issues
    
    def _analyze_test_coverage(self) -> List[DiagnosisIssue]:
        """テストカバレッジ分析"""
        issues = []
        coverage_file = self.tests_path / "coverage_reports" / "coverage.json"
        
        target_coverage = 95.0
        current_coverage = 0.0
        
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                    current_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
            except Exception:
                pass
        
        self.diagnosis_results["test_coverage"] = current_coverage
        
        if current_coverage < target_coverage:
            gap = target_coverage - current_coverage
            issues.append(DiagnosisIssue(
                category="TEST_COVERAGE",
                severity=DiagnosisSeverity.HIGH if gap > 20 else DiagnosisSeverity.MEDIUM,
                description=f"Test coverage {current_coverage:.1f}% below target {target_coverage}%",
                affected_modules=[],
                recommended_actions=[ImprovementActionType.TEST_GENERATION],
                ai_batch_specification={
                    "task_type": "test_coverage_improvement",
                    "current_coverage": current_coverage,
                    "target_coverage": target_coverage,
                    "modules_need_tests": self._identify_low_coverage_modules(),
                    "test_types": ["unit_tests", "integration_tests", "edge_case_tests"]
                }
            ))
        
        return issues
    
    def _analyze_dependencies(self) -> List[DiagnosisIssue]:
        """依存関係分析"""
        issues = []
        
        if self.dependency_checker:
            dep_result = self.dependency_checker.check_all_dependencies()
            
            if dep_result.has_circular_deps:
                issues.append(DiagnosisIssue(
                    category="CIRCULAR_DEPENDENCIES",
                    severity=DiagnosisSeverity.HIGH,
                    description=f"Circular dependencies detected: {len(dep_result.circular_paths)} cycles",
                    affected_modules=[],
                    recommended_actions=[ImprovementActionType.REFACTORING],
                    ai_batch_specification={
                        "task_type": "circular_dependency_resolution",
                        "circular_paths": dep_result.circular_paths,
                        "resolution_strategies": ["interface_extraction", "dependency_injection", "module_splitting"]
                    }
                ))
            
            if dep_result.errors:
                issues.append(DiagnosisIssue(
                    category="DEPENDENCY_ERRORS",
                    severity=DiagnosisSeverity.MEDIUM,
                    description=f"Dependency check errors: {len(dep_result.errors)}",
                    affected_modules=[],
                    recommended_actions=[ImprovementActionType.CODE_FIX]
                ))
        
        return issues
    
    def _analyze_performance(self) -> List[DiagnosisIssue]:
        """パフォーマンス分析"""
        issues = []
        
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # メモリ使用量チェック
            if memory_mb > 100:  # 100MB以上
                issues.append(DiagnosisIssue(
                    category="MEMORY_USAGE",
                    severity=DiagnosisSeverity.MEDIUM,
                    description=f"High memory usage: {memory_mb:.1f} MB",
                    affected_modules=[],
                    recommended_actions=[ImprovementActionType.PERFORMANCE_OPTIMIZATION],
                    ai_batch_specification={
                        "task_type": "memory_optimization",
                        "current_usage": memory_mb,
                        "target_usage": 50.0,
                        "optimization_areas": ["cache_optimization", "object_pooling", "lazy_loading"]
                    }
                ))
        except ImportError:
            pass
        
        return issues
    
    def _analyze_code_quality(self) -> List[DiagnosisIssue]:
        """コード品質分析"""
        issues = []
        
        # YAGNI違反チェック（未使用ファイル）
        test_files = list(self.core_path.glob("test_*.py"))
        if len(test_files) > 20:  # テストファイル過多
            issues.append(DiagnosisIssue(
                category="YAGNI_VIOLATION", 
                severity=DiagnosisSeverity.MEDIUM,
                description=f"Too many test files: {len(test_files)} (consider consolidation)",
                affected_modules=[],
                recommended_actions=[ImprovementActionType.REFACTORING],
                ai_batch_specification={
                    "task_type": "test_consolidation",
                    "current_test_count": len(test_files),
                    "target_test_count": 10,
                    "consolidation_strategy": "merge_similar_tests"
                }
            ))
        
        return issues
    
    def _create_improvement_batch_specifications(self) -> List[ImprovementBatchSpec]:
        """改善バッチ仕様作成"""
        batch_specs = []
        
        for i, issue_data in enumerate(self.diagnosis_results["issues_found"]):
            issue = DiagnosisIssue(**issue_data)
            
            if issue.ai_batch_specification:
                for action_type in issue.recommended_actions:
                    batch_spec = ImprovementBatchSpec(
                        issue_id=f"issue_{i}_{action_type.value}",
                        action_type=action_type,
                        priority=self._get_priority_from_severity(issue.severity),
                        specification={
                            "issue_category": issue.category,
                            "description": issue.description,
                            "affected_modules": issue.affected_modules,
                            "ai_batch_spec": issue.ai_batch_specification,
                            "success_criteria": self._generate_success_criteria(issue),
                            "validation_commands": self._generate_validation_commands(issue)
                        },
                        expected_outcomes=self._generate_expected_outcomes(issue, action_type),
                        validation_commands=self._generate_validation_commands(issue)
                    )
                    batch_specs.append(batch_spec)
        
        return batch_specs
    
    def _generate_ai_optimized_proposals(self, batch_specs: List[ImprovementBatchSpec]) -> List[Dict[str, Any]]:
        """AI往復最適化改善提案生成"""
        proposals = []
        
        for batch_spec in batch_specs:
            proposal = {
                "issue_id": batch_spec.issue_id,
                "action_type": batch_spec.action_type.value,
                "priority": batch_spec.priority,
                
                # AI一括実装指示（仕様書ファースト）
                "ai_implementation_request": self._create_ai_implementation_request(batch_spec),
                
                # バッチ処理仕様
                "batch_processing_spec": {
                    "task_type": batch_spec.action_type.value,
                    "specification": batch_spec.specification,
                    "expected_outcomes": batch_spec.expected_outcomes,
                    "validation_commands": batch_spec.validation_commands
                },
                
                # 往復最適化情報
                "roundtrip_optimization": {
                    "estimated_traditional_rounds": 15-20,
                    "estimated_optimized_rounds": 3-5,
                    "reduction_percentage": "75-85%",
                    "key_optimizations": [
                        "Specification-first approach",
                        "Batch processing integration",
                        "Automated validation cycle",
                        "Self-correction capability"
                    ]
                }
            }
            
            proposals.append(proposal)
        
        return proposals
    
    def _create_ai_implementation_request(self, batch_spec: ImprovementBatchSpec) -> str:
        """AI実装依頼文生成"""
        spec = batch_spec.specification
        
        template = f"""
【AI往復最適化 - 一括改善実装依頼】

## 問題概要
- **カテゴリ**: {spec['issue_category']}
- **説明**: {spec['description']}
- **影響モジュール**: {', '.join(spec['affected_modules']) if spec['affected_modules'] else 'システム全体'}

## 実装要求
AI_COLLABORATION_CONTEXT.mdとSPECIFICATION_TEMPLATE.mdに基づき、以下を**一括で実装**してください:

### 1. 問題解決実装
- 根本原因の修正
- 関連する全ての依存関係の更新
- エラーハンドリングの改善

### 2. テスト実装 (TDD対応)
- RED Phase: 問題再現テスト
- GREEN Phase: 修正後の正常動作テスト
- エッジケースのテスト

### 3. 統合検証
- 既存システムとの統合確認
- パフォーマンス影響確認
- 依存関係の健全性確認

### 4. 自動修正対応
エラー発生時は自動的に以下を試行:
- インポートパスの修正
- 依存関係の解決
- テストの調整

## 成功基準
{chr(10).join(f'- {criteria}' for criteria in spec.get('success_criteria', ['正常動作確認']))}

## 検証コマンド
{chr(10).join(f'```bash{chr(10)}{cmd}{chr(10)}```' for cmd in batch_spec.validation_commands)}

**重要**: エラーが発生した場合は自動修正を試行し、最終的に動作する状態まで完成させてください。
        """
        
        return template.strip()
    
    def _generate_success_criteria(self, issue: DiagnosisIssue) -> List[str]:
        """成功基準生成"""
        criteria = []
        
        if issue.category == "TEST_COVERAGE":
            criteria.append("テストカバレッジ95%以上達成")
            criteria.append("全テスト正常実行")
        elif issue.category == "MODULE_IMPORT":
            criteria.append("全モジュールのインポートエラー解消")
            criteria.append("依存関係の健全性確認")
        elif issue.category == "CIRCULAR_DEPENDENCIES":
            criteria.append("循環依存の完全解消")
            criteria.append("アーキテクチャの改善")
        else:
            criteria.append("問題の完全解決")
            criteria.append("システム安定性の確保")
        
        return criteria
    
    def _generate_validation_commands(self, issue: DiagnosisIssue) -> List[str]:
        """検証コマンド生成"""
        commands = []
        
        if issue.category == "TEST_COVERAGE":
            commands.extend([
                "python -m pytest project/tests/ --cov=system/core --cov-report=term-missing -v",
                "python -m coverage report --fail-under=95"
            ])
        elif issue.category == "MODULE_IMPORT":
            commands.extend([
                "python -c \"import sys; sys.path.insert(0, 'system'); from core import *; print('All imports successful')\"",
                "python system/core/dependency_checker.py"
            ])
        else:
            commands.extend([
                "python -m pytest project/tests/ -v --tb=short",
                "lefthook run ai-ready"
            ])
        
        return commands
    
    def _generate_expected_outcomes(self, issue: DiagnosisIssue, action_type: ImprovementActionType) -> List[str]:
        """期待される成果生成"""
        outcomes = []
        
        if action_type == ImprovementActionType.TEST_GENERATION:
            outcomes.extend([
                "自動生成されたテストファイル",
                "95%以上のテストカバレッジ",
                "全テスト正常実行"
            ])
        elif action_type == ImprovementActionType.CODE_FIX:
            outcomes.extend([
                "エラーの完全修正",
                "正常なモジュール動作",
                "統合テスト通過"
            ])
        elif action_type == ImprovementActionType.REFACTORING:
            outcomes.extend([
                "コード品質の向上",
                "保守性の改善",
                "パフォーマンス最適化"
            ])
        
        return outcomes
    
    def _get_priority_from_severity(self, severity: DiagnosisSeverity) -> int:
        """重要度から優先度を算出"""
        priority_map = {
            DiagnosisSeverity.CRITICAL: 1,
            DiagnosisSeverity.HIGH: 2,
            DiagnosisSeverity.MEDIUM: 3,
            DiagnosisSeverity.LOW: 4,
            DiagnosisSeverity.INFO: 5
        }
        return priority_map.get(severity, 3)
    
    def _identify_low_coverage_modules(self) -> List[str]:
        """カバレッジ不足モジュール特定"""
        # 簡易版 - 実際のカバレッジデータから特定
        py_files = list(self.core_path.glob("*.py"))
        test_files = list(self.tests_path.glob("test_*.py"))
        
        tested_modules = set()
        for test_file in test_files:
            module_name = test_file.name.replace("test_", "").replace(".py", "")
            tested_modules.add(module_name)
        
        low_coverage = []
        for py_file in py_files:
            if py_file.stem not in tested_modules and not py_file.stem.startswith("test_"):
                low_coverage.append(py_file.stem)
        
        return low_coverage[:10]  # 最大10個
    
    def _evaluate_overall_health(self):
        """全体健全性評価"""
        issues = self.diagnosis_results["issues_found"]
        
        critical_count = sum(1 for issue in issues if issue["severity"] == "critical")
        high_count = sum(1 for issue in issues if issue["severity"] == "high")
        
        if critical_count > 0:
            self.diagnosis_results["overall_health"] = "CRITICAL"
        elif high_count > 3:
            self.diagnosis_results["overall_health"] = "NEEDS_ATTENTION"
        elif len(issues) > 5:
            self.diagnosis_results["overall_health"] = "GOOD"
        else:
            self.diagnosis_results["overall_health"] = "EXCELLENT"
    
    def _generate_optimized_report(self, improvement_proposals: List[Dict[str, Any]]) -> BaseResult:
        """最適化レポート生成"""
        try:
            # レポートファイル保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = paths.root / f"OPTIMIZED_DIAGNOSIS_REPORT_{timestamp}.md"
            
            report_content = self._create_detailed_report(improvement_proposals)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"\nOptimized Diagnosis Report: {report_path}")
            print(f"   Issues Found: {len(self.diagnosis_results['issues_found'])}")
            print(f"   AI Proposals: {len(improvement_proposals)}")
            print(f"   Estimated Roundtrip Reduction: 75-85%")
            
            return create_result(True, "Optimized report generated", {"report_path": str(report_path)})
            
        except Exception as e:
            return create_result(False, f"Report generation failed: {e}")
    
    def _create_detailed_report(self, improvement_proposals: List[Dict[str, Any]]) -> str:
        """詳細レポート作成"""
        report = f"""# Alex Team Optimized Diagnosis Report

## 📊 Diagnosis Summary
- **Timestamp**: {self.diagnosis_results['timestamp']}
- **System Version**: v{self.diagnosis_results['version']}
- **Overall Health**: {self.diagnosis_results['overall_health']}
- **Issues Found**: {len(self.diagnosis_results['issues_found'])}
- **Test Coverage**: {self.diagnosis_results['test_coverage']:.1f}%

## 🎯 AI Roundtrip Optimization Results
- **Traditional Approach**: 15-20 AI interactions per issue
- **Optimized Approach**: 3-5 AI interactions per issue
- **Reduction**: **75-85% fewer roundtrips**
- **Time Saving**: 2-3 hours → 30-45 minutes

## 🚀 AI-Optimized Improvement Proposals

"""
        
        for i, proposal in enumerate(improvement_proposals, 1):
            report += f"""
### {i}. {proposal['action_type'].title()} (Priority: {proposal['priority']})

**Issue ID**: {proposal['issue_id']}

#### AI Implementation Request
```
{proposal['ai_implementation_request']}
```

#### Batch Processing Specification
- **Expected Outcomes**: {', '.join(proposal['batch_processing_spec']['expected_outcomes'])}
- **Validation Commands**: {len(proposal['batch_processing_spec']['validation_commands'])} automated checks

#### Roundtrip Optimization
- **Traditional Rounds**: {proposal['roundtrip_optimization']['estimated_traditional_rounds']}
- **Optimized Rounds**: {proposal['roundtrip_optimization']['estimated_optimized_rounds']}
- **Reduction**: {proposal['roundtrip_optimization']['reduction_percentage']}

---
"""
        
        report += f"""
## 📈 Next Steps

### 1. Copy AI Implementation Requests
Copy the above AI implementation requests and send them to AI in sequence.

### 2. Monitor Optimization Metrics
- Expected total rounds: {len(improvement_proposals) * 3}-{len(improvement_proposals) * 5}
- Traditional total rounds: {len(improvement_proposals) * 15}-{len(improvement_proposals) * 20}
- Savings: **{len(improvement_proposals) * 12}-{len(improvement_proposals) * 17} rounds**

### 3. Validation
Run automated validation after each implementation:
```bash
lefthook run ai-ready
python system/core/optimized_self_diagnosis_system.py --validate
```

---

**Generated by**: Alex Team Optimized Self-Diagnosis System v15.0
**Optimization Reference**: https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e
"""
        
        return report


def run_optimized_diagnosis() -> BaseResult:
    """最適化診断実行のメインエントリーポイント"""
    system = OptimizedSelfDiagnosisSystem()
    
    # 初期化
    init_result = system.initialize()
    if not init_result.success:
        return init_result
    
    # 最適化診断サイクル実行
    diagnosis_result = system.run_optimized_diagnosis_cycle()
    
    # クリーンアップ
    system.cleanup()
    
    return diagnosis_result


def main():
    """コマンドライン実行"""
    print("Starting Alex Team Optimized Self-Diagnosis...")
    
    result = run_optimized_diagnosis()
    
    if result.success:
        print("\nSUCCESS: Optimized diagnosis completed successfully!")
        if result.data and 'batch_count' in result.data:
            print(f"   Generated {result.data['batch_count']} AI-optimized improvement proposals")
        return 0
    else:
        print(f"\nERROR: Diagnosis failed: {result.message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())