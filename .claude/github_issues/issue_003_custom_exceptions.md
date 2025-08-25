# Issue #3: カスタム例外クラスの体系化

## 概要
汎用的な例外処理を、体系化されたカスタム例外クラスに置き換える

## 背景
現在は基本的な例外処理のみで、エラーの種類や原因が不明確になりやすい

## タスク

### 1. カスタム例外クラスの作成
**新規ファイル**: `.claude/system/core/exceptions.py`
```python
from typing import Optional, Any

class ClaudeSystemError(Exception):
    """
    Claudeシステムの基底例外クラス
    """
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

# ファイル操作関連
class FileOperationError(ClaudeSystemError):
    """ファイル操作エラーの基底クラス"""
    pass

class FileOrganizationError(FileOperationError):
    """ファイル整理エラー"""
    pass

class FileNotFoundError(FileOperationError):
    """ファイルが見つからないエラー"""
    pass

class PermissionDeniedError(FileOperationError):
    """アクセス権限エラー"""
    pass

# テスト関連
class TestExecutionError(ClaudeSystemError):
    """テスト実行エラー"""
    pass

class TestFailureError(TestExecutionError):
    """テスト失敗エラー"""
    pass

class CoverageError(TestExecutionError):
    """カバレッジ不足エラー"""
    pass

# 設定関連
class ConfigurationError(ClaudeSystemError):
    """設定エラー"""
    pass

class InvalidConfigError(ConfigurationError):
    """不正な設定エラー"""
    pass

# システム関連
class SystemInitializationError(ClaudeSystemError):
    """システム初期化エラー"""
    pass

class CommandExecutionError(ClaudeSystemError):
    """コマンド実行エラー"""
    pass
```

### 2. エラーハンドラーの作成
**新規ファイル**: `.claude/system/core/error_handler.py`
```python
import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps
from .exceptions import ClaudeSystemError
from .i18n import i18n

logger = logging.getLogger(__name__)

class ErrorHandler:
    """統一エラーハンドリング"""
    
    @staticmethod
    def handle_error(error: Exception) -> dict:
        """
        エラーを処理して標準形式で返す
        """
        if isinstance(error, ClaudeSystemError):
            return {
                "success": False,
                "error_code": error.error_code,
                "message": error.message,
                "details": error.details
            }
        else:
            # 予期しないエラー
            logger.error(f"Unexpected error: {traceback.format_exc()}")
            return {
                "success": False,
                "error_code": "UNEXPECTED_ERROR",
                "message": str(error),
                "details": {"traceback": traceback.format_exc()}
            }
    
    @staticmethod
    def safe_execute(func: Callable) -> Callable:
        """
        安全な実行デコレータ
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except ClaudeSystemError as e:
                logger.warning(f"{e.error_code}: {e.message}")
                return ErrorHandler.handle_error(e)
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                return ErrorHandler.handle_error(e)
        return wrapper

# グローバルインスタンス
error_handler = ErrorHandler()
```

### 3. CoreSystemクラスの修正
**ファイル**: `.claude/system/core/core_system.py`

**変更前**:
```python
def organize_files(self) -> Result:
    try:
        # 処理
        return Result(True, f"Organized {moved_count} files")
    except Exception as e:
        return Result(False, f"Organization failed: {e}")
```

**変更後**:
```python
from .exceptions import (
    FileOrganizationError, 
    FileNotFoundError as CustomFileNotFoundError,
    PermissionDeniedError
)
from .error_handler import error_handler

@error_handler.safe_execute
def organize_files(self) -> Result:
    try:
        # 処理
        return Result(True, f"Organized {moved_count} files")
    except FileNotFoundError as e:
        raise CustomFileNotFoundError(
            message=f"Required file not found",
            details={"file": str(e), "operation": "organize"}
        )
    except PermissionError as e:
        raise PermissionDeniedError(
            message=f"Permission denied during file organization",
            details={"file": str(e), "operation": "organize"}
        )
    except Exception as e:
        raise FileOrganizationError(
            message=f"Failed to organize files",
            details={"error": str(e)}
        )
```

### 4. テストの作成
**新規ファイル**: `.claude/project/tests/test_exceptions.py`
```python
import unittest
from system.core.exceptions import (
    ClaudeSystemError,
    FileOrganizationError,
    TestExecutionError
)
from system.core.error_handler import error_handler

class TestCustomExceptions(unittest.TestCase):
    
    def test_base_exception(self):
        """基底例外クラスのテスト"""
        error = ClaudeSystemError(
            message="Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.error_code, "TEST_ERROR")
        self.assertEqual(error.details["key"], "value")
    
    def test_file_organization_error(self):
        """ファイル整理エラーのテスト"""
        error = FileOrganizationError(
            message="Organization failed",
            details={"files": 10}
        )
        self.assertIsInstance(error, ClaudeSystemError)
        self.assertEqual(error.error_code, "FileOrganizationError")
    
    def test_error_handler(self):
        """エラーハンドラーのテスト"""
        error = TestExecutionError("Test failed")
        result = error_handler.handle_error(error)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "TestExecutionError")
        self.assertEqual(result["message"], "Test failed")
    
    def test_safe_execute_decorator(self):
        """安全実行デコレータのテスト"""
        @error_handler.safe_execute
        def failing_function():
            raise FileOrganizationError("Intentional error")
        
        result = failing_function()
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "FileOrganizationError")
```

### 5. ログ設定の更新
**ファイル**: `.claude/config/logging_config.json`
```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "detailed": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
  },
  "handlers": {
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "INFO",
      "formatter": "detailed",
      "filename": ".claude/logs/system.log",
      "maxBytes": 10485760,
      "backupCount": 5
    },
    "error_file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "ERROR",
      "formatter": "detailed",
      "filename": ".claude/logs/errors.log",
      "maxBytes": 10485760,
      "backupCount": 5
    }
  },
  "root": {
    "level": "INFO",
    "handlers": ["file", "error_file"]
  }
}
```

## 受け入れ条件
- [ ] すべてのカスタム例外クラスが作成されている
- [ ] エラーハンドラーが正常に動作する
- [ ] 既存のコードがカスタム例外を使用するよう更新されている
- [ ] エラーログが適切に記録される
- [ ] テストが全て通る

## 実装手順
1. exceptions.pyを作成
2. error_handler.pyを作成
3. CoreSystemクラスを更新
4. テストを作成・実行
5. ログ設定を更新

## 優先度
**高**

## 見積もり工数
2-3時間

## ラベル
- enhancement
- error-handling
- maintainability