#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通基盤モジュール - DRY原則適用
全モジュールで使用される共通のインポート、列挙型、基底クラスを定義

TDD原則: この基盤モジュールは既存機能を統合するためのリファクタリング
YAGNI: 現在使用されている機能のみを統合
DRY: 重複する定義を一箇所にまとめる
KISS: シンプルな構造で必要最小限の抽象化
"""

# === 共通インポート ===
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import sys
import time
import logging
from abc import ABC, abstractmethod

# === 共通列挙型 ===

class TaskStatus(Enum):
    """タスク状態の統一定義 - 全モジュールで共通使用"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class ErrorSeverity(Enum):
    """エラー重要度の統一定義"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CacheStrategy(Enum):
    """キャッシュ戦略の統一定義"""
    MEMORY_ONLY = "memory_only"
    DISK_ONLY = "disk_only" 
    MEMORY_AND_DISK = "memory_and_disk"
    LRU = "lru"
    FIFO = "fifo"


class LogLevel(Enum):
    """ログレベルの統一定義"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# === 共通データ構造 ===

@dataclass
class BaseResult:
    """基本結果クラス - 全操作結果の基底クラス"""
    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration: Optional[float] = None


@dataclass
class FileInfo:
    """ファイル情報の統一構造"""
    path: Path
    size: int
    modified_time: datetime
    hash_value: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheEntry:
    """キャッシュエントリの統一構造"""
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: Optional[int] = None
    access_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TestExecutionResult:
    """テスト実行結果の統一構造 (TestResult名を避けてpytest警告回避)"""
    test_name: str
    status: TaskStatus
    duration: float
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    coverage: Optional[float] = None


# === 共通基底クラス ===

class BaseManager(ABC):
    """管理クラスの基底クラス - 共通インターフェース定義"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.created_at = datetime.now()
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> BaseResult:
        """初期化処理"""
        pass
    
    @abstractmethod
    def cleanup(self) -> BaseResult:
        """クリーンアップ処理"""
        pass
    
    def is_initialized(self) -> bool:
        """初期化状態確認"""
        return self._initialized
    
    def get_status(self) -> Dict[str, Any]:
        """状態取得"""
        return {
            "name": self.name,
            "initialized": self._initialized,
            "created_at": self.created_at.isoformat(),
            "config": self.config
        }


class BaseCache(BaseManager):
    """キャッシュの基底クラス"""
    
    def __init__(self, name: str, strategy: CacheStrategy, max_size: int = 1000):
        super().__init__(name, {"strategy": strategy, "max_size": max_size})
        self.strategy = strategy
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_operations": 0
        }
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """キャッシュから値を取得"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """キャッシュに値を設定"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """キャッシュから値を削除"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計取得"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0.0
        
        return {
            **self._stats,
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self._cache),
            "max_size": self.max_size,
            "strategy": self.strategy.value
        }
    
    def clear_stats(self):
        """統計クリア"""
        for key in self._stats:
            self._stats[key] = 0


# === ユーティリティ関数 ===

def create_result(success: bool, message: str = "", data: Optional[Dict] = None, 
                 duration: Optional[float] = None) -> BaseResult:
    """結果オブジェクト作成のヘルパー関数"""
    return BaseResult(
        success=success,
        message=message,
        data=data,
        duration=duration
    )


def safe_json_serialize(obj: Any) -> Optional[str]:
    """安全なJSON変換 - エラーハンドリング付き"""
    try:
        if isinstance(obj, (datetime, Path)):
            return str(obj)
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        return f"JSON serialization error: {e}"


def calculate_hash(data: Union[str, bytes, Path]) -> str:
    """統一ハッシュ計算"""
    import hashlib
    
    if isinstance(data, Path):
        if not data.exists():
            return ""
        try:
            with data.open('rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception:
            return ""
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()


def format_duration(seconds: float) -> str:
    """実行時間の統一フォーマット"""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def ensure_directory(path: Path) -> bool:
    """ディレクトリ存在確認・作成"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def safe_delete_file(file_path: Path) -> bool:
    """安全なファイル削除"""
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except Exception:
        return False


# === 共通定数 ===

DEFAULT_CACHE_TTL = 3600  # 1時間
DEFAULT_MAX_CACHE_SIZE = 1000
DEFAULT_TIMEOUT = 30  # 30秒

# ファイル除外パターン
EXCLUDE_PATTERNS = {
    '.git', '.gitignore', 
    'node_modules', '__pycache__', 
    '.pytest_cache', 'htmlcov',
    '.coverage', '*.pyc', '*.pyo',
    '.DS_Store', 'Thumbs.db'
}

# サポートされるファイル拡張子
SUPPORTED_EXTENSIONS = {'.py', '.json', '.yaml', '.yml', '.txt', '.md'}


# === モジュールメタデータ ===
__version__ = "1.0.0"
__author__ = "Alex Team"
__description__ = "Common base module for DRY principle compliance"


if __name__ == "__main__":
    # 基本テスト実行
    print(f"Common Base Module v{__version__}")
    print(f"Available enums: {[e.__name__ for e in [TaskStatus, ErrorSeverity, CacheStrategy, LogLevel]]}")
    print(f"Available dataclasses: {[BaseResult, FileInfo, CacheEntry, TestExecutionResult]}")
    print("Module loaded successfully!")