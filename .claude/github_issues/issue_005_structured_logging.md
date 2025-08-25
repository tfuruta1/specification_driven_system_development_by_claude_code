# Issue #5: 構造化ログシステムの実装

## 概要
テキストベースのログを構造化（JSON形式）に変更し、ログ分析を容易にする

## 背景
現在のログはテキスト形式で、自動分析や検索が困難

## タスク

### 1. 構造化ログシステムの作成
**新規ファイル**: `.claude/system/core/structured_logger.py`
```python
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from enum import Enum

class LogLevel(Enum):
    """ログレベル"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredLogger:
    """構造化ログシステム"""
    
    def __init__(self, name: str, log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or Path(".claude/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ログファイルパス
        self.json_log_file = self.log_dir / f"{name}_structured.json"
        self.text_log_file = self.log_dir / f"{name}.log"
        
        # 標準ロガーの設定
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # JSONハンドラー
        json_handler = logging.FileHandler(self.json_log_file)
        json_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(json_handler)
        
        # テキストハンドラー（互換性のため）
        text_handler = logging.FileHandler(self.text_log_file)
        text_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        text_handler.setFormatter(text_formatter)
        self.logger.addHandler(text_handler)
        
        # コンソールハンドラー（開発用）
        if sys.stdout.isatty():
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(text_formatter)
            self.logger.addHandler(console_handler)
    
    def _create_log_entry(self, level: str, event: str, 
                         message: Optional[str] = None, **data) -> Dict[str, Any]:
        """ログエントリを作成"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "event": event,
        }
        
        if message:
            entry["message"] = message
        
        # 追加データ
        if data:
            entry["data"] = data
        
        # コンテキスト情報
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            entry["context"] = {
                "file": caller_frame.f_code.co_filename,
                "function": caller_frame.f_code.co_name,
                "line": caller_frame.f_lineno
            }
        
        return entry
    
    def debug(self, event: str, message: Optional[str] = None, **data):
        """デバッグログ"""
        entry = self._create_log_entry(LogLevel.DEBUG.value, event, message, **data)
        self.logger.debug(json.dumps(entry))
    
    def info(self, event: str, message: Optional[str] = None, **data):
        """情報ログ"""
        entry = self._create_log_entry(LogLevel.INFO.value, event, message, **data)
        self.logger.info(json.dumps(entry))
    
    def warning(self, event: str, message: Optional[str] = None, **data):
        """警告ログ"""
        entry = self._create_log_entry(LogLevel.WARNING.value, event, message, **data)
        self.logger.warning(json.dumps(entry))
    
    def error(self, event: str, message: Optional[str] = None, 
              exception: Optional[Exception] = None, **data):
        """エラーログ"""
        if exception:
            import traceback
            data["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        entry = self._create_log_entry(LogLevel.ERROR.value, event, message, **data)
        self.logger.error(json.dumps(entry))
    
    def critical(self, event: str, message: Optional[str] = None, **data):
        """重大エラーログ"""
        entry = self._create_log_entry(LogLevel.CRITICAL.value, event, message, **data)
        self.logger.critical(json.dumps(entry))

class JSONFormatter(logging.Formatter):
    """JSON形式のフォーマッター"""
    
    def format(self, record: logging.LogRecord) -> str:
        # すでにJSON形式の場合はそのまま返す
        if isinstance(record.msg, str) and record.msg.startswith('{'):
            return record.msg
        
        # 通常のメッセージをJSON形式に変換
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "context": {
                "file": record.pathname,
                "function": record.funcName,
                "line": record.lineno
            }
        }
        
        return json.dumps(log_entry)
```

