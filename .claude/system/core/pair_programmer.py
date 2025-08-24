#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTEM - Claude Code Core v11.0
SDD+TDD+SYSTEM

CTOSYSTEMYAGNISYSTEMDRYSYSTEMKISSCONFIG
"""

from typing import Dict, Any, Optional, List
from .logger import logger
from .config import get_config
from .development_rules import dev_rules, TDDPhase
from .emoji_validator import emoji_validator


class PairProgrammer:
    """- """
    
    def __init__(self, name: str = "", style: str = "friendly"):
        """
        Args:
            name: 
            style:  (friendly/serious/casual)
        """
        self.name = name
        self.style = style
        self.context = {}
        
        # CONFIG
        self.config = get_config()
        self.pair_config = self.config.get_pair_config()
        
        # CONFIG
        self.roles = {
            "driver": "CONFIGCTOCONFIG",
            "navigator": "",
            "rules_enforcer": "",
            "quality_guardian": ""
        }
        
        # 
        self.development_phases = {
            "requirements": "TEST",
            "design": "TEST",
            "test_writing": "TEST",
            "implementation": "TEST",
            "refactoring": "TEST",
            "review": ""
        }
        
        # 
        self.knowledge_base = {
            "sdd_tdd": {
                "red_phase": "",
                "green_phase": "",
                "refactor_phase": "ANALYSIS"
            },
            "development_rules": {
                "checklist": "TEST",
                "test_first": "TEST",
                "incremental": "TEST"
            },
            "quality_principles": {
                "yagni": "",
                "dry": "",
                "kiss": ""
            }
        }
        
        logger.info(f"{self.name}", "PAIR")
        
    def greet(self) -> str:
        """"""
        greetings = {
            "friendly": f"[HELLO] {self.name}",
            "serious": f"{self.name}",
            "casual": f"{self.name}"
        }
        return greetings.get(self.style, greetings["friendly"])
    
    def think_aloud(self, code: str) -> str:
        """"""
        responses = []
        
        # 
        if not code.strip():
            return f"{self.name}: "
        
        # 
        if "\t" in code and "    " in code:
            responses.append("")
        
        # 
        lines = code.split("\n")
        if len(lines) > 50:
            responses.append("")
        
        # 
        if "#" not in code and '"""' not in code:
            responses.append("")
        
        # 
        if "try:" not in code and "except" not in code:
            if "open(" in code or "request" in code:
                responses.append("")
        
        if responses:
            return f"{self.name}: {' '.join(responses)}"
        else:
            return f"{self.name}: TASK"
    
    def suggest_next(self, current_task: str) -> str:
        """TASK"""
        suggestions = {
            "TASK": "TASK",
            "": "TDD",
            "": "",
            "": "",
            "": "",
            "": ""
        }
        
        for key, suggestion in suggestions.items():
            if key in current_task:
                return f"{self.name}: TASK{suggestion}TASK"
        
        return f"{self.name}: "
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """"""
        issues = []
        suggestions = []
        good_points = []
        
        lines = code.split("\n")
        
        # 
        if "def " in code:
            good_points.append("")
        if "class " in code:
            good_points.append("")
        if any(line.strip().startswith("#") for line in lines):
            good_points.append("")
        
        # 
        for i, line in enumerate(lines, 1):
            # 
            if len(line) > 100:
                issues.append(f"L{i}: {len(line)}")
                suggestions.append(f"L{i}: ")
            
            # 
            if any(num in line for num in ["86400", "3600", "1024"]):
                suggestions.append(f"L{i}: ")
            
            # TODO/FIXME
            if "TODO" in line or "FIXME" in line:
                issues.append(f"L{i}: {line.strip()}")
        
        return {
            "reviewer": self.name,
            "good_points": good_points,
            "issues": issues,
            "suggestions": suggestions,
            "overall": self._get_overall_feedback(good_points, issues)
        }
    
    def _get_overall_feedback(self, good_points: list, issues: list) -> str:
        """"""
        if len(good_points) > len(issues):
            return ""
        elif len(issues) > 3:
            return "ERROR"
        else:
            return "ERROR"
    
    def debug_together(self, error_msg: str) -> str:
        """ERROR"""
        debug_hints = {
            "NameError": "ERROR",
            "TypeError": "ERRORstr()ERRORint()ERROR",
            "IndexError": "ERRORlen()ERROR",
            "KeyError": "ERROR.get()ERROR",
            "AttributeError": "ERROR/ERROR",
            "ImportError": "ERROR",
            "SyntaxError": "ERROR",
            "IndentationError": "ERROR"
        }
        
        for error_type, hint in debug_hints.items():
            if error_type in error_msg:
                return f"{self.name}: ERROR{hint}ERROR"
        
        return f"{self.name}: "
    
    def celebrate(self, achievement: str) -> str:
        """SUCCESS"""
        celebrations = {
            "test_pass": "[SUCCESS] SUCCESS",
            "bug_fix": "[FIXED] SUCCESS",
            "feature_complete": "[DONE] SUCCESS",
            "deploy": "[DEPLOY] SUCCESS",
            "refactor": "[CLEAN] SUCCESS"
        }
        
        for key, message in celebrations.items():
            if key in achievement.lower():
                return f"{self.name}: {message}"
        
        return f"{self.name}: [GOOD]"


# 
def demo():
    """"""
    # 
    pair = PairProgrammer("", "friendly")
    
    print(pair.greet())
    print()
    
    # 
    sample_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total
'''
    
    print(": ")
    print(pair.think_aloud(sample_code))
    print()
    
    # 
    review = pair.review_code(sample_code)
    print(f"=== {review['reviewer']} ===")
    print(f": {', '.join(review['good_points'])}")
    if review['suggestions']:
        print(f": {', '.join(review['suggestions'])}")
    print(f"ERROR: {review['overall']}")
    print()
    
    # ERROR
    print("ERROR: ERRORNameError: name 'items' is not definedERROR...ERROR")
    print(pair.debug_together("NameError: name 'items' is not defined"))
    print()
    
    # SUCCESS
    print("SUCCESS: SUCCESS")
    print(pair.celebrate("test_pass"))


if __name__ == "__main__":
    demo()