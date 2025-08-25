#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コアモジュール最小テスト - TDD原則適用
YAGNI: 必要最小限のテストのみ
DRY: 共通テストパターンの共有  
KISS: シンプルなテスト構造
"""

import unittest
import sys
from pathlib import Path

# Standard path setup pattern
current = Path(__file__).resolve()
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    current = current.parent
    if current == current.parent:
        raise RuntimeError("Could not find .claude directory")

system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

# Import core modules
try:
    from core.common_base import BaseManager, BaseResult, TaskStatus, ErrorSeverity, create_result
    from core.emoji_handler import EmojiHandler
    from core.config import get_config, ClaudeCoreConfig
    from core.unified_cache import UnifiedCache
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestCommonBase(unittest.TestCase):
    """Common base module minimal tests"""
    
    def test_create_result_success(self):
        """Test successful result creation"""
        result = create_result(success=True, message="Success")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        
    def test_create_result_failure(self):
        """Test failure result creation"""
        result = create_result(success=False, message="Failed")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Failed")
        
    def test_task_status_enum(self):
        """Test task status enumeration"""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        
    def test_error_severity_enum(self):
        """Test error severity enumeration"""
        self.assertEqual(ErrorSeverity.CRITICAL.value, "critical")
        self.assertEqual(ErrorSeverity.LOW.value, "low")


class TestEmojiHandler(unittest.TestCase):
    """Emoji handler minimal tests"""
    
    def test_emoji_handler_creation(self):
        """Test emoji handler creation"""
        handler = EmojiHandler()
        self.assertIsInstance(handler, EmojiHandler)
        
    def test_process_file_basic(self):
        """Test basic file processing capability"""
        handler = EmojiHandler()
        # Test method exists (even if we don't run it on actual file)
        self.assertTrue(hasattr(handler, 'process_file'))
        
    def test_handler_initialization(self):
        """Test handler initializes without error"""
        handler = EmojiHandler()
        result = handler.initialize()
        self.assertIsInstance(result, BaseResult)


class TestConfig(unittest.TestCase):
    """Config module minimal tests"""
    
    def test_get_config_returns_instance(self):
        """Test config returns valid instance"""
        config = get_config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config, ClaudeCoreConfig)
        
    def test_config_get_logging_config(self):
        """Test logging config retrieval"""
        config = get_config()
        logging_config = config.get_logging_config()
        self.assertIsInstance(logging_config, dict)
        
    def test_config_get_tdd_config(self):
        """Test TDD config retrieval"""
        config = get_config()
        tdd_config = config.get_tdd_config()
        self.assertIsInstance(tdd_config, dict)


class TestUnifiedCache(unittest.TestCase):
    """Unified cache minimal tests"""
    
    def test_unified_cache_creation(self):
        """Test unified cache can be created"""
        cache = UnifiedCache()
        self.assertIsNotNone(cache)
        
    def test_cache_get_set_basic(self):
        """Test basic cache operations"""
        cache = UnifiedCache()
        test_key = "test_key_minimal"
        test_value = "test_value"
        
        # Test set and get
        cache.set(test_key, test_value)
        result = cache.get(test_key)
        self.assertEqual(result, test_value)
        
    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = UnifiedCache()
        cache.set("temp", "value")
        cache.clear()
        result = cache.get("temp")
        self.assertIsNone(result)


if __name__ == '__main__':
    # TDD: Run tests first (RED phase)
    unittest.main(verbosity=2)