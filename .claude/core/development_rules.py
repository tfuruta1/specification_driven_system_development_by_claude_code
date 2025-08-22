#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合開発ルール自動化システム - Claude Code Core v11.0
CTOの3つの教訓の自動実装とアレックスとの連携

3つの教訓:
1. 「推測より確認」 - 修正前の完全理解
2. 「テストファースト」 - TDD強制実行
3. 「段階的修正」 - 単一タスク集中管理
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .config import get_config
from .logger import logger
from .emoji_validator import emoji_validator

class RuleType(Enum):
    """開発ルールタイプ"""
    CHECKLIST = "checklist"           # 修正前チェックリスト
    TEST_FIRST = "test_first"         # テストファースト
    INCREMENTAL = "incremental"       # 段階的修正
    EMOJI_VALIDATION = "emoji"        # 絵文字検証

class TDDPhase(Enum):
    """TDDフェーズ"""
    RED = "red"        # 失敗するテストを書く
    GREEN = "green"    # テストを通す最小限の実装
    REFACTOR = "refactor"  # リファクタリング
    UNKNOWN = "unknown"    # 状態不明

class DevelopmentRulesEngine:
    """統合開発ルール管理エンジン"""
    
    def __init__(self):
        """エンジンの初期化"""
        self.config = get_config()
        self.rules_config = self.config.get_rules_config()
        
        # プロジェクトパス設定
        self.project_paths = self.config.get_project_paths()
        self.state_file = self.project_paths['cache'] / 'development_rules_state.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # TDD状態管理
        self.tdd_state_file = self.project_paths['cache'] / 'tdd_state.json'
        
        # チェックリスト状態管理
        self.checklist_file = self.project_paths['cache'] / 'checklist_status.json'
        
        # 現在の状態を読み込み
        self.current_state = self._load_state()
        
        logger.info("開発ルールエンジン初期化完了", "RULES")
    
    def _load_state(self) -> Dict[str, Any]:
        """開発状態の読み込み"""
        default_state = {
            "version": "11.0",
            "last_updated": datetime.now().isoformat(),
            "active_rules": [],
            "current_task": None,
            "modification_allowed": False,
            "workflow_history": []
        }
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    return {**default_state, **state}
        except Exception as e:
            logger.error(f"状態読み込みエラー: {e}", "RULES")
        
        return default_state
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """開発状態の保存"""
        try:
            state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"状態保存エラー: {e}", "RULES")
    
    # ==================== 教訓1: 推測より確認 ====================
    
    def execute_pre_modification_checklist(self, target_files: List[str], modification_desc: str) -> Dict[str, Any]:
        """
        修正前チェックリストの実行（教訓1）
        
        Args:
            target_files: 対象ファイルリスト
            modification_desc: 修正内容説明
            
        Returns:
            チェックリスト実行結果
        """
        if not self.rules_config.get('enforce_checklist', True):
            return {
                "passed": True,
                "message": "チェックリスト実行はスキップされました",
                "checklist_items": {}
            }
        
        logger.info(f"修正前チェックリスト開始: {modification_desc}", "CHECKLIST")
        
        checklist_items = {
            "file_understanding": False,      # ファイル内容の理解
            "impact_analysis": False,         # 影響範囲の分析
            "similar_code_check": False,      # 類似コードの確認
            "test_written": False,            # テストの作成
            "backup_created": False,          # バックアップの作成
            "dependencies_checked": False     # 依存関係の確認
        }
        
        # 各チェック項目の自動実行
        checklist_result = {
            "target_files": target_files,
            "modification_desc": modification_desc,
            "checklist_items": checklist_items,
            "passed": False,
            "recommendations": [],
            "blockers": []
        }
        
        # 1. ファイル理解チェック
        understanding_result = self._check_file_understanding(target_files)
        checklist_items["file_understanding"] = understanding_result["understood"]
        if not understanding_result["understood"]:
            checklist_result["blockers"].append("ファイル内容の理解が不十分です")
        
        # 2. 影響範囲分析
        impact_result = self._analyze_impact_scope(target_files)
        checklist_items["impact_analysis"] = impact_result["analyzed"]
        if impact_result["high_risk"]:
            checklist_result["recommendations"].append("高リスク修正のため慎重に進めてください")
        
        # 3. 類似コード確認
        similar_result = self._check_similar_code(target_files)
        checklist_items["similar_code_check"] = similar_result["checked"]
        
        # 4. テスト存在確認
        test_result = self._check_tests_exist(target_files)
        checklist_items["test_written"] = test_result["tests_exist"]
        if not test_result["tests_exist"]:
            checklist_result["blockers"].append("対応するテストが存在しません")
        
        # 5. バックアップ作成
        backup_result = self._create_backup(target_files)
        checklist_items["backup_created"] = backup_result["created"]
        
        # 6. 依存関係チェック
        deps_result = self._check_dependencies(target_files)
        checklist_items["dependencies_checked"] = deps_result["checked"]
        
        # 総合判定
        required_items = ["file_understanding", "test_written", "backup_created"]
        checklist_result["passed"] = all(checklist_items[item] for item in required_items)
        
        # チェックリスト状態を保存
        self._save_checklist_status(checklist_result)
        
        if checklist_result["passed"]:
            logger.info("修正前チェックリスト: 全項目完了", "CHECKLIST")
        else:
            logger.warning(f"修正前チェックリスト: {len(checklist_result['blockers'])}個のブロッカー", "CHECKLIST")
        
        return checklist_result
    
    def _check_file_understanding(self, target_files: List[str]) -> Dict[str, Any]:
        """ファイル理解チェック"""
        understood_files = []
        
        for file_path in target_files:
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    # ファイルサイズと行数をチェック
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 簡易複雑度チェック
                    complexity = len([line for line in lines if 'def ' in line or 'class ' in line])
                    
                    understood_files.append({
                        "file": str(file_path),
                        "lines": len(lines),
                        "complexity": complexity,
                        "readable": complexity < 20  # 閾値判定
                    })
                    
                except Exception as e:
                    logger.error(f"ファイル理解チェックエラー ({file_path}): {e}", "CHECKLIST")
        
        understood = all(f["readable"] for f in understood_files)
        
        return {
            "understood": understood,
            "files_analyzed": understood_files,
            "complex_files": [f for f in understood_files if not f["readable"]]
        }
    
    def _analyze_impact_scope(self, target_files: List[str]) -> Dict[str, Any]:
        """影響範囲分析"""
        impact_areas = []
        high_risk = False
        
        for file_path in target_files:
            file_path = Path(file_path)
            
            # ファイルタイプによるリスク判定
            if file_path.suffix in ['.vue', '.js', '.ts']:
                # フロントエンド重要ファイル
                if 'store' in str(file_path) or 'router' in str(file_path):
                    high_risk = True
                    impact_areas.append(f"重要システムファイル: {file_path}")
            
            elif file_path.suffix == '.py':
                # Python重要ファイル
                if 'config' in str(file_path) or 'main' in str(file_path):
                    high_risk = True
                    impact_areas.append(f"重要設定ファイル: {file_path}")
        
        return {
            "analyzed": True,
            "impact_areas": impact_areas,
            "high_risk": high_risk,
            "risk_level": "high" if high_risk else "medium" if impact_areas else "low"
        }
    
    def _check_similar_code(self, target_files: List[str]) -> Dict[str, Any]:
        """類似コード確認"""
        # 簡易的な実装（実際にはより高度な分析が必要）
        similar_files = []
        
        for file_path in target_files:
            file_path = Path(file_path)
            
            # 同じディレクトリ内の類似ファイルを検索
            if file_path.exists():
                parent_dir = file_path.parent
                similar_pattern = f"*{file_path.stem}*{file_path.suffix}"
                
                for similar_file in parent_dir.glob(similar_pattern):
                    if similar_file != file_path:
                        similar_files.append(str(similar_file))
        
        return {
            "checked": True,
            "similar_files": similar_files,
            "pattern_matches": len(similar_files)
        }
    
    def _check_tests_exist(self, target_files: List[str]) -> Dict[str, Any]:
        """テスト存在確認"""
        test_status = {}
        tests_exist = True
        
        for file_path in target_files:
            file_path = Path(file_path)
            
            # テストファイルのパターンを生成
            test_patterns = self._generate_test_patterns(file_path)
            found_tests = []
            
            for pattern in test_patterns:
                test_files = list(self.project_paths['root'].rglob(pattern))
                found_tests.extend([str(f) for f in test_files])
            
            file_has_tests = len(found_tests) > 0
            test_status[str(file_path)] = {
                "has_tests": file_has_tests,
                "test_files": found_tests
            }
            
            if not file_has_tests:
                tests_exist = False
        
        return {
            "tests_exist": tests_exist,
            "test_status": test_status,
            "missing_tests": [f for f, status in test_status.items() if not status["has_tests"]]
        }
    
    def _generate_test_patterns(self, file_path: Path) -> List[str]:
        """テストファイルパターンの生成"""
        patterns = []
        
        if file_path.suffix == '.vue':
            patterns.append(f"**/{file_path.stem}.test.vue.js")
            patterns.append(f"**/{file_path.stem}.spec.vue.js")
        elif file_path.suffix in ['.js', '.ts']:
            patterns.append(f"**/{file_path.stem}.test{file_path.suffix}")
            patterns.append(f"**/{file_path.stem}.spec{file_path.suffix}")
        elif file_path.suffix == '.py':
            patterns.append(f"**/test_{file_path.stem}.py")
            patterns.append(f"**/{file_path.stem}_test.py")
        
        return patterns
    
    def _create_backup(self, target_files: List[str]) -> Dict[str, Any]:
        """バックアップ作成"""
        backup_dir = self.project_paths['workspace'] / 'backups' / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backed_up_files = []
        
        for file_path in target_files:
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    backup_path = backup_dir / file_path.name
                    backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                    backed_up_files.append({
                        "original": str(file_path),
                        "backup": str(backup_path)
                    })
                except Exception as e:
                    logger.error(f"バックアップ作成エラー ({file_path}): {e}", "CHECKLIST")
        
        return {
            "created": len(backed_up_files) > 0,
            "backup_dir": str(backup_dir),
            "backed_up_files": backed_up_files
        }
    
    def _check_dependencies(self, target_files: List[str]) -> Dict[str, Any]:
        """依存関係チェック"""
        dependencies = {}
        
        for file_path in target_files:
            file_path = Path(file_path)
            file_deps = []
            
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # import文やrequire文を検索
                    import_patterns = [
                        r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
                        r'require\([\'"]([^\'"]+)[\'"]\)',
                        r'from\s+([^\s]+)\s+import'
                    ]
                    
                    for pattern in import_patterns:
                        matches = __import__('re').findall(pattern, content)
                        file_deps.extend(matches)
                    
                    dependencies[str(file_path)] = list(set(file_deps))
                    
                except Exception as e:
                    logger.error(f"依存関係チェックエラー ({file_path}): {e}", "CHECKLIST")
        
        return {
            "checked": True,
            "dependencies": dependencies,
            "external_deps": [dep for deps in dependencies.values() for dep in deps if not dep.startswith('.')]
        }
    
    def _save_checklist_status(self, checklist_result: Dict[str, Any]) -> None:
        """チェックリスト状態の保存"""
        try:
            with open(self.checklist_file, 'w', encoding='utf-8') as f:
                json.dump(checklist_result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"チェックリスト状態保存エラー: {e}", "CHECKLIST")
    
    # ==================== 教訓2: テストファースト ====================
    
    def enforce_tdd_workflow(self, operation: str, file_path: str) -> Dict[str, Any]:
        """
        TDDワークフローの強制（教訓2）
        
        Args:
            operation: 実行操作 ('test', 'implement', 'refactor')
            file_path: 対象ファイルパス
            
        Returns:
            TDD強制結果
        """
        if not self.rules_config.get('enforce_test_first', True):
            return {
                "allowed": True,
                "message": "TDD強制は無効化されています",
                "phase": "bypassed"
            }
        
        current_phase = self._get_current_tdd_phase()
        
        enforcement_result = {
            "operation": operation,
            "file_path": file_path,
            "current_phase": current_phase.value,
            "allowed": False,
            "message": "",
            "required_actions": [],
            "recommendations": []
        }
        
        # フェーズ別の操作制御
        if operation == "test":
            # テスト作成は常に許可
            enforcement_result["allowed"] = True
            enforcement_result["message"] = "テスト作成は常に許可されます"
            self._update_tdd_phase(TDDPhase.RED, file_path)
            
        elif operation == "implement":
            if current_phase == TDDPhase.RED:
                # REDフェーズでの実装は許可
                enforcement_result["allowed"] = True
                enforcement_result["message"] = "RED phase: 実装許可"
                enforcement_result["recommendations"].append("最小限の実装でテストを通してください")
                self._update_tdd_phase(TDDPhase.GREEN, file_path)
            else:
                # 他のフェーズでは失敗するテストが必要
                enforcement_result["allowed"] = False
                enforcement_result["message"] = "実装には失敗するテストが必要です（RED phase）"
                enforcement_result["required_actions"].append("先に失敗するテストを作成してください")
                
        elif operation == "refactor":
            if current_phase in [TDDPhase.GREEN, TDDPhase.REFACTOR]:
                # GREEN/REFACTORフェーズでのリファクタリングは許可
                enforcement_result["allowed"] = True
                enforcement_result["message"] = "GREEN phase: リファクタリング許可"
                enforcement_result["recommendations"].append("テストが通り続けることを確認してください")
                self._update_tdd_phase(TDDPhase.REFACTOR, file_path)
            else:
                enforcement_result["allowed"] = False
                enforcement_result["message"] = "リファクタリングには全テストの成功が必要です"
                enforcement_result["required_actions"].append("全テストを成功させてください")
        
        # TDD状態の記録
        self._record_tdd_operation(operation, file_path, enforcement_result)
        
        logger.info(f"TDD強制: {operation} on {Path(file_path).name} - {'許可' if enforcement_result['allowed'] else '拒否'}", "TDD")
        
        return enforcement_result
    
    def _get_current_tdd_phase(self) -> TDDPhase:
        """現在のTDDフェーズを取得"""
        try:
            if not self.tdd_state_file.exists():
                return TDDPhase.UNKNOWN
            
            with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_test_result = state.get('last_test_result')
            
            if not last_test_result:
                return TDDPhase.UNKNOWN
            
            # テストが失敗している場合 = REDフェーズ
            if last_test_result.get('failed', 0) > 0:
                return TDDPhase.RED
            
            # テストが全て通っている場合
            elif last_test_result.get('passed', 0) > 0:
                # 最近実装が行われた場合 = GREENフェーズ
                last_implementation = state.get('last_implementation_time')
                if last_implementation:
                    impl_time = datetime.fromisoformat(last_implementation)
                    if datetime.now() - impl_time < timedelta(hours=1):
                        return TDDPhase.GREEN
                    else:
                        return TDDPhase.REFACTOR
                else:
                    return TDDPhase.GREEN
            
            return TDDPhase.UNKNOWN
            
        except Exception as e:
            logger.error(f"TDDフェーズ取得エラー: {e}", "TDD")
            return TDDPhase.UNKNOWN
    
    def _update_tdd_phase(self, phase: TDDPhase, file_path: str) -> None:
        """TDDフェーズの更新"""
        try:
            state = {}
            if self.tdd_state_file.exists():
                with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            
            state.update({
                "current_phase": phase.value,
                "last_file": file_path,
                "last_update": datetime.now().isoformat()
            })
            
            if phase == TDDPhase.GREEN:
                state["last_implementation_time"] = datetime.now().isoformat()
            
            with open(self.tdd_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"TDDフェーズ更新エラー: {e}", "TDD")
    
    def _record_tdd_operation(self, operation: str, file_path: str, result: Dict[str, Any]) -> None:
        """TDD操作の記録"""
        try:
            state = {}
            if self.tdd_state_file.exists():
                with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            
            if "operations_history" not in state:
                state["operations_history"] = []
            
            operation_record = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "file_path": file_path,
                "phase": result["current_phase"],
                "allowed": result["allowed"],
                "message": result["message"]
            }
            
            state["operations_history"].append(operation_record)
            
            # 履歴は最新100件まで保持
            if len(state["operations_history"]) > 100:
                state["operations_history"] = state["operations_history"][-100:]
            
            with open(self.tdd_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"TDD操作記録エラー: {e}", "TDD")
    
    # ==================== 教訓3: 段階的修正 ====================
    
    def enforce_incremental_fix(self, task_description: str) -> Dict[str, Any]:
        """
        段階的修正の強制（教訓3）
        
        Args:
            task_description: タスクの説明
            
        Returns:
            段階的修正強制結果
        """
        if not self.rules_config.get('enforce_incremental_fix', True):
            return {
                "allowed": True,
                "message": "段階的修正の強制は無効化されています",
                "task_complexity": "bypassed"
            }
        
        # タスクの複雑度を分析
        complexity_analysis = self._analyze_task_complexity(task_description)
        
        # 現在進行中のタスクをチェック
        ongoing_tasks = self._get_ongoing_tasks()
        
        result = {
            "task_description": task_description,
            "complexity": complexity_analysis["complexity"],
            "allowed": False,
            "message": "",
            "ongoing_tasks": ongoing_tasks,
            "recommendations": []
        }
        
        # 複雑度チェック
        if complexity_analysis["complexity"] == "high":
            result["message"] = "高複雑度タスクです。分割を検討してください"
            result["recommendations"].extend(complexity_analysis["split_suggestions"])
            result["allowed"] = False
        
        # 同時タスクチェック
        elif len(ongoing_tasks) > 0:
            result["message"] = f"進行中のタスクがあります: {ongoing_tasks[0]['description']}"
            result["recommendations"].append("現在のタスクを完了してから新しいタスクを開始してください")
            result["allowed"] = False
        
        else:
            result["allowed"] = True
            result["message"] = "段階的修正OK: タスクを開始できます"
            
            # 新しいタスクを記録
            self._record_new_task(task_description, complexity_analysis)
        
        logger.info(f"段階的修正チェック: {task_description[:50]}... - {'許可' if result['allowed'] else '拒否'}", "INCREMENTAL")
        
        return result
    
    def _analyze_task_complexity(self, task_description: str) -> Dict[str, Any]:
        """タスク複雑度の分析"""
        # キーワードベースの簡易分析
        high_complexity_keywords = [
            "リファクタリング", "統合", "移行", "アーキテクチャ", "設計変更",
            "データベース", "API変更", "認証", "セキュリティ", "パフォーマンス"
        ]
        
        medium_complexity_keywords = [
            "修正", "変更", "追加", "更新", "改善", "バグ修正", "機能追加"
        ]
        
        low_complexity_keywords = [
            "文言変更", "スタイル調整", "ログ追加", "コメント", "ドキュメント"
        ]
        
        description_lower = task_description.lower()
        
        high_count = sum(1 for keyword in high_complexity_keywords if keyword in description_lower)
        medium_count = sum(1 for keyword in medium_complexity_keywords if keyword in description_lower)
        low_count = sum(1 for keyword in low_complexity_keywords if keyword in description_lower)
        
        if high_count > 0:
            complexity = "high"
            split_suggestions = [
                "フェーズ別に分割する",
                "依存関係の少ない部分から開始する",
                "テストケースを段階的に作成する"
            ]
        elif medium_count > low_count:
            complexity = "medium"
            split_suggestions = [
                "機能単位で分割する",
                "ファイル単位で実装する"
            ]
        else:
            complexity = "low"
            split_suggestions = []
        
        return {
            "complexity": complexity,
            "high_keywords": high_count,
            "medium_keywords": medium_count,
            "low_keywords": low_count,
            "split_suggestions": split_suggestions
        }
    
    def _get_ongoing_tasks(self) -> List[Dict[str, Any]]:
        """進行中タスクの取得"""
        try:
            tasks_file = self.project_paths['cache'] / 'ongoing_tasks.json'
            
            if not tasks_file.exists():
                return []
            
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # 完了していないタスクのみ返す
            ongoing = [task for task in tasks if not task.get('completed', False)]
            
            return ongoing
            
        except Exception as e:
            logger.error(f"進行中タスク取得エラー: {e}", "INCREMENTAL")
            return []
    
    def _record_new_task(self, task_description: str, complexity_analysis: Dict[str, Any]) -> None:
        """新しいタスクの記録"""
        try:
            tasks_file = self.project_paths['cache'] / 'ongoing_tasks.json'
            
            # 既存タスクを読み込み
            tasks = []
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
            
            # 新しいタスクを追加
            new_task = {
                "id": len(tasks) + 1,
                "description": task_description,
                "complexity": complexity_analysis["complexity"],
                "started_at": datetime.now().isoformat(),
                "completed": False,
                "completed_at": None
            }
            
            tasks.append(new_task)
            
            # ファイルに保存
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
                
            logger.info(f"新しいタスク記録: {task_description}", "INCREMENTAL")
            
        except Exception as e:
            logger.error(f"タスク記録エラー: {e}", "INCREMENTAL")
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """タスクの完了"""
        try:
            tasks_file = self.project_paths['cache'] / 'ongoing_tasks.json'
            
            if not tasks_file.exists():
                return {"success": False, "error": "タスクファイルが見つかりません"}
            
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # タスクを探して完了マーク
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    task["completed_at"] = datetime.now().isoformat()
                    
                    # ファイルに保存
                    with open(tasks_file, 'w', encoding='utf-8') as f:
                        json.dump(tasks, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"タスク完了: {task['description']}", "INCREMENTAL")
                    
                    return {
                        "success": True,
                        "completed_task": task
                    }
            
            return {"success": False, "error": "指定されたタスクが見つかりません"}
            
        except Exception as e:
            logger.error(f"タスク完了エラー: {e}", "INCREMENTAL")
            return {"success": False, "error": str(e)}
    
    # ==================== 統合ワークフロー ====================
    
    def execute_integrated_workflow(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        統合開発ワークフローの実行
        3つの教訓を組み合わせた包括的なチェック
        
        Args:
            modification_request: 修正要求
                - files: 対象ファイルリスト
                - description: 修正内容説明
                - type: 修正タイプ
                
        Returns:
            ワークフロー実行結果
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"統合ワークフロー開始: {workflow_id}", "WORKFLOW")
        
        result = {
            "workflow_id": workflow_id,
            "status": "in_progress",
            "steps_completed": [],
            "current_step": None,
            "errors": [],
            "warnings": [],
            "modification_allowed": False,
            "request": modification_request
        }
        
        try:
            # Step 1: 絵文字検証
            if self.rules_config.get('validate_emojis', True):
                result["current_step"] = "emoji_validation"
                emoji_result = self._validate_emojis_in_request(modification_request)
                result["steps_completed"].append("emoji_validation")
                
                if not emoji_result["valid"]:
                    result["warnings"].append(f"絵文字検出: {emoji_result['emojis_found']}")
            
            # Step 2: 段階的修正チェック（教訓3）
            result["current_step"] = "incremental_fix_check"
            incremental_result = self.enforce_incremental_fix(modification_request["description"])
            result["steps_completed"].append("incremental_fix_check")
            
            if not incremental_result["allowed"]:
                result["status"] = "blocked"
                result["errors"].append(f"段階的修正: {incremental_result['message']}")
                return result
            
            # Step 3: 修正前チェックリスト（教訓1）
            result["current_step"] = "pre_modification_checklist"
            checklist_result = self.execute_pre_modification_checklist(
                modification_request["files"],
                modification_request["description"]
            )
            result["steps_completed"].append("pre_modification_checklist")
            
            if not checklist_result["passed"]:
                result["status"] = "blocked"
                result["errors"].extend(checklist_result["blockers"])
                return result
            
            # Step 4: TDD検証（教訓2）
            result["current_step"] = "tdd_validation"
            tdd_valid = True
            
            for file_path in modification_request["files"]:
                tdd_result = self.enforce_tdd_workflow("implement", file_path)
                if not tdd_result["allowed"]:
                    result["errors"].append(f"TDD: {tdd_result['message']} ({Path(file_path).name})")
                    tdd_valid = False
            
            result["steps_completed"].append("tdd_validation")
            
            if not tdd_valid:
                result["status"] = "blocked"
                return result
            
            # 全ステップ完了
            result["status"] = "completed"
            result["modification_allowed"] = True
            result["current_step"] = "ready_for_modification"
            
            logger.info(f"統合ワークフロー完了: {workflow_id}", "WORKFLOW")
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"ワークフロー実行エラー: {str(e)}")
            logger.error(f"統合ワークフロー失敗 ({workflow_id}): {e}", "WORKFLOW")
        
        finally:
            # ワークフロー履歴に追加
            self._record_workflow_execution(result)
        
        return result
    
    def _validate_emojis_in_request(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """修正要求内の絵文字検証"""
        description = modification_request.get("description", "")
        emojis_found = emoji_validator.detect_emojis(description)
        
        return {
            "valid": len(emojis_found) == 0,
            "emojis_found": emojis_found,
            "cleaned_description": emoji_validator.replace_emojis_with_text(description)
        }
    
    def _record_workflow_execution(self, result: Dict[str, Any]) -> None:
        """ワークフロー実行履歴の記録"""
        try:
            history_file = self.project_paths['cache'] / 'workflow_history.json'
            
            # 既存履歴を読み込み
            history = []
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 新しい実行結果を追加
            history.append({
                "workflow_id": result["workflow_id"],
                "timestamp": datetime.now().isoformat(),
                "status": result["status"],
                "steps_completed": result["steps_completed"],
                "modification_allowed": result["modification_allowed"],
                "errors_count": len(result.get("errors", [])),
                "warnings_count": len(result.get("warnings", []))
            })
            
            # 履歴は最新50件まで保持
            if len(history) > 50:
                history = history[-50:]
            
            # ファイルに保存
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"ワークフロー履歴記録エラー: {e}", "WORKFLOW")
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        return {
            "version": "11.0",
            "rules_enabled": {
                "checklist": self.rules_config.get('enforce_checklist', True),
                "test_first": self.rules_config.get('enforce_test_first', True),
                "incremental": self.rules_config.get('enforce_incremental_fix', True),
                "emoji_validation": self.rules_config.get('validate_emojis', True)
            },
            "current_tdd_phase": self._get_current_tdd_phase().value,
            "ongoing_tasks": len(self._get_ongoing_tasks()),
            "project_paths": {k: str(v) for k, v in self.project_paths.items()},
            "last_updated": self.current_state.get("last_updated")
        }

