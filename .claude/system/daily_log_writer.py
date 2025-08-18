#!/usr/bin/env python3
"""
階層型エージェントシステム - 作業日誌記録システム
エージェントの活動を日誌に記録します
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import json
from jst_config import format_jst_time, format_jst_datetime

class DailyLogWriter:
    """作業日誌への書き込みを管理するクラス"""
    
    def __init__(self):
        # 基本パス設定
        self.base_dir = Path(__file__).parent.parent
        self.log_dir = self.base_dir / ".ActivityReport" / "daily_log"
        self.private_dir = self.log_dir / ".private"
        
        # ディレクトリ作成
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.private_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"{today}_workingLog.md"
        self.private_file = self.private_dir / f"{today}_private.md"
        
    def initialize_log(self):
        """日誌ファイルの初期化"""
        if not self.log_file.exists():
            template = f"""# 📅 階層型エージェントシステム 作業日誌
**日付**: {datetime.now().strftime("%Y-%m-%d")}  
**プロジェクト**: ClaudeCode階層型エージェントシステム  
**フェーズ**: 📊 プロジェクト解析 / 💻 実装  
**監視モード**: 🔴 ACTIVE（全作業記録中）
**タイムゾーン**: JST（日本標準時）

---

"""
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(template)
                
    def write_activity(self, department, activity_type, details, is_private=False):
        """活動を記録する
        
        Args:
            department: 部門名（CTO、人事部、etc）
            activity_type: 活動タイプ（チーム編成、プロジェクト解析、etc）
            details: 詳細内容
            is_private: プライベート記録かどうか
        """
        self.initialize_log()
        
        # タイムスタンプ
        timestamp = format_jst_time()
        
        # エントリ作成
        entry = f"""
#### {timestamp} - {department}
**{activity_type}**: {details}
"""
        
        # ファイルに書き込み
        target_file = self.private_file if is_private else self.log_file
        
        try:
            with open(target_file, 'a', encoding='utf-8') as f:
                f.write(entry)
                f.flush()  # 即座に書き込み
        except Exception as e:
            print(f"日誌書き込みエラー: {e}")
            
    def write_task_progress(self, task_id, task_name, status, assignee=None):
        """タスク進捗を記録"""
        department = assignee if assignee else "システム"
        details = f"[{task_id}] {task_name} - ステータス: {status}"
        self.write_activity(department, "タスク進捗", details)
        
    def write_command_execution(self, command, executor="CTO"):
        """コマンド実行を記録"""
        self.write_activity(executor, "コマンド実行", command)
        
    def write_team_activity(self, member_name, activity):
        """チームメンバーの活動を記録"""
        self.write_activity(member_name, "開発作業", activity)
        
    def write_review_activity(self, reviewer, target, result):
        """レビュー活動を記録"""
        details = f"{target}のレビュー - 結果: {result}"
        self.write_activity(f"品質保証部/{reviewer}", "コードレビュー", details)
        
    def write_daily_summary(self):
        """日次サマリーを作成"""
        summary = f"""
---

### 📊 本日のサマリー
**記録時刻**: {format_jst_datetime()}

#### 活動統計
- 記録されたエントリ数: [集計中]
- アクティブ部門: CTO、人事部、品質保証部、システム開発部
- 主要成果: プロジェクト解析、チーム編成、実装、テスト

#### 明日への申し送り
- 継続タスク: [自動集計]
- 要対応事項: [自動検出]

---
*自動生成: 階層型エージェントシステム v8.7*
"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(summary)

def demo():
    """デモンストレーション"""
    writer = DailyLogWriter()
    
    print("[LOG] 作業日誌システム デモ")
    print("=" * 40)
    
    # サンプル記録
    writer.write_activity("CTO", "プロジェクト開始", "Hello World Python System開発開始")
    writer.write_activity("人事部", "チーム編成", "Python開発チーム7名配属完了")
    writer.write_team_activity("伊藤浩", "venv環境構築")
    writer.write_team_activity("田中太郎", "main.py実装")
    writer.write_review_activity("佐藤優子", "main.py", "合格")
    writer.write_activity("人事部", "", "また架空メンバー作った...", is_private=True)
    
    print(f"[OK] ログファイル作成: {writer.log_file}")
    print(f"[OK] プライベートログ: {writer.private_file}")
    
    # ファイル内容表示
    print("\n[LOG] 作業日誌内容:")
    print("-" * 40)
    with open(writer.log_file, 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == "__main__":
    demo()