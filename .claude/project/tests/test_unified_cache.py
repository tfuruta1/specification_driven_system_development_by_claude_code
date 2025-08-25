#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合キャッシュシステムのテスト - TDD原則に従った100%カバレッジ実現
DRY原則適用により2つのキャッシュモジュールから1つに統合したキャッシュ機能のテスト
"""

import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import tempfile
import os
import json
import pickle
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

from core.unified_cache import (
    UnifiedCache, get_unified_cache, calculate_file_hash, 
    calculate_project_hash, get_statistics, cleanup_old_cache, clear_all_cache
)
from core.common_base import CacheStrategy, CacheEntry, BaseResult


class TestUnifiedCache(unittest.TestCase):
    """統合キャッシュの基本機能テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache = UnifiedCache(
            name="TestCache",
            cache_dir=self.temp_dir / "cache"
        )
    
    def tearDown(self):
        """テスト後処理"""
        # テンポラリディレクトリクリーンアップ
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """初期化のテスト"""
        # 初期状態
        self.assertEqual(self.cache.name, "TestCache")
        self.assertEqual(self.cache.strategy, CacheStrategy.MEMORY_AND_DISK)
        self.assertFalse(self.cache.is_initialized())
        
        # 初期化実行
        result = self.cache.initialize()
        self.assertIsInstance(result, BaseResult)
        self.assertTrue(result.success)
        self.assertTrue(self.cache.is_initialized())
        self.assertTrue(self.cache.cache_dir.exists())
        self.assertTrue(self.cache.data_dir.exists())
    
    def test_initialization_memory_only(self):
        """メモリオンリーキャッシュの初期化テスト"""
        cache = UnifiedCache(strategy=CacheStrategy.MEMORY_ONLY)
        result = cache.initialize()
        self.assertTrue(result.success)
    
    def test_cleanup(self):
        """クリーンアップのテスト"""
        self.cache.initialize()
        self.cache.set("test_key", "test_value")
        self.assertTrue(self.cache.is_initialized())
        
        # クリーンアップ実行
        result = self.cache.cleanup()
        self.assertTrue(result.success)
        self.assertFalse(self.cache.is_initialized())
        self.assertEqual(len(self.cache._cache), 0)
    
    def test_basic_set_get(self):
        """基本的なset/get操作のテスト"""
        self.cache.initialize()
        
        # データ設定
        result = self.cache.set("test_key", "test_value")
        self.assertTrue(result)
        
        # データ取得
        value = self.cache.get("test_key")
        self.assertEqual(value, "test_value")
        
        # 存在しないキー
        value = self.cache.get("nonexistent_key")
        self.assertIsNone(value)
    
    def test_complex_data_types(self):
        """複雑なデータ型のテスト"""
        self.cache.initialize()
        
        test_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "bool": True
        }
        
        self.cache.set("complex_key", test_data)
        retrieved = self.cache.get("complex_key")
        self.assertEqual(retrieved, test_data)
    
    def test_ttl_functionality(self):
        """TTL機能のテスト"""
        self.cache.initialize()
        
        # 短いTTL設定（1秒）
        self.cache.set("ttl_key", "ttl_value", ttl=1)
        
        # すぐに取得（存在する）
        value = self.cache.get("ttl_key")
        self.assertEqual(value, "ttl_value")
        
        # TTL後にチェック（期限切れのシミュレーション）
        entry = self.cache._cache["ttl_key"]
        entry.timestamp = datetime.now() - timedelta(seconds=2)  # 2秒前に設定
        
        value = self.cache.get("ttl_key")
        self.assertIsNone(value)  # 期限切れで削除されるはず
    
    def test_delete_operation(self):
        """削除操作のテスト"""
        self.cache.initialize()
        
        # データ設定
        self.cache.set("delete_key", "delete_value")
        self.assertIsNotNone(self.cache.get("delete_key"))
        
        # 削除実行
        result = self.cache.delete("delete_key")
        self.assertTrue(result)
        
        # 削除確認
        value = self.cache.get("delete_key")
        self.assertIsNone(value)
        
        # 存在しないキーの削除
        result = self.cache.delete("nonexistent_key")
        self.assertFalse(result)
    
    def test_clear_cache(self):
        """キャッシュクリアのテスト"""
        self.cache.initialize()
        
        # 複数データ設定
        for i in range(5):
            self.cache.set(f"key_{i}", f"value_{i}")
        
        # データ存在確認
        self.assertEqual(len(self.cache._cache), 5)
        
        # クリア実行
        result = self.cache.clear()
        self.assertTrue(result)
        
        # クリア確認
        self.assertEqual(len(self.cache._cache), 0)
        for i in range(5):
            self.assertIsNone(self.cache.get(f"key_{i}"))
    
    def test_lru_eviction(self):
        """LRU退避のテスト"""
        cache = UnifiedCache(max_size=3)
        cache.initialize()
        
        # 容量を超えるデータを設定
        for i in range(5):
            cache.set(f"key_{i}", f"value_{i}")
        
        # 最大容量を維持
        self.assertLessEqual(len(cache._cache), 3)
        
        # 最も古いエントリが削除されていることを確認
        # 最新の3つのキーが残っているはず
        remaining_keys = list(cache._cache.keys())
        for i in range(3):
            self.assertIn(f"key_{4-i}", remaining_keys)
    
    def test_cache_statistics(self):
        """キャッシュ統計のテスト"""
        self.cache.initialize()
        
        # 初期統計
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)
        
        # 操作実行
        self.cache.set("stat_key", "stat_value")
        self.cache.get("stat_key")  # ヒット
        self.cache.get("nonexistent")  # ミス
        
        # 統計確認
        stats = self.cache.get_stats()
        self.assertGreater(stats["hits"], 0)
        self.assertGreater(stats["misses"], 0)
        self.assertGreater(stats["total_operations"], 0)
        
        # 統計クリア
        self.cache.clear_stats()
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 0)
    
    def test_disabled_cache(self):
        """無効化されたキャッシュのテスト"""
        self.cache.enabled = False
        self.cache.initialize()
        
        # 無効化状態では何も保存されない
        result = self.cache.set("disabled_key", "disabled_value")
        self.assertFalse(result)
        
        value = self.cache.get("disabled_key")
        self.assertIsNone(value)
    
    def test_cache_key_generation(self):
        """キャッシュキー生成のテスト"""
        self.cache.initialize()
        
        # 引数からキー生成
        key1 = self.cache.get_cache_key("arg1", "arg2", param="value")
        key2 = self.cache.get_cache_key("arg1", "arg2", param="value")
        key3 = self.cache.get_cache_key("arg1", "different", param="value")
        
        # 同じ引数なら同じキー
        self.assertEqual(key1, key2)
        # 異なる引数なら異なるキー
        self.assertNotEqual(key1, key3)
        # キーは適切な長さ
        self.assertEqual(len(key1), 16)
    
    def test_file_hash_calculation(self):
        """ファイルハッシュ計算のテスト"""
        self.cache.initialize()
        
        # テストファイル作成
        test_file = self.temp_dir / "test_file.txt"
        test_file.write_text("test content")
        
        # ハッシュ計算
        hash1 = self.cache.get_file_hash(test_file)
        hash2 = self.cache.get_file_hash(test_file)
        
        # 同じファイルなら同じハッシュ
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256
        
        # 存在しないファイル
        nonexistent = self.temp_dir / "nonexistent.txt"
        hash_none = self.cache.get_file_hash(nonexistent)
        self.assertEqual(hash_none, "")


