#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コアシステム - 統合・単純化されたシステム
YAGNI: 必要な機能のみ
DRY: 重複コード排除
KISS: シンプルな実装
TDD: テスト駆動開発
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import shutil
from datetime import datetime, timedelta

# シンプルなパス設定（DRY原則）
def setup_paths():
    """統一パス設定"""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if current.name == '.claude':
            claude_root = current
            break
        if (current / '.claude').exists():
            claude_root = current / '.claude'
            break
        current = current.parent
    else:
        claude_root = Path(__file__).resolve().parent.parent.parent
    
    sys.path.insert(0, str(claude_root / "system"))
    return claude_root

CLAUDE_ROOT = setup_paths()


class Status(Enum):
    """統一ステータス（KISS原則）"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Result:
    """統一結果クラス（KISS原則）"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class CoreSystem:
    """
    統合コアシステム
    YAGNI: 必要な機能のみ実装
    KISS: シンプルな単一クラス
    """
    
    def __init__(self):
        """初期化"""
        self.root = CLAUDE_ROOT
        self.temp_dir = self.root / "temp"
        self.reports_dir = self.root / "reports"
        self.config_file = self.root / "config" / "system_config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """設定読み込み（KISS原則）"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "temp_max_age_hours": 24,
            "auto_cleanup": True,
            "test_coverage_target": 100.0
        }
    
    def organize_files(self) -> Result:
        """
        ファイル整理（シンプル実装）
        """
        moved_count = 0
        
        # プロジェクトルートの整理
        project_root = self.root.parent
        allowed_root = {"README.md", "CLAUDE.md", ".gitignore", ".mcp.json"}
        
        for file in project_root.glob("*"):
            if file.is_file() and file.name not in allowed_root:
                # レポートは reports フォルダへ
                if "report" in file.name.lower():
                    dest = self.reports_dir / file.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), str(dest))
                    moved_count += 1
        
        return Result(True, f"Organized {moved_count} files")
    
    def cleanup_temp(self) -> Result:
        """
        一時ファイルクリーンアップ（シンプル実装）
        """
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            return Result(True, "No temp files to clean")
        
        deleted_count = 0
        max_age = timedelta(hours=self.config.get("temp_max_age_hours", 24))
        current_time = datetime.now()
        
        for file in self.temp_dir.glob("**/*"):
            if file.is_file():
                file_age = datetime.fromtimestamp(file.stat().st_mtime)
                if current_time - file_age > max_age:
                    file.unlink()
                    deleted_count += 1
        
        # キャッシュディレクトリの削除
        for pattern in ["__pycache__", ".pytest_cache", ".benchmarks"]:
            for path in self.root.parent.rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    deleted_count += 1
        
        return Result(True, f"Cleaned {deleted_count} items")
    
    def run_tests(self) -> Result:
        """
        テスト実行（シンプル実装）
        """
        import subprocess
        
        test_dir = self.root / "project" / "tests"
        if not test_dir.exists():
            return Result(False, "Test directory not found")
        
        try:
            # pytestコマンド実行
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_dir),
                "--cov=system/core",
                "--cov-report=term-missing",
                "-v"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            message = "Tests passed" if success else "Tests failed"
            
            # カバレッジ情報を抽出
            coverage_info = {}
            if "TOTAL" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "TOTAL" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            coverage_info["coverage"] = parts[-1]
            
            return Result(success, message, coverage_info)
            
        except Exception as e:
            return Result(False, f"Test execution error: {e}")
    
    def check_code_quality(self) -> Result:
        """
        コード品質チェック（シンプル実装）
        """
        issues = []
        
        # Pythonファイルをチェック
        for py_file in (self.root / "system" / "core").glob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 長い行をチェック（KISS原則）
            for i, line in enumerate(lines, 1):
                if len(line.rstrip()) > 120:
                    issues.append(f"{py_file.name}:{i} - Line too long")
            
            # 深いネストをチェック
            for i, line in enumerate(lines, 1):
                indent = len(line) - len(line.lstrip())
                if indent > 24:  # 6レベル以上のインデント
                    issues.append(f"{py_file.name}:{i} - Deep nesting")
        
        if issues:
            return Result(False, f"Found {len(issues)} issues", {"issues": issues[:10]})
        return Result(True, "Code quality check passed")
    
    def get_status(self) -> Dict[str, Any]:
        """
        システムステータス取得（シンプル実装）
        """
        return {
            "root": str(self.root),
            "temp_files": len(list(self.temp_dir.glob("**/*"))) if self.temp_dir.exists() else 0,
            "config": self.config,
            "folders": {
                "system": (self.root / "system").exists(),
                "project": (self.root / "project").exists(),
                "reports": self.reports_dir.exists(),
                "temp": self.temp_dir.exists(),
            }
        }
    
    def execute(self, command: str, **kwargs) -> Result:
        """
        コマンド実行（シンプルインターフェース）
        """
        commands = {
            "organize": self.organize_files,
            "cleanup": self.cleanup_temp,
            "test": self.run_tests,
            "check": self.check_code_quality,
            "status": lambda: Result(True, "OK", self.get_status()),
        }
        
        if command in commands:
            return commands[command]()
        return Result(False, f"Unknown command: {command}")


def main():
    """メインエントリーポイント"""
    system = CoreSystem()
    
    # コマンドライン引数処理（シンプル）
    import sys
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    result = system.execute(command)
    print(f"{command}: {result.message}")
    
    if result.data:
        print(json.dumps(result.data, indent=2))
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())