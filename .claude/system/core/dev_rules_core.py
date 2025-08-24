import copy
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIG - Core Engine & Configuration
CONFIG
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .config import get_config
from .logger import logger
from .emoji_validator import emoji_validator

class RuleType(Enum):
    """TEST"""
    CHECKLIST = "checklist"           # TEST
    TEST_FIRST = "test_first"         # TEST
    INCREMENTAL = "incremental"       # TEST
    EMOJI_VALIDATION = "emoji"        # 

class TDDPhase(Enum):
    """TDD"""
    RED = "red"        # 
    GREEN = "green"    # 
    REFACTOR = "refactor"  # SYSTEM
    UNKNOWN = "unknown"    # SYSTEM

class DevelopmentRulesCoreEngine:
    """CONFIG - CONFIG"""
    
    def __init__(self):
        """CONFIG"""
        self.config = get_config()
        self.rules_config = self.config.get_rules_config()
        
        # CONFIG
        self.project_paths = self.config.get_project_paths()
        self.state_file = self.project_paths['cache'] / 'development_rules_state.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # TDD
        self.tdd_state_file = self.project_paths['cache'] / 'tdd_state.json'
        
        # ANALYSIS
        self.checklist_file = self.project_paths['cache'] / 'checklist_status.json'
        
        # SYSTEM
        self.current_state = self._load_state()
        
        logger.info("SYSTEM", "RULES_CORE")
    
    def _load_state(self) -> Dict[str, Any]:
        """SYSTEM"""
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
            logger.error(f"ERROR: {e}", "RULES_CORE")
        
        return default_state
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """"""
        try:
            state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"ERROR: {e}", "RULES_CORE")
    
    def get_system_status(self) -> Dict[str, Any]:
        """SYSTEM"""
        return {
            "version": "11.0",
            "rules_enabled": {
                "checklist": self.rules_config.get('enforce_checklist', True),
                "test_first": self.rules_config.get('enforce_test_first', True),
                "incremental": self.rules_config.get('enforce_incremental_fix', True),
                "emoji_validation": self.rules_config.get('validate_emojis', True)
            },
            "project_paths": {k: str(v) for k, v in self.project_paths.items()},
            "last_updated": self.current_state.get("last_updated")
        }

    def _validate_emojis_in_request(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """"""
        description = modification_request.get("description", "")
        emojis_found = emoji_validator.detect_emojis(description)
        
        return {
            "valid": len(emojis_found) == 0,
            "emojis_found": emojis_found,
            "cleaned_description": emoji_validator.replace_emojis_with_text(description)
        }
    
    def _record_workflow_execution(self, result: Dict[str, Any]) -> None:
        """TASK"""
        try:
            history_file = self.project_paths['cache'] / 'workflow_history.json'
            
            # TASK
            history = []
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # TASK
            history.append({
                "workflow_id": result["workflow_id"],
                "timestamp": datetime.now().isoformat(),
                "status": result["status"],
                "steps_completed": result["steps_completed"],
                "modification_allowed": result["modification_allowed"],
                "errors_count": len(result.get("errors", [])),
                "warnings_count": len(result.get("warnings", []))
            })
            
            # WARNING50WARNING
            if len(history) > 50:
                history = history[-50:]
            
            # 
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"ERROR: {e}", "RULES_CORE")

# ERROR
dev_rules_core = DevelopmentRulesCoreEngine()