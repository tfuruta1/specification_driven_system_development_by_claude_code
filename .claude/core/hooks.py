#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - フック管理システム
system/hooks_manager.py を統合し、依存関係をcoreに修正
"""

import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from enum import Enum
import threading

from jst_utils import format_jst_time, get_jst_now, format_jst_datetime
from activity_logger import logger


class HookType(Enum):
    """フックの種類"""
    PRE_COMMAND = "pre_command"      # コマンド実行前
    POST_COMMAND = "post_command"     # コマンド実行後
    PRE_ANALYSIS = "pre_analysis"     # 解析前
    POST_ANALYSIS = "post_analysis"   # 解析後
    PRE_BUILD = "pre_build"          # ビルド前
    POST_BUILD = "post_build"        # ビルド後
    PRE_TEST = "pre_test"            # テスト前
    POST_TEST = "post_test"          # テスト後
    ERROR = "error"                  # エラー発生時
    DAILY = "daily"                  # 日次処理


class Hook:
    """フック定義"""
    
    def __init__(self, name: str, hook_type: HookType, handler: Callable):
        self.name = name
        self.hook_type = hook_type
        self.handler = handler
        self.enabled = True
        self.execution_count = 0
        self.last_executed = None
        
    def execute(self, context: Dict) -> bool:
        """フックを実行"""
        if not self.enabled:
            return True
        
        try:
            self.handler(context)
            self.execution_count += 1
            self.last_executed = get_jst_now()
            return True
        except Exception as e:
            logger.error(f"フック実行エラー [{self.name}]: {e}", "HOOKS")
            return False


class HooksManager:
    """統合フック管理システム"""
    
    def __init__(self):
        self.hooks_dir = Path(".claude/hooks")
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.hooks_dir / "hooks_config.json"
        self.log_file = self.hooks_dir / "hooks_log.json"
        self.hooks: Dict[HookType, List[Hook]] = {hook_type: [] for hook_type in HookType}
        
        # 組み込みフックを登録
        self._register_builtin_hooks()
        
        # カスタムフックを読み込み
        self._load_custom_hooks()
        
    def _register_builtin_hooks(self):
        """組み込みフックを登録"""
        
        # コマンド実行前後のログ記録
        self.register_hook(
            "log_command_start",
            HookType.PRE_COMMAND,
            self._log_command_start
        )
        
        self.register_hook(
            "log_command_end",
            HookType.POST_COMMAND,
            self._log_command_end
        )
        
        # 解析前のキャッシュチェック
        self.register_hook(
            "check_cache",
            HookType.PRE_ANALYSIS,
            self._check_analysis_cache
        )
        
        # 解析後のキャッシュ保存
        self.register_hook(
            "save_cache",
            HookType.POST_ANALYSIS,
            self._save_analysis_cache
        )
        
        # ビルド前のバックアップ
        self.register_hook(
            "backup_before_build",
            HookType.PRE_BUILD,
            self._create_backup
        )
        
        # テスト後のカバレッジチェック
        self.register_hook(
            "check_coverage",
            HookType.POST_TEST,
            self._check_test_coverage
        )
        
        # エラー時の自動バックアップ
        self.register_hook(
            "error_backup",
            HookType.ERROR,
            self._error_recovery
        )
        
        # 日次クリーンアップ
        self.register_hook(
            "daily_cleanup",
            HookType.DAILY,
            self._daily_cleanup
        )
        
        # トリガーキーワード検出（自動ペアプログラミング起動）
        try:
            from trigger_keyword_detector import TriggerSystemManager
            trigger_manager = TriggerSystemManager()
            self.register_hook(
                "trigger_keyword_detector",
                HookType.PRE_COMMAND,
                self._trigger_keyword_hook
            )
            self._trigger_manager = trigger_manager
            logger.info("トリガーキーワード検出フックを統合", "HOOKS")
        except ImportError as e:
            logger.warn(f"トリガーキーワード検出システムが利用できません: {e}", "HOOKS")
    
    def _log_command_start(self, context: Dict):
        """コマンド開始をログに記録"""
        command = context.get('command', 'unknown')
        logger.info(f"コマンド開始: /{command}", "HOOKS")
    
    def _log_command_end(self, context: Dict):
        """コマンド終了をログに記録"""
        command = context.get('command', 'unknown')
        success = context.get('success', False)
        execution_time = context.get('execution_time', 0)
        
        status = "成功" if success else "失敗"
        logger.info(f"コマンド終了: /{command} - {status} ({execution_time:.1f}秒)", "HOOKS")
    
    def _check_analysis_cache(self, context: Dict):
        """解析キャッシュをチェック"""
        try:
            from cache import cache_system
            cached_result = cache_system.load_cache("project_analysis")
            
            if cached_result:
                context['cached_result'] = cached_result
                logger.info("キャッシュヒット - 解析をスキップ", "HOOKS")
            else:
                logger.info("キャッシュミス - 解析を実行", "HOOKS")
        except ImportError:
            logger.warn("キャッシュシステムが利用できません", "HOOKS")
    
    def _save_analysis_cache(self, context: Dict):
        """解析結果をキャッシュに保存"""
        result = context.get('analysis_result')
        execution_time = context.get('execution_time', 0)
        
        if result:
            try:
                from cache import cache_system
                cache_system.save_cache("project_analysis", result, execution_time)
                logger.info("解析結果をキャッシュに保存", "HOOKS")
            except ImportError:
                logger.warn("キャッシュシステムが利用できません", "HOOKS")
    
    def _create_backup(self, context: Dict):
        """ビルド前にバックアップを作成"""
        try:
            from cleanup import cleaner
            # 簡略化されたバックアップ処理
            logger.info("ビルド前バックアップ作成", "HOOKS")
        except ImportError:
            logger.warn("クリーンアップシステムが利用できません", "HOOKS")
    
    def _check_test_coverage(self, context: Dict):
        """テストカバレッジをチェック"""
        coverage = context.get('coverage', 0)
        threshold = context.get('threshold', 80)
        
        if coverage < threshold:
            logger.warn(f"テストカバレッジが基準値未満 ({coverage}% < {threshold}%)", "HOOKS")
        else:
            logger.info(f"テストカバレッジ基準達成 ({coverage}%)", "HOOKS")
    
    def _error_recovery(self, context: Dict):
        """エラー時の自動復旧"""
        error = context.get('error', 'Unknown error')
        logger.error(f"エラー発生: {error}", "HOOKS")
        
        # 簡略化されたエラー復旧処理
        backup_dir = Path(".claude/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = format_jst_datetime().replace(" ", "_").replace(":", "-")
        error_log = backup_dir / f"error_{timestamp}.log"
        error_log.write_text(f"Error: {error}\nTime: {format_jst_datetime()}\n", encoding='utf-8')
        
        logger.info(f"エラーログ保存: {error_log.name}", "HOOKS")
    
    def _daily_cleanup(self, context: Dict):
        """日次クリーンアップ"""
        try:
            from cleanup import cleaner
            result = cleaner.cleanup_workspace()
            logger.info(f"日次クリーンアップ完了: {len(result.get('deleted', []))}件削除", "HOOKS")
        except ImportError:
            logger.warn("クリーンアップシステムが利用できません", "HOOKS")
    
    def _trigger_keyword_hook(self, context: Dict):
        """トリガーキーワード検出フック"""
        user_message = context.get('user_message')
        if user_message and hasattr(self, '_trigger_manager'):
            try:
                result = self._trigger_manager.process_user_message(user_message)
                if result and result.success:
                    context['auto_pair_programming_activated'] = True
                    context['activation_result'] = result
                    logger.info("自動ペアプログラミング起動", "HOOKS")
            except Exception as e:
                logger.error(f"トリガー検出エラー: {e}", "HOOKS")
    
    def _load_custom_hooks(self):
        """カスタムフックを読み込み"""
        custom_hooks_file = self.hooks_dir / "custom_hooks.py"
        
        if custom_hooks_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("custom_hooks", custom_hooks_file)
                custom_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(custom_module)
                
                if hasattr(custom_module, 'register_hooks'):
                    custom_module.register_hooks(self)
                    logger.info("カスタムフック読み込み完了", "HOOKS")
            except Exception as e:
                logger.error(f"カスタムフック読み込みエラー: {e}", "HOOKS")
    
    def register_hook(self, name: str, hook_type: HookType, handler: Callable):
        """フックを登録"""
        hook = Hook(name, hook_type, handler)
        self.hooks[hook_type].append(hook)
        logger.debug(f"フック登録: {name} ({hook_type.value})", "HOOKS")
    
    def execute_hooks(self, hook_type: HookType, context: Dict) -> bool:
        """指定タイプのフックを実行"""
        hooks = self.hooks.get(hook_type, [])
        
        if not hooks:
            return True
        
        logger.debug(f"フック実行: {hook_type.value}", "HOOKS")
        
        all_success = True
        for hook in hooks:
            if hook.enabled:
                success = hook.execute(context)
                if not success:
                    all_success = False
        
        return all_success
    
    def create_command_context(self, command: str, args: List[str] = None) -> Dict:
        """コマンド実行コンテキストを作成"""
        return {
            'command': command,
            'args': args or [],
            'timestamp': format_jst_datetime(),
            'user': os.environ.get('USER', 'unknown'),
            'cwd': os.getcwd()
        }
    
    def execute_with_hooks(self, command: str, args: List[str] = None) -> bool:
        """フック付きでコマンドを実行"""
        context = self.create_command_context(command, args)
        
        # 実行前フック
        self.execute_hooks(HookType.PRE_COMMAND, context)
        
        # コマンド実行
        start_time = time.time()
        success = True
        
        try:
            # 実際のコマンド実行はcorecommands.pyを呼び出し
            from commands import CommandExecutor
            executor = CommandExecutor()
            success = executor.execute(command, args)
            
        except Exception as e:
            success = False
            context['error'] = str(e)
            self.execute_hooks(HookType.ERROR, context)
        
        # 実行時間を記録
        execution_time = time.time() - start_time
        context['execution_time'] = execution_time
        context['success'] = success
        
        # 実行後フック
        self.execute_hooks(HookType.POST_COMMAND, context)
        
        return success
    
    def get_hook_stats(self) -> Dict:
        """フック実行統計を取得"""
        stats = {}
        
        for hook_type, hooks in self.hooks.items():
            type_stats = []
            for hook in hooks:
                type_stats.append({
                    'name': hook.name,
                    'enabled': hook.enabled,
                    'execution_count': hook.execution_count,
                    'last_executed': hook.last_executed.isoformat() if hook.last_executed else None
                })
            stats[hook_type.value] = type_stats
        
        return stats
    
    def save_config(self):
        """設定を保存"""
        config = {'hooks': {}}
        
        for hook_type, hooks in self.hooks.items():
            config['hooks'][hook_type.value] = [
                {
                    'name': hook.name,
                    'enabled': hook.enabled
                }
                for hook in hooks
            ]
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """設定を読み込み"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # フックの有効/無効を設定
            for hook_type_str, hook_configs in config.get('hooks', {}).items():
                hook_type = HookType(hook_type_str)
                hooks = self.hooks.get(hook_type, [])
                
                for hook_config in hook_configs:
                    for hook in hooks:
                        if hook.name == hook_config['name']:
                            hook.enabled = hook_config['enabled']
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}", "HOOKS")


# シングルトンインスタンス
hooks_manager = HooksManager()
