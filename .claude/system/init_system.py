#!/usr/bin/env python3
"""
階層型エージェントシステム - 初期化スクリプト
システム起動時に自動実行され、必要な環境を準備します
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

class SystemInitializer:
    def __init__(self):
        self.root = Path(".claude")
        self.tmp_root = self.root / ".tmp"
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now()
        
    def _generate_session_id(self):
        """セッションIDを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"ses_{timestamp}_{random_part}"
    
    def initialize(self):
        """システム初期化のメインエントリポイント"""
        print("=" * 60)
        print("🚀 階層型エージェントシステム v8.0 起動中...")
        print("=" * 60)
        
        # 1. ディレクトリ構造の確認と作成
        self._ensure_directory_structure()
        
        # 2. 前回セッションのクリーンアップ
        self._cleanup_previous_session()
        
        # 3. 新規セッションの準備
        self._prepare_new_session()
        
        # 4. エージェント活動モニタリング開始
        self._start_monitoring()
        
        # 5. バックアップシステム初期化
        self._init_backup_system()
        
        # 6. MCP連携チェック
        self._check_mcp_integration()
        
        print("\n✅ システム初期化完了")
        print(f"📋 セッションID: {self.session_id}")
        print("=" * 60)
        
    def _ensure_directory_structure(self):
        """必要なディレクトリ構造を作成"""
        print("\n[1/6] 📁 ディレクトリ構造を確認中...")
        
        directories = [
            # エージェント作業領域
            ".tmp/agent_workspace/cto",
            ".tmp/agent_workspace/hr_dept",
            ".tmp/agent_workspace/strategy_dept",
            ".tmp/agent_workspace/qa_dept",
            ".tmp/agent_workspace/dev_dept/frontend",
            ".tmp/agent_workspace/dev_dept/backend",
            ".tmp/agent_workspace/dev_dept/testing",
            
            # キャッシュ領域
            ".tmp/analysis_cache/checksums",
            ".tmp/analysis_cache/parsed",
            ".tmp/analysis_cache/results",
            
            # 生成ドキュメント
            ".tmp/generated_docs/requirements",
            ".tmp/generated_docs/design",
            ".tmp/generated_docs/reports",
            
            # バックアップ
            ".tmp/backups/instant",
            ".tmp/backups/checkpoint",
            ".tmp/backups/archive",
            
            # ログ
            ".tmp/agent_logs/daily",
            
            # セッション
            ".tmp/session/current",
            ".tmp/session/history",
            
            # 通常のディレクトリ
            "specs/new",
            "specs/existing",
            "steering",
            "modifications",
            "progress",
            "cache"
        ]
        
        for dir_path in directories:
            full_path = self.root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        print("   ✓ ディレクトリ構造準備完了")
    
    def _cleanup_previous_session(self):
        """前回セッションの一時ファイルをクリーンアップ"""
        print("\n[2/6] 🧹 前回セッションのクリーンアップ中...")
        
        # 現在のセッションファイルを履歴に移動
        current_session = self.tmp_root / "session" / "current"
        if current_session.exists():
            for item in current_session.iterdir():
                if item.is_file():
                    # 履歴フォルダに移動
                    history_path = self.tmp_root / "session" / "history"
                    shutil.move(str(item), str(history_path / item.name))
        
        # agent_workspaceのクリーンアップ
        workspace = self.tmp_root / "agent_workspace"
        if workspace.exists():
            for dept in workspace.iterdir():
                if dept.is_dir():
                    for item in dept.rglob("tmp_*"):
                        if item.is_file():
                            item.unlink()
                            print(f"   🗑️ 削除: {item.name}")
        
        # 古いインスタントバックアップを削除
        instant_backups = self.tmp_root / "backups" / "instant"
        if instant_backups.exists():
            for backup in instant_backups.iterdir():
                if backup.is_file():
                    # 24時間以上経過したものを削除
                    age = datetime.now() - datetime.fromtimestamp(backup.stat().st_mtime)
                    if age.days >= 1:
                        backup.unlink()
                        print(f"   🗑️ 古いバックアップ削除: {backup.name}")
        
        print("   ✓ クリーンアップ完了")
    
    def _prepare_new_session(self):
        """新規セッションの準備"""
        print("\n[3/6] 📋 新規セッション準備中...")
        
        # セッション情報ファイル作成
        session_info = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "system_version": "8.0.0",
            "status": "active",
            "departments": {
                "cto": {"status": "ready", "activities": []},
                "hr_dept": {"status": "ready", "activities": []},
                "strategy_dept": {"status": "ready", "activities": []},
                "qa_dept": {"status": "ready", "activities": []},
                "dev_dept": {"status": "ready", "activities": []}
            }
        }
        
        session_file = self.tmp_root / "session" / "current" / f"{self.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ セッション {self.session_id} 準備完了")
    
    def _start_monitoring(self):
        """エージェント活動モニタリング開始"""
        print("\n[4/6] 🔍 エージェント活動モニタリング開始...")
        
        # activity_stream.logファイル初期化
        log_file = self.tmp_root / "agent_logs" / "activity_stream.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"セッション開始: {self.session_id}\n")
            f.write(f"開始時刻: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
        
        # モニタリング設定
        monitor_config = {
            "enabled": True,
            "level": "normal",  # verbose, normal, quiet
            "realtime": True,
            "filters": [],
            "log_file": str(log_file)
        }
        
        config_file = self.tmp_root / "agent_logs" / "monitor_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(monitor_config, f, indent=2)
        
        print("   ✓ モニタリング開始")
    
    def _init_backup_system(self):
        """バックアップシステム初期化"""
        print("\n[5/6] 💾 バックアップシステム初期化中...")
        
        # 変更履歴ファイル初期化
        history_file = self.tmp_root / "backups" / "change_history.json"
        
        history_data = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "changes": []
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        # バックアップ設定
        backup_config = {
            "auto_backup": True,
            "instant_backup": True,
            "checkpoint_interval_minutes": 30,
            "retention_policy": {
                "instant": {"max_age_hours": 24, "max_count": 100},
                "checkpoint": {"max_age_days": 7, "max_count": 50},
                "archive": {"max_age_days": 30, "max_size_gb": 10}
            }
        }
        
        config_file = self.tmp_root / "backups" / "backup_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(backup_config, f, indent=2)
        
        print("   ✓ バックアップシステム準備完了")
    
    def _check_mcp_integration(self):
        """MCP連携の確認"""
        print("\n[6/6] 🔌 MCP連携確認中...")
        
        mcp_status = {
            "gemini_cli": False,
            "o3_mcp": False,
            "checked_at": datetime.now().isoformat()
        }
        
        # MCP利用可能性チェック（実際にはコマンド実行が必要）
        # ここではプレースホルダとして
        try:
            # import subprocess
            # result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True)
            # if "gemini-cli" in result.stdout:
            #     mcp_status["gemini_cli"] = True
            # if "o3" in result.stdout:
            #     mcp_status["o3_mcp"] = True
            pass
        except:
            pass
        
        # MCP状態保存
        mcp_file = self.tmp_root / "session" / "current" / "mcp_status.json"
        with open(mcp_file, 'w', encoding='utf-8') as f:
            json.dump(mcp_status, f, indent=2)
        
        if mcp_status["gemini_cli"]:
            print("   ✓ Gemini-CLI 連携確認")
        if mcp_status["o3_mcp"]:
            print("   ✓ o3 MCP 連携確認")
        
        if not (mcp_status["gemini_cli"] or mcp_status["o3_mcp"]):
            print("   ℹ️ MCP未連携（Claude Code内蔵機能で動作）")
        
        return mcp_status

def main():
    """メインエントリポイント"""
    initializer = SystemInitializer()
    
    try:
        initializer.initialize()
        
        # エージェント起動通知を表示
        print("\n" + "="*60)
        print("🎯 CTO: システム起動完了。ご用件をお聞かせください。")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ エラー: システム初期化に失敗しました")
        print(f"   詳細: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()