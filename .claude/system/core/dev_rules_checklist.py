#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSIS - Checklist Manager
ANALYSIS1ANALYSIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dev_rules_core import dev_rules_core, logger

class ChecklistManager:
    """SYSTEM"""
    
    def __init__(self):
        """SYSTEM"""
        self.core = dev_rules_core
        self.checklist_file = self.core.checklist_file
        logger.info("SYSTEM", "CHECKLIST")
    
    def execute_pre_modification_checklist(self, target_files: List[str], modification_desc: str) -> Dict[str, Any]:
        """
        1
        
        Args:
            target_files: 
            modification_desc: CONFIG
            
        Returns:
            CONFIG
        """
        if not self.core.rules_config.get('enforce_checklist', True):
            return {
                "passed": True,
                "message": "SUCCESS",
                "checklist_items": {}
            }
        
        logger.info(f"ANALYSIS: {modification_desc}", "CHECKLIST")
        
        checklist_items = {
            "file_understanding": False,      # ANALYSIS
            "impact_analysis": False,         # TEST
            "similar_code_check": False,      # TEST
            "test_written": False,            # TEST
            "backup_created": False,          # TEST
            "dependencies_checked": False     # REPORT
        }
        
        # REPORT
        checklist_result = {
            "target_files": target_files,
            "modification_desc": modification_desc,
            "checklist_items": checklist_items,
            "passed": False,
            "recommendations": [],
            "blockers": []
        }
        
        # 1. REPORT
        understanding_result = self._check_file_understanding(target_files)
        checklist_items["file_understanding"] = understanding_result["understood"]
        if not understanding_result["understood"]:
            checklist_result["blockers"].append("REPORT")
        
        # 2. REPORT
        impact_result = self._analyze_impact_scope(target_files)
        checklist_items["impact_analysis"] = impact_result["analyzed"]
        if impact_result["high_risk"]:
            checklist_result["recommendations"].append("REPORT")
        
        # 3. REPORT
        similar_result = self._check_similar_code(target_files)
        checklist_items["similar_code_check"] = similar_result["checked"]
        
        # 4. TEST
        test_result = self._check_tests_exist(target_files)
        checklist_items["test_written"] = test_result["tests_exist"]
        if not test_result["tests_exist"]:
            checklist_result["blockers"].append("TEST")
        
        # 5. TEST
        backup_result = self._create_backup(target_files)
        checklist_items["backup_created"] = backup_result["created"]
        
        # 6. REPORT
        deps_result = self._check_dependencies(target_files)
        checklist_items["dependencies_checked"] = deps_result["checked"]
        
        # TEST
        required_items = ["file_understanding", "test_written", "backup_created"]
        checklist_result["passed"] = all(checklist_items[item] for item in required_items)
        
        # SUCCESS
        self._save_checklist_status(checklist_result)
        
        if checklist_result["passed"]:
            logger.info("SUCCESS: SUCCESS", "CHECKLIST")
        else:
            logger.warning(f"WARNING: {len(checklist_result['blockers'])}WARNING", "CHECKLIST")
        
        return checklist_result
    
    def _check_file_understanding(self, target_files: List[str]) -> Dict[str, Any]:
        """ANALYSIS"""
        understood_files = []
        
        for file_path in target_files:
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    # 
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 
                    complexity = len([line for line in lines if 'def ' in line or 'class ' in line])
                    
                    understood_files.append({
                        "file": str(file_path),
                        "lines": len(lines),
                        "complexity": complexity,
                        "readable": complexity < 20  # ERROR
                    })
                    
                except Exception as e:
                    logger.error(f"ERROR ({file_path}): {e}", "CHECKLIST")
        
        understood = all(f["readable"] for f in understood_files)
        
        return {
            "understood": understood,
            "files_analyzed": understood_files,
            "complex_files": [f for f in understood_files if not f["readable"]]
        }
    
    def _analyze_impact_scope(self, target_files: List[str]) -> Dict[str, Any]:
        """ANALYSIS"""
        impact_areas = []
        high_risk = False
        
        for file_path in target_files:
            file_path = Path(file_path)
            
            # 
            if file_path.suffix in ['.vue', '.js', '.ts']:
                # 
                if 'store' in str(file_path) or 'router' in str(file_path):
                    high_risk = True
                    impact_areas.append(f": {file_path}")
            
            elif file_path.suffix == '.py':
                # PythonCONFIG
                if 'config' in str(file_path) or 'main' in str(file_path):
                    high_risk = True
                    impact_areas.append(f"ANALYSIS: {file_path}")
        
        return {
            "analyzed": True,
            "impact_areas": impact_areas,
            "high_risk": high_risk,
            "risk_level": "high" if high_risk else "medium" if impact_areas else "low"
        }
    
    def _check_similar_code(self, target_files: List[str]) -> Dict[str, Any]:
        """ANALYSIS"""
        # 
        similar_files = []
        
        for file_path in target_files:
            file_path = Path(file_path)
            
            # 
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
        """TEST"""
        test_status = {}
        tests_exist = True
        
        for file_path in target_files:
            file_path = Path(file_path)
            
            # TEST
            test_patterns = self._generate_test_patterns(file_path)
            found_tests = []
            
            for pattern in test_patterns:
                test_files = list(self.core.project_paths['root'].rglob(pattern))
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
        """TEST"""
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
        """SYSTEM"""
        backup_dir = self.core.project_paths['workspace'] / 'backups' / datetime.now().strftime("%Y%m%d_%H%M%S")
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
                    logger.error(f"ERROR ({file_path}): {e}", "CHECKLIST")
        
        return {
            "created": len(backed_up_files) > 0,
            "backup_dir": str(backup_dir),
            "backed_up_files": backed_up_files
        }
    
    def _check_dependencies(self, target_files: List[str]) -> Dict[str, Any]:
        """ANALYSIS"""
        dependencies = {}
        
        for file_path in target_files:
            file_path = Path(file_path)
            file_deps = []
            
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # importrequire
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
                    logger.error(f"ERROR ({file_path}): {e}", "CHECKLIST")
        
        return {
            "checked": True,
            "dependencies": dependencies,
            "external_deps": [dep for deps in dependencies.values() for dep in deps if not dep.startswith('.')]
        }
    
    def _save_checklist_status(self, checklist_result: Dict[str, Any]) -> None:
        """REPORT"""
        try:
            with open(self.checklist_file, 'w', encoding='utf-8') as f:
                json.dump(checklist_result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"ERROR: {e}", "CHECKLIST")

# ERROR
checklist_manager = ChecklistManager()