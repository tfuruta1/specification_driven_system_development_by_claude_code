#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動クリーンアップシステム
作業後に一時ファイルを自動削除し、ファイル構造を維持
"""

# Auto-generated import setup
import sys
from pathlib import Path
import time
import atexit
from datetime import datetime

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

try:
    from core.file_manager import FileManager
    from core.logger import get_logger
except ImportError:
    from file_manager import FileManager
    from logger import get_logger

logger = get_logger(__name__)


class AutoCleanup:
    """
    自動クリーンアップシステム
    作業終了時に自動的に実行される
    """
    
    _instance = None
    _registered = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初期化"""
        if not AutoCleanup._registered:
            self.file_manager = FileManager()
            self.start_time = datetime.now()
            self.cleaned_files = []
            
            # プロセス終了時に自動実行を登録
            atexit.register(self.cleanup_on_exit)
            AutoCleanup._registered = True
            
            logger.info("Auto cleanup system initialized")
    
    def cleanup_on_exit(self):
        """
        プロセス終了時の自動クリーンアップ
        """
        try:
            logger.info("Starting automatic cleanup...")
            
            # ファイル整理
            result = self.file_manager.organize_files()
            if result.success and result.data:
                moved_count = len(result.data.get("moved_files", []))
                if moved_count > 0:
                    logger.info(f"Organized {moved_count} misplaced files")
            
            # 一時ファイルクリーンアップ（1時間以上古いファイル）
            result = self.file_manager.cleanup_temp_files(max_age_hours=1)
            if result.success and result.data:
                deleted_count = len(result.data.get("deleted", []))
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} temp files")
            
            # 実行時間記録
            duration = datetime.now() - self.start_time
            logger.info(f"Session duration: {duration}")
            
            # クリーンアップレポート作成
            self._create_cleanup_report()
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def _create_cleanup_report(self):
        """
        クリーンアップレポートを作成
        """
        try:
            report_path = self.file_manager.temp_dir / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Auto Cleanup Report\n")
                f.write(f"===================\n\n")
                f.write(f"Session Start: {self.start_time}\n")
                f.write(f"Session End: {datetime.now()}\n")
                f.write(f"Duration: {datetime.now() - self.start_time}\n\n")
                
                if self.cleaned_files:
                    f.write(f"Cleaned Files:\n")
                    for file in self.cleaned_files:
                        f.write(f"  - {file}\n")
            
        except Exception as e:
            logger.error(f"Failed to create cleanup report: {e}")
    
    def manual_cleanup(self):
        """
        手動クリーンアップ実行
        """
        logger.info("Manual cleanup triggered")
        
        # ファイル整理
        result = self.file_manager.organize_files()
        print(f"File organization: {result.message}")
        
        # 一時ファイルクリーンアップ
        result = self.file_manager.cleanup_temp_files(max_age_hours=0)
        print(f"Temp file cleanup: {result.message}")
        
        # 構造チェック
        result = self.file_manager.enforce_structure()
        print(f"Structure check: {result.message}")
        
        return result


# グローバルインスタンス作成（インポート時に自動登録）
_auto_cleanup = AutoCleanup()


def cleanup_now():
    """
    即座にクリーンアップを実行
    """
    return _auto_cleanup.manual_cleanup()


def get_cleanup_instance():
    """
    クリーンアップインスタンスを取得
    """
    return _auto_cleanup


if __name__ == "__main__":
    print("Auto cleanup system is active")
    print("Running manual cleanup...")
    cleanup_now()
    print("Cleanup completed. System will auto-cleanup on exit.")