# シングルトンインスタンス
dev_rules = DevelopmentRulesEngine()

# 便利関数
def check_modification_allowed(files: List[str], description: str) -> bool:
    """修正が許可されているかチェック"""
    request = {
        "files": files,
        "description": description,
        "type": "modification"
    }
    result = dev_rules.execute_integrated_workflow(request)
    return result["modification_allowed"]

def get_tdd_phase() -> str:
    """現在のTDDフェーズを取得"""
    return dev_rules._get_current_tdd_phase().value

def complete_current_task() -> Dict[str, Any]:
    """現在のタスクを完了"""
    ongoing = dev_rules._get_ongoing_tasks()
    if ongoing:
        return dev_rules.complete_task(ongoing[0]["id"])
    return {"success": False, "error": "進行中のタスクはありません"}

# デモ実行
if __name__ == "__main__":
    print("=== 統合開発ルール自動化システム v11.0 ===")
    
    # システム状態表示
    status = dev_rules.get_system_status()
    print(f"バージョン: {status['version']}")
    print(f"現在のTDDフェーズ: {status['current_tdd_phase']}")
    print(f"進行中タスク: {status['ongoing_tasks']}件")
    
    # ルール状態
    print("\n有効ルール:")
    for rule, enabled in status['rules_enabled'].items():
        status_mark = "✓" if enabled else "✗"
        print(f"  {status_mark} {rule}")
    
    print("\n統合ワークフローテスト...")
    test_request = {
        "files": ["test_file.vue"],
        "description": "テスト用の簡単な修正",
        "type": "enhancement"
    }
    
    result = dev_rules.execute_integrated_workflow(test_request)
    print(f"結果: {result['status']}")
    print(f"修正許可: {result['modification_allowed']}")
    
    if result.get('errors'):
        print("エラー:")
        for error in result['errors']:
            print(f"  - {error}")