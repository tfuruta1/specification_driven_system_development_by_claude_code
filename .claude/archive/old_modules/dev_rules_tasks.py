#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK - Task & Incremental Manager
TASK3TASK
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dev_rules_core import dev_rules_core, logger

class TaskIncrementalManager:
    """SYSTEM"""
    
    def __init__(self):
        """SYSTEM"""
        self.core = dev_rules_core
        logger.info("SYSTEM", "TASKS")
    
    def enforce_incremental_fix(self, task_description: str) -> Dict[str, Any]:
        """
        TASK3TASK
        
        Args:
            task_description: CONFIG
            
        Returns:
            CONFIG
        """
        if not self.core.rules_config.get('enforce_incremental_fix', True):
            return {
                "allowed": True,
                "message": "SUCCESS",
                "task_complexity": "bypassed"
            }
        
        # SUCCESS
        complexity_analysis = self._analyze_task_complexity(task_description)
        
        # TASK
        ongoing_tasks = self._get_ongoing_tasks()
        
        result = {
            "task_description": task_description,
            "complexity": complexity_analysis["complexity"],
            "allowed": False,
            "message": "",
            "ongoing_tasks": ongoing_tasks,
            "recommendations": []
        }
        
        # TASK
        if complexity_analysis["complexity"] == "high":
            result["message"] = "REPORT"
            result["recommendations"].extend(complexity_analysis["split_suggestions"])
            result["allowed"] = False
        
        # TASK
        elif len(ongoing_tasks) > 0:
            result["message"] = f"TASK: {ongoing_tasks[0]['description']}"
            result["recommendations"].append("TASK")
            result["allowed"] = False
        
        else:
            result["allowed"] = True
            result["message"] = "TASKOK: TASK"
            
            # TASK
            self._record_new_task(task_description, complexity_analysis)
        
        logger.info(f"TASK: {task_description[:50]}... - {'TASK' if result['allowed'] else 'TASK'}", "TASKS")
        
        return result
    
    def _analyze_task_complexity(self, task_description: str) -> Dict[str, Any]:
        """TASK"""
        # TASK
        high_complexity_keywords = [
            "", "", "", "", "",
            "", "API", "", "", ""
        ]
        
        medium_complexity_keywords = [
            "", "", "", "", "", "", ""
        ]
        
        low_complexity_keywords = [
            "TASK", "TASK", "TASK", "TASK", "TASK"
        ]
        
        description_lower = task_description.lower()
        
        high_count = sum(1 for keyword in high_complexity_keywords if keyword in description_lower)
        medium_count = sum(1 for keyword in medium_complexity_keywords if keyword in description_lower)
        low_count = sum(1 for keyword in low_complexity_keywords if keyword in description_lower)
        
        if high_count > 0:
            complexity = "high"
            split_suggestions = [
                "",
                "",
                ""
            ]
        elif medium_count > low_count:
            complexity = "medium"
            split_suggestions = [
                "",
                ""
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
        """SYSTEM"""
        try:
            tasks_file = self.core.project_paths['cache'] / 'ongoing_tasks.json'
            
            if not tasks_file.exists():
                return []
            
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # SUCCESS
            ongoing = [task for task in tasks if not task.get('completed', False)]
            
            return ongoing
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "TASKS")
            return []
    
    def _record_new_task(self, task_description: str, complexity_analysis: Dict[str, Any]) -> None:
        """SYSTEM"""
        try:
            tasks_file = self.core.project_paths['cache'] / 'ongoing_tasks.json'
            
            # SYSTEM
            tasks = []
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
            
            # TASK
            new_task = {
                "id": len(tasks) + 1,
                "description": task_description,
                "complexity": complexity_analysis["complexity"],
                "started_at": datetime.now().isoformat(),
                "completed": False,
                "completed_at": None
            }
            
            tasks.append(new_task)
            
            # TASK
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
                
            logger.info(f"ERROR: {task_description}", "TASKS")
            
        except Exception as e:
            logger.error(f"SUCCESS: {e}", "TASKS")
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """SUCCESS"""
        try:
            tasks_file = self.core.project_paths['cache'] / 'ongoing_tasks.json'
            
            if not tasks_file.exists():
                return {"success": False, "error": "SUCCESS"}
            
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # TASK
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    task["completed_at"] = datetime.now().isoformat()
                    
                    # SUCCESS
                    with open(tasks_file, 'w', encoding='utf-8') as f:
                        json.dump(tasks, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"TASK: {task['description']}", "TASKS")
                    
                    return {
                        "success": True,
                        "completed_task": task
                    }
            
            return {"success": False, "error": "SUCCESS"}
            
        except Exception as e:
            logger.error(f"SUCCESS: {e}", "TASKS")
            return {"success": False, "error": str(e)}
    
    def get_ongoing_tasks(self) -> List[Dict[str, Any]]:
        """ERRORAPIERROR"""
        return self._get_ongoing_tasks()

# TASK
task_manager = TaskIncrementalManager()