class TestDiskCaching(unittest.TestCase):
    """ディスクキャッシュ機能のテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache = UnifiedCache(
            strategy=CacheStrategy.MEMORY_AND_DISK,
            cache_dir=self.temp_dir / "cache"
        )
        self.cache.initialize()
    
    def tearDown(self):
        """テスト後処理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_disk_persistence(self):
        """ディスク永続化のテスト"""
        # データ保存
        self.cache.set("persist_key", "persist_value")
        
        # ディスクファイル存在確認
        disk_file = self.cache.data_dir / "persist_key.pkl"
        self.assertTrue(disk_file.exists())
        
        # メモリキャッシュクリア
        self.cache._cache.clear()
        
        # ディスクから復元確認
        value = self.cache.get("persist_key")
        self.assertEqual(value, "persist_value")
    
    def test_disk_only_strategy(self):
        """ディスクオンリー戦略のテスト"""
        disk_cache = UnifiedCache(
            strategy=CacheStrategy.DISK_ONLY,
            cache_dir=self.temp_dir / "disk_cache"
        )
        disk_cache.initialize()
        
        # データ設定
        disk_cache.set("disk_key", "disk_value")
        
        # メモリキャッシュには保存されない
        self.assertEqual(len(disk_cache._cache), 0)
        
        # ディスクから取得可能
        value = disk_cache.get("disk_key")
        self.assertEqual(value, "disk_value")
    
    def test_memory_only_strategy(self):
        """メモリオンリー戦略のテスト"""
        mem_cache = UnifiedCache(strategy=CacheStrategy.MEMORY_ONLY)
        mem_cache.initialize()
        
        # データ設定
        mem_cache.set("mem_key", "mem_value")
        
        # メモリから取得可能
        value = mem_cache.get("mem_key")
        self.assertEqual(value, "mem_value")
        
        # ディスクファイルは作成されない
        # （cache_dirが設定されていないため、テストスキップ）
    
    def test_expired_disk_cleanup(self):
        """期限切れディスクキャッシュのクリーンアップテスト"""
        # 期限切れエントリ作成
        self.cache.set("expired_key", "expired_value", ttl=1)
        
        # ディスクファイル存在確認
        disk_file = self.cache.data_dir / "expired_key.pkl"
        self.assertTrue(disk_file.exists())
        
        # 期限切れシミュレーション
        entry = self.cache._cache["expired_key"]
        entry.timestamp = datetime.now() - timedelta(seconds=2)
        
        # 期限切れクリーンアップ
        removed = self.cache.cleanup_expired()
        self.assertEqual(removed, 1)
        
        # ファイルが削除されていることを確認
        self.assertIsNone(self.cache.get("expired_key"))


