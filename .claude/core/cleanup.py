#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合クリーンアップシステム
auto_cleanup_manager.py と cleanup_system.py を統合
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
from logger import logger


class UnifiedCleanupManager:
    """統合クリーンアップマネージャー（KISS原則）"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.temp_extensions = ['.tmp', '.bak', '.log~', '.swp']
        self.temp_dirs = ['__pycache__', '.pytest_cache', 'node_modules']
    
    def cleanup_project(self) -> Dict:
        """プロジェクト終了時の完全クリーンアップ"""
        logger.info("プロジェクトクリーンアップ開始", "CLEANUP")
        
        results = {
            "deleted_files": [],
            "deleted_dirs": [],
            "errors": []
        }
        
        # 一時ファイル削除
        for ext in self.temp_extensions:
            for file in self.base_path.rglob(f"*{ext}"):
                try:
                    file.unlink()
                    results["deleted_files"].append(str(file))
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
            f"ディレクトリ{len(results['deleted_dirs'])}個削除",
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


# シングルトンインスタンス
cleaner = UnifiedCleanupManager()