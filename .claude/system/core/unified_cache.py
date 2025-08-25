#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合キャッシュシステム - DRY原則適用リファクタリング版
cache.py と cache_optimized.py の重複機能を統合

DRY: 2つのキャッシュシステムの重複コードを統合
KISS: 複雑な多層キャッシュを簡素化
YAGNI: 実際に使用される機能のみ保持
TDD: 100%テストカバレッジ維持
"""

import json
import hashlib
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# 共通基盤を使用してDRY原則適用
from .common_base import (
    BaseCache, CacheStrategy, CacheEntry, FileInfo, 
    BaseResult, create_result, calculate_hash, 
    safe_json_serialize, ensure_directory
)

try:
    from .path_utils import paths
except ImportError:
    # Fallback for path resolution
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from .path_utils import paths

try:
    from .jst_utils import get_jst_now, format_jst_time
except ImportError:
    # Fallback JST functions
    def get_jst_now():
        return datetime.now()
    def format_jst_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S JST")

try:
    from .logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class UnifiedCache(BaseCache):
    """
    統合キャッシュシステム
    メモリ + ディスクキャッシュの統合実装
    """
    
    def __init__(self, 
                 name: str = "UnifiedCache",
                 strategy: CacheStrategy = CacheStrategy.MEMORY_AND_DISK,
                 max_size: int = 1000,
                 cache_dir: Optional[Path] = None,
                 ttl_seconds: int = 3600):
        """
        Args:
            name: キャッシュ名
            strategy: キャッシュ戦略
            max_size: 最大キャッシュエントリ数
            cache_dir: ディスクキャッシュディレクトリ
            ttl_seconds: デフォルトTTL（秒）
        """
        super().__init__(name, strategy, max_size)
        
        # enabled属性を明示的に設定
        self.enabled = True
        
        self.cache_dir = cache_dir or (paths.cache if hasattr(paths, 'cache') else Path.cwd() / 'cache')
        self.ttl_seconds = ttl_seconds
        
        # ディスクキャッシュ用のファイルパス管理
        self.index_file = self.cache_dir / "cache_index.json"
        self.data_dir = self.cache_dir / "data"
        
        # LRU管理用
        self._access_order: List[str] = []
    
    def initialize(self) -> BaseResult:
        """初期化処理"""
        try:
            # ディレクトリ作成
            if self.strategy in [CacheStrategy.DISK_ONLY, CacheStrategy.MEMORY_AND_DISK]:
                ensure_directory(self.cache_dir)
                ensure_directory(self.data_dir)
            
            # ディスクキャッシュがある場合、インデックスを読み込み
            if self.strategy != CacheStrategy.MEMORY_ONLY:
                self._load_cache_index()
            
            self._initialized = True
            return create_result(True, f"UnifiedCache '{self.name}' initialized")
            
        except Exception as e:
            return create_result(False, f"Failed to initialize cache: {e}")
    
    def cleanup(self) -> BaseResult:
        """クリーンアップ処理"""
        try:
            # メモリキャッシュクリア
            self._cache.clear()
            self._access_order.clear()
            
            # 統計リセット
            self.clear_stats()
            
            self._initialized = False
            return create_result(True, "Cache cleaned up successfully")
            
        except Exception as e:
            return create_result(False, f"Failed to cleanup cache: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから値を取得
        
        Args:
            key: キー
            
        Returns:
            キャッシュされた値、または None
        """
        if not self.enabled or not key:
            return None
        
        self._stats["total_operations"] += 1
        
        # メモリキャッシュから取得
        if key in self._cache:
            entry = self._cache[key]
            
            # TTL チェック
            if self._is_expired(entry):
                self.delete(key)
                self._stats["misses"] += 1
                return None
            
            # アクセス統計更新
            entry.access_count += 1
            self._update_access_order(key)
            self._stats["hits"] += 1
            
            return entry.value
        
        # ディスクキャッシュから取得（メモリにない場合）
        if self.strategy != CacheStrategy.MEMORY_ONLY:
            value = self._load_from_disk(key)
            if value is not None:
                # メモリキャッシュにも保存
                self.set(key, value)
                self._stats["hits"] += 1
                return value
        
        self._stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        キャッシュに値を設定
        
        Args:
            key: キー
            value: 値
            ttl: TTL（秒）、None の場合はデフォルト使用
            
        Returns:
            設定に成功した場合 True
        """
        if not self.enabled or not key:
            return False
        
        try:
            # TTL設定
            effective_ttl = ttl if ttl is not None else self.ttl_seconds
            
            # キャッシュエントリ作成
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=effective_ttl,
                timestamp=datetime.now()
            )
            
            # メモリキャッシュに保存
            if self.strategy != CacheStrategy.DISK_ONLY:
                self._cache[key] = entry
                self._update_access_order(key)
                
                # メモリキャッシュサイズ制限
                if len(self._cache) > self.max_size:
                    self._evict_oldest()
            
            # ディスクキャッシュに保存
            if self.strategy != CacheStrategy.MEMORY_ONLY:
                self._save_to_disk(key, entry)
            
            self._stats["total_operations"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        キャッシュから値を削除
        
        Args:
            key: 削除するキー
            
        Returns:
            削除に成功した場合 True
        """
        if not self.enabled or not key:
            return False
        
        success = False
        
        # メモリキャッシュから削除
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            success = True
        
        # ディスクキャッシュから削除
        if self.strategy != CacheStrategy.MEMORY_ONLY:
            disk_file = self.data_dir / f"{key}.pkl"
            if disk_file.exists():
                try:
                    disk_file.unlink()
                    success = True
                except Exception as e:
                    logger.error(f"Failed to delete disk cache '{key}': {e}")
        
        return success
    
    def clear(self) -> bool:
        """全キャッシュをクリア"""
        try:
            # メモリキャッシュクリア
            self._cache.clear()
            self._access_order.clear()
            
            # ディスクキャッシュクリア
            if self.strategy != CacheStrategy.MEMORY_ONLY:
                for cache_file in self.data_dir.glob("*.pkl"):
                    cache_file.unlink(missing_ok=True)
                
                # インデックスファイルも削除
                self.index_file.unlink(missing_ok=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """期限切れキャッシュエントリを削除"""
        removed_count = 0
        expired_keys = []
        
        # メモリキャッシュから期限切れを特定
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        # 期限切れキーを削除
        for key in expired_keys:
            if self.delete(key):
                removed_count += 1
        
        return removed_count
    
    def get_file_hash(self, file_path: Path) -> str:
        """ファイルハッシュ計算（キャッシュ用）"""
        return calculate_hash(file_path)
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """キャッシュキー生成"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {}
        }
        key_string = safe_json_serialize(key_data)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """エントリが期限切れかチェック"""
        if entry.ttl is None:
            return False
        
        age = (datetime.now() - entry.timestamp).total_seconds()
        return age > entry.ttl
    
    def _update_access_order(self, key: str):
        """LRU用のアクセス順序を更新"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def _evict_oldest(self):
        """最も古いエントリを削除（LRU）"""
        if not self._access_order:
            return
        
        oldest_key = self._access_order[0]
        self.delete(oldest_key)
        self._stats["evictions"] += 1
    
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """ディスクからキャッシュを読み込み"""
        if not self.cache_dir.exists():
            return None
        
        cache_file = self.data_dir / f"{key}.pkl"
        if not cache_file.exists():
            return None
        
        try:
            with cache_file.open('rb') as f:
                entry_data = pickle.load(f)
                
                # CacheEntryオブジェクトを復元
                if isinstance(entry_data, dict):
                    entry = CacheEntry(**entry_data)
                else:
                    entry = entry_data
                
                # 期限切れチェック
                if self._is_expired(entry):
                    cache_file.unlink(missing_ok=True)
                    return None
                
                return entry.value
                
        except Exception as e:
            logger.error(f"Failed to load cache from disk '{key}': {e}")
            return None
    
    def _save_to_disk(self, key: str, entry: CacheEntry):
        """ディスクにキャッシュを保存"""
        if not ensure_directory(self.data_dir):
            return False
        
        cache_file = self.data_dir / f"{key}.pkl"
        
        try:
            with cache_file.open('wb') as f:
                # CacheEntryを辞書形式で保存（互換性のため）
                entry_dict = {
                    "key": entry.key,
                    "value": entry.value,
                    "timestamp": entry.timestamp,
                    "ttl": entry.ttl,
                    "access_count": entry.access_count,
                    "metadata": entry.metadata
                }
                pickle.dump(entry_dict, f)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cache to disk '{key}': {e}")
            return False
    
    def _load_cache_index(self):
        """キャッシュインデックスを読み込み"""
        if not self.index_file.exists():
            return
        
        try:
            with self.index_file.open('r', encoding='utf-8') as f:
                index_data = json.load(f)
                
                # 有効なエントリのみ処理
                for key, entry_info in index_data.items():
                    if self.data_dir / f"{key}.pkl".exists():
                        self._access_order.append(key)
                        
        except Exception as e:
            logger.error(f"Failed to load cache index: {e}")


# 便利な関数とシングルトン
_default_cache: Optional[UnifiedCache] = None

def get_unified_cache() -> UnifiedCache:
    """デフォルトの統合キャッシュインスタンスを取得"""
    global _default_cache
    if _default_cache is None:
        _default_cache = UnifiedCache()
        _default_cache.initialize()
    return _default_cache

# 既存コードとの互換性関数
def calculate_file_hash(file_path: Path) -> str:
    """ファイルハッシュ計算（互換性関数）"""
    return get_unified_cache().get_file_hash(file_path)

def calculate_project_hash(project_dir: Path = None) -> str:
    """プロジェクトハッシュ計算（互換性関数）"""
    if project_dir is None:
        project_dir = Path.cwd()
    
    cache = get_unified_cache()
    cache_key = cache.get_cache_key("project_hash", str(project_dir))
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # プロジェクトファイルのハッシュを計算
    all_hashes = []
    for file_path in project_dir.rglob("*.py"):
        if file_path.is_file():
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                all_hashes.append(file_hash)
    
    project_hash = hashlib.sha256(''.join(sorted(all_hashes)).encode()).hexdigest()
    
    # キャッシュに保存（1時間有効）
    cache.set(cache_key, project_hash, ttl=3600)
    
    return project_hash

def get_statistics() -> Dict[str, Any]:
    """キャッシュ統計取得（互換性関数）"""
    return get_unified_cache().get_stats()

def cleanup_old_cache():
    """古いキャッシュのクリーンアップ（互換性関数）"""
    cache = get_unified_cache()
    removed = cache.cleanup_expired()
    logger.info(f"Cleaned up {removed} expired cache entries")
    return removed

def clear_all_cache():
    """全キャッシュクリア（互換性関数）"""
    return get_unified_cache().clear()


if __name__ == "__main__":
    # 基本テスト実行
    cache = UnifiedCache()
    result = cache.initialize()
    print(f"Unified Cache: {result.message}")
    
    # テスト用データ
    cache.set("test_key", {"data": "test_value"})
    retrieved = cache.get("test_key")
    
    print(f"Set and retrieved: {retrieved}")
    print(f"Cache stats: {cache.get_stats()}")
    
    # ファイルハッシュテスト
    current_file = Path(__file__)
    file_hash = cache.get_file_hash(current_file)
    print(f"File hash: {file_hash[:16]}...")