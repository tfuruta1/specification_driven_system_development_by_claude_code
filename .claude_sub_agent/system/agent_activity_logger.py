#!/usr/bin/env python3
"""
エージェント活動ロガー - リアルタイムでエージェントの動作を可視化
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

class ActivityType(Enum):
    """アクティビティタイプ"""
    PLANNING = "📋 計画中"
    ANALYZING = "🔍 解析中"
    DESIGNING = "📐 設計中"
    IMPLEMENTING = "💻 実装中"
    TESTING = "🧪 テスト中"
    REVIEWING = "👀 レビュー中"
    DEPLOYING = "🚀 デプロイ中"
    DOCUMENTING = "📝 文書作成中"
    COORDINATING = "🤝 調整中"
    WAITING = "⏳ 待機中"
    ERROR = "❌ エラー"
    SUCCESS = "✅ 完了"

class CommunicationType(Enum):
    """通信タイプ"""
    REQUEST = "→"      # 依頼
    RESPONSE = "←"     # 応答
    BROADCAST = "📢"   # 全体通知
    ALERT = "⚠️"      # 警告
    SUCCESS = "✅"     # 成功
    ERROR = "❌"       # エラー

class Agent:
    """エージェント基底クラス"""
    def __init__(self, name: str, emoji: str, department: str):
        self.name = name
        self.emoji = emoji
        self.department = department
        self.folder_name = name.lower().replace(" ", "_")

# エージェント定義
AGENTS = {
    "cto": Agent("CTO", "🎯", "経営層"),
    "hr_dept": Agent("人事部", "🏢", "管理部門"),
    "strategy_dept": Agent("経営企画部", "💡", "管理部門"),
    "qa_dept": Agent("品質保証部", "🛡️", "技術部門"),
    "dev_dept": Agent("システム開発部", "💻", "技術部門"),
    "frontend_lead": Agent("フロントエンドリーダー", "🎨", "システム開発部"),
    "backend_lead": Agent("バックエンドリーダー", "⚙️", "システム開発部"),
    "qa_lead": Agent("QAリーダー", "🧪", "システム開発部"),
    "devops_lead": Agent("DevOpsリーダー", "🚀", "システム開発部"),
}

class AgentActivityLogger:
    """エージェント活動ロガー"""
    
    def __init__(self):
        self.tmp_root = Path(".claude_sub_agent/.tmp")
        self.log_file = self.tmp_root / "agent_logs" / "activity_stream.log"
        self.current_activities = {}
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """ログファイルの存在を確認"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.touch()
    
    def _get_timestamp(self) -> str:
        """タイムスタンプを取得"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _write_to_log(self, message: str):
        """ログファイルに書き込み"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    
    def _print_to_terminal(self, message: str):
        """ターミナルに出力"""
        print(message)
        sys.stdout.flush()  # バッファをフラッシュして即座に表示
    
    def log_activity(
        self,
        agent_key: str,
        activity_type: ActivityType,
        details: str = "",
        progress: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        エージェントの活動をログ記録
        
        Args:
            agent_key: エージェントキー (AGENTS辞書のキー)
            activity_type: アクティビティタイプ
            details: 詳細情報
            progress: 進捗率 (0-100)
            metadata: 追加メタデータ
        """
        agent = AGENTS.get(agent_key)
        if not agent:
            return
        
        timestamp = self._get_timestamp()
        
        # プログレスバー付きの場合
        if progress is not None:
            progress_bar = self._create_progress_bar(progress)
            message = f"[{progress_bar}] {progress}% | {agent.emoji} {agent.name} > {activity_type.value}"
            if details:
                message += f" - {details}"
        else:
            # 通常のログ
            message = f"[{timestamp}] {agent.emoji} {agent.name} > {activity_type.value}"
            if details:
                message += f" - {details}"
        
        # ターミナル出力
        self._print_to_terminal(message)
        
        # ログファイル記録
        log_entry = {
            "timestamp": timestamp,
            "agent": agent.name,
            "department": agent.department,
            "activity": activity_type.name,
            "details": details,
            "progress": progress,
            "metadata": metadata or {}
        }
        self._write_to_log(json.dumps(log_entry, ensure_ascii=False))
        
        # 現在のアクティビティを更新
        self.current_activities[agent_key] = {
            "activity": activity_type,
            "details": details,
            "progress": progress,
            "started_at": timestamp
        }
    
    def log_communication(
        self,
        from_agent: str,
        to_agent: str,
        comm_type: CommunicationType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        エージェント間の通信をログ記録
        
        Args:
            from_agent: 送信元エージェントキー
            to_agent: 送信先エージェントキー
            comm_type: 通信タイプ
            content: 通信内容
            metadata: 追加メタデータ
        """
        sender = AGENTS.get(from_agent)
        receiver = AGENTS.get(to_agent)
        
        if not sender or not receiver:
            return
        
        timestamp = self._get_timestamp()
        arrow = comm_type.value
        
        message = (f"[{timestamp}] {sender.emoji} {sender.name} {arrow} "
                  f"{receiver.emoji} {receiver.name} > {content}")
        
        # ターミナル出力
        self._print_to_terminal(message)
        
        # ログファイル記録
        log_entry = {
            "timestamp": timestamp,
            "type": "communication",
            "from": sender.name,
            "to": receiver.name,
            "comm_type": comm_type.name,
            "content": content,
            "metadata": metadata or {}
        }
        self._write_to_log(json.dumps(log_entry, ensure_ascii=False))
    
    def _create_progress_bar(self, percent: int) -> str:
        """プログレスバーを作成"""
        filled = int(percent / 10)
        bar = "=" * filled
        if filled < 10:
            bar += ">"
            bar += " " * (10 - filled - 1)
        return bar
    
    def log_phase_transition(self, phase_name: str, status: str = "開始"):
        """フェーズ遷移をログ記録"""
        timestamp = self._get_timestamp()
        separator = "="*60
        
        message = f"\n{separator}\n[{timestamp}] 📍 フェーズ: {phase_name} - {status}\n{separator}"
        
        self._print_to_terminal(message)
        self._write_to_log(message)
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """現在のアクティビティサマリーを取得"""
        summary = {
            "timestamp": self._get_timestamp(),
            "active_agents": len(self.current_activities),
            "activities": {}
        }
        
        for agent_key, activity in self.current_activities.items():
            agent = AGENTS[agent_key]
            summary["activities"][agent.name] = {
                "status": activity["activity"].value,
                "details": activity["details"],
                "progress": activity["progress"],
                "started_at": activity["started_at"]
            }
        
        return summary

# グローバルロガーインスタンス
logger = AgentActivityLogger()

def demo_usage():
    """使用例のデモンストレーション"""
    
    # フェーズ開始
    logger.log_phase_transition("修正要求分析", "開始")
    
    # CTO活動
    logger.log_activity("cto", ActivityType.ANALYZING, "修正要求を分析中")
    
    # 部門間通信
    logger.log_communication("cto", "dev_dept", CommunicationType.REQUEST, "影響範囲の調査を依頼")
    logger.log_communication("cto", "qa_dept", CommunicationType.REQUEST, "現在の品質状況を確認")
    
    # 各部門の活動（プログレス付き）
    import time
    for i in range(0, 101, 20):
        logger.log_activity("backend_lead", ActivityType.ANALYZING, "API endpoints確認中", progress=i)
        time.sleep(0.5)
    
    # 成功報告
    logger.log_activity("backend_lead", ActivityType.SUCCESS, "API解析完了")
    
    # 人事部の活動
    logger.log_activity("hr_dept", ActivityType.COORDINATING, "必要スキルセットを分析中")
    logger.log_activity("hr_dept", ActivityType.PLANNING, "田中さくら(Frontend)を配属準備")
    
    # エラー処理
    logger.log_activity("qa_dept", ActivityType.ERROR, "テスト環境接続エラー")
    
    # フェーズ完了
    logger.log_phase_transition("修正要求分析", "完了")
    
    # サマリー表示
    summary = logger.get_activity_summary()
    print("\n📊 アクティビティサマリー:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # デモ実行
    demo_usage()