### 2. ログ分析ツールの作成
**新規ファイル**: `.claude/system/core/log_analyzer.py`
```python
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter

class LogAnalyzer:
    """ログ分析ツール"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.logs: List[Dict[str, Any]] = []
        self._load_logs()
    
    def _load_logs(self):
        """ログファイルを読み込み"""
        if not self.log_file.exists():
            return
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    self.logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
    
    def filter_by_level(self, level: str) -> List[Dict[str, Any]]:
        """レベルでフィルタリング"""
        return [log for log in self.logs if log.get('level') == level]
    
    def filter_by_event(self, event: str) -> List[Dict[str, Any]]:
        """イベントでフィルタリング"""
        return [log for log in self.logs if log.get('event') == event]
    
    def filter_by_time_range(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """時間範囲でフィルタリング"""
        filtered = []
        for log in self.logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
                if start <= timestamp <= end:
                    filtered.append(log)
        return filtered
    
    def get_error_summary(self) -> Dict[str, Any]:
        """エラーサマリーを取得"""
        errors = self.filter_by_level('ERROR')
        
        if not errors:
            return {"total_errors": 0}
        
        # エラータイプ別集計
        error_types = Counter()
        for error in errors:
            if 'data' in error and 'exception' in error['data']:
                error_type = error['data']['exception'].get('type', 'Unknown')
                error_types[error_type] += 1
        
        return {
            "total_errors": len(errors),
            "error_types": dict(error_types),
            "recent_errors": errors[-10:]  # 最新10件
        }
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """パフォーマンス関連の洞察を取得"""
        perf_logs = [
            log for log in self.logs 
            if 'data' in log and 'duration' in log.get('data', {})
        ]
        
        if not perf_logs:
            return {"slow_operations": []}
        
        # 遅い操作を特定（1秒以上）
        slow_ops = [
            {
                "event": log['event'],
                "duration": log['data']['duration'],
                "timestamp": log['timestamp']
            }
            for log in perf_logs
            if log['data']['duration'] > 1.0
        ]
        
        return {
            "slow_operations": sorted(slow_ops, key=lambda x: x['duration'], reverse=True)[:10],
            "total_slow_operations": len(slow_ops)
        }
    
    def generate_report(self) -> str:
        """分析レポートを生成"""
        report = ["Log Analysis Report", "=" * 50, ""]
        
        # 全体統計
        report.append(f"Total Logs: {len(self.logs)}")
        
        # レベル別統計
        level_counts = Counter(log.get('level') for log in self.logs)
        report.append("\nLog Levels:")
        for level, count in level_counts.most_common():
            report.append(f"  {level}: {count}")
        
        # エラーサマリー
        error_summary = self.get_error_summary()
        report.append(f"\nTotal Errors: {error_summary['total_errors']}")
        if error_summary.get('error_types'):
            report.append("Error Types:")
            for error_type, count in error_summary['error_types'].items():
                report.append(f"  {error_type}: {count}")
        
        # パフォーマンス洞察
        perf_insights = self.get_performance_insights()
        if perf_insights['slow_operations']:
            report.append(f"\nSlow Operations (>1s): {perf_insights['total_slow_operations']}")
            report.append("Top 5 Slowest:")
            for op in perf_insights['slow_operations'][:5]:
                report.append(f"  {op['event']}: {op['duration']:.2f}s")
        
        return "\n".join(report)
```

### 3. CoreSystemへの適用
**ファイル**: `.claude/system/core/core_system.py`

**変更前**:
```python
import logging
logger = logging.getLogger(__name__)

def organize_files(self) -> Result:
    # ...
    logger.info(f"Moved: {source.name} -> {destination}")
```

**変更後**:
```python
from .structured_logger import StructuredLogger

class CoreSystem:
    def __init__(self):
        # ...
        self.logger = StructuredLogger("core_system")
    
    def organize_files(self) -> Result:
        self.logger.info(
            "file_organization_started",
            "Starting file organization"
        )
        
        # ...
        
        self.logger.info(
            "file_moved",
            source=str(source),
            destination=str(destination),
            size=source.stat().st_size
        )
        
        self.logger.info(
            "file_organization_completed",
            f"Organized {moved_count} files",
            moved_count=moved_count,
            duration=duration
        )
        
        return Result(True, f"Organized {moved_count} files")
```

