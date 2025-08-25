#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通基盤モジュールのテスト - TDD原則に従った100%カバレッジ実現
"""

import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import tempfile
import json
from datetime import datetime, timedelta

# Setup relative imports from .claude folder
import sys
current_file = Path(__file__).resolve()
current = current_file.parent

# Navigate up to find .claude folder
claude_root = None
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    if current.parent == current:
        break
    current = current.parent

if claude_root is None:
    current = current_file.parent
    for _ in range(10):
        if (current / '.claude').exists() and (current / '.claude' / 'system').exists():
            claude_root = current / '.claude'
            break
        if current.parent == current:
            break
        current = current.parent

if claude_root is None:
    claude_root = current_file.parent.parent.parent

system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

from core.common_base import (
    TaskStatus, ErrorSeverity, CacheStrategy, LogLevel,
    BaseResult, FileInfo, CacheEntry, TestExecutionResult,
    BaseManager, BaseCache,
    create_result, safe_json_serialize, calculate_hash,
    format_duration, ensure_directory, safe_delete_file,
    DEFAULT_CACHE_TTL, EXCLUDE_PATTERNS
)


class TestEnums(unittest.TestCase):
    """列挙型のテスト"""
    
    def test_task_status_enum(self):
        """TaskStatus列挙型のテスト"""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.FAILED.value, "failed")
        self.assertEqual(TaskStatus.NEEDS_REVIEW.value, "needs_review")
        
        # 全ての値が異なることを確認
        values = [status.value for status in TaskStatus]
        self.assertEqual(len(values), len(set(values)))
    
    def test_error_severity_enum(self):
        """ErrorSeverity列挙型のテスト"""
        self.assertEqual(ErrorSeverity.CRITICAL.value, "critical")
        self.assertEqual(ErrorSeverity.HIGH.value, "high")
        self.assertEqual(ErrorSeverity.MEDIUM.value, "medium")
        self.assertEqual(ErrorSeverity.LOW.value, "low")
        self.assertEqual(ErrorSeverity.INFO.value, "info")
    
    def test_cache_strategy_enum(self):
        """CacheStrategy列挙型のテスト"""
        self.assertEqual(CacheStrategy.MEMORY_ONLY.value, "memory_only")
        self.assertEqual(CacheStrategy.DISK_ONLY.value, "disk_only")
        self.assertEqual(CacheStrategy.MEMORY_AND_DISK.value, "memory_and_disk")
        self.assertEqual(CacheStrategy.LRU.value, "lru")
        self.assertEqual(CacheStrategy.FIFO.value, "fifo")
    
    def test_log_level_enum(self):
        """LogLevel列挙型のテスト"""
        self.assertEqual(LogLevel.DEBUG.value, "debug")
        self.assertEqual(LogLevel.INFO.value, "info")
        self.assertEqual(LogLevel.WARNING.value, "warning")
        self.assertEqual(LogLevel.ERROR.value, "error")
        self.assertEqual(LogLevel.CRITICAL.value, "critical")


class TestDataClasses(unittest.TestCase):
    """データクラスのテスト"""
    
    def test_base_result(self):
        """BaseResultデータクラスのテスト"""
        # 基本作成
        result = BaseResult(success=True, message="Test message")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Test message")
        self.assertIsNone(result.data)
        self.assertIsInstance(result.timestamp, datetime)
        self.assertIsNone(result.duration)
        
        # 全パラメータ指定
        test_data = {"key": "value"}
        result = BaseResult(
            success=False,
            message="Error occurred",
            data=test_data,
            duration=1.5
        )
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Error occurred")
        self.assertEqual(result.data, test_data)
        self.assertEqual(result.duration, 1.5)
    
    def test_file_info(self):
        """FileInfoデータクラスのテスト"""
        path = Path("/test/file.txt")
        modified_time = datetime.now()
        
        file_info = FileInfo(path=path, size=1024, modified_time=modified_time)
        self.assertEqual(file_info.path, path)
        self.assertEqual(file_info.size, 1024)
        self.assertEqual(file_info.modified_time, modified_time)
        self.assertIsNone(file_info.hash_value)
        self.assertIsNone(file_info.metadata)
        
        # 全パラメータ指定
        metadata = {"encoding": "utf-8"}
        file_info = FileInfo(
            path=path,
            size=2048,
            modified_time=modified_time,
            hash_value="abc123",
            metadata=metadata
        )
        self.assertEqual(file_info.hash_value, "abc123")
        self.assertEqual(file_info.metadata, metadata)
    
    def test_cache_entry(self):
        """CacheEntryデータクラスのテスト"""
        entry = CacheEntry(key="test_key", value="test_value")
        self.assertEqual(entry.key, "test_key")
        self.assertEqual(entry.value, "test_value")
        self.assertIsInstance(entry.timestamp, datetime)
        self.assertIsNone(entry.ttl)
        self.assertEqual(entry.access_count, 0)
        self.assertIsNone(entry.metadata)
        
        # 全パラメータ指定
        metadata = {"source": "api"}
        entry = CacheEntry(
            key="api_key",
            value={"data": "value"},
            ttl=3600,
            metadata=metadata
        )
        entry.access_count = 5
        self.assertEqual(entry.ttl, 3600)
        self.assertEqual(entry.access_count, 5)
        self.assertEqual(entry.metadata, metadata)
    
    def test_test_execution_result(self):
        """TestExecutionResultデータクラスのテスト"""
        result = TestExecutionResult(
            test_name="test_function",
            status=TaskStatus.COMPLETED,
            duration=0.5
        )
        self.assertEqual(result.test_name, "test_function")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.duration, 0.5)
        self.assertEqual(result.message, "")
        self.assertIsNone(result.details)
        self.assertIsNone(result.coverage)


class TestBaseManager(unittest.TestCase):
    """BaseManager抽象クラスのテスト"""
    
    def setUp(self):
        """テスト用のBaseManager実装を作成"""
        class TestManager(BaseManager):
            def initialize(self):
                self._initialized = True
                return create_result(True, "Initialized")
            
            def cleanup(self):
                self._initialized = False
                return create_result(True, "Cleaned up")
        
        self.TestManager = TestManager
    
    def test_base_manager_creation(self):
        """BaseManager作成のテスト"""
        manager = self.TestManager("test_manager")
        self.assertEqual(manager.name, "test_manager")
        self.assertEqual(manager.config, {})
        self.assertFalse(manager.is_initialized())
        self.assertIsInstance(manager.created_at, datetime)
    
    def test_base_manager_with_config(self):
        """設定付きBaseManager作成のテスト"""
        config = {"setting1": "value1", "setting2": 42}
        manager = self.TestManager("test_manager", config)
        self.assertEqual(manager.config, config)
    
    def test_base_manager_initialization(self):
        """BaseManager初期化のテスト"""
        manager = self.TestManager("test_manager")
        
        # 初期化前
        self.assertFalse(manager.is_initialized())
        
        # 初期化実行
        result = manager.initialize()
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Initialized")
        self.assertTrue(manager.is_initialized())
    
    def test_base_manager_cleanup(self):
        """BaseManagerクリーンアップのテスト"""
        manager = self.TestManager("test_manager")
        manager.initialize()
        self.assertTrue(manager.is_initialized())
        
        # クリーンアップ実行
        result = manager.cleanup()
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Cleaned up")
        self.assertFalse(manager.is_initialized())
    
    def test_base_manager_status(self):
        """BaseManager状態取得のテスト"""
        config = {"test": True}
        manager = self.TestManager("test_manager", config)
        
        status = manager.get_status()
        self.assertEqual(status["name"], "test_manager")
        self.assertFalse(status["initialized"])
        self.assertEqual(status["config"], config)
        self.assertIn("created_at", status)


class TestBaseCache(unittest.TestCase):
    """BaseCache抽象クラスのテスト"""
    
    def setUp(self):
        """テスト用のBaseCache実装を作成"""
        class TestCache(BaseCache):
            def initialize(self):
                self._initialized = True
                return create_result(True, "Cache initialized")
            
            def cleanup(self):
                self._cache.clear()
                self._initialized = False
                return create_result(True, "Cache cleaned up")
            
            def get(self, key: str):
                if key in self._cache:
                    entry = self._cache[key]
                    entry.access_count += 1
                    self._stats["hits"] += 1
                    return entry.value
                self._stats["misses"] += 1
                return None
            
            def set(self, key: str, value, ttl=None):
                entry = CacheEntry(key=key, value=value, ttl=ttl)
                self._cache[key] = entry
                self._stats["total_operations"] += 1
                return True
            
            def delete(self, key: str):
                if key in self._cache:
                    del self._cache[key]
                    return True
                return False
        
        self.TestCache = TestCache
    
    def test_base_cache_creation(self):
        """BaseCache作成のテスト"""
        cache = self.TestCache("test_cache", CacheStrategy.MEMORY_ONLY)
        self.assertEqual(cache.name, "test_cache")
        self.assertEqual(cache.strategy, CacheStrategy.MEMORY_ONLY)
        self.assertEqual(cache.max_size, 1000)
        self.assertEqual(len(cache._cache), 0)
    
    def test_base_cache_with_custom_size(self):
        """カスタムサイズでのBaseCache作成のテスト"""
        cache = self.TestCache("test_cache", CacheStrategy.LRU, max_size=500)
        self.assertEqual(cache.max_size, 500)
    
    def test_base_cache_operations(self):
        """BaseCacheの基本操作のテスト"""
        cache = self.TestCache("test_cache", CacheStrategy.MEMORY_ONLY)
        
        # セット操作
        result = cache.set("key1", "value1")
        self.assertTrue(result)
        
        # ゲット操作（ヒット）
        value = cache.get("key1")
        self.assertEqual(value, "value1")
        
        # ゲット操作（ミス）
        value = cache.get("nonexistent_key")
        self.assertIsNone(value)
        
        # 削除操作
        result = cache.delete("key1")
        self.assertTrue(result)
        
        # 存在しないキーの削除
        result = cache.delete("nonexistent_key")
        self.assertFalse(result)
    
    def test_base_cache_stats(self):
        """BaseCacheの統計機能のテスト"""
        cache = self.TestCache("test_cache", CacheStrategy.MEMORY_ONLY)
        
        # 初期統計
        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)
        self.assertEqual(stats["hit_rate"], 0.0)
        self.assertEqual(stats["cache_size"], 0)
        self.assertEqual(stats["strategy"], "memory_only")
        
        # 操作実行
        cache.set("key1", "value1")
        cache.get("key1")  # ヒット
        cache.get("key2")  # ミス
        
        # 統計確認
        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hit_rate"], 50.0)
        self.assertEqual(stats["cache_size"], 1)
        
        # 統計クリア
        cache.clear_stats()
        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)


class TestUtilityFunctions(unittest.TestCase):
    """ユーティリティ関数のテスト"""
    
    def test_create_result(self):
        """create_result関数のテスト"""
        # 基本使用
        result = create_result(True, "Success")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        self.assertIsNone(result.data)
        self.assertIsNone(result.duration)
        
        # 全パラメータ指定
        data = {"key": "value"}
        result = create_result(False, "Error", data, 1.5)
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Error")
        self.assertEqual(result.data, data)
        self.assertEqual(result.duration, 1.5)
    
    def test_safe_json_serialize(self):
        """safe_json_serialize関数のテスト"""
        # 通常のオブジェクト
        data = {"name": "test", "value": 42}
        result = safe_json_serialize(data)
        self.assertIn("test", result)
        self.assertIn("42", result)
        
        # datetime変換
        dt = datetime.now()
        result = safe_json_serialize(dt)
        self.assertIsInstance(result, str)
        
        # Path変換
        path = Path("/test/path")
        result = safe_json_serialize(path)
        self.assertIn("test", result)
        self.assertIn("path", result)
        
        # 変換できないオブジェクト
        class UnserializableObject:
            pass
        
        obj = UnserializableObject()
        result = safe_json_serialize(obj)
        self.assertIn("JSON serialization error", result)
    
    def test_calculate_hash(self):
        """calculate_hash関数のテスト"""
        # 文字列ハッシュ
        hash1 = calculate_hash("test string")
        hash2 = calculate_hash("test string")
        hash3 = calculate_hash("different string")
        
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
        self.assertEqual(len(hash1), 64)  # SHA256
        
        # バイトハッシュ
        hash_bytes = calculate_hash(b"test bytes")
        self.assertEqual(len(hash_bytes), 64)
        
        # 存在しないファイル
        nonexistent_path = Path("/nonexistent/file.txt")
        result = calculate_hash(nonexistent_path)
        self.assertEqual(result, "")
    
    def test_calculate_hash_file(self):
        """ファイルハッシュ計算のテスト"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            hash_result = calculate_hash(temp_path)
            self.assertEqual(len(hash_result), 64)
            
            # 同じ内容なら同じハッシュ
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
                f2.write("test content")
                temp_path2 = Path(f2.name)
            
            try:
                hash_result2 = calculate_hash(temp_path2)
                self.assertEqual(hash_result, hash_result2)
            finally:
                temp_path2.unlink(missing_ok=True)
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_format_duration(self):
        """format_duration関数のテスト"""
        # ミリ秒
        self.assertEqual(format_duration(0.5), "500.0ms")
        self.assertEqual(format_duration(0.001), "1.0ms")
        
        # 秒
        self.assertEqual(format_duration(1.5), "1.50s")
        self.assertEqual(format_duration(30.0), "30.00s")
        
        # 分
        self.assertEqual(format_duration(60.0), "1m 0.0s")
        self.assertEqual(format_duration(90.5), "1m 30.5s")
        self.assertEqual(format_duration(125.3), "2m 5.3s")
    
    def test_ensure_directory(self):
        """ensure_directory関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test" / "nested" / "directory"
            
            # ディレクトリ作成
            result = ensure_directory(test_dir)
            self.assertTrue(result)
            self.assertTrue(test_dir.exists())
            self.assertTrue(test_dir.is_dir())
            
            # 既存ディレクトリ
            result = ensure_directory(test_dir)
            self.assertTrue(result)
    
    def test_safe_delete_file(self):
        """safe_delete_file関数のテスト"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        # ファイル削除
        self.assertTrue(temp_path.exists())
        result = safe_delete_file(temp_path)
        self.assertTrue(result)
        self.assertFalse(temp_path.exists())
        
        # 存在しないファイル削除
        result = safe_delete_file(temp_path)
        self.assertTrue(result)  # エラーにならず成功扱い


class TestConstants(unittest.TestCase):
    """定数のテスト"""
    
    def test_constants_exist(self):
        """定数が定義されていることをテスト"""
        self.assertIsInstance(DEFAULT_CACHE_TTL, int)
        self.assertEqual(DEFAULT_CACHE_TTL, 3600)
        
        self.assertIsInstance(EXCLUDE_PATTERNS, set)
        self.assertIn('.git', EXCLUDE_PATTERNS)
        self.assertIn('__pycache__', EXCLUDE_PATTERNS)


class TestModuleMain(unittest.TestCase):
    """モジュールmain実行のテスト"""
    
    def test_main_execution(self):
        """__main__実行のテスト"""
        # main blockの実行をシミュレート
        import core.common_base
        
        self.assertEqual(core.common_base.__version__, "1.0.0")
        self.assertEqual(core.common_base.__author__, "Alex Team")
        self.assertIn("Common base module", core.common_base.__description__)


if __name__ == '__main__':
    unittest.main(verbosity=2)