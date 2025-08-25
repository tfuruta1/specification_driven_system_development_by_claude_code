#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDDTASK - TDD Workflow Manager
TASK2TASK
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .dev_rules_core import dev_rules_core, TDDPhase, logger

class TDDWorkflowManager:
    """TDDSYSTEM"""
    
    def __init__(self):
        """TDDSYSTEM"""
        self.core = dev_rules_core
        self.tdd_state_file = self.core.tdd_state_file
        logger.info("TDDSYSTEM", "TDD")
    
    def enforce_tdd_workflow(self, operation: str, file_path: str) -> Dict[str, Any]:
        """
        TDDTEST2TEST
        
        Args:
            operation: TEST ('test', 'implement', 'refactor')
            file_path: TEST
            
        Returns:
            TDDTEST
        """
        if not self.core.rules_config.get('enforce_test_first', True):
            return {
                "allowed": True,
                "message": "TDDSUCCESS",
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
        
        # TEST
        if operation == "test":
            # TEST
            enforcement_result["allowed"] = True
            enforcement_result["message"] = "REPORT"
            self._update_tdd_phase(TDDPhase.RED, file_path)
            
        elif operation == "implement":
            if current_phase == TDDPhase.RED:
                # REDREPORT
                enforcement_result["allowed"] = True
                enforcement_result["message"] = "RED phase: REPORT"
                enforcement_result["recommendations"].append("REPORT")
                self._update_tdd_phase(TDDPhase.GREEN, file_path)
            else:
                # REPORT
                enforcement_result["allowed"] = False
                enforcement_result["message"] = "REPORTRED phaseREPORT"
                enforcement_result["required_actions"].append("REPORT")
                
        elif operation == "refactor":
            if current_phase in [TDDPhase.GREEN, TDDPhase.REFACTOR]:
                # GREEN/REFACTORREPORT
                enforcement_result["allowed"] = True
                enforcement_result["message"] = "GREEN phase: REPORT"
                enforcement_result["recommendations"].append("REPORT")
                self._update_tdd_phase(TDDPhase.REFACTOR, file_path)
            else:
                enforcement_result["allowed"] = False
                enforcement_result["message"] = "REPORT"
                enforcement_result["required_actions"].append("REPORT")
        
        # TDDREPORT
        self._record_tdd_operation(operation, file_path, enforcement_result)
        
        logger.info(f"TDDREPORT: {operation} on {Path(file_path).name} - {'REPORT' if enforcement_result['allowed'] else 'REPORT'}", "TDD")
        
        return enforcement_result
    
    def _get_current_tdd_phase(self) -> TDDPhase:
        """REPORTTDDREPORT"""
        try:
            if not self.tdd_state_file.exists():
                return TDDPhase.UNKNOWN
            
            with open(self.tdd_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_test_result = state.get('last_test_result')
            
            if not last_test_result:
                return TDDPhase.UNKNOWN
            
            # ERROR = REDERROR
            if last_test_result.get('failed', 0) > 0:
                return TDDPhase.RED
            
            # SUCCESS
            elif last_test_result.get('passed', 0) > 0:
                # SUCCESS = GREENSUCCESS
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
            logger.error(f"TDDERROR: {e}", "TDD")
            return TDDPhase.UNKNOWN
    
    def _update_tdd_phase(self, phase: TDDPhase, file_path: str) -> None:
        """TDD"""
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
            logger.error(f"TDDERROR: {e}", "TDD")
    
    def _record_tdd_operation(self, operation: str, file_path: str, result: Dict[str, Any]) -> None:
        """TDDREPORT"""
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
            
            # 100
            if len(state["operations_history"]) > 100:
                state["operations_history"] = state["operations_history"][-100:]
            
            with open(self.tdd_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"TDDERROR: {e}", "TDD")
    
    def get_current_phase(self) -> str:
        """ERRORTDDERRORAPITASK"""
        return self._get_current_tdd_phase().value

# TASK
tdd_manager = TDDWorkflowManager()