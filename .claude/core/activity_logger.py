#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - 統合活動ログシステム
基本ログ機能 + agent_monitor.py の監視機能を統合
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from jst_utils import (
    get_date_str,
    get_time_str, 
    get_session_time,
    get_log_timestamp,
    format_jst_header,
    get_jst_now,
    format_jst_time,
    format_jst_datetime
)


class LogLevel(Enum):
    """ログレベル"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class ActivityType(Enum):
    """アクティビティタイプ（エージェント監視用）"""
    PLANNING = "[PLAN] 計画中"
    ANALYZING = "[ANALYZE] 解析中"
    DESIGNING = "[DESIGN] 設計中"
    IMPLEMENTING = "[IMPL] 実装中"
    TESTING = "[TEST] テスト中"
    REVIEWING = "[REVIEW] レビュー中"
    DEPLOYING = "[DEPLOY] デプロイ中"
    DOCUMENTING = "[DOC] 文書作成中"
    COORDINATING = "[COORD] 調整中"
    WAITING = "[WAIT] 待機中"


class UnifiedLogger:
    """統合ログシステム"""
    
    def __init__(self):
        # 基本設定
        self.base_dir = Path(".claude/ActivityReport")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 基本ログ設定
        self.session_start = get_session_time()
        self.date_str = get_date_str()
        
        # 監視ログ設定
        self.log_dir = Path(".claude/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.activity_log = self.log_dir / "activity_stream.log"
        
        # 設定
        self.monitor_level = "normal"  # verbose, normal, quiet
        self.realtime = True
        self.max_log_size = 100 * 1024 * 1024  # 100MB
        
    # ========== 基本ログ機能 ==========
    
    def log(self, actor: str, action: str, reflection: str = None):
        """
        基本作業ログを記録
        既存ファイルがある場合は読み込んでから追記
        """
        time_str = get_time_str()
        log_file = self.base_dir / f"{self.date_str}_{self.session_start}_workingLog.md"
        
        # 既存ファイルの内容を読み込み
        existing_content = ""
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 新規作成または追記
        with open(log_file, 'w', encoding='utf-8') as f:
            if existing_content:
                f.write(existing_content)
            else:
                header = format_jst_header(self.date_str, self.session_start)
                f.write(header)
            
            # 新しいログを追記
            f.write(f"## [{time_str} JST] {actor}\n\n")
            f.write(f"**作業内容:** {action}\n\n")
            
            if reflection:
                f.write(f"**所感・改善提案:** {reflection}\n\n")
            
            f.write("---\n\n")
    
    def log_cto(self, action: str, reflection: str = None):
        """CTO用のログメソッド"""
        self.log("CTO", action, reflection)
    
    def log_alex(self, action: str, reflection: str = None):
        """アレックス用のログメソッド"""
        self.log("アレックス", action, reflection)
    
    # ========== 構造化ログ機能 ==========
    
    def debug(self, message: str, component: str = "SYSTEM"):
        """デバッグログ"""
        self._log_structured(LogLevel.DEBUG, message, component)
    
    def info(self, message: str, component: str = "SYSTEM"):
        """情報ログ"""
        self._log_structured(LogLevel.INFO, message, component)
    
    def warn(self, message: str, component: str = "SYSTEM"):
        """警告ログ"""
        self._log_structured(LogLevel.WARN, message, component)
    
    def error(self, message: str, component: str = "SYSTEM"):
        """エラーログ"""
        self._log_structured(LogLevel.ERROR, message, component)
    
    def _log_structured(self, level: LogLevel, message: str, component: str):
        """構造化ログの内部実装"""
        timestamp = format_jst_time()
        
        # コンソール出力
        if self.realtime and (level != LogLevel.DEBUG or self.monitor_level == "verbose"):
            print(f"[{timestamp}] [{level.value}] [{component}] {message}")
        
        # ファイル出力
        log_entry = {
            'timestamp': timestamp,
            'level': level.value,
            'component': component,
            'message': message,
            'type': 'structured_log'
        }
        
        self._write_activity_log(log_entry)
    
    # ========== エージェント監視機能 ==========
    
    def log_activity(self, agent_name: str, agent_emoji: str, 
                     activity_type: ActivityType, details: str = "", 
                     progress: Optional[int] = None):
        """エージェントの活動をログに記録"""
        timestamp = get_jst_now()
        timestamp_str = format_jst_datetime(timestamp)
        
        # ターミナル出力
        if self.realtime:
            if progress is not None:
                bar = self._progress_bar(progress)
                message = f"[{bar}] {progress}% | {agent_emoji} {agent_name} > {activity_type.value}"
                if details:
                    message += f" [{details}]"
            else:
                message = f"[{timestamp_str}] {agent_emoji} {agent_name} > {activity_type.value}"
                if details:
                    message += f" [{details}]"
            
            if self.monitor_level == "verbose" or (self.monitor_level == "normal" and activity_type != ActivityType.WAITING):
                print(message)
        
        # ログファイル記録
        log_entry = {
            'timestamp': timestamp_str,
            'type': 'activity',
            'agent': {
                'name': agent_name,
                'emoji': agent_emoji
            },
            'activity_type': activity_type.name,
            'details': details,
            'progress': progress
        }
        
        self._write_activity_log(log_entry)
        self._check_log_rotation()
    
    def log_communication(self, from_agent: Dict, to_agent: Dict, 
                         comm_type: str, content: str):
        """部門間通信を記録"""
        timestamp = get_jst_now()
        timestamp_str = format_jst_datetime(timestamp)
        
        # ターミナル出力
        if self.realtime and self.monitor_level != "quiet":
            message = (f"[{timestamp_str}] {from_agent['emoji']} {from_agent['name']} "
                      f"-> {to_agent['emoji']} {to_agent['name']} > {content}")
            print(message)
        
        # ログファイル記録
        log_entry = {
            'timestamp': timestamp_str,
            'type': 'communication',
            'from': from_agent,
            'to': to_agent,
            'comm_type': comm_type,
            'content': content
        }
        
        self._write_activity_log(log_entry)
    
    def _progress_bar(self, percent: int) -> str:
        """プログレスバーを生成"""
        filled = int(percent / 10)
        bar = "=" * filled
        if filled < 10:
            bar += ">"
            bar += " " * (10 - filled - 1)
        return bar
    
    def _write_activity_log(self, log_entry: Dict):
        """活動ログファイルに記録"""
        with open(self.activity_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _check_log_rotation(self):
        """ログローテーションを確認"""
        if self.activity_log.exists() and self.activity_log.stat().st_size > self.max_log_size:
            # 現在のログを日次アーカイブに移動
            archive_dir = self.log_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            archive_name = archive_dir / f"{get_log_timestamp()}.log"
            self.activity_log.rename(archive_name)
            self.info(f"ログファイルをアーカイブしました: {archive_name.name}")
    
    # ========== 設定・管理機能 ==========
    
    def set_monitor_level(self, level: str):
        """モニタリング詳細度を設定"""
        if level in ["verbose", "normal", "quiet"]:
            self.monitor_level = level
            self.info(f"モニタリングレベル: {level}")
        else:
            self.warn(f"無効なレベル: {level}")
    
    def set_realtime(self, enabled: bool):
        """リアルタイム表示の切り替え"""
        self.realtime = enabled
        status = "ON" if enabled else "OFF"
        self.info(f"リアルタイム表示: {status}")
    
    def clear_logs(self):
        """ログをクリア"""
        if self.activity_log.exists():
            self.activity_log.unlink()
        self.info("ログをクリアしました")
    
    def cleanup_old_logs(self):
        """古いログファイルを削除"""
        cutoff_date = get_jst_now() - timedelta(days=7)
        deleted_count = 0
        
        archive_dir = self.log_dir / "archive"
        if archive_dir.exists():
            for log_file in archive_dir.glob("*.log"):
                try:
                    file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                except:
                    pass
        
        if deleted_count > 0:
            self.info(f"古いログを{deleted_count}件削除しました")
    
    def show_summary(self):
        """活動サマリーを表示"""
        if not self.activity_log.exists():
            self.info("ログファイルが存在しません")
            return
        
        activities = {}
        communications = 0
        
        with open(self.activity_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry['type'] == 'activity':
                        agent = entry['agent']['name']
                        if agent not in activities:
                            activities[agent] = 0
                        activities[agent] += 1
                    elif entry['type'] == 'communication':
                        communications += 1
                except:
                    continue
        
        self.info("活動サマリー:")
        for agent, count in sorted(activities.items(), key=lambda x: x[1], reverse=True):
            self.info(f"  {agent}: {count} 件")
        self.info(f"  部門間通信: {communications} 件")


# シングルトンインスタンス
logger = UnifiedLogger()

# 使用例
if __name__ == "__main__":
    logger = ActivityLogger()
    
    # CTOのログ
    logger.log_cto(
        "Claude Code v10.3への移行作業を開始", 
        "階層型システムからシンプルなペアプロ体制への移行は正しい判断だった"
    )
    
    # アレックスのログ
    logger.log_alex(
        "不要ファイルのクリーンアップ実行",
        "83ファイルの整理により、プロジェクトが大幅にシンプルになった"
    )