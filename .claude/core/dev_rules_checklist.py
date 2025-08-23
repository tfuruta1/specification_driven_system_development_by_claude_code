#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
チェックリスト管理システム - Checklist Manager
教訓1「推測より確認」の実装
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dev_rules_core import dev_rules_core, logger

class ChecklistManager:
    """修正前チェックリスト管理システム"""
    
    def __init__(self):
        """チェックリスト管理システムの初期化"""
        self.core = dev_rules_core
        self.checklist_file = self.core.checklist_file
        logger.info("チェックリスト管理システム初期化完了", "CHECKLIST")
    
    def execute_pre_modification_checklist(self, target_files: List[str], modification_desc: str) -> Dict[str, Any]:
        """
        修正前チェックリストの実行（教訓1）
        
        Args:
            target_files: 対象ファイルリスト
            modification_desc: 修正内容説明
            
        Returns:
            チェックリスト実行結果
        """
        if not self.core.rules_config.get('enforce_checklist', True):
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

# シングルトンインスタンス
checklist_manager = ChecklistManager()