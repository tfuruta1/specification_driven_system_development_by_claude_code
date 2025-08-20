#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡素化されたコマンドシステム
KISS原則: 10個の基本コマンドに集約
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json

from system import ClaudeCodeSystem
from logger import logger


class CommandExecutor:
    """統合コマンド実行システム"""
    
    def __init__(self):
        self.system = ClaudeCodeSystem()
        self.commands = {
            "init": self.cmd_init,
            "analyze": self.cmd_analyze,
            "plan": self.cmd_plan,
            "implement": self.cmd_implement,
            "test": self.cmd_test,
            "review": self.cmd_review,
            "deploy": self.cmd_deploy,
            "status": self.cmd_status,
            "clean": self.cmd_clean,
            "help": self.cmd_help
        }
        self.current_context = {}
    
    def execute(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """コマンド実行"""
        if command not in self.commands:
            logger.error(f"不明なコマンド: {command}")
            return {"error": f"Unknown command: {command}"}
        
        logger.info(f"コマンド実行: {command}", "COMMAND")
        try:
            result = self.commands[command](args or {})
            logger.info(f"コマンド完了: {command}", "COMMAND")
            return result
        except Exception as e:
            logger.error(f"コマンドエラー: {str(e)}", "COMMAND")
            return {"error": str(e)}
    
    # ========== 基本10コマンド ==========
    
    def cmd_init(self, args: Dict) -> Dict:
        """1. init - 新規プロジェクト初期化"""
        project_name = args.get("name", "new_project")
        requirements = args.get("requirements", "")
        
        logger.info(f"新規プロジェクト初期化: {project_name}", "INIT")
        
        # 新規開発フロー実行
        result = self.system.new_development_flow(project_name, requirements)
        self.current_context = {"project": project_name, "type": "new"}
        
        return result
    
    def cmd_analyze(self, args: Dict) -> Dict:
        """2. analyze - 既存システム解析"""
        target = args.get("target", ".")
        modification = args.get("modification", "")
        
        logger.info(f"既存システム解析: {target}", "ANALYZE")
        
        if modification:
            # 修正フロー実行
            result = self.system.existing_modification_flow(target, modification)
            self.current_context = {"project": target, "type": "existing"}
        else:
            # 単純な解析
            result = self.system._analyze_existing_system(target, "解析のみ")
        
        return result
    
    def cmd_plan(self, args: Dict) -> Dict:
        """3. plan - 設計・計画"""
        logger.info("設計フェーズ", "PLAN")
        
        if not self.current_context:
            return {"error": "プロジェクトが初期化されていません"}
        
        # 設計書作成
        requirements = args.get("requirements", {})
        design = self.system._create_design(requirements)
        
        return design
    
    def cmd_implement(self, args: Dict) -> Dict:
        """4. implement - 実装"""
        logger.info("実装フェーズ", "IMPLEMENT")
        
        if not self.current_context:
            return {"error": "プロジェクトが初期化されていません"}
        
        design = args.get("design", {})
        if self.current_context.get("type") == "existing":
            result = self.system._implement_modifications(design)
        else:
            result = self.system._implement(design)
        
        return result
    
    def cmd_test(self, args: Dict) -> Dict:
        """5. test - テスト実行"""
        logger.info("テスト実行", "TEST")
        
        tests = args.get("tests", {})
        result = self.system._run_tests(tests)
        
        return result
    
    def cmd_review(self, args: Dict) -> Dict:
        """6. review - レビュー"""
        logger.info("レビュー実施", "REVIEW")
        
        target = args.get("target", {})
        result = self.system._review_design(target)
        
        return result
    
    def cmd_deploy(self, args: Dict) -> Dict:
        """7. deploy - デプロイ"""
        logger.info("デプロイ準備", "DEPLOY")
        
        return {
            "status": "ready",
            "message": "デプロイの準備が完了しました",
            "checklist": [
                "テスト完了",
                "レビュー完了",
                "ドキュメント更新"
            ]
        }
    
    def cmd_status(self, args: Dict) -> Dict:
        """8. status - 状態確認"""
        logger.info("ステータス確認", "STATUS")
        
        return {
            "current_project": self.current_context.get("project", "なし"),
            "project_type": self.current_context.get("type", "未定"),
            "workspace": str(self.system.workspace),
            "docs": str(self.system.docs),
            "cache": str(self.system.cache)
        }
    
    def cmd_clean(self, args: Dict) -> Dict:
        """9. clean - クリーンアップ"""
        logger.info("クリーンアップ実行", "CLEAN")
        
        result = self.system.cleanup()
        return result
    
    def cmd_help(self, args: Dict) -> Dict:
        """10. help - ヘルプ"""
        return {
            "commands": {
                "init": "新規プロジェクト初期化",
                "analyze": "既存システム解析",
                "plan": "設計・計画",
                "implement": "実装",
                "test": "テスト実行",
                "review": "レビュー",
                "deploy": "デプロイ",
                "status": "状態確認",
                "clean": "クリーンアップ",
                "help": "ヘルプ表示"
            },
            "flows": {
                "new": "init → plan → review → test → implement → test → deploy",
                "existing": "analyze → plan → review → test → implement → test → deploy"
            }
        }


def main():
    """テスト用メイン"""
    executor = CommandExecutor()
    
    # ヘルプ表示
    result = executor.execute("help")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()