### 4. ログビューアーの作成
**新規ファイル**: `.claude/system/core/log_viewer.py`
```python
#!/usr/bin/env python3
"""ログビューアー - 構造化ログを見やすく表示"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def view_logs(log_file: Path, level: Optional[str] = None, 
              last_n: Optional[int] = None, follow: bool = False):
    """ログを表示"""
    
    def format_log(log_entry: dict) -> str:
        """ログエントリをフォーマット"""
        timestamp = log_entry.get('timestamp', 'N/A')
        level = log_entry.get('level', 'INFO')
        event = log_entry.get('event', '')
        message = log_entry.get('message', '')
        
        # レベルによる色付け
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m'  # Magenta
        }
        color = colors.get(level, '')
        reset = '\033[0m'
        
        output = f"{color}[{timestamp}] {level:8} {event:30} {message}{reset}"
        
        # データがあれば表示
        if 'data' in log_entry:
            data_str = json.dumps(log_entry['data'], indent=2)
            output += f"\n  Data: {data_str}"
        
        return output
    
    if follow:
        # tail -f のような動作
        import time
        with open(log_file, 'r') as f:
            f.seek(0, 2)  # ファイルの末尾へ
            while True:
                line = f.readline()
                if line:
                    try:
                        log_entry = json.loads(line.strip())
                        if not level or log_entry.get('level') == level:
                            print(format_log(log_entry))
                    except json.JSONDecodeError:
                        pass
                else:
                    time.sleep(0.1)
    else:
        # 通常表示
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if last_n:
                lines = lines[-last_n:]
            
            for line in lines:
                try:
                    log_entry = json.loads(line.strip())
                    if not level or log_entry.get('level') == level:
                        print(format_log(log_entry))
                except json.JSONDecodeError:
                    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='View structured logs')
    parser.add_argument('log_file', help='Path to log file')
    parser.add_argument('--level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Filter by log level')
    parser.add_argument('--last', type=int, help='Show last N lines')
    parser.add_argument('--follow', action='store_true', help='Follow log file (like tail -f)')
    
    args = parser.parse_args()
    view_logs(Path(args.log_file), args.level, args.last, args.follow)
```

### 5. テストの作成
**新規ファイル**: `.claude/project/tests/test_structured_logger.py`
```python
import unittest
import json
import tempfile
from pathlib import Path
from system.core.structured_logger import StructuredLogger

class TestStructuredLogger(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = StructuredLogger("test", Path(self.temp_dir))
    
    def test_info_logging(self):
        """情報ログのテスト"""
        self.logger.info("test_event", "Test message", value=123)
        
        # ログファイルを確認
        log_file = Path(self.temp_dir) / "test_structured.json"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            log_entry = json.loads(f.readline())
            self.assertEqual(log_entry['level'], 'INFO')
            self.assertEqual(log_entry['event'], 'test_event')
            self.assertEqual(log_entry['message'], 'Test message')
            self.assertEqual(log_entry['data']['value'], 123)
    
    def test_error_logging_with_exception(self):
        """例外付きエラーログのテスト"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.logger.error("error_event", "Error occurred", exception=e)
        
        log_file = Path(self.temp_dir) / "test_structured.json"
        with open(log_file, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
            self.assertEqual(log_entry['level'], 'ERROR')
            self.assertIn('exception', log_entry['data'])
            self.assertEqual(log_entry['data']['exception']['type'], 'ValueError')
```

## 受け入れ条件
- [ ] 構造化ログシステムが実装されている
- [ ] JSON形式でログが出力される
- [ ] ログ分析ツールが動作する
- [ ] ログビューアーが動作する
- [ ] 既存のログ出力が構造化ログに置き換えられている
- [ ] テストが全て通る

## 実装手順
1. structured_logger.pyを作成
2. log_analyzer.pyを作成
3. log_viewer.pyを作成
4. CoreSystemのログを構造化ログに変更
5. テストを作成・実行

## 優先度
**中**

## 見積もり工数
3-4時間

## ラベル
- enhancement
- logging
- observability