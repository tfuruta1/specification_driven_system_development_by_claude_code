#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - SYSTEM
auto_cleanup_manager.py SYSTEMYAGNISYSTEM
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from logger import logger
from jst_utils import format_jst_datetime, get_filename_timestamp, get_jst_now


@dataclass
class BackupInfo:
    """ERROR"""
    timestamp: str
    backup_type: str  # checkpoint, error, manual
    file_path: str
    size_mb: float
    description: str


class UnifiedCleanupManager:
    """KISS + """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.temp_extensions = ['.tmp', '.bak', '.log~', '.swp']
        self.temp_dirs = ['__pycache__', '.pytest_cache', 'node_modules']
        
        # TEST
        self.backup_dir = self.base_path / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backup_age_days = 7
        self.max_backup_count = 5
    
    def cleanup_project(self) -> Dict:
        """REPORT"""
        logger.info("REPORT", "CLEANUP")
        
        results = {
            "deleted_files": [],
            "deleted_dirs": [],
            "errors": [],
            "space_freed_mb": 0
        }
        
        initial_size = self._get_folder_size(self.base_path / "logs")
        
        # 
        for ext in self.temp_extensions:
            for file in self.base_path.rglob(f"*{ext}"):
                try:
                    file_size = file.stat().st_size
                    file.unlink()
                    results["deleted_files"].append(str(file))
                    results["space_freed_mb"] += file_size / (1024 * 1024)
                    logger.debug(f"ERROR: {file}", "CLEANUP")
                except Exception as e:
                    results["errors"].append(f"Failed to delete {file}: {e}")
        
        # ERROR
        for dir_name in self.temp_dirs:
            for dir_path in self.base_path.rglob(dir_name):
                if dir_path.is_dir():
                    try:
                        shutil.rmtree(dir_path)
                        results["deleted_dirs"].append(str(dir_path))
                        logger.debug(f"ERROR: {dir_path}", "CLEANUP")
                    except Exception as e:
                        results["errors"].append(f"Failed to delete {dir_path}: {e}")
        
        # ERROR
        self._cleanup_old_logs()
        
        # 
        self._cleanup_old_cache()
        
        # 
        self._cleanup_old_backups()
        
        # 
        for dir_path in sorted(self.base_path.rglob("*"), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    results["deleted_dirs"].append(str(dir_path))
                except:
                    pass  # SUCCESS
        
        logger.info(
            f"SUCCESS: SUCCESS{len(results['deleted_files'])}REPORT"
            f"REPORT{len(results['deleted_dirs'])}REPORT"
            f"{results['space_freed_mb']:.2f}MBTASK",
            "CLEANUP"
        )
        
        return results
    
    def cleanup_workspace(self) -> Dict:
        """TASK"""
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
        """"""
        timestamp = get_filename_timestamp()
        backup_name = f"{backup_type}_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        logger.info(f": {backup_name}", "BACKUP")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 
                important_patterns = ["*.py", "*.js", "*.vue", "*.md", "*.json"]
                protected_dirs = [".git", "node_modules", "__pycache__", "logs"]
                
                for pattern in important_patterns:
                    for file_path in Path(".").rglob(pattern):
                        # 
                        if any(protected in str(file_path) for protected in protected_dirs):
                            continue
                        
                        try:
                            zf.write(file_path, file_path.relative_to(Path(".")))
                        except:
                            pass
            
            # SUCCESS
            backup_info = BackupInfo(
                timestamp=format_jst_datetime(),
                backup_type=backup_type,
                file_path=str(backup_path),
                size_mb=backup_path.stat().st_size / (1024 * 1024),
                description=description
            )
            
            self._record_backup_info(backup_info)
            logger.info(f": {backup_name} ({backup_info.size_mb:.2f}MB)", "BACKUP")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "BACKUP")
            return None
    
    def create_error_backup(self, error_description: str = "") -> Optional[Path]:
        """ERROR"""
        return self.create_backup("error", f"ERROR: {error_description}")
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """ERROR"""
        logger.info(f": {backup_path.name}", "RESTORE")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extractall(".")
            
            logger.info("ERROR", "RESTORE")
            return True
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "RESTORE")
            return False
    
    def get_disk_usage_report(self) -> Dict:
        """REPORT"""
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
        """"""
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
            logger.info(f"SUCCESS{deleted_count}SUCCESS", "CLEANUP")
    
    def _cleanup_old_cache(self):
        """"""
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
            logger.info(f"SUCCESS{deleted_count}SUCCESS", "CLEANUP")
    
    def _cleanup_old_backups(self):
        """"""
        cutoff_date = get_jst_now() - timedelta(days=self.max_backup_age_days)
        backups = sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        
        # 
        for backup_file in backups:
            try:
                file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_date < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"SUCCESS: {backup_file.name}", "CLEANUP")
            except:
                pass
        
        # SUCCESS
        remaining_backups = sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        if len(remaining_backups) > self.max_backup_count:
            for old_backup in remaining_backups[:-self.max_backup_count]:
                try:
                    old_backup.unlink()
                    logger.info(f"SUCCESS: {old_backup.name}", "CLEANUP")
                except:
                    pass
    
    def _get_folder_size(self, folder: Path) -> int:
        """SUCCESS"""
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
        """"""
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
        
        # 20
        infos = infos[-20:]
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(infos, f, indent=2, ensure_ascii=False)


# 
cleaner = UnifiedCleanupManager()