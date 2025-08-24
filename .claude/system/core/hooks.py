#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - SYSTEM
system/hooks_manager.py SYSTEMcoreSYSTEM
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
from logger import logger


class HookType(Enum):
    """"""
    PRE_COMMAND = "pre_command"      # ANALYSIS
    POST_COMMAND = "post_command"     # ANALYSIS
    PRE_ANALYSIS = "pre_analysis"     # ANALYSIS
    POST_ANALYSIS = "post_analysis"   # ANALYSIS
    PRE_BUILD = "pre_build"          # TEST
    POST_BUILD = "post_build"        # TEST
    PRE_TEST = "pre_test"            # ERROR
    POST_TEST = "post_test"          # ERROR
    ERROR = "error"                  # ERROR
    DAILY = "daily"                  # ERROR


class Hook:
    """"""
    
    def __init__(self, name: str, hook_type: HookType, handler: Callable):
        self.name = name
        self.hook_type = hook_type
        self.handler = handler
        self.enabled = True
        self.execution_count = 0
        self.last_executed = None
        
    def execute(self, context: Dict) -> bool:
        """"""
        if not self.enabled:
            return True
        
        try:
            self.handler(context)
            self.execution_count += 1
            self.last_executed = get_jst_now()
            return True
        except Exception as e:
            logger.error(f"ERROR [{self.name}]: {e}", "HOOKS")
            return False


