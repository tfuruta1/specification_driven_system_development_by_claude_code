#!/usr/bin/env python3
"""
階層型エージェントシステム - エージェント活動モニタリングシステム
リアルタイムでエージェントの動作状況を可視化します
"""

import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from jst_config import format_jst_time, format_jst_datetime, format_jst_timestamp

class ActivityType(Enum):
    """アクティビティタイプ"""
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

class CommunicationType(Enum):
    """通信パターン"""
    REQUEST = "->"      # 依頼
    RESPONSE = "<-"     # 応答
    BROADCAST = "[ALL]"   # 全体通知
    ALERT = "[ALERT]"      # 警告
    SUCCESS = "[OK]"     # 成功
    ERROR = "[ERROR]"       # エラー

class AgentMonitor:
    """エージェント活動モニタリングシステム"""
    
    def __init__(self):
        self.current_activities = {}
        self.log_dir = Path(".claude/.tmp/agent_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "activity_stream.log"
        self.daily_dir = self.log_dir / "daily"
        self.daily_dir.mkdir(exist_ok=True)
        self.monitor_level = "normal"  # verbose, normal, quiet
        self.filter_agents = None  # None means show all
        self.realtime = True
        self.max_log_size = 100 * 1024 * 1024  # 100MB
        
    def log_activity(self, agent_name: str, agent_emoji: str, 
                     activity_type: ActivityType, details: str = "", 
                     progress: Optional[int] = None):
        """エージェントの活動をログに記録"""
        timestamp = datetime.now()
        timestamp_str = format_jst_datetime(timestamp)
        
        # フィルター適用
        if self.filter_agents and agent_name.lower() not in self.filter_agents:
            return
        
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
        self._write_to_log(timestamp, agent_name, agent_emoji, activity_type, details, progress)
        
        # ログローテーション確認
        self._check_log_rotation()
    
    def log_communication(self, from_agent: Dict, to_agent: Dict, 
                         comm_type: CommunicationType, content: str):
        """部門間通信を記録"""
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%H:%M:%S")
        
        # フィルター適用
        if self.filter_agents:
            if (from_agent['name'].lower() not in self.filter_agents and 
                to_agent['name'].lower() not in self.filter_agents):
                return
        
        # ターミナル出力
        if self.realtime:
            message = (f"[{timestamp_str}] {from_agent['emoji']} {from_agent['name']} "
                      f"{comm_type.value} {to_agent['emoji']} {to_agent['name']} > {content}")
            
            if self.monitor_level != "quiet":
                print(message)
        
        # ログファイル記録
        log_entry = {
            'timestamp': format_jst_datetime(timestamp),
            'type': 'communication',
            'from': from_agent,
            'to': to_agent,
            'comm_type': comm_type.name,
            'content': content
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _progress_bar(self, percent: int) -> str:
        """プログレスバーを生成"""
        filled = int(percent / 10)
        bar = "=" * filled
        if filled < 10:
            bar += ">"
            bar += " " * (10 - filled - 1)
        return bar
    
    def _write_to_log(self, timestamp: datetime, agent_name: str, 
                      agent_emoji: str, activity_type: ActivityType, 
                      details: str, progress: Optional[int]):
        """ログファイルに記録"""
        log_entry = {
            'timestamp': format_jst_datetime(timestamp),
            'type': 'activity',
            'agent': {
                'name': agent_name,
                'emoji': agent_emoji
            },
            'activity_type': activity_type.name,
            'details': details,
            'progress': progress
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _check_log_rotation(self):
        """ログローテーションを確認"""
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_log_size:
            # 現在のログを日次アーカイブに移動
            archive_name = self.daily_dir / f"{format_jst_timestamp()}.log"
            self.log_file.rename(archive_name)
            print(f"ログファイルをアーカイブしました: {archive_name.name}")
    
    def cleanup_old_logs(self):
        """古いログファイルを削除"""
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for log_file in self.daily_dir.glob("*.log"):
            file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_date < cutoff_date:
                log_file.unlink()
                print(f"古いログを削除: {log_file.name}")
    
    def set_monitor_level(self, level: str):
        """モニタリング詳細度を設定"""
        if level in ["verbose", "normal", "quiet"]:
            self.monitor_level = level
            print(f"モニタリングレベル: {level}")
        else:
            print(f"無効なレベル: {level}")
    
    def set_filter(self, agents: List[str]):
        """表示するエージェントをフィルタリング"""
        self.filter_agents = [a.lower() for a in agents] if agents else None
        if self.filter_agents:
            print(f"フィルター設定: {', '.join(agents)}")
        else:
            print("フィルター解除: 全エージェント表示")
    
    def clear_logs(self):
        """ログをクリア"""
        if self.log_file.exists():
            self.log_file.unlink()
        print("🧹 ログをクリアしました")
    
    def set_realtime(self, enabled: bool):
        """リアルタイム表示の切り替え"""
        self.realtime = enabled
        status = "ON" if enabled else "OFF"
        print(f"📺 リアルタイム表示: {status}")
    
    def show_summary(self):
        """活動サマリーを表示"""
        if not self.log_file.exists():
            print("📊 ログファイルが存在しません")
            return
        
        activities = {}
        communications = 0
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
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
        
        print("\n" + "=" * 60)
        print("📊 活動サマリー")
        print("=" * 60)
        
        for agent, count in sorted(activities.items(), key=lambda x: x[1], reverse=True):
            print(f"  {agent}: {count} 件")
        
        print(f"\n  部門間通信: {communications} 件")
        print("=" * 60)

class MonitorDemo:
    """モニタリングシステムのデモ"""
    
    @staticmethod
    def run_demo():
        """デモを実行"""
        monitor = AgentMonitor()
        
        print("\n" + "=" * 60)
        print("🔍 エージェント活動モニタリングシステム デモ")
        print("=" * 60 + "\n")
        
        # CTO主導の修正フロー
        monitor.log_activity("CTO", "🎯", ActivityType.ANALYZING, 
                           "修正要求を分析中...")
        time.sleep(0.5)
        
        # 部門への依頼
        monitor.log_communication(
            {"name": "CTO", "emoji": "🎯"},
            {"name": "システム開発部", "emoji": "💻"},
            CommunicationType.REQUEST,
            "影響範囲の調査を依頼"
        )
        time.sleep(0.3)
        
        monitor.log_communication(
            {"name": "CTO", "emoji": "🎯"},
            {"name": "品質保証部", "emoji": "🛡️"},
            CommunicationType.REQUEST,
            "現在の品質状況を確認"
        )
        time.sleep(0.3)
        
        # 各部門の活動（プログレス付き）
        for i in range(0, 101, 20):
            monitor.log_activity("システム開発部", "💻", ActivityType.ANALYZING,
                               "backend-lead: API endpoints確認中", i)
            time.sleep(0.3)
        
        for i in range(0, 101, 25):
            monitor.log_activity("品質保証部", "🛡️", ActivityType.TESTING,
                               "既存テストの実行中", i)
            time.sleep(0.3)
        
        # 人事部のチーム編成
        monitor.log_activity("人事部", "🏢", ActivityType.COORDINATING,
                           "必要スキルセットを分析中")
        time.sleep(0.5)
        
        monitor.log_activity("人事部", "🏢", ActivityType.PLANNING,
                           "田中さくら(Frontend)を配属準備")
        time.sleep(0.3)
        
        # 経営企画部の戦略分析
        monitor.log_activity("経営企画部", "💡", ActivityType.ANALYZING,
                           "ビジネス影響度: 中")
        time.sleep(0.5)
        
        # 成功報告
        monitor.log_communication(
            {"name": "システム開発部", "emoji": "💻"},
            {"name": "CTO", "emoji": "🎯"},
            CommunicationType.SUCCESS,
            "影響範囲調査完了"
        )
        
        monitor.log_communication(
            {"name": "品質保証部", "emoji": "🛡️"},
            {"name": "CTO", "emoji": "🎯"},
            CommunicationType.SUCCESS,
            "品質チェック完了"
        )
        
        print("\n" + "=" * 60)
        monitor.show_summary()
        print("\n✅ デモ完了\n")

def main():
    """メイン処理"""
    import argparse
    parser = argparse.ArgumentParser(description='エージェント活動モニタリング')
    parser.add_argument('command', nargs='?', default='demo',
                      choices=['demo', 'clear', 'summary', 'cleanup'])
    parser.add_argument('--level', choices=['verbose', 'normal', 'quiet'],
                      help='モニタリング詳細度')
    parser.add_argument('--filter', nargs='+', help='表示するエージェント')
    parser.add_argument('--realtime', choices=['on', 'off'], help='リアルタイム表示')
    
    args = parser.parse_args()
    
    monitor = AgentMonitor()
    
    if args.level:
        monitor.set_monitor_level(args.level)
    
    if args.filter:
        monitor.set_filter(args.filter)
    
    if args.realtime:
        monitor.set_realtime(args.realtime == 'on')
    
    if args.command == 'demo':
        MonitorDemo.run_demo()
    elif args.command == 'clear':
        monitor.clear_logs()
    elif args.command == 'summary':
        monitor.show_summary()
    elif args.command == 'cleanup':
        monitor.cleanup_old_logs()

if __name__ == "__main__":
    main()