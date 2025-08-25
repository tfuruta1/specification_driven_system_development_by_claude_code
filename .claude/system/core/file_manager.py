#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル管理システム - プロジェクト構造の自動管理
一時ファイルと永続ファイルの分離、自動クリーンアップ機能
"""

# Auto-generated import setup
import sys
from pathlib import Path
import shutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum

# Setup import paths
current_file = Path(__file__).resolve()
claude_root = None
current = current_file.parent
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    if (current / '.claude').exists():
        claude_root = current / '.claude'
        break
    current = current.parent

if claude_root:
    sys.path.insert(0, str(claude_root / "system"))
    sys.path.insert(0, str(claude_root))

try:
    from core.common_base import BaseManager, BaseResult, create_result
    from core.logger import get_logger
    from core.path_utils import get_claude_root
except ImportError:
    from common_base import BaseManager, BaseResult, create_result
    from logger import get_logger
    from path_utils import get_claude_root

logger = get_logger(__name__)


class FileType(Enum):
    """ファイルタイプ分類"""
    TEMP = "temporary"          # 一時ファイル
    REPORT = "report"           # レポート（永続）
    CONFIG = "config"           # 設定ファイル（永続）
    SOURCE = "source"           # ソースコード（永続）
    TEST = "test"              # テストファイル（永続）
    DOC = "documentation"       # ドキュメント（永続）
    ARCHIVE = "archive"         # アーカイブ（永続）


class FolderStructure:
    """プロジェクトフォルダ構造定義"""
    
    # .claude内の標準フォルダ構造
    STRUCTURE = {
        "system": {
            "core": "コアシステムモジュール",
            "templates": "テンプレートファイル",
        },
        "project": {
            "tests": "プロジェクトテスト",
            "docs": "プロジェクトドキュメント",
        },
        "reports": {
            "coverage": "カバレッジレポート",
            "diagnosis": "診断レポート",
            "refactoring": "リファクタリングレポート",
        },
        "temp": "一時ファイル（自動削除対象）",
        "archive": {
            "old_modules": "古いモジュール",
            "backups": "バックアップ",
        },
        "config": "設定ファイル",
    }
    
    # ルートディレクトリに許可されるファイル
    ROOT_ALLOWED = {
        "README.md",
        "CLAUDE.md",
        ".gitignore",
        ".mcp.json",
    }
    
    # 一時ファイルのパターン
    TEMP_PATTERNS = [
        "*.tmp",
        "*.temp",
        "*.log",
        "*.cache",
        ".coverage",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".benchmarks",
    ]


class FileManager(BaseManager):
    """
    ファイル管理システム
    プロジェクト構造の維持と自動クリーンアップ
    """
    
    def __init__(self):
        """初期化"""
        super().__init__("FileManager")
        self.root_path = get_claude_root()
        self.project_root = self.root_path.parent
        self.temp_dir = self.root_path / "temp"
        self.reports_dir = self.root_path / "reports"
        self.archive_dir = self.root_path / "archive"
        
    def initialize(self) -> BaseResult:
        """システム初期化とフォルダ構造作成"""
        try:
            logger.info("Initializing File Manager")
            
            # 標準フォルダ構造を作成
            self._create_folder_structure()
            
            return create_result(True, "File Manager initialized")
        except Exception as e:
            return create_result(False, f"Initialization failed: {e}")
    
    def cleanup(self) -> BaseResult:
        """クリーンアップ"""
        try:
            # 一時ファイルの削除
            self.cleanup_temp_files()
            
            return create_result(True, "Cleanup completed")
        except Exception as e:
            return create_result(False, f"Cleanup failed: {e}")
    
    def _create_folder_structure(self):
        """標準フォルダ構造を作成"""
        def create_structure(base_path: Path, structure: dict):
            for name, value in structure.items():
                path = base_path / name
                if isinstance(value, dict):
                    path.mkdir(parents=True, exist_ok=True)
                    create_structure(path, value)
                else:
                    # 説明文の場合はフォルダを作成
                    path.mkdir(parents=True, exist_ok=True)
        
        create_structure(self.root_path, FolderStructure.STRUCTURE)
        logger.info("Folder structure created/verified")
    
    def organize_files(self) -> BaseResult:
        """
        プロジェクト内のファイルを整理
        散らばったファイルを適切な場所に移動
        """
        try:
            moved_files = []
            
            # プロジェクトルートのファイルを整理
            for file_path in self.project_root.glob("*"):
                if file_path.is_file():
                    # 許可されたファイル以外を移動
                    if file_path.name not in FolderStructure.ROOT_ALLOWED:
                        new_location = self._determine_file_location(file_path)
                        if new_location and new_location != file_path:
                            self._move_file(file_path, new_location)
                            moved_files.append({
                                "from": str(file_path),
                                "to": str(new_location)
                            })
            
            # .claude直下のファイルを整理
            for file_path in self.root_path.glob("*"):
                if file_path.is_file():
                    file_type = self._classify_file(file_path)
                    if file_type == FileType.REPORT:
                        # レポートをreportsフォルダに移動
                        category = self._get_report_category(file_path.name)
                        new_location = self.reports_dir / category / file_path.name
                        new_location.parent.mkdir(parents=True, exist_ok=True)
                        self._move_file(file_path, new_location)
                        moved_files.append({
                            "from": str(file_path),
                            "to": str(new_location)
                        })
            
            return create_result(
                True,
                f"Organized {len(moved_files)} files",
                {"moved_files": moved_files}
            )
            
        except Exception as e:
            logger.error(f"File organization error: {e}")
            return create_result(False, f"Organization failed: {e}")
    
    def _determine_file_location(self, file_path: Path) -> Optional[Path]:
        """ファイルの適切な配置場所を決定"""
        file_name = file_path.name.lower()
        
        # レポート系
        if any(word in file_name for word in ["report", "coverage", "diagnosis"]):
            category = self._get_report_category(file_name)
            return self.reports_dir / category / file_path.name
        
        # ドキュメント系
        if file_name.endswith(".md") and file_name != "README.md":
            return self.root_path / "project" / "docs" / file_path.name
        
        # 一時ファイル
        if any(file_path.match(pattern) for pattern in FolderStructure.TEMP_PATTERNS):
            return self.temp_dir / file_path.name
        
        return None
    
    def _get_report_category(self, file_name: str) -> str:
        """レポートのカテゴリを判定"""
        file_name = file_name.lower()
        
        if "coverage" in file_name:
            return "coverage"
        elif "diagnosis" in file_name or "diagnostic" in file_name:
            return "diagnosis"
        elif "refactor" in file_name:
            return "refactoring"
        else:
            return "general"
    
    def _classify_file(self, file_path: Path) -> FileType:
        """ファイルタイプを分類"""
        file_name = file_path.name.lower()
        
        # 一時ファイル判定
        if any(file_path.match(pattern) for pattern in FolderStructure.TEMP_PATTERNS):
            return FileType.TEMP
        
        # レポート判定
        if "report" in file_name or "diagnosis" in file_name:
            return FileType.REPORT
        
        # 設定ファイル判定
        if file_name.endswith((".json", ".yml", ".yaml", ".ini")):
            return FileType.CONFIG
        
        # テストファイル判定
        if file_name.startswith("test_") or "_test" in file_name:
            return FileType.TEST
        
        # ドキュメント判定
        if file_name.endswith(".md"):
            return FileType.DOC
        
        # ソースコード判定
        if file_name.endswith(".py"):
            return FileType.SOURCE
        
        return FileType.TEMP
    
    def _move_file(self, source: Path, destination: Path):
        """ファイルを移動"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            logger.info(f"Moved: {source.name} -> {destination}")
        except Exception as e:
            logger.error(f"Failed to move {source}: {e}")
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> BaseResult:
        """
        一時ファイルをクリーンアップ
        
        Args:
            max_age_hours: この時間以上古いファイルを削除
        """
        try:
            deleted_files = []
            current_time = datetime.now()
            max_age = timedelta(hours=max_age_hours)
            
            # tempフォルダ内のファイルをチェック
            if self.temp_dir.exists():
                for file_path in self.temp_dir.glob("**/*"):
                    if file_path.is_file():
                        # ファイルの更新時刻をチェック
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if current_time - file_time > max_age:
                            file_path.unlink()
                            deleted_files.append(str(file_path))
                            logger.info(f"Deleted temp file: {file_path.name}")
            
            # プロジェクト全体の一時ファイルパターンをクリーンアップ
            for pattern in [".pytest_cache", "__pycache__", ".benchmarks"]:
                for path in self.project_root.rglob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path)
                        deleted_files.append(str(path))
                        logger.info(f"Deleted temp directory: {path}")
            
            return create_result(
                True,
                f"Cleaned up {len(deleted_files)} temp files/directories",
                {"deleted": deleted_files}
            )
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return create_result(False, f"Cleanup failed: {e}")
    
    def enforce_structure(self) -> BaseResult:
        """
        フォルダ構造を強制
        新しいファイルが作成された時に適切な場所に配置されているか確認
        """
        try:
            violations = []
            
            # プロジェクトルートをチェック
            for item in self.project_root.glob("*"):
                if item.is_file() and item.name not in FolderStructure.ROOT_ALLOWED:
                    violations.append({
                        "file": str(item),
                        "reason": "Unauthorized file in project root",
                        "suggested_location": str(self._determine_file_location(item))
                    })
            
            # .claude直下をチェック
            for item in self.root_path.glob("*"):
                if item.is_file():
                    # 一部の設定ファイルは許可
                    allowed_root_files = {".pending_reviews", ".review_status", 
                                         "lefthook.yml", "mcp.json"}
                    if item.name not in allowed_root_files:
                        violations.append({
                            "file": str(item),
                            "reason": "File should be in subdirectory",
                            "suggested_location": str(self._determine_file_location(item))
                        })
            
            if violations:
                return create_result(
                    False,
                    f"Found {len(violations)} structure violations",
                    {"violations": violations}
                )
            else:
                return create_result(True, "Folder structure is compliant")
                
        except Exception as e:
            logger.error(f"Structure enforcement error: {e}")
            return create_result(False, f"Enforcement failed: {e}")
    
    def get_status(self) -> Dict[str, any]:
        """
        ファイル管理システムのステータスを取得
        """
        status = {
            "root_path": str(self.root_path),
            "project_root": str(self.project_root),
            "folder_structure": {},
            "temp_files_count": 0,
            "violations": []
        }
        
        # フォルダ構造の確認
        for folder_name in FolderStructure.STRUCTURE.keys():
            folder_path = self.root_path / folder_name
            status["folder_structure"][folder_name] = folder_path.exists()
        
        # 一時ファイルのカウント
        if self.temp_dir.exists():
            status["temp_files_count"] = len(list(self.temp_dir.glob("**/*")))
        
        # 構造違反のチェック
        result = self.enforce_structure()
        if not result.success and result.data:
            status["violations"] = result.data.get("violations", [])
        
        return status


def main():
    """メインエントリーポイント"""
    manager = FileManager()
    
    # 初期化
    result = manager.initialize()
    print(f"Initialization: {result.message}")
    
    # ファイル整理
    result = manager.organize_files()
    print(f"Organization: {result.message}")
    if result.data and result.data.get("moved_files"):
        for move in result.data["moved_files"]:
            print(f"  Moved: {Path(move['from']).name}")
    
    # 構造チェック
    result = manager.enforce_structure()
    print(f"Structure check: {result.message}")
    
    # 一時ファイルクリーンアップ
    result = manager.cleanup_temp_files()
    print(f"Cleanup: {result.message}")
    
    # ステータス表示
    status = manager.get_status()
    print(f"\nStatus:")
    print(f"  Temp files: {status['temp_files_count']}")
    print(f"  Violations: {len(status['violations'])}")


if __name__ == "__main__":
    main()