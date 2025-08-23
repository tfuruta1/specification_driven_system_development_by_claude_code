"""
Claude Code SDD+TDD Core Module
統合されたコアシステムのパッケージ初期化
"""

# 統合システム
from .unified_system import UnifiedSystem

# Auto Mode関連
from .auto_mode_config import AutoModeConfig
from .auto_mode_state import AutoModeStateManager
from .auto_mode_core import AutoModeManager
from .auto_mode import AutoMode

# Development Rules関連
from .dev_rules_core import DevelopmentRulesEngine
from .dev_rules_checklist import ChecklistManager
from .dev_rules_tdd import TDDWorkflowManager
from .dev_rules_tasks import TaskManager
from .dev_rules_integration import IntegrationWorkflowManager
from .development_rules import DevelopmentRules

# その他のコアモジュール
from .logger import Logger
from .jst_utils import JSTManager
from .trigger_keyword_detector import TriggerKeywordDetector
from .emoji_validator import EmojiValidator
from .cleanup import CleanupManager
from .cache import CacheManager
from .config import ConfigManager
from .commands import CommandManager
from .hooks import HookManager
from .activity_logger import ActivityLogger
from .file_access_logger import FileAccessLogger
from .pair_programmer import PairProgrammer

__all__ = [
    # 統合システム
    'UnifiedSystem',
    
    # Auto Mode
    'AutoMode',
    'AutoModeManager',
    'AutoModeConfig',
    'AutoModeStateManager',
    
    # Development Rules
    'DevelopmentRules',
    'DevelopmentRulesEngine',
    'ChecklistManager',
    'TDDWorkflowManager',
    'TaskManager',
    'IntegrationWorkflowManager',
    
    # ユーティリティ
    'Logger',
    'JSTManager',
    'TriggerKeywordDetector',
    'EmojiValidator',
    'CleanupManager',
    'CacheManager',
    'ConfigManager',
    'CommandManager',
    'HookManager',
    'ActivityLogger',
    'FileAccessLogger',
    'PairProgrammer',
]

# バージョン情報
__version__ = '12.0.0'
__author__ = 'Alex Team'