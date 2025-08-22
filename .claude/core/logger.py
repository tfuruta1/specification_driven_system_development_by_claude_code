#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合ログシステム
DRY原則: すべてのログ処理を一元化
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# JSTサポート
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
try:
    from system.jst_config import get_jst_now, format_jst_time
except ImportError:
    # フォールバック
    from datetime import datetime, timezone, timedelta
    JST = timezone(timedelta(hours=9))
    
    def get_jst_now():
        return datetime.now(JST)
    
    def format_jst_time():
        return get_jst_now().strftime("%Y-%m-%d %H:%M:%S JST")


class UnifiedLogger:
    """統合ログシステム（agent_monitor + agent_activity_logger + daily_log_writer を統合）"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.log_dir = self.base_path / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 今日のログファイル
        today = get_jst_now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"{today}.log"
    
    def log(self, level: str, message: str, component: Optional[str] = None) -> None:
        """統一ログ出力"""
        timestamp = format_jst_time()
        component_str = f"[{component}] " if component else ""
        log_entry = f"{timestamp} [{level}] {component_str}{message}\n"
        
        # ファイルに追記
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # コンソールにも出力
        print(log_entry.strip())
    
    def info(self, message: str, component: Optional[str] = None) -> None:
        """情報ログ"""
        self.log("INFO", message, component)
    
    def warning(self, message: str, component: Optional[str] = None) -> None:
        """警告ログ"""
        self.log("WARN", message, component)
    
    def error(self, message: str, component: Optional[str] = None) -> None:
        """エラーログ"""
        self.log("ERROR", message, component)
    
    def debug(self, message: str, component: Optional[str] = None) -> None:
        """デバッグログ"""
        self.log("DEBUG", message, component)
    
    def critical(self, message: str, component: Optional[str] = None) -> None:
        """重大エラーログ"""
        self.log("CRITICAL", message, component)
    
    def get_today_logs(self) -> str:
        """今日のログを取得"""
        if self.log_file.exists():
            return self.log_file.read_text(encoding='utf-8')
        return "ログなし"


class IntegratedLogger(UnifiedLogger):
    """統合ログシステム（テスト用エイリアス）"""
    
    def __init__(self, name: str = "ClaudeCore"):
        super().__init__()
        self.name = name
        self.context_history = {}
    
    def configure(self, config: dict):
        """ログ設定の適用（テスト用）"""
        # 基本的な設定適用
        pass
    
    def set_file_output(self, file_path: str):
        """ログファイル出力の設定（テスト用）"""
        self.log_file = Path(file_path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_context_history(self, context: str):
        """コンテキスト履歴の取得（テスト用）"""
        return self.context_history.get(context, [])


class FileUtils:
    """ファイルユーティリティクラス（統合テスト用）"""
    
    def safe_read(self, file_path: str) -> Optional[str]:
        """安全なファイル読み込み"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"ファイル読み込みエラー ({file_path}): {e}", "FILE_UTILS")
            return None
    
    def safe_write(self, file_path: str, content: str) -> bool:
        """安全なファイル書き込み"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"ファイル書き込みエラー ({file_path}): {e}", "FILE_UTILS")
            return False


class PathUtils:
    """パスユーティリティクラス（統合テスト用）"""
    
    def find_project_root(self) -> Path:
        """プロジェクトルートの検出"""
        current = Path.cwd()
        while current.parent != current:
            if (current / ".claude").exists():
                return current
            current = current.parent
        return Path.cwd()  # フォールバック
    
    def to_relative(self, abs_path: Path) -> str:
        """絶対パスから相対パスへの変換"""
        try:
            project_root = self.find_project_root()
            rel_path = abs_path.relative_to(project_root)
            return str(rel_path)
        except ValueError:
            return str(abs_path)


# シングルトンインスタンス
logger = UnifiedLogger()