class HooksManager:
    """ERROR"""
    
    def __init__(self):
        self.hooks_dir = Path(".claude/hooks")
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.hooks_dir / "hooks_config.json"
        self.log_file = self.hooks_dir / "hooks_log.json"
        self.hooks: Dict[HookType, List[Hook]] = {hook_type: [] for hook_type in HookType}
        
        # 
        self._register_builtin_hooks()
        
        # 
        self._load_custom_hooks()
        
    def _register_builtin_hooks(self):
        """"""
        
        # 
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
        
        # ANALYSIS
        self.register_hook(
            "check_cache",
            HookType.PRE_ANALYSIS,
            self._check_analysis_cache
        )
        
        # ANALYSIS
        self.register_hook(
            "save_cache",
            HookType.POST_ANALYSIS,
            self._save_analysis_cache
        )
        
        # ANALYSIS
        self.register_hook(
            "backup_before_build",
            HookType.PRE_BUILD,
            self._create_backup
        )
        
        # TEST
        self.register_hook(
            "check_coverage",
            HookType.POST_TEST,
            self._check_test_coverage
        )
        
        # ERROR
        self.register_hook(
            "error_backup",
            HookType.ERROR,
            self._error_recovery
        )
        
        # ERROR
        self.register_hook(
            "daily_cleanup",
            HookType.DAILY,
            self._daily_cleanup
        )
        
        # SYSTEM
        try:
            from trigger_keyword_detector import TriggerSystemManager
            trigger_manager = TriggerSystemManager()
            self.register_hook(
                "trigger_keyword_detector",
                HookType.PRE_COMMAND,
                self._trigger_keyword_hook
            )
            self._trigger_manager = trigger_manager
            logger.info("ERROR", "HOOKS")
        except ImportError as e:
            logger.warn(f"ERROR: {e}", "HOOKS")
    
    def _log_command_start(self, context: Dict):
        """WARNING"""
        command = context.get('command', 'unknown')
        logger.info(f": /{command}", "HOOKS")
    
    def _log_command_end(self, context: Dict):
        """SUCCESS"""
        command = context.get('command', 'unknown')
        success = context.get('success', False)
        execution_time = context.get('execution_time', 0)
        
        status = "SUCCESS" if success else "SUCCESS"
        logger.info(f"SUCCESS: /{command} - {status} ({execution_time:.1f}SUCCESS)", "HOOKS")
    
    def _check_analysis_cache(self, context: Dict):
        """SYSTEM"""
        try:
            from cache import cache_system
            cached_result = cache_system.load_cache("project_analysis")
            
            if cached_result:
                context['cached_result'] = cached_result
                logger.info("REPORT - REPORT", "HOOKS")
            else:
                logger.info("ERROR - ERROR", "HOOKS")
        except ImportError:
            logger.warn("ERROR", "HOOKS")
    
    def _save_analysis_cache(self, context: Dict):
        """WARNING"""
        result = context.get('analysis_result')
        execution_time = context.get('execution_time', 0)
        
        if result:
            try:
                from cache import cache_system
                cache_system.save_cache("project_analysis", result, execution_time)
                logger.info("ERROR", "HOOKS")
            except ImportError:
                logger.warn("ERROR", "HOOKS")
    
    def _create_backup(self, context: Dict):
        """WARNING"""
        try:
            from cleanup import cleaner
            # ERROR
            logger.info("ERROR", "HOOKS")
        except ImportError:
            logger.warn("ERROR", "HOOKS")
    
    def _check_test_coverage(self, context: Dict):
        """WARNING"""
        coverage = context.get('coverage', 0)
        threshold = context.get('threshold', 80)
        
        if coverage < threshold:
            logger.warn(f"WARNING ({coverage}% < {threshold}%)", "HOOKS")
        else:
            logger.info(f"ERROR ({coverage}%)", "HOOKS")
    
    def _error_recovery(self, context: Dict):
        """ERROR"""
        error = context.get('error', 'Unknown error')
        logger.error(f"ERROR: {error}", "HOOKS")
        
        # ERROR
        backup_dir = Path(".claude/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = format_jst_datetime().replace(" ", "_").replace(":", "-")
        error_log = backup_dir / f"error_{timestamp}.log"
        error_log.write_text(f"Error: {error}\nTime: {format_jst_datetime()}\n", encoding='utf-8')
        
        logger.info(f"ERROR: {error_log.name}", "HOOKS")
    
    def _daily_cleanup(self, context: Dict):
        """ERROR"""
        try:
            from cleanup import cleaner
            result = cleaner.cleanup_workspace()
            logger.info(f"ERROR: {len(result.get('deleted', []))}ERROR", "HOOKS")
        except ImportError:
            logger.warn("ERROR", "HOOKS")
    
    def _trigger_keyword_hook(self, context: Dict):
        """WARNING"""
        user_message = context.get('user_message')
        if user_message and hasattr(self, '_trigger_manager'):
            try:
                result = self._trigger_manager.process_user_message(user_message)
                if result and result.success:
                    context['auto_pair_programming_activated'] = True
                    context['activation_result'] = result
                    logger.info("ERROR", "HOOKS")
            except Exception as e:
                logger.error(f"ERROR: {e}", "HOOKS")
    
    def _load_custom_hooks(self):
        """ERROR"""
        custom_hooks_file = self.hooks_dir / "custom_hooks.py"
        
        if custom_hooks_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("custom_hooks", custom_hooks_file)
                custom_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(custom_module)
                
                if hasattr(custom_module, 'register_hooks'):
                    custom_module.register_hooks(self)
                    logger.info("ERROR", "HOOKS")
            except Exception as e:
                logger.error(f"ERROR: {e}", "HOOKS")
    
    def register_hook(self, name: str, hook_type: HookType, handler: Callable):
        """"""
        hook = Hook(name, hook_type, handler)
        self.hooks[hook_type].append(hook)
        logger.debug(f": {name} ({hook_type.value})", "HOOKS")
    
    def execute_hooks(self, hook_type: HookType, context: Dict) -> bool:
        """"""
        hooks = self.hooks.get(hook_type, [])
        
        if not hooks:
            return True
        
        logger.debug(f"SUCCESS: {hook_type.value}", "HOOKS")
        
        all_success = True
        for hook in hooks:
            if hook.enabled:
                success = hook.execute(context)
                if not success:
                    all_success = False
        
        return all_success
    
    def create_command_context(self, command: str, args: List[str] = None) -> Dict:
        """"""
        return {
            'command': command,
            'args': args or [],
            'timestamp': format_jst_datetime(),
            'user': os.environ.get('USER', 'unknown'),
            'cwd': os.getcwd()
        }
    
    def execute_with_hooks(self, command: str, args: List[str] = None) -> bool:
        """"""
        context = self.create_command_context(command, args)
        
        # 
        self.execute_hooks(HookType.PRE_COMMAND, context)
        
        # SUCCESS
        start_time = time.time()
        success = True
        
        try:
            # SUCCESScorecommands.pySUCCESS
            from commands import CommandExecutor
            executor = CommandExecutor()
            success = executor.execute(command, args)
            
        except Exception as e:
            success = False
            context['error'] = str(e)
            self.execute_hooks(HookType.ERROR, context)
        
        # ERROR
        execution_time = time.time() - start_time
        context['execution_time'] = execution_time
        context['success'] = success
        
        # SUCCESS
        self.execute_hooks(HookType.POST_COMMAND, context)
        
        return success
    
    def get_hook_stats(self) -> Dict:
        """SUCCESS"""
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
        """CONFIG"""
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
        """CONFIG"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # CONFIG/CONFIG
            for hook_type_str, hook_configs in config.get('hooks', {}).items():
                hook_type = HookType(hook_type_str)
                hooks = self.hooks.get(hook_type, [])
                
                for hook_config in hook_configs:
                    for hook in hooks:
                        if hook.name == hook_config['name']:
                            hook.enabled = hook_config['enabled']
        except Exception as e:
            logger.error(f"ERROR: {e}", "HOOKS")


# ERROR
hooks_manager = HooksManager()
