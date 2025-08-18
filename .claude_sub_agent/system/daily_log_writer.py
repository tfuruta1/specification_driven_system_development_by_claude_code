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
import locale
import time

# 日本のロケール設定を試みる
try:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Japanese_Japan.932')
    except:
        pass  # ロケール設定失敗しても続行

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
            self.log_file.write_text(template, encoding='utf-8')
    
    def write_activity(self, agent, activity_type, content, is_private=False):
        """
        活動を日誌に記録
        
        Args:
            agent: エージェント名（CTO、経営企画部など）
            activity_type: 活動タイプ（作業、思考、指示、報告など）
            content: 記録内容
            is_private: プライベート記録かどうか
        """
        # 日本標準時として記録（Windows環境ではシステム時刻がJST）
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_private:
            # プライベート記録
            if not self.private_file.exists():
                header = f"# 🔒 プライベート記録\n**日付**: {datetime.now().strftime('%Y-%m-%d')}\n**タイムゾーン**: JST\n\n---\n\n"
                self.private_file.write_text(header, encoding='utf-8')
            
            with open(self.private_file, 'a', encoding='utf-8') as f:
                f.write(f"\n#### {timestamp} JST - {agent}の本音\n")
                f.write(f"{content}\n")
        else:
            # 通常記録
            self.initialize_log()
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n#### {timestamp} JST - {agent}\n")
                f.write(f"**{activity_type}**: {content}\n")
    
    def record_project_analysis(self):
        """プロジェクト解析フェーズの記録"""
        self.write_activity("CTO", "解析開始", 
                          "プロジェクトの全体構造を把握開始")
        self.write_activity("経営企画部", "市場調査", 
                          "競合分析と差別化ポイントの特定")
        self.write_activity("システム開発部", "技術調査", 
                          "技術スタックとレガシーコードの確認")
        self.write_activity("品質保証部", "テスト戦略", 
                          "テスト可能性の初期評価")
        self.write_activity("人事部", "リソース見積", 
                          "必要人員の算出開始")
        
        # プライベート記録
        self.write_activity("CTO", "", 
                          "このスケジュール、正直きつい...", True)
        self.write_activity("経営企画部", "", 
                          "また新しいプロジェクトか...前のやつまだ終わってないのに", True)
        self.write_activity("人事部", "", 
                          "9人も必要とか言われても、どこから調達するんだよ", True)
    
    def record_team_formation(self):
        """チーム編成フェーズの記録"""
        self.write_activity("CTO", "指示", 
                          "→ 人事部: フロントエンド3名、バックエンド4名、QA2名必要")
        self.write_activity("人事部", "チーム編成", 
                          "仮想メンバーの即座配属を実施")
        self.write_activity("人事部", "配属完了", 
                          "田中、鈴木、佐藤、山田を配属（全員仮想）")
        
        # プライベート記録
        self.write_activity("人事部", "", 
                          "実在しないメンバーの経歴書作るの疲れた...", True)
    
    def record_daily_work(self):
        """日常作業の記録"""
        self.write_activity("システム開発部", "実装", 
                          "APIエンドポイント15個定義完了")
        self.write_activity("品質保証部", "テスト", 
                          "単体テスト324件実行、全件合格")
        self.write_activity("経営企画部", "要件更新", 
                          "優先度変更: 決済フロー最優先")
        
        # 気分転換記録
        self.write_activity("CTO", "休憩", 
                          "コーヒーブレイク（3杯目）")
        self.write_activity("品質保証部", "気分転換", 
                          "YouTube猫動画3本視聴（10分）")
        
        # プライベート記録
        self.write_activity("システム開発部", "", 
                          "このコード書いた人、オブジェクト指向わかってる？", True)
        self.write_activity("品質保証部", "", 
                          "また夜更かししそう...明日きつい", True)

def main():
    """メイン処理"""
    writer = DailyLogWriter()
    
    import argparse
    parser = argparse.ArgumentParser(description='作業日誌記録システム')
    parser.add_argument('--phase', choices=['analysis', 'team', 'work', 'all'],
                      default='all', help='記録するフェーズ')
    parser.add_argument('--agent', type=str, help='エージェント名')
    parser.add_argument('--type', type=str, help='活動タイプ')
    parser.add_argument('--content', type=str, help='記録内容')
    parser.add_argument('--private', action='store_true', help='プライベート記録')
    
    args = parser.parse_args()
    
    if args.agent and args.content:
        # 個別記録
        writer.write_activity(args.agent, args.type or "活動", 
                            args.content, args.private)
        print(f"記録完了: {args.agent}")
    else:
        # フェーズ別記録
        if args.phase in ['analysis', 'all']:
            print("プロジェクト解析フェーズを記録中...")
            writer.record_project_analysis()
            
        if args.phase in ['team', 'all']:
            print("チーム編成フェーズを記録中...")
            writer.record_team_formation()
            
        if args.phase in ['work', 'all']:
            print("日常作業を記録中...")
            writer.record_daily_work()
        
        print(f"日誌記録完了: {writer.log_file.name}")

if __name__ == "__main__":
    main()