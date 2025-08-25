#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
システムマネージャー - 全モジュールの統合管理
KISS原則に基づき、シンプルな単一エントリーポイントを提供
DRY原則に基づき、共通処理を一元化
YAGNI原則に基づき、必要な機能のみ実装
"""

# Auto-generated import setup
import sys
from pathlib import Path

# Setup import paths
current_file = Path(__file__).resolve()
claude_root = None
current = current_file.parent
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    if (current / '.claude').exists():
        claude_root = current / '.claude'
        break
    current = current.parent

if claude_root:
    sys.path.insert(0, str(claude_root / "system"))
    sys.path.insert(0, str(claude_root))

from typing import Dict, List, Optional, Any
import json

# 統合モジュールを使用（DRY原則）
try:
    from core.alex_team_unified import AlexTeamUnified
    from core.dev_rules_unified import DevRulesUnified
    from core.unified_cache import UnifiedCache
    from core.file_manager import FileManager
    from core.auto_cleanup import AutoCleanup
    from core.common_base import BaseManager, BaseResult, create_result
    from core.logger import get_logger
    from core.config import ConfigManager
    from core.path_utils import get_claude_root
except ImportError:
    # Direct import for standalone execution
    from alex_team_unified import AlexTeamUnified
    from dev_rules_unified import DevRulesUnified
    from unified_cache import UnifiedCache
    from file_manager import FileManager
    from auto_cleanup import AutoCleanup
    from common_base import BaseManager, BaseResult, create_result
    from logger import get_logger
    from config import ConfigManager
    from path_utils import get_claude_root

logger = get_logger(__name__)


class SystemManager(BaseManager):
    """
    システム全体の統合管理クラス
    全機能への単一エントリーポイント（KISS原則）
    """
    
    def __init__(self):
        """初期化"""
        super().__init__("SystemManager")
        self.alex_team = None
        self.dev_rules = None
        self.cache = None
        self.file_manager = None
        self.auto_cleanup = None
        self.config = ConfigManager()
        self.root_path = get_claude_root()
        
    def initialize(self) -> BaseResult:
        """システム全体の初期化"""
        try:
            logger.info("Initializing System Manager")
            
            # 各サブシステムの初期化
            self.alex_team = AlexTeamUnified()
            self.dev_rules = DevRulesUnified()
            self.cache = UnifiedCache()
            self.file_manager = FileManager()
            self.auto_cleanup = AutoCleanup()
            
            # 初期化実行
            results = []
            results.append(self.alex_team.initialize())
            results.append(self.dev_rules.initialize())
            results.append(self.cache.initialize())
            results.append(self.file_manager.initialize())
            
            # 全て成功したか確認
            if all(r.success for r in results):
                return create_result(True, "System Manager initialized successfully")
            else:
                failed = [r.message for r in results if not r.success]
                return create_result(False, f"Initialization failed: {', '.join(failed)}")
                
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return create_result(False, f"Initialization error: {e}")
    
    def cleanup(self) -> BaseResult:
        """システム全体のクリーンアップ"""
        try:
            results = []
            
            if self.alex_team:
                results.append(self.alex_team.cleanup())
            if self.dev_rules:
                results.append(self.dev_rules.cleanup())
            if self.cache:
                results.append(self.cache.cleanup())
            
            if all(r.success for r in results):
                return create_result(True, "System cleanup completed")
            else:
                return create_result(False, "Some cleanup operations failed")
                
        except Exception as e:
            return create_result(False, f"Cleanup error: {e}")
    
    def run_self_diagnosis(self) -> BaseResult:
        """
        システム自己診断実行（シンプル化）
        
        Returns:
            診断結果
        """
        try:
            logger.info("Running system self-diagnosis")
            
            # Alex Teamの診断機能を使用
            if self.alex_team:
                return self.alex_team.run_self_diagnosis()
            else:
                return create_result(False, "Alex Team not initialized")
                
        except Exception as e:
            return create_result(False, f"Diagnosis error: {e}")
    
    def check_code_quality(self, target_path: Optional[Path] = None) -> BaseResult:
        """
        コード品質チェック（シンプル化）
        
        Args:
            target_path: チェック対象パス（省略時はシステム全体）
            
        Returns:
            チェック結果
        """
        try:
            if not self.dev_rules:
                return create_result(False, "Dev Rules not initialized")
            
            # デフォルトパス
            if target_path is None:
                target_path = self.root_path / "system" / "core"
            
            # Pythonファイルをチェック
            violations_count = 0
            files_checked = 0
            
            for py_file in target_path.glob("**/*.py"):
                result = self.dev_rules.check_file(py_file)
                files_checked += 1
                if not result.success and result.data:
                    violations = result.data.get("violations", [])
                    violations_count += len(violations)
            
            summary = self.dev_rules.get_summary()
            
            return create_result(
                violations_count == 0,
                f"Checked {files_checked} files, found {violations_count} violations",
                summary
            )
            
        except Exception as e:
            return create_result(False, f"Quality check error: {e}")
    
    def run_tests(self, coverage_target: float = 100.0) -> BaseResult:
        """
        テスト実行（シンプル化）
        
        Args:
            coverage_target: カバレッジ目標
            
        Returns:
            テスト結果
        """
        try:
            if self.alex_team:
                return self.alex_team.run_tests(coverage_target)
            else:
                return create_result(False, "Alex Team not initialized")
                
        except Exception as e:
            return create_result(False, f"Test execution error: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        システムステータス取得（シンプル化）
        
        Returns:
            ステータス情報
        """
        status = {
            "initialized": all([
                self.alex_team is not None,
                self.dev_rules is not None,
                self.cache is not None
            ]),
            "components": {
                "alex_team": self.alex_team is not None,
                "dev_rules": self.dev_rules is not None,
                "cache": self.cache is not None,
            },
            "root_path": str(self.root_path),
        }
        
        # 各コンポーネントの詳細
        if self.alex_team:
            status["alex_team_summary"] = self.alex_team.get_task_summary()
        
        if self.dev_rules:
            status["dev_rules_summary"] = self.dev_rules.get_summary()
        
        if self.cache:
            status["cache_stats"] = self.cache.get_stats()
        
        return status
    
    def organize_files(self) -> BaseResult:
        """
        ファイル整理実行
        
        Returns:
            整理結果
        """
        try:
            if not self.file_manager:
                return create_result(False, "File Manager not initialized")
            
            return self.file_manager.organize_files()
            
        except Exception as e:
            return create_result(False, f"File organization error: {e}")
    
    def execute_command(self, command: str, **kwargs) -> BaseResult:
        """
        コマンド実行（シンプルなインターフェース）
        
        Args:
            command: 実行コマンド
            **kwargs: コマンドパラメータ
            
        Returns:
            実行結果
        """
        commands = {
            "diagnose": self.run_self_diagnosis,
            "check": lambda: self.check_code_quality(kwargs.get("path")),
            "test": lambda: self.run_tests(kwargs.get("coverage", 100.0)),
            "status": lambda: create_result(True, "Status retrieved", self.get_system_status()),
            "init": self.initialize,
            "cleanup": self.cleanup,
            "organize": self.organize_files,
        }
        
        if command in commands:
            return commands[command]()
        else:
            return create_result(False, f"Unknown command: {command}")


def main():
    """メインエントリーポイント"""
    manager = SystemManager()
    
    # システム初期化
    result = manager.initialize()
    print(f"System initialization: {result.message}")
    
    # ステータス確認
    status = manager.get_system_status()
    print(f"System status: {json.dumps(status, indent=2)}")
    
    # 診断実行
    result = manager.execute_command("diagnose")
    print(f"Diagnosis: {result.message}")
    
    # クリーンアップ
    result = manager.cleanup()
    print(f"Cleanup: {result.message}")


if __name__ == "__main__":
    main()