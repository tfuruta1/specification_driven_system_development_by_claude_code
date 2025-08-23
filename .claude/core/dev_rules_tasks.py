#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タスク・段階的修正管理システム - Task & Incremental Manager
教訓3「段階的修正」の実装
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dev_rules_core import dev_rules_core, logger

class TaskIncrementalManager:
    """タスク・段階的修正管理システム"""
    
    def __init__(self):
        """タスク・段階的修正管理システムの初期化"""
        self.core = dev_rules_core
        logger.info("タスク・段階的修正管理システム初期化完了", "TASKS")
    
    def enforce_incremental_fix(self, task_description: str) -> Dict[str, Any]:
        """
        段階的修正の強制（教訓3）
        
        Args:
            task_description: タスクの説明
            
        Returns:
            段階的修正強制結果
        """
        if not self.core.rules_config.get('enforce_incremental_fix', True):
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
        
        logger.info(f"段階的修正チェック: {task_description[:50]}... - {'許可' if result['allowed'] else '拒否'}", "TASKS")
        
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
            tasks_file = self.core.project_paths['cache'] / 'ongoing_tasks.json'
            
            if not tasks_file.exists():
                return []
            
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # 完了していないタスクのみ返す
            ongoing = [task for task in tasks if not task.get('completed', False)]
            
            return ongoing
            
        except Exception as e:
            logger.error(f"進行中タスク取得エラー: {e}", "TASKS")
            return []
    
    def _record_new_task(self, task_description: str, complexity_analysis: Dict[str, Any]) -> None:
        """新しいタスクの記録"""
        try:
            tasks_file = self.core.project_paths['cache'] / 'ongoing_tasks.json'
            
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
                
            logger.info(f"新しいタスク記録: {task_description}", "TASKS")
            
        except Exception as e:
            logger.error(f"タスク記録エラー: {e}", "TASKS")
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """タスクの完了"""
        try:
            tasks_file = self.core.project_paths['cache'] / 'ongoing_tasks.json'
            
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
                    
                    logger.info(f"タスク完了: {task['description']}", "TASKS")
                    
                    return {
                        "success": True,
                        "completed_task": task
                    }
            
            return {"success": False, "error": "指定されたタスクが見つかりません"}
            
        except Exception as e:
            logger.error(f"タスク完了エラー: {e}", "TASKS")
            return {"success": False, "error": str(e)}
    
    def get_ongoing_tasks(self) -> List[Dict[str, Any]]:
        """進行中タスクの取得（外部API用）"""
        return self._get_ongoing_tasks()

# シングルトンインスタンス
task_manager = TaskIncrementalManager()