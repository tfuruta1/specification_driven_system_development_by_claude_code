#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

DRY: 
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 相対パスユーティリティをインポート
try:
    from path_utils import paths, setup_import_path
    setup_import_path()
except ImportError:
    # path_utilsが見つからない場合は直接パスを設定
    sys.path.insert(0, str(Path(__file__).parent))
    from path_utils import paths, setup_import_path
    setup_import_path()
try:
    from system.jst_config import get_jst_now, format_jst_time
except ImportError:
    # ERROR
    from datetime import datetime, timezone, timedelta
    JST = timezone(timedelta(hours=9))
    
    def get_jst_now():
        return datetime.now(JST)
    
    def format_jst_time():
        return get_jst_now().strftime("%Y-%m-%d %H:%M:%S JST")


def get_logger(name: Optional[str] = None):
    """
    ロガーインスタンスを取得（互換性のため追加）
    
    Args:
        name: ロガー名
        
    Returns:
        UnifiedLoggerインスタンス
    """
    return UnifiedLogger(name)


class UnifiedLogger:
    """agent_monitor + agent_activity_logger + daily_log_writer """
    
    def __init__(self, name: Optional[str] = None):
        """Initialize UnifiedLogger with optional name for compatibility"""
        self.name = name or "default"
        self.base_path = paths.root
        self.log_dir = paths.logs
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 
        today = get_jst_now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"{today}.log"
    
    def log(self, level: str, message: str, component: Optional[str] = None) -> None:
        """"""
        timestamp = format_jst_time()
        component_str = f"[{component}] " if component else ""
        log_entry = f"{timestamp} [{level}] {component_str}{message}\n"
        
        # 
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 
        print(log_entry.strip())
    
    def info(self, message: str, component: Optional[str] = None) -> None:
        """WARNING"""
        self.log("INFO", message, component)
    
    def warning(self, message: str, component: Optional[str] = None) -> None:
        """ERROR"""
        self.log("WARN", message, component)
    
    def error(self, message: str, component: Optional[str] = None) -> None:
        """ERROR"""
        self.log("ERROR", message, component)
    
    def debug(self, message: str, component: Optional[str] = None) -> None:
        """"""
        self.log("DEBUG", message, component)
    
    def critical(self, message: str, component: Optional[str] = None) -> None:
        """"""
        self.log("CRITICAL", message, component)
    
    def warn(self, message: str, component: Optional[str] = None) -> None:
        """Alias for warning() for backward compatibility"""
        self.warning(message, component)
    
    def get_today_logs(self) -> str:
        """"""
        if self.log_file.exists():
            return self.log_file.read_text(encoding='utf-8')
        return ""


class IntegratedLogger(UnifiedLogger):
    """SYSTEM"""
    
    def __init__(self, name: str = "ClaudeCore"):
        super().__init__()
        self.name = name
        self.context_history = {}
    
    def configure(self, config: dict):
        """SUCCESS"""
        # SUCCESS
        pass
    
    def set_file_output(self, file_path: str):
        """SUCCESS"""
        self.log_file = Path(file_path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_context_history(self, context: str):
        """"""
        return self.context_history.get(context, [])


class FileUtils:
    """"""
    
    def safe_read(self, file_path: str) -> Optional[str]:
        """"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"ERROR ({file_path}): {e}", "FILE_UTILS")
            return None
    
    def safe_write(self, file_path: str, content: str) -> bool:
        """"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"ERROR ({file_path}): {e}", "FILE_UTILS")
            return False


class PathUtils:
    """"""
    
    def find_project_root(self) -> Path:
        """"""
        current = Path.cwd()
        while current.parent != current:
            if (current / ".claude").exists():
                return current
            current = current.parent
        return Path.cwd()  # 
    
    def to_relative(self, abs_path: Path) -> str:
        """"""
        try:
            project_root = self.find_project_root()
            rel_path = abs_path.relative_to(project_root)
            return str(rel_path)
        except ValueError:
            return str(abs_path)


# Global logger instance and aliases for compatibility
logger = UnifiedLogger()

# Create aliases for backward compatibility
Logger = UnifiedLogger
OptimizedLogger = IntegratedLogger

# Global utility instances
_file_utils = FileUtils()
_path_utils = PathUtils()

# Module-level convenience functions
def log(level: str, message: str, component: Optional[str] = None) -> None:
    """Log a message at specified level"""
    logger.log(level, message, component)

def info(message: str, component: Optional[str] = None) -> None:
    """Log info message"""
    logger.info(message, component)

def warning(message: str, component: Optional[str] = None) -> None:
    """Log warning message"""
    logger.warning(message, component)

def error(message: str, component: Optional[str] = None) -> None:
    """Log error message"""
    logger.error(message, component)

def debug(message: str, component: Optional[str] = None) -> None:
    """Log debug message"""
    logger.debug(message, component)

def critical(message: str, component: Optional[str] = None) -> None:
    """Log critical message"""
    logger.critical(message, component)

def warn(message: str, component: Optional[str] = None) -> None:
    """Log warning message (alias for warning)"""
    logger.warn(message, component)

def get_today_logs() -> str:
    """Get today's log content"""
    return logger.get_today_logs()

def configure(config: dict):
    """Configure logger with settings"""
    integrated_logger = IntegratedLogger()
    integrated_logger.configure(config)
    return integrated_logger

def set_file_output(file_path: str):
    """Set log file output path"""
    logger.log_file = Path(file_path)
    logger.log_file.parent.mkdir(parents=True, exist_ok=True)

def get_context_history(context: str):
    """Get context history from integrated logger"""
    integrated_logger = IntegratedLogger()
    return integrated_logger.get_context_history(context)

def safe_read(file_path: str) -> Optional[str]:
    """Safely read file content"""
    return _file_utils.safe_read(file_path)

def safe_write(file_path: str, content: str) -> bool:
    """Safely write file content"""
    return _file_utils.safe_write(file_path, content)

def find_project_root() -> Path:
    """Find project root directory"""
    return _path_utils.find_project_root()

def to_relative(abs_path: Path) -> str:
    """Convert absolute path to relative path"""
    return _path_utils.to_relative(abs_path)

# Export all classes, instance, and functions
__all__ = ['UnifiedLogger', 'IntegratedLogger', 'FileUtils', 'PathUtils', 'Logger', 'OptimizedLogger', 'logger',
           'log', 'info', 'warning', 'error', 'debug', 'critical', 'warn', 'get_today_logs', 'configure', 
           'set_file_output', 'get_context_history', 'safe_read', 'safe_write', 'find_project_root', 'to_relative']