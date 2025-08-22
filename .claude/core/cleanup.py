#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - 統合クリーンアップシステム
auto_cleanup_manager.py の基本機能を統合（YAGNIに準拠）
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from activity_logger import logger
from jst_utils import format_jst_datetime, format_jst_timestamp, get_jst_now


@dataclass
class BackupInfo:
    """バックアップ情報"""
    timestamp: str
    backup_type: str  # checkpoint, error, manual
    file_path: str
    size_mb: float
    description: str


class UnifiedCleanupManager:
    """統合クリーンアップマネージャー（KISS + 必要最小限機能）"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.temp_extensions = ['.tmp', '.bak', '.log~', '.swp']
        self.temp_dirs = ['__pycache__', '.pytest_cache', 'node_modules']
        
        # バックアップ設定
        self.backup_dir = self.base_path / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backup_age_days = 7
        self.max_backup_count = 5
    
    def cleanup_project(self) -> Dict:
        """プロジェクト終了時の完全クリーンアップ"""
        logger.info("プロジェクトクリーンアップ開始", "CLEANUP")
        
        results = {
            "deleted_files": [],
            "deleted_dirs": [],
            "errors": [],
            "space_freed_mb": 0
        }
        
        initial_size = self._get_folder_size(self.base_path / "logs")
        
        # 一時ファイル削除
        for ext in self.temp_extensions:
            for file in self.base_path.rglob(f"*{ext}"):
                try:
                    file_size = file.stat().st_size
                    file.unlink()
                    results["deleted_files"].append(str(file))
                    results["space_freed_mb"] += file_size / (1024 * 1024)
                    logger.debug(f"削除: {file}", "CLEANUP")
                except Exception as e:
                    results["errors"].append(f"Failed to delete {file}: {e}")
        
        # 一時ディレクトリ削除
        for dir_name in self.temp_dirs:
            for dir_path in self.base_path.rglob(dir_name):
                if dir_path.is_dir():
                    try:
                        shutil.rmtree(dir_path)
                        results["deleted_dirs"].append(str(dir_path))
                        logger.debug(f"削除: {dir_path}", "CLEANUP")
                    except Exception as e:
                        results["errors"].append(f"Failed to delete {dir_path}: {e}")
        
        # 古いログファイルクリーンアップ
        self._cleanup_old_logs()
        
        # 古いキャッシュクリーンアップ
        self._cleanup_old_cache()
        
        # 古いバックアップクリーンアップ
        self._cleanup_old_backups()
        
        # 空のディレクトリ削除
        for dir_path in sorted(self.base_path.rglob("*"), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    results["deleted_dirs"].append(str(dir_path))
                except:
                    pass  # 削除できない場合は無視
        
        logger.info(
            f"クリーンアップ完了: ファイル{len(results['deleted_files'])}個、"
            f"ディレクトリ{len(results['deleted_dirs'])}個削除、"
            f"{results['space_freed_mb']:.2f}MB解放",
            "CLEANUP"
        )
        
        return results
    
    def cleanup_workspace(self) -> Dict:
        """ワークスペースのみクリーンアップ"""
        workspace = self.base_path / "workspace"
        if not workspace.exists():
            return {"status": "no workspace"}
        
        deleted = []
        for file in workspace.glob("*"):
            if file.is_file():
                file.unlink()
                deleted.append(str(file))
        
        return {"deleted": deleted}
    
    def create_backup(self, backup_type: str = "manual", description: str = "") -> Optional[Path]:
        """重要ファイルのバックアップを作成"""
        timestamp = format_jst_timestamp()
        backup_name = f"{backup_type}_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        logger.info(f"バックアップ作成中: {backup_name}", "BACKUP")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 重要なファイルのみバックアップ
                important_patterns = ["*.py", "*.js", "*.vue", "*.md", "*.json"]
                protected_dirs = [".git", "node_modules", "__pycache__", "logs"]
                
                for pattern in important_patterns:
                    for file_path in Path(".").rglob(pattern):
                        # 除外対象をスキップ
                        if any(protected in str(file_path) for protected in protected_dirs):
                            continue
                        
                        try:
                            zf.write(file_path, file_path.relative_to(Path(".")))
                        except:
                            pass
            
            # バックアップ情報を記録
            backup_info = BackupInfo(
                timestamp=format_jst_datetime(),
                backup_type=backup_type,
                file_path=str(backup_path),
                size_mb=backup_path.stat().st_size / (1024 * 1024),
                description=description
            )
            
            self._record_backup_info(backup_info)
            logger.info(f"バックアップ完了: {backup_name} ({backup_info.size_mb:.2f}MB)", "BACKUP")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"バックアップ作成エラー: {e}", "BACKUP")
            return None
    
    def create_error_backup(self, error_description: str = "") -> Optional[Path]:
        """エラー時の自動バックアップ"""
        return self.create_backup("error", f"エラー復旧用: {error_description}")
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """バックアップから復元"""
        logger.info(f"バックアップから復元中: {backup_path.name}", "RESTORE")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extractall(".")
            
            logger.info("復元完了", "RESTORE")
            return True
            
        except Exception as e:
            logger.error(f"復元エラー: {e}", "RESTORE")
            return False
    
    def get_disk_usage_report(self) -> Dict:
        """ディスク使用量レポートを取得"""
        total_size = 0
        file_count = 0
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        
        return {
            "total_size_mb": size_mb,
            "file_count": file_count,
            "timestamp": format_jst_datetime()
        }
    
    def _cleanup_old_logs(self):
        """古いログファイルを削除"""
        log_dir = self.base_path / "logs"
        if not log_dir.exists():
            return
        
        cutoff_date = get_jst_now() - timedelta(days=7)
        deleted_count = 0
        
        for log_file in log_dir.rglob("*.log"):
            try:
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except:
                pass
        
        if deleted_count > 0:
            logger.info(f"古いログファイルを{deleted_count}件削除", "CLEANUP")
    
    def _cleanup_old_cache(self):
        """古いキャッシュファイルを削除"""
        cache_dir = self.base_path / "cache"
        if not cache_dir.exists():
            return
        
        cutoff_date = get_jst_now() - timedelta(days=7)
        deleted_count = 0
        
        for cache_file in cache_dir.rglob("*.pkl"):
            try:
                file_date = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_date < cutoff_date:
                    cache_file.unlink()
                    deleted_count += 1
            except:
                pass
        
        if deleted_count > 0:
            logger.info(f"古いキャッシュファイルを{deleted_count}件削除", "CLEANUP")
    
    def _cleanup_old_backups(self):
        """古いバックアップを削除"""
        cutoff_date = get_jst_now() - timedelta(days=self.max_backup_age_days)
        backups = sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        
        # 日数制限による削除
        for backup_file in backups:
            try:
                file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_date < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"古いバックアップ削除: {backup_file.name}", "CLEANUP")
            except:
                pass
        
        # 件数制限による削除
        remaining_backups = sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        if len(remaining_backups) > self.max_backup_count:
            for old_backup in remaining_backups[:-self.max_backup_count]:
                try:
                    old_backup.unlink()
                    logger.info(f"件数制限でバックアップ削除: {old_backup.name}", "CLEANUP")
                except:
                    pass
    
    def _get_folder_size(self, folder: Path) -> int:
        """フォルダサイズを取得"""
        total = 0
        if folder.exists():
            for entry in folder.rglob("*"):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except:
                        pass
        return total
    
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
        
        # 最新20件のみ保持
        infos = infos[-20:]
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(infos, f, indent=2, ensure_ascii=False)


# シングルトンインスタンス
cleaner = UnifiedCleanupManager()