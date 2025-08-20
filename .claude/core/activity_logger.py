#!/usr/bin/env python3
"""
Activity Logger for Claude Code v10.3
CTOとアレックスの作業記録を保存するシンプルなロガー
"""

import os
from datetime import datetime
from pathlib import Path

class ActivityLogger:
    def __init__(self):
        self.base_dir = Path(".claude/ActivityReport")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, actor: str, action: str, reflection: str = None):
        """
        作業ログを記録
        
        Args:
            actor: 実行者（CTO/アレックス）
            action: 実行した作業
            reflection: 改善提案や感想（オプション）
        """
        # 日付を取得
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # ファイルパス
        log_file = self.base_dir / f"{date_str}_workingLog.md"
        
        # 初回作成時はヘッダーを追加
        if not log_file.exists():
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# 作業ログ - {date_str}\n\n")
                f.write("CTOとアレックスのペアプログラミング記録\n\n")
                f.write("---\n\n")
        
        # ログ内容を追記
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"## [{time_str}] {actor}\n\n")
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