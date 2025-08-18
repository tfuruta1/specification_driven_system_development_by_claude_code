#!/usr/bin/env python3
"""
階層型エージェントシステム - 自動クリーンアップ管理システム
30分毎のチェックポイント、1時間毎の一時ファイル削除、日次完全クリーンアップを実行
"""

import os
import sys
import time
import json
import shutil
import threading
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import zipfile
from jst_config import format_jst_datetime, format_jst_timestamp, format_jst_time

@dataclass
class BackupInfo:
    """バックアップ情報"""
    timestamp: str
    backup_type: str  # checkpoint, error, daily
    file_path: str
    size_mb: float
    description: str

class AutoCleanupManager:
    """自動クリーンアップ管理システム"""
    
    def __init__(self):
        self.base_dir = Path(".claude_sub_agent")
        self.tmp_dir = self.base_dir / ".tmp"
        self.backup_dir = self.tmp_dir / "backups"
        self.checkpoint_dir = self.backup_dir / "checkpoints"
        self.error_backup_dir = self.backup_dir / "error_recovery"
        self.daily_backup_dir = self.backup_dir / "daily"
        
        # ディレクトリ作成
        for dir_path in [self.checkpoint_dir, self.error_backup_dir, self.daily_backup_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.base_dir / "cleanup_config.json"
        self.load_config()
        self.is_running = False
        self.scheduler_thread = None
        
    def load_config(self):
        """設定を読み込み"""
        default_config = {
            "checkpoint_interval_minutes": 30,
            "temp_cleanup_interval_minutes": 60,
            "daily_cleanup_hour": 3,  # 午前3時
            "max_checkpoint_count": 10,
            "max_backup_age_days": 7,
            "auto_cleanup_enabled": True,
            "protected_dirs": [".git", "node_modules", ".ActivityReport", "docs", "specs"]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """設定を保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def create_checkpoint(self):
        """チェックポイントを作成（30分毎）"""
        if not self.config["auto_cleanup_enabled"]:
            return
        
        timestamp = format_jst_timestamp()
        checkpoint_name = f"checkpoint_{timestamp}.zip"
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        
        print(f"💾 チェックポイント作成中... [{timestamp}]")
        
        try:
            # 重要なファイルをバックアップ
            with zipfile.ZipFile(checkpoint_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for pattern in ["*.py", "*.js", "*.vue", "*.md", "*.json"]:
                    for file_path in Path(".").rglob(pattern):
                        # 除外対象をスキップ
                        if any(protected in str(file_path) for protected in self.config["protected_dirs"]):
                            continue
                        if ".tmp" in str(file_path) or ".git" in str(file_path):
                            continue
                        
                        try:
                            zf.write(file_path, file_path.relative_to(Path(".")))
                        except:
                            pass
            
            # バックアップ情報を記録
            backup_info = BackupInfo(
                timestamp=format_jst_datetime(),
                backup_type="checkpoint",
                file_path=str(checkpoint_path),
                size_mb=checkpoint_path.stat().st_size / (1024 * 1024),
                description="30分毎の自動チェックポイント"
            )
            
            self._record_backup_info(backup_info)
            
            # 古いチェックポイントを削除
            self._cleanup_old_checkpoints()
            
            print(f"✅ チェックポイント作成完了: {checkpoint_name} ({backup_info.size_mb:.2f}MB)")
            
        except Exception as e:
            print(f"❌ チェックポイント作成エラー: {e}")
    
    def cleanup_temp_files(self):
        """一時ファイルをクリーンアップ（1時間毎）"""
        if not self.config["auto_cleanup_enabled"]:
            return
        
        print(f"一時ファイルクリーンアップ開始... [{format_jst_time()}]")
        
        cleanup_targets = [
            ("*.tmp", 0),  # .tmpファイルは即削除
            ("*.log", 24),  # ログファイルは24時間後
            ("*.bak", 48),  # バックアップは48時間後
            ("*~", 0),      # エディタの一時ファイルは即削除
        ]
        
        deleted_count = 0
        freed_space = 0
        
        for pattern, hours_old in cleanup_targets:
            cutoff_time = datetime.now() - timedelta(hours=hours_old)
            
            for file_path in self.tmp_dir.rglob(pattern):
                try:
                    if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        deleted_count += 1
                        freed_space += file_size
                except:
                    pass
        
        # 空のディレクトリを削除
        for dir_path in sorted(self.tmp_dir.rglob("*"), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                except:
                    pass
        
        if deleted_count > 0:
            freed_mb = freed_space / (1024 * 1024)
            print(f"✅ {deleted_count}個のファイルを削除 ({freed_mb:.2f}MB解放)")
        else:
            print(f"✅ クリーンアップ対象なし")
    
    def daily_cleanup(self):
        """日次完全クリーンアップ（午前3時）"""
        if not self.config["auto_cleanup_enabled"]:
            return
        
        print(f"日次完全クリーンアップ開始... [{format_jst_datetime()}]")
        
        # 日次バックアップを作成
        self._create_daily_backup()
        
        # 包括的なクリーンアップ
        cleanup_actions = [
            self._cleanup_analysis_cache,
            self._cleanup_agent_logs,
            self._cleanup_old_backups,
            self._cleanup_generated_docs,
            self._cleanup_workspace
        ]
        
        for action in cleanup_actions:
            try:
                action()
            except Exception as e:
                print(f"⚠️ クリーンアップエラー: {e}")
        
        # ディスク使用量レポート
        self._report_disk_usage()
        
        print(f"✅ 日次完全クリーンアップ完了")
    
    def _create_daily_backup(self):
        """日次バックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d")
        backup_name = f"daily_backup_{timestamp}_JST.zip"
        backup_path = self.daily_backup_dir / backup_name
        
        if backup_path.exists():
            return  # 今日のバックアップは既に存在
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # プロジェクト全体をバックアップ（除外対象を除く）
                for file_path in Path(".").rglob("*"):
                    if file_path.is_file():
                        if any(skip in str(file_path) for skip in ['.git', '.tmp', '__pycache__']):
                            continue
                        try:
                            zf.write(file_path, file_path.relative_to(Path(".")))
                        except:
                            pass
            
            print(f"💾 日次バックアップ作成: {backup_name}")
        except Exception as e:
            print(f"⚠️ 日次バックアップエラー: {e}")
    
    def _cleanup_old_checkpoints(self):
        """古いチェックポイントを削除"""
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.zip"))
        
        if len(checkpoints) > self.config["max_checkpoint_count"]:
            for old_checkpoint in checkpoints[:-self.config["max_checkpoint_count"]]:
                old_checkpoint.unlink()
                print(f"🗑️ 古いチェックポイント削除: {old_checkpoint.name}")
    
    def _cleanup_old_backups(self):
        """古いバックアップを削除"""
        cutoff_date = datetime.now() - timedelta(days=self.config["max_backup_age_days"])
        
        for backup_dir in [self.daily_backup_dir, self.error_backup_dir]:
            for backup_file in backup_dir.glob("*.zip"):
                if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                    backup_file.unlink()
                    print(f"🗑️ 古いバックアップ削除: {backup_file.name}")
    
    def _cleanup_analysis_cache(self):
        """解析キャッシュをクリーンアップ"""
        cache_dir = self.base_dir / "cache"
        if cache_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=7)
            for cache_file in cache_dir.rglob("*.pkl"):
                if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff_date:
                    cache_file.unlink()
    
    def _cleanup_agent_logs(self):
        """エージェントログをクリーンアップ"""
        log_dir = self.tmp_dir / "agent_logs"
        if log_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=3)
            for log_file in log_dir.rglob("*.log"):
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
    
    def _cleanup_generated_docs(self):
        """生成されたドキュメントをクリーンアップ"""
        docs_dir = self.tmp_dir / "generated_docs"
        if docs_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=7)
            for doc_file in docs_dir.rglob("*"):
                if doc_file.is_file() and datetime.fromtimestamp(doc_file.stat().st_mtime) < cutoff_date:
                    doc_file.unlink()
    
    def _cleanup_workspace(self):
        """エージェント作業領域をクリーンアップ"""
        workspace_dir = self.tmp_dir / "agent_workspace"
        if workspace_dir.exists():
            for agent_dir in workspace_dir.iterdir():
                if agent_dir.is_dir():
                    # 24時間以上古いファイルを削除
                    cutoff_date = datetime.now() - timedelta(hours=24)
                    for file_path in agent_dir.rglob("*"):
                        if file_path.is_file() and datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
                            file_path.unlink()
    
    def _report_disk_usage(self):
        """ディスク使用量をレポート"""
        total_size = 0
        file_count = 0
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        print(f"📊 ディスク使用量: {size_mb:.2f}MB ({file_count}ファイル)")
    
    def _record_backup_info(self, backup_info: BackupInfo):
        """バックアップ情報を記録"""
        info_file = self.backup_dir / "backup_info.json"
        
        infos = []
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    infos = json.load(f)
            except:
                pass
        
        infos.append({
            'timestamp': backup_info.timestamp,
            'backup_type': backup_info.backup_type,
            'file_path': backup_info.file_path,
            'size_mb': backup_info.size_mb,
            'description': backup_info.description
        })
        
        # 最新100件のみ保持
        infos = infos[-100:]
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(infos, f, indent=2, ensure_ascii=False)
    
    def create_error_backup(self, error_description: str = ""):
        """エラー時の自動バックアップ"""
        timestamp = format_jst_timestamp()
        backup_name = f"error_backup_{timestamp}.zip"
        backup_path = self.error_backup_dir / backup_name
        
        print(f"🆘 エラーバックアップ作成中...")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 現在の状態を全て保存
                for file_path in Path(".").rglob("*"):
                    if file_path.is_file():
                        if ".git" in str(file_path):
                            continue
                        try:
                            zf.write(file_path, file_path.relative_to(Path(".")))
                        except:
                            pass
            
            backup_info = BackupInfo(
                timestamp=format_jst_datetime(),
                backup_type="error",
                file_path=str(backup_path),
                size_mb=backup_path.stat().st_size / (1024 * 1024),
                description=f"エラー復旧用バックアップ: {error_description}"
            )
            
            self._record_backup_info(backup_info)
            
            print(f"✅ エラーバックアップ作成完了: {backup_name}")
            return backup_path
            
        except Exception as e:
            print(f"❌ エラーバックアップ失敗: {e}")
            return None
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """バックアップから復元"""
        print(f"🔄 バックアップから復元中: {backup_path.name}")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extractall(".")
            
            print(f"✅ 復元完了")
            return True
            
        except Exception as e:
            print(f"❌ 復元エラー: {e}")
            return False
    
    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.is_running:
            return
        
        print("🚀 自動クリーンアップスケジューラー起動")
        
        # スケジュール設定
        schedule.every(self.config["checkpoint_interval_minutes"]).minutes.do(self.create_checkpoint)
        schedule.every(self.config["temp_cleanup_interval_minutes"]).minutes.do(self.cleanup_temp_files)
        schedule.every().day.at(f"{self.config['daily_cleanup_hour']:02d}:00").do(self.daily_cleanup)
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _run_scheduler(self):
        """スケジューラーを実行"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 1分毎にチェック
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        self.is_running = False
        print("⏹️ 自動クリーンアップスケジューラー停止")
    
    def manual_cleanup(self):
        """手動クリーンアップ"""
        print("🔧 手動クリーンアップ実行")
        self.cleanup_temp_files()
        self._cleanup_old_checkpoints()
        self._cleanup_old_backups()
        self._report_disk_usage()

def demo():
    """デモンストレーション"""
    print("\n" + "=" * 60)
    print("🧹 自動クリーンアップシステム デモ")
    print("=" * 60 + "\n")
    
    manager = AutoCleanupManager()
    
    # 現在の設定表示
    print("📋 現在の設定:")
    print(f"  チェックポイント間隔: {manager.config['checkpoint_interval_minutes']}分")
    print(f"  一時ファイル削除間隔: {manager.config['temp_cleanup_interval_minutes']}分")
    print(f"  日次クリーンアップ時刻: {manager.config['daily_cleanup_hour']}:00")
    print(f"  自動クリーンアップ: {'有効' if manager.config['auto_cleanup_enabled'] else '無効'}")
    
    print("\n" + "-" * 40 + "\n")
    
    # チェックポイント作成デモ
    print("【チェックポイント作成】")
    manager.create_checkpoint()
    
    print("\n" + "-" * 40 + "\n")
    
    # 一時ファイルクリーンアップデモ
    print("【一時ファイルクリーンアップ】")
    manager.cleanup_temp_files()
    
    print("\n" + "-" * 40 + "\n")
    
    # ディスク使用量レポート
    manager._report_disk_usage()
    
    print("\n✅ デモ完了\n")

def main():
    """メイン処理"""
    import argparse
    parser = argparse.ArgumentParser(description='自動クリーンアップ管理')
    parser.add_argument('command', nargs='?', default='status',
                      choices=['status', 'start', 'stop', 'checkpoint', 'cleanup', 'demo'])
    parser.add_argument('--restore', help='バックアップから復元')
    
    args = parser.parse_args()
    
    manager = AutoCleanupManager()
    
    if args.restore:
        backup_path = Path(args.restore)
        if backup_path.exists():
            manager.restore_from_backup(backup_path)
        else:
            print(f"❌ バックアップファイルが見つかりません: {args.restore}")
    elif args.command == 'status':
        print(f"自動クリーンアップ: {'有効' if manager.config['auto_cleanup_enabled'] else '無効'}")
        manager._report_disk_usage()
    elif args.command == 'start':
        manager.start_scheduler()
        print("スケジューラーを開始しました。Ctrl+Cで停止します。")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_scheduler()
    elif args.command == 'stop':
        manager.config['auto_cleanup_enabled'] = False
        manager.save_config()
        print("自動クリーンアップを無効化しました")
    elif args.command == 'checkpoint':
        manager.create_checkpoint()
    elif args.command == 'cleanup':
        manager.manual_cleanup()
    elif args.command == 'demo':
        demo()

if __name__ == "__main__":
    main()