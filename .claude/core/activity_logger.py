#!/usr/bin/env python3
"""
Activity Logger for Claude Code v10.6
CTOとアレックスの作業記録を保存するシンプルなロガー

注意: Claude Codeでの実際の使用時は、
- 新規作成: Writeツールを使用
- 既存ファイルへの追記: Readツール → Editツールの順で使用
"""

import os
from pathlib import Path
from .jst_utils import (
    get_date_str,
    get_time_str, 
    get_session_time,
    get_log_timestamp,
    format_jst_header
)

class ActivityLogger:
    def __init__(self):
        self.base_dir = Path(".claude/ActivityReport")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # セッション開始時刻を記録（ファイル名に使用、JST）
        self.session_start = get_session_time()
        self.date_str = get_date_str()
        
    def log(self, actor: str, action: str, reflection: str = None):
        """
        作業ログを記録
        既存ファイルがある場合は読み込んでから追記
        
        Args:
            actor: 実行者（CTO/アレックス）
            action: 実行した作業
            reflection: 改善提案や感想（オプション）
        """
        # 日付と時刻を取得（JST）
        time_str = get_time_str()
        
        # ファイルパス（セッション開始時刻を含む）
        log_file = self.base_dir / f"{self.date_str}_{self.session_start}_workingLog.md"
        
        # 既存ファイルの内容を読み込み（存在する場合）
        existing_content = ""
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 新規作成または追記
        with open(log_file, 'w', encoding='utf-8') as f:
            if existing_content:
                # 既存内容を書き戻し
                f.write(existing_content)
            else:
                # 初回作成時はヘッダーを追加
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