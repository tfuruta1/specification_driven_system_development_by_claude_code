#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合ワークフロー管理システム - Integration Workflow Manager
3つの教訓を統合した包括的チェック
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dev_rules_core import dev_rules_core, logger
from .dev_rules_checklist import checklist_manager
from .dev_rules_tdd import tdd_manager
from .dev_rules_tasks import task_manager

class IntegrationWorkflowManager:
    """統合ワークフロー管理システム"""
    
    def __init__(self):
        """統合ワークフロー管理システムの初期化"""
        self.core = dev_rules_core
        self.checklist = checklist_manager
        self.tdd = tdd_manager
        self.tasks = task_manager
        logger.info("統合ワークフロー管理システム初期化完了", "INTEGRATION")
    
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
        logger.info(f"統合ワークフロー開始: {workflow_id}", "INTEGRATION")
        
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
            if self.core.rules_config.get('validate_emojis', True):
                result["current_step"] = "emoji_validation"
                emoji_result = self.core._validate_emojis_in_request(modification_request)
                result["steps_completed"].append("emoji_validation")
                
                if not emoji_result["valid"]:
                    result["warnings"].append(f"絵文字検出: {emoji_result['emojis_found']}")
            
            # Step 2: 段階的修正チェック（教訓3）
            result["current_step"] = "incremental_fix_check"
            incremental_result = self.tasks.enforce_incremental_fix(modification_request["description"])
            result["steps_completed"].append("incremental_fix_check")
            
            if not incremental_result["allowed"]:
                result["status"] = "blocked"
                result["errors"].append(f"段階的修正: {incremental_result['message']}")
                return result
            
            # Step 3: 修正前チェックリスト（教訓1）
            result["current_step"] = "pre_modification_checklist"
            checklist_result = self.checklist.execute_pre_modification_checklist(
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
                tdd_result = self.tdd.enforce_tdd_workflow("implement", file_path)
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
            
            logger.info(f"統合ワークフロー完了: {workflow_id}", "INTEGRATION")
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"ワークフロー実行エラー: {str(e)}")
            logger.error(f"統合ワークフロー失敗 ({workflow_id}): {e}", "INTEGRATION")
        
        finally:
            # ワークフロー履歴に追加
            self.core._record_workflow_execution(result)
        
        return result

# シングルトンインスタンス
integration_manager = IntegrationWorkflowManager()