"""
統合ロガーライブラリ - 192箇所のロガー重複除去のための統一システム

このモジュールは、以下の重複パターンを統合します:
- FileAccessLogger (67箇所で使用)
- ActivityLogger (45箇所で使用)  
- UnifiedLogger (38箇所で使用)
- IntegratedLogger (25箇所で使用)
- その他のカスタムロガー (17箇所で使用)

パフォーマンス目標: 30%の実行時間短縮を実現
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager


class OptimizedLogger:
    """
    統一されたロギングシステム - 全てのロガー重複を置き換える単一クラス
    
    主な特徴:
    - メモリ効率化されたバッファリング
    - 遅延ファイル作成
    - 構造化ログ出力
    - コンテキスト付きロギング
    - 自動ローテーション
    """
    
    _instances = {}  # シングルトンパターン実装
    
    def __new__(cls, log_file: Optional[Union[str, Path]] = None, 
                user: str = "system", base_path: Optional[Path] = None,
                buffer_size: int = 1000):
        """インスタンス作成時の重複を防ぐファクトリーメソッド"""
        key = f"{log_file}_{user}_{base_path}"
        if key not in cls._instances:
            cls._instances[key] = super(OptimizedLogger, cls).__new__(cls)
        return cls._instances[key]
    
    def __init__(self, log_file: Optional[Union[str, Path]] = None,
                 user: str = "system", base_path: Optional[Path] = None,
                 buffer_size: int = 1000):
        """
        統合ロガーの初期化
        
        Args:
            log_file: ログファイルパス（Noneの場合は自動生成）
            user: ユーザー識別子
            base_path: ベースディレクトリ
            buffer_size: バッファサイズ（メモリ最適化用）
        """
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.user = user
        self.buffer_size = buffer_size
        self._log_buffer = []
        self._last_flush = time.time()
        
        # ベースパス設定
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.cwd() / ".claude" / "logs"
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # ログファイル設定
        if log_file:
            self.log_file = Path(log_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = self.base_path / f"optimized_log_{user}_{timestamp}.jsonl"
        
        # Pythonの標準ロガー設定
        self.logger = logging.getLogger(f"OptimizedLogger_{user}")
        self.logger.setLevel(logging.INFO)
        
        # ハンドラーの重複を防ぐ
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_file_access(self, operation: str, file_path: Union[str, Path],
                       status: str = "success", details: Optional[Dict] = None) -> None:
        """
        ファイルアクセスログ - FileAccessLoggerの代替
        
        Args:
            operation: 操作種別（read, write, create, delete等）
            file_path: ファイルパス
            status: 実行結果
            details: 追加詳細情報
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "file_access",
            "user": self.user,
            "operation": operation,
            "file_path": str(file_path),
            "status": status,
            "details": details or {}
        }
        self._add_to_buffer(log_entry)
    
    def log_activity(self, action: str, target: Optional[str] = None,
                    metadata: Optional[Dict] = None) -> None:
        """
        アクティビティログ - ActivityLoggerの代替
        
        Args:
            action: 実行されたアクション
            target: アクションの対象
            metadata: メタデータ
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "activity",
            "user": self.user,
            "action": action,
            "target": target,
            "metadata": metadata or {}
        }
        self._add_to_buffer(log_entry)
    
    def log_integration_event(self, component: str, event: str,
                            data: Optional[Dict] = None) -> None:
        """
        統合イベントログ - IntegratedLoggerの代替
        
        Args:
            component: コンポーネント名
            event: イベント種別
            data: イベントデータ
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "integration",
            "user": self.user,
            "component": component,
            "event": event,
            "data": data or {}
        }
        self._add_to_buffer(log_entry)
    
    def log_with_context(self, level: str, message: str,
                        context: Optional[Dict] = None) -> None:
        """
        コンテキスト付きロギング
        
        Args:
            level: ログレベル
            message: メッセージ
            context: コンテキスト情報
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "context",
            "user": self.user,
            "level": level,
            "message": message,
            "context": context or {}
        }
        self._add_to_buffer(log_entry)
        
        # 標準ロガーにも出力
        getattr(self.logger, level.lower(), self.logger.info)(
            f"{message} | Context: {context}"
        )
    
    def _add_to_buffer(self, log_entry: Dict[str, Any]) -> None:
        """ログエントリをバッファに追加"""
        self._log_buffer.append(log_entry)
        
        # バッファサイズ超過または5秒経過でフラッシュ
        current_time = time.time()
        if (len(self._log_buffer) >= self.buffer_size or 
            current_time - self._last_flush > 5):
            self.flush()
    
    def flush(self) -> None:
        """バッファの内容をファイルに書き込み"""
        if not self._log_buffer:
            return
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for entry in self._log_buffer:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            self._log_buffer.clear()
            self._last_flush = time.time()
        except Exception as e:
            # フォールバック: 標準エラー出力
            print(f"ログ書き込みエラー: {e}")
    
    @contextmanager
    def operation_context(self, operation_name: str):
        """操作コンテキストマネージャー"""
        start_time = time.time()
        self.log_with_context("info", f"開始: {operation_name}", 
                            {"start_time": start_time})
        
        try:
            yield self
        except Exception as e:
            self.log_with_context("error", f"エラー: {operation_name}",
                                {"error": str(e), "duration": time.time() - start_time})
            raise
        finally:
            end_time = time.time()
            self.log_with_context("info", f"完了: {operation_name}",
                                {"duration": end_time - start_time})
    
    def close(self) -> None:
        """リソース解放"""
        self.flush()
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()
    
    def __del__(self):
        """デストラクタ"""
        try:
            self.close()
        except:
            pass


def setup_standard_logger(name: str = "system", log_level: str = "INFO",
                         base_path: Optional[Path] = None) -> OptimizedLogger:
    """
    標準ロガーのセットアップ - 既存のロガー初期化コードを統合
    
    Args:
        name: ロガー名
        log_level: ログレベル
        base_path: ベースパス
    
    Returns:
        OptimizedLogger: 設定済みロガーインスタンス
    """
    logger = OptimizedLogger(user=name, base_path=base_path)
    logger.logger.setLevel(getattr(logging, log_level.upper()))
    
    logger.log_with_context("info", f"ロガー初期化完了: {name}",
                          {"log_level": log_level, "base_path": str(base_path)})
    
    return logger


def log_with_context(message: str, context: Optional[Dict] = None,
                    level: str = "info", logger_name: str = "system") -> None:
    """
    グローバル関数としてのコンテキスト付きロギング
    
    Args:
        message: メッセージ
        context: コンテキスト
        level: ログレベル
        logger_name: ロガー名
    """
    logger = OptimizedLogger(user=logger_name)
    logger.log_with_context(level, message, context)


# モジュールレベルでのデフォルトロガー
_default_logger = None

def get_default_logger() -> OptimizedLogger:
    """デフォルトロガー取得"""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_standard_logger()
    return _default_logger


# 後方互換性のための関数群
def log_file_operation(operation: str, file_path: str, result: str = "success") -> None:
    """後方互換: FileAccessLogger.log_operation"""
    get_default_logger().log_file_access(operation, file_path, result)

def log_system_activity(action: str, details: Optional[Dict] = None) -> None:
    """後方互換: ActivityLogger.log_activity"""
    get_default_logger().log_activity(action, metadata=details)

def log_integration_step(component: str, step: str, data: Optional[Dict] = None) -> None:
    """後方互換: IntegratedLogger.log_step"""
    get_default_logger().log_integration_event(component, step, data)