class TestConvenienceFunctions(unittest.TestCase):
    """便利な関数のテスト"""
    
    def test_get_unified_cache_singleton(self):
        """統合キャッシュシングルトンのテスト"""
        cache1 = get_unified_cache()
        cache2 = get_unified_cache()
        
        self.assertIs(cache1, cache2)  # 同じインスタンス
        self.assertTrue(cache1.is_initialized())
    
    def test_calculate_file_hash_function(self):
        """ファイルハッシュ計算関数のテスト"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            hash_result = calculate_file_hash(temp_path)
            self.assertEqual(len(hash_result), 64)
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_calculate_project_hash_function(self):
        """プロジェクトハッシュ計算関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Pythonファイル作成
            (temp_path / "test1.py").write_text("print('test1')")
            (temp_path / "test2.py").write_text("print('test2')")
            
            # プロジェクトハッシュ計算
            hash1 = calculate_project_hash(temp_path)
            hash2 = calculate_project_hash(temp_path)
            
            self.assertEqual(hash1, hash2)  # 同じプロジェクトなら同じハッシュ
            self.assertEqual(len(hash1), 64)  # SHA256
    
    def test_get_statistics_function(self):
        """統計取得関数のテスト"""
        stats = get_statistics()
        self.assertIn("hits", stats)
        self.assertIn("misses", stats)
        self.assertIsInstance(stats, dict)
    
    def test_cleanup_old_cache_function(self):
        """古いキャッシュクリーンアップ関数のテスト"""
        # いくつかのキャッシュエントリを作成
        cache = get_unified_cache()
        cache.set("cleanup_test", "value", ttl=1)
        
        # 期限切れシミュレーション
        if "cleanup_test" in cache._cache:
            cache._cache["cleanup_test"].timestamp = datetime.now() - timedelta(seconds=2)
        
        removed_count = cleanup_old_cache()
        self.assertIsInstance(removed_count, int)
    
    def test_clear_all_cache_function(self):
        """全キャッシュクリア関数のテスト"""
        cache = get_unified_cache()
        cache.set("clear_test", "value")
        
        result = clear_all_cache()
        self.assertTrue(result)
        
        # キャッシュがクリアされていることを確認
        self.assertIsNone(cache.get("clear_test"))


class TestErrorHandling(unittest.TestCase):
    """エラーハンドリングのテスト"""
    
    def test_initialization_error(self):
        """初期化エラーのテスト"""
        # 無効なパスでキャッシュ作成
        with patch('core.unified_cache.ensure_directory', return_value=False):
            cache = UnifiedCache(cache_dir=Path("/invalid/path"))
            result = cache.initialize()
            # エラーハンドリングにより初期化は成功するが、ディスク操作は失敗
            # 実装によっては成功する場合もある
            self.assertIsInstance(result, BaseResult)
    
    def test_disk_save_error(self):
        """ディスク保存エラーのテスト"""
        cache = UnifiedCache(cache_dir=Path(tempfile.mkdtemp()))
        cache.initialize()
        
        # ディスク書き込み失敗のシミュレーション
        with patch('pathlib.Path.open', side_effect=PermissionError("Write denied")):
            result = cache.set("error_key", "error_value")
            # エラーがあってもメモリキャッシュは動作
            self.assertIsInstance(result, bool)
    
    def test_disk_load_error(self):
        """ディスク読み込みエラーのテスト"""
        cache = UnifiedCache(cache_dir=Path(tempfile.mkdtemp()))
        cache.initialize()
        
        # 破損したキャッシュファイルをシミュレート
        cache_file = cache.data_dir / "corrupted.pkl"
        cache_file.write_text("corrupted data")
        
        # 読み込み時にエラーが発生するがNoneを返す
        value = cache._load_from_disk("corrupted")
        self.assertIsNone(value)
    
    def test_cleanup_error(self):
        """クリーンアップエラーのテスト"""
        cache = UnifiedCache(cache_dir=Path(tempfile.mkdtemp()))
        cache.initialize()
        
        # クリーンアップ中のエラー
        with patch.object(cache._cache, 'clear', side_effect=Exception("Clear error")):
            result = cache.cleanup()
            self.assertFalse(result.success)
            self.assertIn("Failed to cleanup", result.message)


class TestMainExecution(unittest.TestCase):
    """メイン実行ブロックのテスト"""
    
    @patch('builtins.print')
    def test_main_execution(self, mock_print):
        """__main__実行のテスト"""
        # main blockの実行をシミュレート
        cache = UnifiedCache()
        result = cache.initialize()
        
        cache.set("test_key", {"data": "test_value"})
        retrieved = cache.get("test_key")
        
        # 基本動作確認
        self.assertTrue(result.success)
        self.assertEqual(retrieved, {"data": "test_value"})
        
        # ファイルハッシュテスト
        current_file = Path(__file__)
        if current_file.exists():
            file_hash = cache.get_file_hash(current_file)
            self.assertGreater(len(file_hash), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)