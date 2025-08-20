#!/usr/bin/env python3
"""
階層型エージェントシステム - クリーンアップスクリプト
作業完了時やシステム終了時に実行され、環境をクリーンに保ちます
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import fnmatch
sys.path.insert(0, str(Path(__file__).parent))
from jst_config import format_jst_datetime, get_jst_now, JST

class SystemCleanup:
    def __init__(self, mode="normal"):
        """
        Args:
            mode: "normal" (通常), "deep" (完全), "emergency" (緊急)
        """
        self.root = Path(".claude")
        self.tmp_root = self.root / ".tmp"
        self.mode = mode
        self.cleanup_report = {
            "timestamp": format_jst_datetime(),
            "mode": mode,
            "deleted_files": [],
            "deleted_folders": [],
            "archived_files": [],
            "space_freed_mb": 0
        }
        
    def cleanup(self):
        """クリーンアップのメインエントリポイント"""
        print("=" * 60)
        print(f"[CLEAN] システムクリーンアップ開始 (モード: {self.mode})")
        print("=" * 60)
        
        initial_size = self._get_folder_size(self.tmp_root)
        
        # 1. セッション終了処理
        self._finalize_session()
        
        # 2. 一時ファイルクリーンアップ
        self._cleanup_temp_files()
        
        # 3. キャッシュクリーンアップ
        self._cleanup_cache()
        
        # 4. バックアップ整理
        self._cleanup_backups()
        
        # 5. ログファイル整理
        self._cleanup_logs()
        
        # 6. 深層クリーンアップ（必要時のみ）
        if self.mode in ["deep", "emergency"]:
            self._deep_cleanup()
        
        # 7. 空ディレクトリ削除
        self._remove_empty_directories()
        
        # 結果レポート
        final_size = self._get_folder_size(self.tmp_root)
        self.cleanup_report["space_freed_mb"] = (initial_size - final_size) / 1024 / 1024
        
        self._save_cleanup_report()
        self._display_results()
        
    def _finalize_session(self):
        """セッション終了処理"""
        print("\n[1/7] [LOG] セッション終了処理中...")
        
        current_session = self.tmp_root / "session" / "current"
        history = self.tmp_root / "session" / "history"
        
        if current_session.exists():
            for session_file in current_session.glob("*.json"):
                # セッション情報を読み込み
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # 終了時刻を追加
                session_data["end_time"] = format_jst_datetime()
                session_data["status"] = "completed"
                
                # 履歴に保存
                history_file = history / f"{session_data['session_id']}_completed.json"
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                
                # 元ファイル削除
                session_file.unlink()
                self.cleanup_report["archived_files"].append(str(history_file))
        
        print("   [OK] セッション終了処理完了")
    
    def _cleanup_temp_files(self):
        """一時ファイルのクリーンアップ"""
        print("\n[2/7] [DEL] 一時ファイル削除中...")
        
        patterns = ["tmp_*", "*.tmp", "*.temp", "*~", "*.bak"]
        workspace = self.tmp_root / "agent_workspace"
        
        if workspace.exists():
            for pattern in patterns:
                for temp_file in workspace.rglob(pattern):
                    if temp_file.is_file():
                        try:
                            file_size = temp_file.stat().st_size
                            temp_file.unlink()
                            self.cleanup_report["deleted_files"].append(str(temp_file))
                            print(f"   [DEL] 削除: {temp_file.name} ({file_size/1024:.1f}KB)")
                        except Exception as e:
                            print(f"   [WARN] 削除失敗: {temp_file.name} - {e}")
        
        print("   [OK] 一時ファイル削除完了")
    
    def _cleanup_cache(self):
        """キャッシュのクリーンアップ"""
        print("\n[3/7] [CACHE] キャッシュ整理中...")
        
        cache_dir = self.tmp_root / "analysis_cache"
        if not cache_dir.exists():
            print("   [INFO] キャッシュディレクトリなし")
            return
        
        # 古いキャッシュファイルを削除
        cutoff_date = get_jst_now() - timedelta(days=7)
        
        for cache_file in cache_dir.rglob("*"):
            if cache_file.is_file():
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_date:
                    cache_file.unlink()
                    self.cleanup_report["deleted_files"].append(str(cache_file))
                    print(f"   [DEL] 古いキャッシュ削除: {cache_file.name}")
        
        print("   [OK] キャッシュ整理完了")
    
    def _cleanup_backups(self):
        """バックアップの整理"""
        print("\n[4/7] [BACKUP] バックアップ整理中...")
        
        backups_dir = self.tmp_root / "backups"
        if not backups_dir.exists():
            print("   [INFO] バックアップディレクトリなし")
            return
        
        # ポリシーに基づく削除
        policies = {
            "instant": {"max_age_hours": 24, "max_count": 100},
            "checkpoint": {"max_age_days": 7, "max_count": 50},
            "archive": {"max_age_days": 30, "max_count": 20}
        }
        
        for backup_type, policy in policies.items():
            backup_path = backups_dir / backup_type
            if backup_path.exists():
                files = sorted(backup_path.glob("*"), key=lambda x: x.stat().st_mtime)
                
                # 古いファイルを削除
                if "max_age_hours" in policy:
                    cutoff = get_jst_now() - timedelta(hours=policy["max_age_hours"])
                else:
                    cutoff = get_jst_now() - timedelta(days=policy["max_age_days"])
                
                for file in files:
                    if file.is_file():
                        file_time = datetime.fromtimestamp(file.stat().st_mtime)
                        if file_time < cutoff or len(files) > policy["max_count"]:
                            file.unlink()
                            self.cleanup_report["deleted_files"].append(str(file))
                            print(f"   [DEL] 古いバックアップ削除: {file.name}")
                            files.remove(file)
        
        print("   [OK] バックアップ整理完了")
    
    def _cleanup_logs(self):
        """ログファイルの整理"""
        print("\n[5/7] [LOG] ログファイル整理中...")
        
        logs_dir = self.tmp_root / "agent_logs"
        if not logs_dir.exists():
            print("   [INFO] ログディレクトリなし")
            return
        
        # activity_stream.logのローテーション
        stream_log = logs_dir / "activity_stream.log"
        if stream_log.exists() and stream_log.stat().st_size > 100 * 1024 * 1024:  # 100MB
            # アーカイブ
            from jst_config import format_jst_timestamp
            timestamp = format_jst_timestamp()
            archive_name = logs_dir / "daily" / f"activity_{timestamp}.log"
            shutil.move(str(stream_log), str(archive_name))
            print(f"   [ARCH] ログローテーション: {archive_name.name}")
        
        # 古い日次ログを削除
        daily_logs = logs_dir / "daily"
        if daily_logs.exists():
            cutoff = get_jst_now() - timedelta(days=7)
            for log_file in daily_logs.glob("*.log"):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff:
                    log_file.unlink()
                    self.cleanup_report["deleted_files"].append(str(log_file))
                    print(f"   [DEL] 古いログ削除: {log_file.name}")
        
        print("   [OK] ログファイル整理完了")
    
    def _deep_cleanup(self):
        """深層クリーンアップ（deepモード時のみ）"""
        print("\n[6/7] [DEEP] 深層クリーンアップ実行中...")
        
        if self.mode == "emergency":
            # 緊急モード：ほぼすべて削除
            print("   [WARN] 緊急モード: 重要ファイル以外をすべて削除")
            
            # 保護パターン
            protected = ["*.checkpoint", "*.backup", "current_session*", ".gitkeep"]
            
            for item in self.tmp_root.rglob("*"):
                if item.is_file():
                    # 保護されていないファイルを削除
                    is_protected = any(fnmatch.fnmatch(item.name, p) for p in protected)
                    if not is_protected:
                        item.unlink()
                        self.cleanup_report["deleted_files"].append(str(item))
        
        elif self.mode == "deep":
            # 深層モード：生成ドキュメントもクリア
            print("   [DEEP] 深層モード: 生成ドキュメントを含めて削除")
            
            generated_docs = self.tmp_root / "generated_docs"
            if generated_docs.exists():
                shutil.rmtree(generated_docs)
                generated_docs.mkdir(parents=True)
                self.cleanup_report["deleted_folders"].append(str(generated_docs))
        
        print("   [OK] 深層クリーンアップ完了")
    
    def _remove_empty_directories(self):
        """空ディレクトリの削除"""
        print("\n[7/7] [DIR] 空ディレクトリ削除中...")
        
        # ボトムアップで空ディレクトリを削除
        for dirpath, dirnames, filenames in os.walk(self.tmp_root, topdown=False):
            if not dirnames and not filenames:
                dir_path = Path(dirpath)
                # .gitkeepがある場合は削除しない
                if not (dir_path / ".gitkeep").exists():
                    try:
                        dir_path.rmdir()
                        self.cleanup_report["deleted_folders"].append(str(dir_path))
                        print(f"   [DIR] 空ディレクトリ削除: {dir_path.name}")
                    except:
                        pass
        
        print("   [OK] 空ディレクトリ削除完了")
    
    def _get_folder_size(self, folder):
        """フォルダサイズを取得"""
        total = 0
        if folder.exists():
            for entry in folder.rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
        return total
    
    def _save_cleanup_report(self):
        """クリーンアップレポートを保存"""
        report_dir = self.root / "system" / "cleanup_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = format_jst_timestamp()
        report_file = report_dir / f"cleanup_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)
    
    def _display_results(self):
        """クリーンアップ結果を表示"""
        print("\n" + "="*60)
        print("[REPORT] クリーンアップ完了レポート")
        print("="*60)
        print(f"モード: {self.mode}")
        print(f"削除ファイル数: {len(self.cleanup_report['deleted_files'])}")
        print(f"削除フォルダ数: {len(self.cleanup_report['deleted_folders'])}")
        print(f"アーカイブ数: {len(self.cleanup_report['archived_files'])}")
        print(f"解放容量: {self.cleanup_report['space_freed_mb']:.2f} MB")
        print("="*60)

def main():
    """メインエントリポイント"""
    # コマンドライン引数でモードを指定可能
    mode = "normal"
    if len(sys.argv) > 1:
        if sys.argv[1] in ["normal", "deep", "emergency"]:
            mode = sys.argv[1]
    
    cleanup = SystemCleanup(mode)
    
    try:
        cleanup.cleanup()
        print("\n[SUCCESS] クリーンアップが正常に完了しました")
        
    except Exception as e:
        print(f"\n[ERROR] エラー: クリーンアップに失敗しました")
        print(f"   詳細: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()