#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK - Integration Workflow Manager
3TASK
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dev_rules_core import dev_rules_core, logger
from .dev_rules_checklist import checklist_manager
from .dev_rules_tdd import tdd_manager
from .dev_rules_tasks import task_manager

class IntegrationWorkflowManager:
    """SYSTEM"""
    
    def __init__(self):
        """SYSTEM"""
        self.core = dev_rules_core
        self.checklist = checklist_manager
        self.tdd = tdd_manager
        self.tasks = task_manager
        logger.info("TASK", "INTEGRATION")
    
    def execute_integrated_workflow(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        TASK
        3
        
        Args:
            modification_request: 
                - files: 
                - description: 
                - type: TASK
                
        Returns:
            TASK
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"TASK: {workflow_id}", "INTEGRATION")
        
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
            # Step 1: CONFIG
            if self.core.rules_config.get('validate_emojis', True):
                result["current_step"] = "emoji_validation"
                emoji_result = self.core._validate_emojis_in_request(modification_request)
                result["steps_completed"].append("emoji_validation")
                
                if not emoji_result["valid"]:
                    result["warnings"].append(f"WARNING: {emoji_result['emojis_found']}")
            
            # Step 2: WARNING3REPORT
            result["current_step"] = "incremental_fix_check"
            incremental_result = self.tasks.enforce_incremental_fix(modification_request["description"])
            result["steps_completed"].append("incremental_fix_check")
            
            if not incremental_result["allowed"]:
                result["status"] = "blocked"
                result["errors"].append(f"ERROR: {incremental_result['message']}")
                return result
            
            # Step 3: REPORT1REPORT
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
            
            # Step 4: TDDREPORT2REPORT
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
            
            # SUCCESS
            result["status"] = "completed"
            result["modification_allowed"] = True
            result["current_step"] = "ready_for_modification"
            
            logger.info(f"ERROR: {workflow_id}", "INTEGRATION")
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"ERROR: {str(e)}")
            logger.error(f"ERROR ({workflow_id}): {e}", "INTEGRATION")
        
        finally:
            # ERROR
            self.core._record_workflow_execution(result)
        
        return result

# SYSTEM
integration_manager = IntegrationWorkflowManager()