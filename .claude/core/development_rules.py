#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合開発ルール自動化システム - Claude Code Core v12.0
CTOの3つの教訓の自動実装とアレックスとの連携 (モジュラー構造)

3つの教訓:
1. 「推測より確認」 - 修正前の完全理解
2. 「テストファースト」 - TDD強制実行
3. 「段階的修正」 - 単一タスク集中管理
"""

from typing import Dict, List, Optional, Any

# 分割されたモジュールをインポート
from .dev_rules_core import dev_rules_core, RuleType, TDDPhase
from .dev_rules_checklist import checklist_manager
from .dev_rules_tdd import tdd_manager
from .dev_rules_tasks import task_manager
from .dev_rules_integration import integration_manager

class DevelopmentRulesEngine:
    """統合開発ルール管理エンジン（ファサード）"""
    
    def __init__(self):
        """エンジンの初期化"""
        self.core = dev_rules_core
        self.checklist = checklist_manager
        self.tdd = tdd_manager
        self.tasks = task_manager
        self.integration = integration_manager
    
    # ==================== 教訓1: 推測より確認 ====================
    
    def execute_pre_modification_checklist(self, target_files: List[str], modification_desc: str) -> Dict[str, Any]:
        """修正前チェックリストの実行（教訓1）"""
        return self.checklist.execute_pre_modification_checklist(target_files, modification_desc)
    
    # ==================== 教訓2: テストファースト ====================
    
    def enforce_tdd_workflow(self, operation: str, file_path: str) -> Dict[str, Any]:
        """TDDワークフローの強制（教訓2）"""
        return self.tdd.enforce_tdd_workflow(operation, file_path)
    
    def _get_current_tdd_phase(self):
        """現在のTDDフェーズを取得"""
        return self.tdd._get_current_tdd_phase()
    
    # ==================== 教訓3: 段階的修正 ====================
    
    def enforce_incremental_fix(self, task_description: str) -> Dict[str, Any]:
        """段階的修正の強制（教訓3）"""
        return self.tasks.enforce_incremental_fix(task_description)
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """タスクの完了"""
        return self.tasks.complete_task(task_id)
    
    def _get_ongoing_tasks(self) -> List[Dict[str, Any]]:
        """進行中タスクの取得"""
        return self.tasks.get_ongoing_tasks()
    
    # ==================== 統合ワークフロー ====================
    
    def execute_integrated_workflow(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """統合開発ワークフローの実行"""
        return self.integration.execute_integrated_workflow(modification_request)
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        status = self.core.get_system_status()
        # TDDフェーズを追加
        status["current_tdd_phase"] = self.tdd.get_current_phase()
        status["ongoing_tasks"] = len(self.tasks.get_ongoing_tasks())
        return status

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
    print("=== 統合開発ルール自動化システム v12.0 (モジュラー構造) ===")
    
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